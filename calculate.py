from sqlalchemy.orm import Session
import models
from operator import itemgetter
import pandas as pd
import numpy as np
import financeapi
from typing import List
from datetime import timedelta

def transaction_record_to_account_movement(transaction: dict):

  # convert different types of transaction to generic movement

  date, action, stock_symbol, shares, value, fee = \
    itemgetter('date', 'action', 'stock_symbol', 'shares', 'value', 'fee')(transaction)

  share_change = 0
  cost_change = 0

  if action == 'buy':
      share_change = shares
      cost_change = value * shares + fee

  if action == 'sell':
      share_change = -shares
      cost_change = - value * shares - fee

  if action == 'dividend-cash':
      cost_change = -value + fee

  if action == 'adjustShare':
      share_change = shares
      cost_cahgne = fee


  return {
    'date': date,
    'stock_symbol': stock_symbol,
    'share_change': share_change,
    'cost_change': cost_change,
  }

def stock_movements_to_balance(movements_df: pd.DataFrame):

  # convert movements to cumulative balance df ['date', 'cost', 'share']
  balance_df = movements_df\
    .groupby('date')\
    .sum()\
    .sort_values('date')\
    .reset_index(drop=True)

  balance_df['cost'] = np.cumsum(movements_df['cost_change'])
  balance_df['share'] = np.cumsum(movements_df['share_change'])

  balance_df = balance_df[['date', 'cost', 'share']]

  return balance_df

def calculate_profit_statistics(balance_df: pd.DataFrame):

  # add column ['market_value', 'net_profit', 'daily_profit', 'daily_profit_percentage',
  # 'return_rate', 'money_weighted_return_rate', 'time_weighted_return_rate']

  def calculate_adjusted_cost(df):
    # calculate adjusted cost according to formula of money weighted return rate
    start_date = df['date'].iloc[0]
    df['cash_flow'] = np.diff(resultDF['cost'], prepend=0)

    def calculate_adjusted_cost_row(row):
      sub_df = df.iloc[:row.name+1]
      weight = (row.date - sub_df['date'] + timedelta(days=1)) / (row.date - start_date + timedelta(days=1))
      return (sub_df['cash_flow'] * weight).sum()

    result = df.apply(calculate_adjusted_cost_row, axis=1)
    df.drop(columns='cash_flow')
    return result

  balance_df['market_value'] = balance_df['price'] * balance_df['share']
  balance_df['net_profit'] = balance_df['market_value'] - balance_df['cost']
  balance_df['daily_profit'] = np.diff(balance_df['net_profit'], prepend=0)
  balance_df['daily_profit_percentage'] = balance_df['daily_profit'] / balance_df['cost']
  balance_df['return_rate'] = balance_df['net_profit'] / balance_df['cost']
  balance_df['money_weighted_return_rate'] = balance_df['net_profit'] / calculate_adjusted_cost(balance_df)
  balance_df['time_weighted_return_rate'] = np.cumprod(balance_df['daily_profit_percentage'] + 1)

  return balance_df


def calculate_portfolio_stock(transactions: List[dict], stock_prices: List[dict]):
  account_movements_df = pd.DataFrame(
    map(transaction_record_to_account_movement, transactions)
  )

  balance_df = stock_movements_to_balance(account_movements_df)

  stock_prices_df = pd.DataFrame(stock_prices)



  return [{"calculate_portfolio_stock": "TODO"}]


def get_portfolio_stock_calculation_result(portfolio_id: int, stock_symbol: str, db: Session):

  transactions = db.query(models.PortfolioStock.transactions)\
    .filter(
      models.PortfolioStock.portfolio_id == portfolio_id and
      models.PortfolioStock.stock_symbol == stock_symbol
    )\
    .all()

  if ( db.query(models.StockPrice)
    .filter(models.StockPrice.stock_symbol == stock_symbol)
    .first()
    is None
  ):
    financeapi.update_stock_price_history(db, stock_symbol)

  stock_prices = db.query(models.StockPrice)\
    .filter(models.StockPrice.stock_symbol == stock_symbol)\
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
