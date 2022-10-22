import base64
import hashlib
import hmac
import math
import time

import requests


def place_limit_order(ticker:str, budget:float, private_key:str, public_key:str):

    bid_price:str = get_bid_price(ticker)
    volume:str = get_trade_volume(budget, bid_price)
    nonce:int = int(time.time()*1000)
    api_sign:str = get_api_sign(nonce=str(nonce), ticker=ticker, bid_price=bid_price, volume=volume, private_key=private_key)

    requests.post(
        url="https://api.kraken.com/0/private/AddOrder",
        data={
                "nonce": nonce,
                "ordertype": "limit",
                "pair": ticker,
                "price": bid_price,
                "type": "buy",
                "volume": volume,
        },
        headers={
            "API-Key": public_key,
            "API-Sign": api_sign
        }
    )

def round_down(n:float, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier

def get_api_sign(nonce:str, ticker:str, bid_price:str, volume:str, private_key:str) ->str:
    api_path = '/0/private/AddOrder'
    api_post=f'nonce={nonce}&ordertype=limit&pair={ticker}&price={bid_price}&type=buy&volume={volume}'

    api_sha256 = hashlib.sha256(nonce.encode('utf8') + api_post.encode('utf8'))
    api_hmac = hmac.new(base64.b64decode(private_key), api_path.encode('utf8') + api_sha256.digest(), hashlib.sha512)
    api_signature:bytes = base64.b64encode(api_hmac.digest())
    api_signature_decoded:str = api_signature.decode()
    return api_signature_decoded

def get_bid_price(ticker:str) -> str:
    market_data:dict = requests.get(url=f"https://api.kraken.com/0/public/Ticker?pair={ticker}").json()
    top_market_bid = float(market_data["result"][ticker]["b"][0])
    my_bid_price = str(round_down(top_market_bid, decimals=6))
    
    return my_bid_price

def get_trade_volume(budget:float, bid_price:str) -> str:
    return str(budget/float(bid_price))

# TODO: Am i passing arguments correctly? Should it be in body or in a header??