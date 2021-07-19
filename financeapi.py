import yfinance as yf
from sqlalchemy.orm import Session
import requests

import models
import schemas

def fetch_stock_list():
  headers = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
  }
  request = requests.get('https://api.nasdaq.com/api/screener/stocks?tableonly=true&download=true', headers=headers)
  return request.json()["data"]["rows"]

def update_stock_list(db: Session, stock_list=fetch_stock_list()):

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

  stock_list = fetch_stock_list()
  update_stock_list(db, stock_list)
  stock_list_df = pd.DataFrame(stock_list)

  def update_stock_today(stock_price_today):
    _stock_price_today = schemas.StockClosePrice(
      stock_symbol = stock_price_today['symbol'],
      close_price = stock_price_today['Close'],
      date = close_price_daily['date']
    )

    db_stock_price_today = models.StockClosePrice(**_stock_price_today.dict())
    db.merge(stock_price_today)
    return

  stocks_with_transactions = db.query(models.Stock.stock_symbol)\
    .filter(models.Stock.transactions is not None)\
    .all()

  stock_list_df
    [stock_list_df.symbol in stocks_with_transactions]
    .apply(update_stock_today, axis=1)

  return