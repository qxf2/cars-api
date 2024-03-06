/*
terraform/variables.tf
Modify default values of variables as needed for aws_region, profile, keyname*/

variable "aws_region" {
  default = "us-east-1"
  description = "The AWS region to create resources in"
  type        = string
}

variable "profile" {
  default = "personal"
  type    = string
}

variable "key_name" {
  description = "The EC2 Key Pair name"
  default = "carsapi-key-pair"
  type        = string
}

# to declare private key path
variable "private_key_path" {
  default = "/tmp"
  type        = string
  description = "Path to the PEM private key file"
}

variable "home_directory" {
  default = "/home/ubuntu"
  type        = string
  description = "Path to the home directory"
}