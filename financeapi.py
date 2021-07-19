import yfinance as yf
from sqlalchemy.orm import Session
import requests

import models
import schemas

def update_stock_list(db: Session):

  headers = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
  }
  request = requests.get('https://api.nasdaq.com/api/screener/stocks?tableonly=true&download=true', headers=headers)
  stock_list = request.json()["data"]["rows"]

  for stock in stock_list:
    _stock = schemas.StockCreate(stock_symbol = stock['symbol'], name = stock['name'])
    db_stock = models.Stock(**_stock.dict())
    db.merge(db_stock)

  db.commit()
  print('stock_list updated')
  return



def update_stock_history(db: Session, stock_symbol: str):

  stock = yf.Ticker(stock_symbol)
  close_price = msft.history(period="max")[['Close']]

  def update_stock_history_daily(close_price_daily):
    _close_price_daily = schemas.StockClosePrice(
      stock_symbol = stock_symbol,
      close_price = close_price_daily['Close'],
      date = close_price_daily['date']
    )
    db_stock_close_price = models.StockClosePrice(**_close_price_daily.dict())
    db.merge(db_stock_close_price)

  db.commit()
  print('stock history updated', stock_symbol)
  return



def update_stocks_today(db: Session):

  return