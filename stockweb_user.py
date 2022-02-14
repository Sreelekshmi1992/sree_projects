from pickle import TRUE
import streamlit as st
from genericpath import exists
import pandas as pd
import pandas_ta as ta
import numpy as np
import matplotlib.pyplot as plt
import vectorbt as vbt
import sys
import yfinance as yf # https://pypi.org/project/yfinance/
from ta.volatility import BollingerBands
from ta.trend import MACD
from ta.momentum import RSIIndicator
import datetime
from PIL import Image

st.header("A Basic Data Science Web Application")


image = Image.open('/home/nodeusr/sreelekshmi/images/stock copy.jpg')

st.image(image)


###########
# sidebar #
###########
#img1 = st.sidebar.image('/home/nodeusr/sreelekshmi/images/stock2.png')
option = st.sidebar.selectbox('Select one symbol', ( 'AAPL', 'MSFT',"SPY",'WMT','BTC-USD','AAL'))
today = datetime.date.today()
before = today - datetime.timedelta(days=700)
start_date = st.sidebar.date_input('Start date', before)
end_date = st.sidebar.date_input('End date', today)
if start_date < end_date:
    st.sidebar.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
else:
    st.sidebar.error('Error: End date must fall after start date.')



##############
# Stock data #
##############

# Download data
df = yf.download(option,start= start_date,end= end_date, progress=False)

# Bollinger Bands
indicator_bb = BollingerBands(df['Close'])
bb = df
bb['bb_h'] = indicator_bb.bollinger_hband()
bb['bb_l'] = indicator_bb.bollinger_lband()
bb = bb[['Close','bb_h','bb_l']]

# Moving Average Convergence Divergence
macd = MACD(df['Close']).macd()

# Resistence Strength Indicator
rsi = RSIIndicator(df['Close']).rsi()




###################
# Set up main app #
###################

# Plot the prices and the bolinger bands
# Data of recent days
st.header('Recent data ')
st.dataframe(df.tail(10))


st.header("Check Golden Cross - Stock Data From User Input ")

Ticker = st.text_input("Enter the stock name: \n")
fastavg =st.number_input('Fast Average\n')
slowavg = st.number_input('Slow Average\n')
df = pd.DataFrame().ta.ticker(Ticker , period="12mo") # requires 'yfinance' installed

# Create the "Golden Cross" 
df["GC"] = df.ta.sma(fastavg, append=True) > df.ta.sma(slowavg, append=True) #slowavg and fastavg as ui


# Create the "Golden Cross" 

st.table(df.tail())



# Create boolean Signals(TS_Entries, TS_Exits) for vectorbt
golden = df.ta.tsignals(df.GC, asbool=True, append=True)
st.dataframe(golden)


# Sanity Check (Ensure data exists)


#entry and exit declare
entries=golden.TS_Entries
exits=golden.TS_Exits

# Create the Signals Portfolio
pf = vbt.Portfolio.from_signals(df.Close, entries=golden.TS_Entries, exits=golden.TS_Exits, freq="D", init_cash=100_000, fees=0.0025, slippage=0.0025)

#print entry and exit dates
entries = entries[entries == True]
exits = exits[exits == True]

st.dataframe(entries)





st.dataframe(exits)



# Print Portfolio Stats and Return Stats

print(pf.stats())


#print(pf.returns_stats())
st.line_chart(df)