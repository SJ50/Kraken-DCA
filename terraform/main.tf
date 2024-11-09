terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.36.1"
    }
  }
  
  backend "s3" {
    bucket = "sj50-aws-remote-tfstate-tf-state-us-east-1"
    key    = "kraken-dca/terraform.tfstate"
    region = "us-east-1"

    dynamodb_table = "sj50-aws-remote-tfstate"
    encrypt        = true
  }
}

provider "aws" {
  region = "us-east-1"
}