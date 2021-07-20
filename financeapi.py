import yfinance as yf
from sqlalchemy.orm import Session
import requests
import pandas as pd
from datetime import date
from typing import Optional

import models
import schemas

def fetch_stock_list():

  # return a stock_list dataframe with columns = ['stock_symbol', 'name', 'close_price']
  headers = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
  }
  request_stock = requests.get('https://api.nasdaq.com/api/screener/stocks?tableonly=true&download=true', headers=headers)
  request_etf = requests.get('https://api.nasdaq.com/api/screener/etf?download=true', headers=headers)

  stock_df = pd.DataFrame(request_stock.json()["data"]["rows"])\
    .rename(columns = { 'symbol': 'stock_symbol', 'lastsale': 'close_price'})\
    [['stock_symbol', 'name', 'close_price']]

  etf_df = pd.DataFrame(request_etf.json()["data"]["data"]["rows"])\
    .rename(columns = { 'symbol': 'stock_symbol', 'companyName': 'name', 'lastSalePrice': 'close_price'})\
    [['stock_symbol', 'name', 'close_price']]

  return pd.concat([stock_df, etf_df])

def update_stock_list(db: Session, stock_list: Optional[pd.DataFrame] = None):

  # update database "stock", fetch stock list from nasdaq if not provided
  if stock_list is None:
    stock_list = fetch_stock_list()

  def update_stock(stock):
    _stock = schemas.StockCreate(stock_symbol = stock['stock_symbol'], name = stock['name'])
    db_stock = models.Stock(**_stock.dict())
    db.merge(db_stock)

  stock_list.apply(update_stock, axis=1)

  db.commit()
  print('stock_list updated')
  return



def update_stock_price_history(db: Session, stock_symbol: str):

  stock = yf.Ticker(stock_symbol)
  close_price = msft.history(period="max")\
    .reset_index()\
    .rename(columns = { 'Close': 'close_price'})

  def update_stock_price_daily(close_price_daily):
    _close_price_daily = schemas.StockClosePrice(
      stock_symbol = stock_symbol,
      close_price = close_price_daily['close_price'],
      date = close_price_daily['date']
    )
    db_stock_close_price = models.StockClosePrice(**_close_price_daily.dict())
    db.merge(db_stock_close_price)

  close_price.apply(update_stock_price_daily, axis=1)
  db.commit()
  print('stock history updated', stock_symbol)
  return



def update_stock_price_today(db: Session, stock_list: Optional[pd.DataFrame] = None):

  if stock_list is None:
    stock_list = fetch_stock_list()
  # update database "stock.stock_close_prices", fetch_stock_list if stock list not provided

  def update_stock_today(stock_price_today):
    _stock_price_today = schemas.StockClosePrice(
      stock_symbol = stock_price_today['stock_symbol'],
      close_price = stock_price_today['close_price'],
      date = date.today()
    )

    db_stock_price_today = models.StockClosePrice(**_stock_price_today.dict())
    db.merge(stock_price_today)
    return

  stocks_with_transactions = db.query(models.Stock.stock_symbol)\
    .filter(models.Stock.transactions is not None)\
    .all()

  stock_list\
    [stock_list_df.symbol in stocks_with_transactions]\
    .apply(update_stock_today, axis=1)

  return