resource "random_integer" "minutes" {
  min = (23 * 60)
  max = (24 * 60)
  keepers = {
    first = "${timestamp()}"
    }  
}

resource "aws_cloudwatch_event_rule" "kraken_dca_lambda_event_rule" {
  name                = "kraken_dca_lambda_event_rule"
  description         = "Buy BTC every 23-24 hours."
  schedule_expression = "rate(${random_integer.minutes.result} minutes)"
}

locals {
 order_expires = random_integer.minutes.result - 60 
}

resource "aws_cloudwatch_event_target" "kraken_dca_lambda_event_target" {
  arn   = aws_lambda_function.kraken-dca-lambda.arn
  rule  = aws_cloudwatch_event_rule.kraken_dca_lambda_event_rule.name
  input = <<EOF
    {
        "trading_pair": "XBTAUD",
        "crypto_to_buy": "BTC",
        "currency": "ZAUD",
        "order_expires": "${local.order_expires}"
    }
    EOF
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_lambda" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.kraken-dca-lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.kraken_dca_lambda_event_rule.arn
}
# resource "aws_cloudwatch_event_rule" "kraken_btc_withdraw_lambda_event_rule" {
#   name                = "kraken_btc_withdraw_lambda_event_rule"
#   description         = "Withdraw BTC 09:00 UTC on the first of the month"
#   schedule_expression = "cron(0 9 1 * ? *)"
# }

# resource "aws_cloudwatch_event_target" "btc_withdraw_lambda_event_target" {
#   arn   = aws_lambda_function.kraken-withdraw-lambda.arn
#   rule  = aws_cloudwatch_event_rule.kraken_btc_withdraw_lambda_event_rule.name
#   input = <<EOF
#     {
#         "ticker": "XXBT"
#     }
#     EOF
# }

# resource "aws_lambda_permission" "allow_cloudwatch_to_call_withdraw_lambda" {
#   statement_id  = "AllowExecutionFromCloudWatch"
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.kraken-withdraw-lambda.function_name
#   principal     = "events.amazonaws.com"
#   source_arn    = aws_cloudwatch_event_rule.kraken_btc_withdraw_lambda_event_rule.arn
# }
# resource "aws_cloudwatch_event_rule" "kraken_eth_withdraw_lambda_event_rule" {
#   name                = "kraken_eth_withdraw_lambda_event_rule"
#   description         = "Withdraw ETH 09:15 UTC on the first of the month"
#   schedule_expression = "cron(15 9 1 * ? *)"
# }

# resource "aws_cloudwatch_event_target" "eth_withdraw_lambda_event_target" {
#   arn   = aws_lambda_function.kraken-withdraw-lambda.arn
#   rule  = aws_cloudwatch_event_rule.kraken_eth_withdraw_lambda_event_rule.name
#   input = <<EOF
#     {
#         "ticker": "XETH"
#     }
#     EOF
# }

# resource "aws_lambda_permission" "allow_cloudwatch_eth_event_to_call_withdraw_lambda" {
#   statement_id  = "AllowExecutionFromCloudWatchForEthWithdrawal"
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.kraken-withdraw-lambda.function_name
#   principal     = "events.amazonaws.com"
#   source_arn    = aws_cloudwatch_event_rule.kraken_eth_withdraw_lambda_event_rule.arn
# }