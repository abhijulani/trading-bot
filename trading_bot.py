import os
import sys
import logging
import argparse
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv


# 1. LOGGING LAYER

def setup_logger():
    logger = logging.getLogger("TradingBot")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Log to file
    file_handler = logging.FileHandler("trading_bot.log")
    file_handler.setFormatter(formatter)

    # Log to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

logger = setup_logger()


# 2. VALIDATION LAYER

def validate_inputs(symbol, side, order_type, quantity, price):
    if not symbol.endswith("USDT"):
        raise ValueError("Symbol must be a USDT pair (e.g., BTCUSDT)")
    if side not in ["BUY", "SELL"]:
        raise ValueError("Side must be BUY or SELL")
    if order_type not in ["MARKET", "LIMIT"]:
        raise ValueError("Order type must be MARKET or LIMIT")
    if quantity <= 0:
        raise ValueError("Quantity must be greater than 0")
    if order_type == "LIMIT" and (price is None or price <= 0):
        raise ValueError("Price is required and must be > 0 for LIMIT orders")


# 3. API / CLIENT LAYER

class OrderManager:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_API_SECRET")
        
        if not api_key or not api_secret:
            raise ValueError("API Keys not found in .env file!")
            
        # Initialize for Testnet
        self.client = Client(api_key, api_secret, testnet=True)

    def place_order(self, symbol, side, order_type, quantity, price=None):
        try:
            params = {
                "symbol": symbol.upper(),
                "side": side.upper(),
                "type": order_type.upper(),
                "quantity": quantity,
            }

            if order_type.upper() == "LIMIT":
                params["price"] = str(price)
                params["timeInForce"] = "GTC"

            logger.info(f"Request: {params}")
            
            # Execute on Futures Testnet
            response = self.client.futures_create_order(**params)
            
            logger.info(f"Response: {response}")
            return response

        except BinanceAPIException as e:
            logger.error(f"Binance Error: {e.message}")
            return None
        except Exception as e:
            logger.error(f"System Error: {str(e)}")
            return None


# 4. CLI / EXECUTION LAYER

def main():
    parser = argparse.ArgumentParser(description="Binance Futures Testnet Bot")
    parser.add_argument("--symbol", type=str, required=True)
    parser.add_argument("--side", type=str, choices=["BUY", "SELL"], required=True)
    parser.add_argument("--type", type=str, choices=["MARKET", "LIMIT"], required=True)
    parser.add_argument("--quantity", type=float, required=True)
    parser.add_argument("--price", type=float)

    args = parser.parse_args()

    try:
        # Validate
        validate_inputs(args.symbol, args.side, args.type, args.quantity, args.price)

        # Execute
        manager = OrderManager()
        res = manager.place_order(args.symbol, args.side, args.type, args.quantity, args.price)

        if res:
            print("\n✅ ORDER SUCCESSFUL")
            print(f"ID: {res.get('orderId')}")
            print(f"Status: {res.get('status')}")
            print(f"Filled Qty: {res.get('executedQty')}")
        else:
            print("\n❌ ORDER FAILED (Check trading_bot.log)")

    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")

if __name__ == "__main__":
    main()