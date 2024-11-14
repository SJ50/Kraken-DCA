import base64
import hashlib
import hmac
import math
import time
from datetime import datetime, timedelta
from pip._vendor import requests 
import boto3
import json
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_nonce() -> str:
    return str(int(time.time() * 1000))

def round_down_decimal_number(number: float, desired_result_decimals: int) -> float:
    multiplier: int = 10**desired_result_decimals
    return math.floor(number * multiplier) / multiplier

def get_api_sign(api_path: str, urlencoded_body: str, nonce: str, private_key: str) -> str:
    api_sha256: hashlib._Hash = hashlib.sha256(nonce.encode() + urlencoded_body.encode())
    api_hmac: hmac.HMAC = hmac.new(
        base64.b64decode(private_key),
        api_path.encode() + api_sha256.digest(),
        hashlib.sha512,
    )
    api_signature: bytes = base64.b64encode(api_hmac.digest())
    return api_signature.decode()

def get_server_time() -> float:
    response = requests.get("https://api.kraken.com/0/public/Time")
    response.raise_for_status()
    server_time = response.json()["result"]["unixtime"]
    return float(server_time)

def get_bid_price(trading_pair: str) -> str:
    response = requests.get(f"https://api.kraken.com/0/public/Ticker?pair={trading_pair}")
    response.raise_for_status()
    market_data = response.json()
    top_market_bid: float = float(market_data["result"][trading_pair]["b"][0])
    return str(round_down_decimal_number(top_market_bid, desired_result_decimals=6))

def get_trade_volume(budget: float, bid_price: str) -> str:
    return str(budget / float(bid_price))

def get_aws_ssm_securestring_parameter(paramname: str) -> str:
    client = boto3.client("ssm")
    response = client.get_parameter(Name=paramname, WithDecryption=True)
    return response["Parameter"]["Value"]

def my_balance_on_kraken(private_key: str, public_key: str) -> dict:
    nonce: str = get_nonce()
    url_encoded_body: str = f"nonce={nonce}"
    api_sign: str = get_api_sign(
        api_path="/0/private/Balance",
        urlencoded_body=url_encoded_body,
        nonce=nonce,
        private_key=private_key,
    )

    response = requests.post(
        url="https://api.kraken.com/0/private/Balance",
        data={"nonce": nonce},
        headers={"API-Key": public_key, "API-Sign": api_sign},
    )
    response.raise_for_status()
    return response.json()

def calculate_order_expiration(server_time, order_expires):
    server_datetime = datetime.fromtimestamp(int(server_time))
    expiration_datetime = server_datetime + timedelta(minutes=(int(order_expires) - 1))
    return int(expiration_datetime.timestamp())

def place_limit_order_on_kraken(
    crypto_to_buy: str, currency: str, trading_pair: str, budget: float, 
    private_key: str, public_key: str, order_expires: str
) -> dict:
    bid_price: str = get_bid_price(trading_pair)
    volume: str = get_trade_volume(budget, bid_price)
    nonce: str = get_nonce()
    server_time = get_server_time()
    order_expires_in = calculate_order_expiration(server_time, order_expires)
    
    url_encoded_body: str = (
        f"nonce={nonce}&ordertype=limit&pair={trading_pair}&price={bid_price}"
        f"&type=buy&volume={volume}&oflags=fciq&timeinforce=GTD&expiretm={order_expires_in}"
    )
    
    api_sign: str = get_api_sign(
        api_path="/0/private/AddOrder",
        urlencoded_body=url_encoded_body,
        nonce=nonce,
        private_key=private_key,
    )
    
    logger.info(f"Placing order: {volume}{crypto_to_buy} @ {bid_price}{currency}")
    
    response = requests.post(
        url="https://api.kraken.com/0/private/AddOrder",
        data={
            "nonce": nonce,
            "ordertype": "limit",
            "pair": trading_pair,
            "price": bid_price,
            "type": "buy",
            "volume": volume,
            "oflags": "fciq",
            "timeinforce": "GTD",
            "expiretm": order_expires_in
        },
        headers={"API-Key": public_key, "API-Sign": api_sign},
    )
    
    response.raise_for_status()
    return response.json()

def lambda_handler(event: dict, context) -> dict:
    try:
        crypto_to_buy: str = event["crypto_to_buy"]
        trading_pair: str = event["trading_pair"]
        currency: str = event["currency"]
        order_expires: str = event["order_expires"]
        
        private_key: str = get_aws_ssm_securestring_parameter("kraken-private-api-key")
        public_key: str = get_aws_ssm_securestring_parameter("kraken-public-api-key")
        
        balance_data = my_balance_on_kraken(private_key=private_key, public_key=public_key)
        
        if 'error' in balance_data and balance_data['error']:
            raise ValueError(f"Error fetching balance: {balance_data['error']}")
        
        budget = float(balance_data['result'][currency])
        
        order_data = place_limit_order_on_kraken(
            crypto_to_buy=crypto_to_buy,
            currency=currency,
            trading_pair=trading_pair,
            budget=budget,
            private_key=private_key,
            public_key=public_key,
            order_expires=order_expires,
        )
        
        if 'error' in order_data and order_data['error']:
            raise ValueError(f"Error placing order: {order_data['error']}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Order placed successfully',
                'result': order_data['result']
            })
        }
    
    except KeyError as e:
        logger.error(f"Missing required parameter: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing required parameter', 'error': str(e)})
        }
    
    except ValueError as e:
        logger.error(str(e))
        return {
            'statusCode': 400,
            'body': json.dumps({'message': str(e)})
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'API request failed', 'error': str(e)})
        }
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)})
        }
