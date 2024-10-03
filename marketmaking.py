import os
import time
from kiteconnect import KiteConnect
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
access_token = os.getenv('ACCESS_TOKEN')

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)


symbol = "NSE:RELIANCE"
spread = 0.5
order_quantity = 1 
refresh_time = 5 

def get_bid_ask(symbol):
    try:
        ltp_data = kite.ltp([symbol])
        ltp = ltp_data[symbol]['last_price']
        depth = kite.quote([symbol])[symbol]['depth']
        bid_price = depth['buy'][0]['price']
        ask_price = depth['sell'][0]['price']
        return ltp, bid_price, ask_price
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return None, None, None

def place_orders(symbol, bid_price, ask_price, quantity):
    try:
        buy_order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=kite.EXCHANGE_NSE,
            tradingsymbol=symbol.split(":")[1],
            transaction_type=kite.TRANSACTION_TYPE_BUY,
            quantity=quantity,
            price=bid_price,
            order_type=kite.ORDER_TYPE_LIMIT,
            product=kite.PRODUCT_MIS
        )
        # Buy order placed 

        # Place sell order at the ask price
        sell_order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=kite.EXCHANGE_NSE,
            tradingsymbol=symbol.split(":")[1],
            transaction_type=kite.TRANSACTION_TYPE_SELL,
            quantity=quantity,
            price=ask_price,
            order_type=kite.ORDER_TYPE_LIMIT,
            product=kite.PRODUCT_MIS
        )
        # Sell order placed

        return buy_order_id, sell_order_id
    except Exception as e:
        print(f"Error placing orders: {e}")
        return None, None


def cancel_orders(buy_order_id, sell_order_id):
    try:
        if buy_order_id:
            kite.cancel_order(variety=kite.VARIETY_REGULAR, order_id=buy_order_id)
            print(f"Buy order {buy_order_id} cancelled.")
        if sell_order_id:
            kite.cancel_order(variety=kite.VARIETY_REGULAR, order_id=sell_order_id)
            print(f"Sell order {sell_order_id} cancelled.")
    except Exception as e:
        print(f"Error cancelling orders: {e}")


def market_making(symbol, spread, order_quantity, refresh_time):
    buy_order_id = None
    sell_order_id = None

    while True:
        
        ltp, bid_price, ask_price = get_bid_ask(symbol)

        if bid_price and ask_price:
            
            current_spread = ask_price - bid_price
            if current_spread >= spread:
                print(f"Current Spread: {current_spread}, Bid: {bid_price}, Ask: {ask_price}")

                if buy_order_id or sell_order_id:
                    
                    cancel_orders(buy_order_id, sell_order_id)

                
                buy_order_id, sell_order_id = place_orders(symbol, bid_price, ask_price, order_quantity)

            else:
                print(f"Spread too narrow ({current_spread}), not placing orders.")

        else:
            print("Error fetching market prices, retrying...")
        time.sleep(refresh_time)

if __name__ == "__main__":
    market_making(symbol, spread, order_quantity, refresh_time)
