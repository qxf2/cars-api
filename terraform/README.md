# terraform configuration files to deploy cars-api app

1) AWS credentials configuration - https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html


2) Steps on how to install Terraform.: https://phoenixnap.com/kb/how-to-install-terraform 

            or

step#1) Run the following commands at the terminal
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -

step#2) sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"

step#3) sudo apt-get update && sudo apt-get install terraform


3) To test the installation successfully, run the command 
        --terraform version


4) change directory to terraform.

5) review variables.tf. Modify as per your requirement.

6) run the command to initialize terraform - terraform init.

7) run the command to validate if any errors - terraform validate.

8) run the command to plan and apply - terraform plan followed by terraform apply --auto-approve.

9) run the command to destroy - terraform destroy --auto-approve.