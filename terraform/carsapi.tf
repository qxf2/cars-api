provider "aws" {
  region = var.aws_region
  profile = var.profile
}

// Generate a secure private TLS key
resource "tls_private_key" "carsapiprivate" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "deployer" {
  key_name   = var.key_name
  public_key = tls_private_key.carsapiprivate.public_key_openssh
  provisioner "local-exec" {
    command = <<-EOT
      echo '${tls_private_key.carsapiprivate.private_key_pem}' > "${var.private_key_path}/${var.key_name}.pem"
      chmod 400 "${var.private_key_path}/${var.key_name}.pem"
    EOT
  }
}

locals {
  # Create the contents of the carsapi service file using the template
  carsapi_service_content = templatefile("${path.module}/carsapi.service.tpl", {
    home_directory = "/home/ubuntu"
  })
  
  # Create the contents of the NGINX configuration file using the template
  nginx_conf_content = templatefile("${path.module}/nginx.conf.tpl", {})
}

resource "aws_instance" "carsapp_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t2.micro"
  key_name               = aws_key_pair.deployer.key_name
  vpc_security_group_ids = [aws_security_group.carsapp_sg.id]
  user_data              = <<-EOF
    #!/bin/bash
    export HOME="/home/ubuntu"
    export DEBIAN_FRONTEND=noninteractive
    # Variables for file paths
    SERVICE_FILE="/etc/systemd/system/carsapi.service"
    NGINX_CONF="/etc/nginx/sites-available/carsapi"

    # Create code directory and clone repo
    su - ubuntu -c "mkdir -p $HOME/code"
    su - ubuntu -c "cd $HOME/code && git clone https://github.com/qxf2/cars-api.git"
    
    # System Update & Package Installation as root
    apt-get update
    apt-get install -y software-properties-common
    add-apt-repository -y universe
    apt-get update
    apt-get -y upgrade
    apt-get install -y python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools nginx python3-venv
    # Install Certbot Nginx package
    apt-get install -y python3-certbot-nginx

    # Setup virtual environment and install dependencies
    su - ubuntu -c "cd \$HOME/code && python3 -m venv venv-carsapi"
    
    # Activate virtual environment and install dependencies
    su - ubuntu -c "source \$HOME/code/venv-carsapi/bin/activate && pip install -r \$HOME/code/cars-api/requirements.txt && pip install gunicorn"

    # Generate systemd service file from template provided by local variable
    echo "${local.carsapi_service_content}" > $SERVICE_FILE

    # Reload daemon and start service
    sudo systemctl daemon-reload
    sudo systemctl start carsapi.service
    sudo systemctl enable carsapi.service

    # Generate NGINX configuration file from template provided by local variable
    echo "${local.nginx_conf_content}" > $NGINX_CONF

    # Link and reload NGINX
    sudo ln -s /etc/nginx/sites-available/carsapi /etc/nginx/sites-enabled
    sudo rm /etc/nginx/sites-enabled/default
    sudo nginx -t
    sudo systemctl reload nginx
    # Configure certbot for SSL/TLS certificate installation
    sudo certbot --nginx --non-interactive --agree-tos -m mak@qxf2.com -d cars-app.qxf2.com -d www.cars-app.qxf2.com --redirect
  EOF
  
  tags = {
    Name = "carsapi"
  }
}


// EBS Volume
resource "aws_ebs_volume" "carsapp_volume" {
  availability_zone = aws_instance.carsapp_server.availability_zone
  size              = 8
  type              = "gp2"

  tags = {
    Name = "carsapi"
  }
}

// Attach the volume to the server
resource "aws_volume_attachment" "ebs_attach" {
  device_name = "/dev/sdh"
  volume_id   = aws_ebs_volume.carsapp_volume.id
  instance_id = aws_instance.carsapp_server.id
}

# deleting the private key when terminating the instance.
resource "null_resource" "delete_key" {
  triggers = {
    key_path = "${var.private_key_path}/${var.key_name}.pem" 
    }
provisioner "local-exec" {
  when = destroy
  command = "rm -f ${self.triggers.key_path}"
  on_failure = continue // This allows the destroy provisioner to not fail even if the file doesn't exist.
}
depends_on = [ aws_key_pair.deployer ]
}
