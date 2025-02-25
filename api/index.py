import requests
from fastapi import FastAPI, HTTPException
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv
import os
from pydantic import BaseModel
import re
import logging
from datetime import datetime
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables

load_dotenv()

# Initialize FastAPI app

app = FastAPI(title="Alpaca Trading API")

# Configure Alpaca credentials
alpaca_api = os.getenv("ALPACA_API_KEY")
alpaca_secret = os.getenv("ALPACA_SECRET_KEY")
print("alpaca_api: ", alpaca_api)
print("alpaca_secret: ", alpaca_secret)
trading_client = TradingClient(alpaca_api, alpaca_secret, paper=True)
quantity = os.getenv("QUANTITY")

# Pydantic model for order request
class SignalRequest(BaseModel):
    message: str

    def parse_signal(self):
        # Parse the message like "buySignal\nsymbol : CRYPTO10\nprice : 17697.7"
        lines = self.message.split('\n')
        
        signal_type = lines[0]  # "buySignal" or "sellSignal"
        
        # Extract symbol and price using regex or split
        symbol_match = re.search(r'symbol : (.+)', self.message)
        quantity_match = re.search(r'quantity : (.+)', self.message)
        price_match = re.search(r'price : (.+)', self.message)
        
        symbol = symbol_match.group(1) if symbol_match else None
        quantity = float(quantity_match.group(1)) if quantity_match else None
        price = float(price_match.group(1)) if price_match else None
        
        return {
            "signal_type": signal_type,
            "symbol": symbol,
            "quantity": quantity,
            "price": price
        }


@app.post("/signal")
async def receive_signal(signal_request: SignalRequest):
    
    try:
        parsed_data = signal_request.parse_signal()
        logger.info(f"[{datetime.now()}] Received signal endpoint called with data: {parsed_data}")
        
        # Handle buy signals
        if parsed_data["signal_type"] == "buyOrder":
            symbol = parsed_data["symbol"]
            quantity = parsed_data["quantity"]
            # Your buy order logic here
            result = await create_order(symbol,quantity)
            return {"message": "Buy order processed", "buy_result->": result}
        
        # Handle sell signals
        elif parsed_data["signal_type"] == "sellOrder":
            # Your sell order logic here
            symbol = parsed_data["symbol"]
            quantity = parsed_data["quantity"]
            result = await create_sell_order(symbol,quantity)
            return {"message": "Sell order processed", "sell_result->": result}
            
        return {"message": "Signal received", "data": parsed_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/account")
async def get_account():
    logger.info(f"[{datetime.now()}] Account endpoint called")
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

async def create_order(symbol,quantity):
    try:
        print("create_order2--------->occured",symbol)
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        print("market_order_data: ", market_order_data)
        market_order = trading_client.submit_order(order_data=market_order_data)
        logging.info(f"[{datetime.now()}] Buy order created for symbol: {symbol}, quantity: {quantity}")
        return market_order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/sellOrder")
async def create_sell_order(symbol , quantity):
    try:
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        market_order = trading_client.submit_order(order_data=market_order_data)
        return market_order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/test")
async def test_endpoint():
    print("test")
    return {"message":"test url"}

# Fix the main block to properly run the server
if __name__ == "__main__":  # Fix the string comparison
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
