#This is the beta version for a stock trading bot.
#He's not an artificial intelligence, so he's not worthy of a name.
#The site used will be alpaca and data from yfinance
#***CAUTION***
#Dataframe may not be accurate. yfinance unreliable for volume data
#Created by Ian Kobi

import webbrowser
import yfinance as yf
import matplotlib as plt
import pandas as pd
import numpy as np
import datetime
from datetime import date
import alpaca_trade_api as tradeapi
import time as t
import pytz
from datetime import datetime as dt
from time import time, sleep
import csv

import sys

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

#Auto launch work playlist
#webbrowser.open('https://www.youtube.com/watch?v=VUSct_4afHo')
#Api documentation for paper brokerage account
key = 'YOURKEYHERE'
sec = 'YOURSECRETKEYHERE'
url = 'https://paper-api.alpaca.markets'
api = tradeapi.REST(key, sec, url, api_version='v2')
account = api.get_account()
equity = account.last_equity
symbol = 'MRNA'
qty = "100"
type = "market"


while 1:
    #Download live 2 minute security data
    df2m = yf.download(
        tickers = 'MRNA',
        period = '30d',
        interval = '2m',
        group_by = True,
        prepost = True,
        threads = True,
        proxy = None
    )

    #Convert index to time to work with time data
    df2m['Time'] = df2m.index
    df2m['Time'] = df2m['Time'].dt.strftime('%H:%M:%S')

    df2m['Date'] = df2m.index
    df2m['Date'] = df2m['Date'].dt.strftime('%Y-%m-%d')

    tz_NY = pytz.timezone('America/New_York')
    datetime_NY = dt.now(tz_NY)

    #Identify which positions of data are within market hours
    #Use session positions for backtesting in the future
    #print(df2m.Histo.iloc[Session]) will return the histo values
    #for our specified times that the market is open
    Session = []
    c = [None] * len(df2m)

    for i in range(0, len(df2m)):
        c[i] = str((df2m.Time).iloc[i])
        mkto = datetime.time(7,30,00)
        mktot = mkto.strftime('%H:%M:%S')
        mktc = datetime.time(10,30,00)
        mktct = mktc.strftime('%H:%M:%S')
        if c[i] >= mktot and c[i] <= mktct:
            Session.append(i)

    #Sort dataframe to only include open hours. This is
    # where the data discrepancy will be if there is one
    df2m = df2m.iloc[Session]

    #Calculate Money Flow for 2 minute security data
    #Formula for Raw Money Flow = Price * Volume
    MF2m = []
    MF2m.append(0)

    for i in range(1, len(df2m.Close)):
        if df2m.Close[i] > df2m.Close[i-1]:
            MF2m.append(MF2m[-1] + df2m.Volume[i]*df2m.Close[i])
        elif df2m.Close[i] + df2m.Close[i-1]:
            MF2m.append(MF2m[-1] - df2m.Volume[i]*df2m.Close[i])
        else:
            MF2m.append(MF2m[-1])
    df2m['MoneyFlow'] = MF2m

    #Calculate Kobi_MACD for 2 minute security data
    #Data Science Reasoning: Kobi_MACD = Moving Average Convergence Divergence
    #of Money Flow best used to spot rapid movements in Money, best also
    #used during market open due to rapid change in MF during market open
    def Kobi_MACD2m(MF2m):
        df2m['EMA3'] = df2m['MoneyFlow'].ewm(span=3, min_periods=6).mean()
        df2m['EMA6'] = df2m['MoneyFlow'].ewm(span=6, min_periods=6).mean()
        df2m['MACD'] = df2m['EMA3'] - df2m['EMA6']
        df2m['Signal'] = df2m['MACD'].ewm(span=9, min_periods=9).mean()
        df2m['Histo'] = df2m['MACD'] - df2m['Signal']
        return df2m.loc[:, ["Histo"]]
    Kobi_MACD2m(df2m)

    # del df2m['MoneyFlow']
    # del df2m['EMA3']
    # del df2m['EMA6']
    # del df2m['MACD']
    # del df2m['Signal']

    #Download daily historical security data
    MRNA = yf.Ticker("MRNA")
    MRNA

    today = date.today()
    #print(today)
    days_ago = datetime.timedelta(days=59)
    lookback = today - days_ago
    #print(lookback)

    #Create Daily Historical Data Frame for stock being analyzed
    df1D = MRNA.history(start=lookback, end=today, interval="1h", prepost=True,
                        proxy = None)
    del df1D['Dividends']
    del df1D['Stock Splits']

    #Include Data Frame of current day for stock being analyzed
    df1DL = yf.download(
        tickers='MRNA',
        period='1d',
        interval='1h',
        group_by=True,
        prepost=True,
        threads=True,
        proxy=None
    )

    del df1DL['Adj Close']

    #Combine the Daily Historical Data Frames
    df1D = pd.concat([df1D,df1DL], ignore_index=False)

    df1D['Time'] = df1D.index
    df1D['Time'] = df1D['Time'].dt.strftime('%H:%M:%S')
    # df1D['Date'] = df1D.index
    # df1D['Date'] = df1D['Date'].dt.strftime('%Y-%m-%d')

    #Use this session to cleanse Data Frame and remove
    #unnecessary data/increase processing speed of code
    Session2 = []
    e = [None] * len(df1D)

    for k in range(0, len(df1D)):
        c[k] = str((df1D.Time).iloc[k])
        mkto = datetime.time(7, 30, 00)
        mktot = mkto.strftime('%H:%M:%S')
        mktc = datetime.time(10, 30, 00)
        mktct = mktc.strftime('%H:%M:%S')
        if c[k] >= mktot and c[k] <= mktct:
            Session2.append(k)

    #Calculate Money Flow for 1 Day historical data
    MF1D = []
    MF1D.append(0)

    for i in range(1, len(df1D.Close)):
        if df1D.Close[i] > df1D.Close[i-1]:
            MF1D.append(MF1D[-1] + df1D.Volume[i]*df1D.Close[i])
        elif df1D.Close[i] + df1D.Close[i-1]:
            MF1D.append(MF1D[-1] - df1D.Volume[i]*df1D.Close[i])
        else:
            MF1D.append(MF1D[-1])
    df1D['MoneyFlow'] = MF1D

    #Calculate Kobi_MACD for 1 Day historical data
    def Kobi_MACD1D(MF1D):
        df1D['EMA12'] = df1D['MoneyFlow'].ewm(span=3, min_periods=3).mean()
        df1D['EMA26'] = df1D['MoneyFlow'].ewm(span=6, min_periods=6).mean()
        df1D['MACD'] = df1D['EMA12'] - df1D['EMA26']
        df1D['Signal'] = df1D['MACD'].ewm(span=9, min_periods=9).mean()
        df1D['Histo'] = df1D['MACD'] - df1D['Signal']
        return df1D.loc[:, ["Histo"]]
    Kobi_MACD1D(df1D)

    # del df1D['MoneyFlow']
    # del df1D['EMA12']
    # del df1D['EMA26']
    # del df1D['MACD']
    # del df1D['Signal']

    #Combine Daily Historical Data Frame with 2 minute
    #Data Frame
    df1D['Date'] = df1D.index
    df1D['Date'] = df1D['Date'].dt.strftime('%Y-%m-%d')
    df2m['SameDate'] = [None]*len(df2m)
    # df2m['DHisto'] = [None]*len(df2m)
    df2m['P1DHisto'] = [None]*len(df2m)
    df2m['P2DHisto'] = [None]*len(df2m)

    SameDate = []
    d1D = [None] * len(df1D)
    d2mD = [None] * len(df2m)

    df1D = df1D.iloc[Session2]

    for i in range(0, len(df1D)):
        d1D[i] = (df1D.Date).iloc[i]
        for j in range(0, len(df2m)):
            d2mD[j] = (df2m.Date).iloc[j]
            if d1D[i] == d2mD[j]:
                # SameDate.append(j)
                # df2m.SameDate[j] = df1D.Date[i]
                # df2m.DHisto[j] = df1D.Histo[i]
                df2m.P1DHisto[j] = df1D.Histo[i-1]
                df2m.P2DHisto[j] = df1D.Histo[i-2]

    Mod = []
    Mod = df2m
    Mod.index = Mod.index.date

    #Create logical conditions to enter & exit orders
    EnterLong =((Mod.Histo.iloc[-2] >= Mod.Histo.iloc[-3]) and (Mod.P1DHisto[-1] > Mod.P2DHisto[-1])) and Mod.Histo.iloc[-2] <=0
    EnterShort =((Mod.Histo.iloc[-2] <= Mod.Histo.iloc[-3]) and (Mod.P1DHisto[-1] < Mod.P2DHisto[-1])) and Mod.Histo.iloc[-2] >=0

    #Determine the trading session time, so automated
    #trading only occurs during this window in time
    Open = datetime.time(9,36,00)
    Close = datetime.time(10,30,00)
    Go = bool(str(Open) <= (datetime_NY.strftime("%H:%M:%S")) <= str(Close))
    Stop = bool((datetime_NY.strftime("%H:%M:%S")) >= str(Close))
    Count = 0

    #Create conditions for pyramiding orders, maximum pyramiding is 3 orders
    if EnterLong and Go and Count<=3:
        api.submit_order(symbol=symbol, qty=qty, type=type, side="buy")
        Count +=1
        sleep(100 - time() % 100)
    if EnterShort and Go and Count>=-3:
        api.submit_order(symbol=symbol, qty=qty, type=type, side="sell")
        Count +=-1
        sleep(100 - time() % 100)
    #Also create end of day closing of all positions
    if Stop:
        api.close_all_positions()
        api.cancel_all_orders()

    #Output current account analytics
    print("Working Hard, Boss!")
    print("Account Status: "+ account.status)
    print("Equity: " + account.last_equity)
    now = dt.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time= ", current_time)
    if (Count<=3 and Count !=0):
        position = api.get_position("MRNA")
        print("Position :" + position.side)
    sleep(20 - time() % 20)
    import os
    clear = lambda: os.system('cls')
    clear()
    #Optional memory usage analytic, useful for determining
    #which model of Raspberry Pi to purchase/amount of RAM needed
    #to run during total program uptime
    import os, psutil;
    print(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)

    #Mod.to_csv('Data.csv')
    Mod.to_csv('C:/Users/ianko/Desktop/SkyArrow Captial/Quant/TWENTYTHREE/Data2.csv')



