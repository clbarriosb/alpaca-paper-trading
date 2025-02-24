import requests
from fastapi import FastAPI, HTTPException
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv
import os
from pydantic import BaseModel
# Load environment variables

load_dotenv()

# Initialize FastAPI app

app = FastAPI(title="Alpaca Trading API")

# Configure Alpaca credentials
alpaca_api = os.getenv("ALPACA_API_KEY")
alpaca_secret = os.getenv("ALPACA_SECRET_KEY")
trading_client = TradingClient(alpaca_api, alpaca_secret, paper=True)

# Pydantic model for order request
class OrderRequest(BaseModel):
    symbol: str
    quantity: int

@app.get("/account")
async def get_account():
    print("alpaca_api: ", alpaca_api)
    print("alpaca_secret: ", alpaca_secret)
    url = "https://paper-api.alpaca.markets/v2/account"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": alpaca_api,
        "APCA-API-SECRET-KEY": alpaca_secret
    }
    response = requests.get(url, headers=headers)
    return response.json()

@app.post("/order")
async def create_order(order_request: OrderRequest):
    try:
        market_order_data = MarketOrderRequest(
            symbol=order_request.symbol,
            qty=order_request.quantity,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        market_order = trading_client.submit_order(order_data=market_order_data)
        return market_order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# @app.get("/")
# async def root():
#     print("root")
#     return {"message": "Hello World"}

@app.get("/test")
async def test_endpoint():
    print("test")
    return {"message":"test"}

# Fix the main block to properly run the server

# if __name__ == "__main__":  # Fix the string comparison
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
