# Define servers using map using locals
locals {
  servers = {
    "Prod" = {
      name = "Prod server"
    }
    "Non-prod" = {
      name = "Non-prod server"
    }
  }
}

# Create EC2 Instances using for_each
resource "aws_instance" "servers" {
  for_each      = local.servers
  ami           = "ami-02774d409be696d81"   # Amazon Linux 2 AMI (replace with your region's AMI)
  instance_type = "t3.micro"
  tags = {
    Name = each.value.name
  }
}

# Output instance IDs
output "instance_ids" {
  value       = { for key, instance in aws_instance.servers : key => instance.id }
  description = "IDs of all created instances"
}
