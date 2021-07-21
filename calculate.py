from sqlalchemy.orm import Session
import models
from operator import itemgetter
import pandas as pd
import financeapi

def transaction_record_to_account_movement(transaction):

  date, action, stock_symbol, shares, value, fee = \
    itemgetter('date', 'action', 'stock_symbol', 'shares', 'value', 'fee')(transaction)

  share_change = 0
  cash_change = 0

  if action == 'buy':
      share_change = shares
      cash_change = -value * shares - fee

  if action == 'sell':
      share_change = -shares
      cash_change = value * shares + fee

  if action == 'dividend-cash':
      cash_change = value - fee

  if action == 'adjustShare':
      share_change = shares
      cash_cahgne = - fee


  return {
    'date': date,
    'stock_symbol': stock_symbol,
    'share_change': share_change,
    'cash_change': cash_change,
  }


def calculate_portfolio_stock(transactions, stock_prices):
  return [{"calculate_portfolio_stock": "TODO"}]


def get_portfolio_stock_calculation_result(portfolio_id: int, stock_symbol: str, db: Session):

  transactions = db.query(models.PortfolioStock.transactions)\
    .filter(
      models.PortfolioStock.portfolio_id == portfolio_id and
      models.PortfolioStock.stock_symbol == stock_symbol
    )\
    .all()

  if ( db.query(models.StockClosePrice)
    .filter(models.StockClosePrice.stock_symbol == stock_symbol)
    .first()
    is None
  ):
    financeapi.update_stock_price_history(db, stock_symbol)

  stock_prices = db.query(models.StockClosePrice)\
    .filter(models.StockClosePrice.stock_symbol == stock_symbol)\
    .all()

  return calculate_portfolio_stock(transactions, stock_prices)

def get_portfolio_calculation_result(portfolio_id: int, db: Session):

  portfolio_stocks = db.Query(models.Portfolio.portfolio_stocks)\
    .filter(models.Portfolio.portfolio_id == portfolio_id)\
    .all()

  portfoliio_stocks_result = [
    get_portfolio_stock_calculation_result(
      portfolio_stock.portfolio_id,
      portfolio_stock.stock,
      db
    )
    for portfolio_stock in portfolio_stocks
  ]

  portfolio_result = calculate_portfolio(portfoliio_stocks_result)

  return {
    portfolio_result: portfolio_result,
    portfoliio_stocks_result: portfoliio_stocks_result
  }
