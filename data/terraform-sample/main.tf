provider "aws" {
  region = "eu-west-1"
}

# --- VPC Module ---
resource "aws_vpc" "main_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "production-vpc"
    Project = "Phoenix"
  }
}

resource "aws_subnet" "public_subnet" {
  vpc_id     = aws_vpc.main_vpc.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "eu-west-1a"
}

resource "aws_subnet" "private_subnet" {
  vpc_id     = aws_vpc.main_vpc.id
  cidr_block = "10.0.2.0/24"
  availability_zone = "eu-west-1b"
}

# --- Compute ---
resource "aws_instance" "web_server" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public_subnet.id
  
  # Critical: Security Group Attachment
  vpc_security_group_ids = [aws_security_group.web_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              echo "Hello, World" > index.html
              python3 -m http.server 80
              EOF

  tags = {
    Name = "web-server-01"
    Environment = "Production"
  }
}