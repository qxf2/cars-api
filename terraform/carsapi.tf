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

// App server EC2 instance
resource "aws_instance" "carsapp_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t2.micro"
  key_name               = aws_key_pair.deployer.key_name
  vpc_security_group_ids = [aws_security_group.carsapp_sg.id]
  user_data              = <<-EOF
    #!/bin/bash
    export DEBIAN_FRONTEND=noninteractive
    # Create code directory and clone repo
    su - ubuntu -c "mkdir -p /home/ubuntu/code"
    su - ubuntu -c "cd /home/ubuntu/code && git clone https://github.com/qxf2/cars-api.git"
    
    # System Update & Package Installation as root
    apt-get update
    apt-get install -y software-properties-common
    add-apt-repository -y universe
    apt-get update
    apt-get -y upgrade
    apt-get install -y python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools nginx python3-venv
    # Install Certbot Nginx package
    apt-get install -y python3-certbot-nginx

    # Setup virtual environment in the code directory
    su - ubuntu -c "cd /home/ubuntu/code && python3 -m venv venv-carsapi"
    
    # Activate virtual environment and install dependencies
    su - ubuntu -c "source /home/ubuntu/code/venv-carsapi/bin/activate && pip install -r /home/ubuntu/code/cars-api/requirements.txt && pip install gunicorn"

    # Systemd service file setup
    cat << EOF_SERVICE > /etc/systemd/system/carsapi.service
    [Unit]
    Description=Gunicorn instance to serve carsapi
    After=network.target
    StartLimitIntervalSec=0

    [Service]
    WorkingDirectory=/home/ubuntu/code/cars-api
    Environment="PATH=/home/ubuntu/code/venv-carsapi/bin"
    ExecStart=/home/ubuntu/code/venv-carsapi/bin/gunicorn --workers 3 -b 0.0.0.0:5000 cars_app:app
    Restart=always
    RestartSec=1

    [Install]
    WantedBy=multi-user.target
    EOF_SERVICE

    # Reload daemon and start service
    sudo systemctl daemon-reload
    sudo systemctl start carsapi.service
    sudo systemctl enable carsapi.service
    # NGINX setup
    cat << 'EOF_NGINX' > /etc/nginx/sites-available/carsapi
    server {
      listen 80;
      server_name _;

      location / {
        include proxy_params;
        proxy_pass http://0.0.0.0:5000;
      }
    }
    EOF_NGINX

    # Link and reload NGINX
    sudo ln -s /etc/nginx/sites-available/carsapi /etc/nginx/sites-enabled
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