from fastapi import FastAPI, HTTPException
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from pydantic import BaseModel
import os

# Initialize FastAPI app
app = FastAPI()

# Configure Alpaca credentials - for Vercel, set these in the Vercel dashboard
alpaca_api = os.environ.get("ALPACA_API_KEY")
alpaca_secret = os.environ.get("ALPACA_SECRET_KEY")
trading_client = TradingClient(alpaca_api, alpaca_secret, paper=True)

# Pydantic model for order request
class OrderRequest(BaseModel):
    symbol: str
    quantity: int

@app.get("/api/account")
async def get_account():
    try:
        account = trading_client.get_account()
        return account
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/order")
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

@app.get("/api")
async def root():
    return {"message": "Hello World"}

@app.get("/test")
async def test_endpoint():
    return {"message":"test"}

# Fix the main block to properly run the server

# if __name__ == "__main__":  # Fix the string comparison
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
