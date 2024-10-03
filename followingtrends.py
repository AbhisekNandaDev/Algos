import pandas as pd
import talib
from kiteconnect import KiteConnect
import os

load_dotenv()

api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
access_token = os.getenv('ACCESS_TOKEN')

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

def fetch_historical_data(ticker, interval='5minute', duration=7):
    instrument_token = kite.ltp(ticker)[ticker]['instrument_token']
    data = kite.historical_data(instrument_token, pd.to_datetime('today') - pd.DateOffset(days=duration), pd.to_datetime('today'), interval)
    df = pd.DataFrame(data)
    return df

def trend_following_strategy(ticker):
    df = fetch_historical_data(ticker)
    df['ema_50'] = talib.EMA(df['close'], timeperiod=50)
    df['ema_200'] = talib.EMA(df['close'], timeperiod=200)
    df['signal'] = 0
    df['signal'][df['ema_50'] > df['ema_200']] = 1  
    df['signal'][df['ema_50'] < df['ema_200']] = -1  
    df['position'] = df['signal'].diff()

    return df

def place_order(symbol, signal):
    if signal == 1:
        # Buying
        kite.place_order(variety=kite.VARIETY_REGULAR,
                         exchange=kite.EXCHANGE_NSE,
                         tradingsymbol=symbol,
                         transaction_type=kite.TRANSACTION_TYPE_BUY,
                         quantity=1,
                         order_type=kite.ORDER_TYPE_MARKET,
                         product=kite.PRODUCT_MIS)
    elif signal == -1:
        # Selling
        kite.place_order(variety=kite.VARIETY_REGULAR,
                         exchange=kite.EXCHANGE_NSE,
                         tradingsymbol=symbol,
                         transaction_type=kite.TRANSACTION_TYPE_SELL,
                         quantity=1,
                         order_type=kite.ORDER_TYPE_MARKET,
                         product=kite.PRODUCT_MIS)
    else:
        print(f"Holding position on {symbol}")

def execute_strategy(ticker):
    df = trend_following_strategy(ticker)
    last_signal = df['position'].iloc[-1]
    place_order(ticker, last_signal)

if __name__ == "__main__":
    stock_symbol = 'NSE:INFY'
    execute_strategy(stock_symbol)
