terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = "ap-south-2"
  profile = "authprofile"
}

# Define servers using map
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
  ami           = "ami-02774d409be696d81" # Amazon Linux 2 AMI (replace with your region's AMI)
  instance_type = "t3.micro"
  #key_name      = "myServerKey" # Replace with your .pem file name (without .pem extension)
  #key_name       = "myServerKey.pem" # Replace with your .pem file name

  tags = {
    Name = each.value.name
  }
}

# Output instance IDs
output "instance_ids" {
  value       = { for key, instance in aws_instance.servers : key => instance.id }
  description = "IDs of all created instances"
}
