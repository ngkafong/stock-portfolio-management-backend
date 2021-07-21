import yfinance as yf
from sqlalchemy.orm import Session
import requests
import pandas as pd
from datetime import date
from typing import Optional

import models
import schemas


def update_stock_price_history(db: Session, stock_symbol: str):

  stock = yf.Ticker(stock_symbol)
  close_price = stock.history(period="max")\
    .reset_index()\
    .rename(columns = { 'Close': 'close_price', 'Date': 'date'})

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