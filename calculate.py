import pandas as pd
import numpy as np
import yfinance as yf
from datetime import timedelta

transactions = [
    {'date': '2020-07-02', 'action': 'buy', 'ticker': 'SOXX', 'share': 2, 'price': 300.0}, #buy
    {'date': '2021-08-20', 'action': 'sell', 'ticker': 'SOXX', 'share': 2, 'price': 320.0}, #sell
    {'date': '2020-07-24', 'action': 'dividendCash', 'ticker': 'SOXQ', 'amount': 3 }, #cash dividend
    {'date': '2020-08-20', 'action': 'adjustShare', 'ticker': 'SOXX', 'share': 1}, #share dividend/ merge/ split
]


def transactionRecordsToTickersBalance(transactions):

    def transactionRecordToAccountMovement(transaction):

        date = pd.to_datetime(transaction['date'])
        action = transaction['action']
        ticker = transaction['ticker']
        share = transaction.get('share', 0)
        price = transaction.get('price', 0)
        amount = transaction.get('amount', 0)
        fee = transaction.get('fee', 0)

        shareChange = 0
        cashChange = 0

        if action == 'buy':
            shareChange = share
            cashChange = -price * share - fee

        if action == 'sell':
            shareChange = -share
            cashChange = price * share + fee

        if action == 'dividendCash':
            cashChange = amount

        if action == 'adjustShare':
            shareChange = share


        return {
          'date': date, 
          'ticker': ticker,
          'shareChange': shareChange, 
          'cashChange': cashChange
        }
    
    accountMovements = pd.DataFrame(map(transactionRecordToAccountMovement, transactions))

    tickersBalance = {}
    
    for ticker, tickerMovements in accountMovements.groupby('ticker'):
        
        tickerMovements = tickerMovements.sort_values('date')
        tickerMovements['cashes'] = np.cumsum(tickerMovements['cashChange'])
        tickerMovements['shares'] = np.cumsum(tickerMovements['shareChange'])
        
        tickersBalance[ticker] =             tickerMovements[['date', 'shares', 'cashes']]                 .drop_duplicates('date', keep='last')

    return tickersBalance


def mergeBalanceWithClosePrice(tickerBalance, ticker):
    
    startDate = min(tickerBalance['date'])
    closePrice = ydf[['Close']]
    #closePrice = yf.Ticker(ticker).history(start='2020-07-02')[['Close']]
    
    return closePrice         .merge(tickerBalance, how='outer', left_index = True, right_on='date')         .fillna(method='pad')         .fillna(0)         .reset_index(drop=True)
    
    
    
def calculateTickerDailyStat(tickerBalanceAndPriceDF):
    
    resultDF = tickerBalanceAndPriceDF.reset_index(drop=True)
    
    resultDF['marketValue'] = resultDF['Close'] * resultDF['shares']
    
    resultDF['netProfit'] = resultDF['marketValue'] + resultDF['cashes']
    
    resultDF['dailyProfit'] = np.diff(resultDF['netProfit'], prepend=0)
    
    resultDF['cashFlow'] = np.diff(resultDF['cashes'], prepend=resultDF.head(1)['marketValue'])
    
    startDate = min(resultDF['date'])
    endDate = max(resultDF['date'])
    

    def adjustedCost(df):
        def calculateRowAdjustedCost(row):
            subDF = df.iloc[:row.name+1]
            weight = (row.date - subDF['date'] + timedelta(days=1)) / (row.date - startDate + timedelta(days=1))
            return -(subDF['cashFlow'] * weight).sum()

        return df.apply(calculateRowAdjustedCost, axis=1)
    
    resultDF['adjustedCost'] = adjustedCost(resultDF[['date', 'cashFlow']])
    resultDF['dollarWeightedReturnRate'] = resultDF['netProfit']/ adjustedCost(resultDF[['date', 'cashFlow']])
    
    return resultDF.fillna(0)

tickerBalanceAndPriceDF = mergeBalanceWithClosePrice(transactionRecordsToTickersBalance(transactions)['SOXX'], 'SOXX')


calculateTickerDailyStat(tickerBalanceAndPriceDF)




