# --- Security Groups ---

# Alerta: Este grupo permite tráfico HTTP abierto
resource "aws_security_group" "web_sg" {
  name        = "web-server-sg"
  description = "Allow HTTP traffic"
  vpc_id      = aws_vpc.main_vpc.id

  ingress {
    description = "HTTP from Internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH only from VPN"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"] # Internal VPN only
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}