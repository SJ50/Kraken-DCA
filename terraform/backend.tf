# resource "aws_s3_bucket" "terraform_state" {
#   bucket = "sjain-aws-remote-tfstate"

#   lifecycle {
#     prevent_destroy = true
#   }
# }

# resource "aws_s3_bucket_versioning" "enabled" {
#   bucket = aws_s3_bucket.terraform_state.id
#   versioning_configuration {
#     status = "Enabled"
#   }
# }

# resource "aws_dynamodb_table" "terraform_locks" {
#   name         = "sjain-aws-remote-tfstate-locks"
#   billing_mode = "PAY_PER_REQUEST"
#   hash_key     = "LockID"

#   attribute {
#     name = "LockID"
#     type = "S"
#   }
# }

terraform {
  backend "s3" {
    bucket = "sjain-aws-remote-tfstate"
    key    = "kraken-dca/terraform.tfstate"
    region = "us-east-1"

    dynamodb_table = "sjain-aws-remote-tfstate"
    encrypt        = true
  }
}