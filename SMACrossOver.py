from binance import Client
import pandas as pd
import os

# py -m pip show websocket-client
import websocket
import json

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

# Init binance API and websocket
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')
client = Client(api_key, api_secret, {"timeout": 20})

ST = 7
LT = 25


def gethistoricals(symbol, LT):
    df = pd.DataFrame(client.get_historical_klines(symbol,
                                                   '1d',
                                                   str(LT) + 'days ago UTC',
                                                   '1 day ago UTC'))
    closes = pd.DataFrame(df[4])
    closes.columns = ['Close']
    closes['ST'] = closes.Close.rolling(ST - 1).sum()
    closes['LT'] = closes.Close.rolling(LT - 1).sum()
    closes.dropna(inplace=True)

    return closes


historicals = gethistoricals('ADAUSDT', LT)


def SMAstrat(coin, usdt, SL_limit=0.98, open_position=False):
    def on_message(wsapp, message):
        frame = createframe(json.loads(message))
        print(frame)
        qty = round( usdt / frame.Price[0], 2)
        if liveSMA(historicals, frame) and not open_position:
            try:

                order = client.create_order(symbol=coin,
                                            side='BUY',
                                            type='MARKET',
                                            quantity=qty)
                print(order)
                buyprice = float(order['fills'][0]['price'])
                open_posiiton = True

            except BinanceAPIException as e:
                # error handling goes here
                print(e)
            except BinanceOrderException as e:
                # error handling goes here
                print(e)

        if open_posiiton:
            if frame.Price < buyprice * SL_limit or frame.Price > 1.02 * buyprice:
                order = client.create_order(symbol=coin,
                                            side='SELL',
                                            type='MARKET',
                                            quantity=qty)
                print(order)
                quit()

    wsapp = websocket.WebSocketApp(f'wss://stream.binance.com:9443/ws/{coin.lower()}@trade', on_message=on_message)
    wsapp.run_forever()


def on_message(wsapp, message):
    print(createframe(json.loads(message)))


def createframe(msg):
    df = pd.DataFrame([msg])
    df = df.loc[:, ['s', 'E', 'p']]
    df.columns = ['symbol', 'Time', 'Price']
    df.Price = df.Price.astype(float)
    df.Time = pd.to_datetime(df.Time, unit='ms')

    return df


def liveSMA(hist, live):
    liveST = (hist['ST'].values + live.Price.values) / ST
    liveLT = (hist['LT'].values + live.Price.values) / LT

    if liveST > liveLT:
        return True


SMAstrat('BNBUSDT', 2)
