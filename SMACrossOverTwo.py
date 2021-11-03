import asyncio

from binance import Client
import pandas as pd
import os

# py -m pip show websocket-client
import websocket
import json

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from binance import BinanceSocketManager

# Init binance API and websocket
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')
client = Client(api_key, api_secret, {"timeout": 20})
bsm = BinanceSocketManager(client)

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
historicals['ST'] = 52


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

    return liveST, liveLT


async def main(coin, qty, SL_limit, open_position=False):
    bm = BinanceSocketManager(client)
    ts = bm.trade_socket(coin)
    async with ts as tscm:
        while True:
            res = await tscm.recv()
            if res:
                frame = createframe(res)
                print(frame)
                livest, livelt = liveSMA(historicals, frame)
                if livest > livelt and not open_position:
                    order = client.create_order(symbol=coin,
                                                side='BUY',
                                                type='MARKET',
                                                quantity=qty)
                    print(order)
                    buyprice = float(order['fills'][0]['price'])
                    open_position = True
                if open_position:
                    if frame.Price[0] < buyprice * SL_limit or frame.Price[0] > 1.02 * buyprice:
                        order = client.create_order(symbol=coin,
                                                    side='SELL',
                                                    type='MARKET',
                                                    quantity=qty)
                        print(order)
                        loop.stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main('ADAUSDT', 8, 0.98))