#gotta add order limiter (limit total orders to 3) count+1 or count-1


#api.submit_order(symbol, qty=qty, type=type, side=side, time_in_force=time_in_force)

#time.sleep(5)

# Buy, Sell = [],[]
# for i in range(2, len(Mod)):
#         if ((Mod.Histo.iloc[i] >= Mod.Histo.iloc[i-1]) and (Mod.DHisto[i] > Mod.P1DHisto[i])) and Mod.Histo.iloc[i] <=0:
#             Buy.append(i)
# for i in range(2, len(Mod)):
#         if ((Mod.Histo.iloc[i] <= Mod.Histo.iloc[i-1]) and (Mod.DHisto[i] < Mod.P1DHisto[i])) and Mod.Histo.iloc[i]>=0:
#             Sell.append(i)

# RealBuys = [i for i in Buy]
# RealSells = [i for i in Sell]
# BuyPrices = Mod.Close.iloc[RealBuys]
# SellPrices = Mod.Close.iloc[RealSells]
#
# if SellPrices.index[0] < BuyPrices.index[0]:
#     SellPrices = SellPrices.drop(SellPrices.index[0])
# elif BuyPrices.index[-1] > SellPrices.index[-1]:
#     BuyPrices = BuyPrices.drop(BuyPrices.index[-1])
#
# profitsrel = []
#
# for i in range(0, len(BuyPrices)):
#     profitsrel.append((SellPrices[i] - BuyPrices[i])/BuyPrices[i])
#
# totalprofit = sum(profitsrel)/len(profitsrel)


#For exiting positions due to changing daily MACD
# positions = api.list_positions()
# for position in positions:
#           if(position.side == 'long') and EnterShort and Go:
#                 api.cancel_all_orders()
#                 api.close_all_positions()
#                 Count = 0
#           else(position.side == 'short') and EnterLong and Go:
#                 api.cancel_all_orders()
#                 api.close_all_positions()
#                 Count = 0
