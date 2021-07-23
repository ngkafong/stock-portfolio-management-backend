import yfinance as yf
from sqlalchemy.orm import Session
import pandas as pd
from datetime import date
from typing import Optional

import models
import schemas


def update_stock_price_history(db: Session, stock_symbol: str):

  stock = yf.Ticker(stock_symbol)
  prices = stock.history(period="max")\
    .reset_index()\
    .rename(columns = { 'Close': 'price', 'Date': 'date'})

  def update_stock_price_daily(price_daily):
    _price_daily = schemas.StockPrice(
      stock_symbol = stock_symbol,
      price = price_daily['price'],
      date = price_daily['date']
    )
    db_stock_price = models.StockPrice(**_price_daily.dict())
    db.merge(db_stock_price)

  prices.apply(update_stock_price_daily, axis=1)
  db.commit()
  print('stock history updated', stock_symbol)

  return



def update_all_stock_price_history(db: Session):

  stocks = db.query(models.Stock).all()
  for stock in stocks:
    update_stock_price_history(db, stock.stock_symbol)

  return