module "bootstrap" {
  source = "trussworks/bootstrap/aws"

  region               = "us-east-1"
  account_alias        = var.account_alias
  dynamodb_table_name  = var.dynamodb_table_name
  manage_account_alias = false
}

variable "account_alias" {
  type = string
  default = "sj50-aws-remote-tfstate"
}

variable "dynamodb_table_name" {
  type = string
  default = "sj50-aws-remote-tfstate"
}