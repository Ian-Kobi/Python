## Python

This is a trimmed down version of the bot I created to trade stocks on the NYSE while living in Murcia, Spain for a year. I taught myself Python, and this bot was end-to-end developed solely by myself. It has the following properties:  

-It uses API keys to link to a paper account through the brokerage Alpaca  
-It uses the API to receive account analytics (account #, status, trades, equity)  
-It imports data from yfinance and then organizes it using Pandas Dataframe  
-The data is then cleaned for more efficient processing speed  
-It calculates the money flowing in or out of a specific security within a time frame  
-It uses this "Money Flow" to calculate a novel financial indicator, "Kobi MACD"  
-Based on the reading from Kobi MACD, it initiates buy and sell signals  
-These signals are then automatically executed as buy and sell orders respectively  
-These orders are pyramided algorithmically using conditional statements within a while loop (to optimize risk vs return)  
-The algorithm determines the time of day and trades accordingly  
-The algorithm automatically ends the day flat --i.e. once outside the pre-determined time window to trade, it closes all positions and cancels all open orders  
-It outputs progress in terminal so it can be monitored and also outputs dataframe data in the form of a .csv file for future possible data analysis  
