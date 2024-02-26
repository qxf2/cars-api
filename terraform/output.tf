/*The Public IP of the instance displayed on the console*/
output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.carsapp_server.public_ip
}
