# --- Database ---
resource "aws_db_instance" "default" {
  allocated_storage    = 10
  db_name              = "mydb"
  engine               = "mysql"
  engine_version       = "5.7"
  instance_class       = "db.t3.micro"
  username             = var.db_username
  password             = var.db_password # Sensitive!
  parameter_group_name = "default.mysql5.7"
  skip_final_snapshot  = true
  
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
}

resource "aws_security_group" "db_sg" {
  name        = "database-sg"
  vpc_id      = aws_vpc.main_vpc.id

  # Only allow traffic from Web Server
  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.web_sg.id]
  }
}