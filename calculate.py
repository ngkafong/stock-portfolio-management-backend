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

  shares_change = 0
  cost_change = 0

  if action == 'buy':
      shares_change = shares
      cost_change = value * shares + fee

  if action == 'sell':
      shares_change = -shares
      cost_change = - value * shares - fee

  if action == 'dividend-cash':
      cost_change = -value + fee

  if action == 'dividend-shares':
      shares_change = shares
      cost_change = fee


  return {
    'date': date,
    'stock_symbol': stock_symbol,
    'shares_change': shares_change,
    'cost_change': cost_change,
  }



def stock_movements_to_balance(movements_df: pd.DataFrame):

  # convert movements to cumulative balance df ['date', 'cost', 'shares']
  balance_df = movements_df\
    .groupby('date', sort=True, as_index=False)\
    .sum()\
    .reset_index(drop=True)

  balance_df['cost'] = np.cumsum(movements_df['cost_change'])
  balance_df['shares'] = np.cumsum(movements_df['shares_change'])

  balance_df = balance_df[['date', 'cost', 'shares']]

  return balance_df



def calculate_return_statistics(asset_df: pd.DataFrame):

  # input: df with column [ 'date', 'market_value', 'cost', ... ]
  # output: df with column [ ...input_colums, 'net_profit', 'daily_profit', 'daily_profit_rate',
  # 'return_rate', 'money_weighted_return_rate', 'time_weighted_return_rate']


  def calculate_adjusted_cost(df):
    # calculate adjusted cost according to formula of money weighted return rate
    start_date = df['date'].iloc[0]
    cash_flow = np.diff(df['cost'], prepend=0)

    def calculate_adjusted_cost_row(row):
      weight = (row.date - df['date'].iloc[:row.name+1] + timedelta(days=1)) / (row.date - start_date + timedelta(days=1))
      return (cash_flow[:row.name+1] * weight).sum()

    result = df.apply(calculate_adjusted_cost_row, axis=1)
    return result

  result_df = asset_df.copy()
  result_df['net_profit'] = result_df['market_value'] - result_df['cost']
  result_df['daily_profit'] = np.diff(result_df['net_profit'], prepend=0)
  result_df['daily_profit_rate'] = result_df['daily_profit'] / result_df['cost']
  result_df['return_rate'] = result_df['net_profit'] / result_df['cost']
  result_df['money_weighted_return_rate'] = result_df['net_profit'] / calculate_adjusted_cost(result_df)
  result_df['time_weighted_return_rate'] = np.cumprod(result_df['daily_profit_rate'] + 1)

  return result_df



def calculate_portfolio_stock(transactions_df: pd.DataFrame, stock_prices_df: pd.DataFrame):

  account_movements_df = transactions_df.apply(
    transaction_record_to_account_movement, axis=1
  ).apply(pd.Series)

  balance_df = stock_movements_to_balance(account_movements_df)
  stock_prices_df = stock_prices_df[['date', 'price']].sort_values('date')

  balance_price_df = pd.merge_ordered(
    balance_df, stock_prices_df,
    on='date',
    fill_method='ffill'
  ).dropna()

  balance_price_df['market_value'] = balance_price_df['shares'] * balance_price_df['price']

  result_df = calculate_return_statistics(balance_price_df)

  return result_df



def get_portfolio_stock_calculation_result(portfolio_id: int, stock_symbol: str, db: Session):

  transactions_query = db.query(models.Transaction)\
    .filter(
      (models.Transaction.portfolio_id == portfolio_id) &
      (models.Transaction.stock_symbol == stock_symbol)
    )
  
  transactions_df = pd.read_sql(transactions_query.statement, db.bind)

  # fetch from api if database contain no price data
  if ( db.query(models.StockPrice)
    .filter(models.StockPrice.stock_symbol == stock_symbol)
    .first()
    is None
  ):
    financeapi.update_stock_price_history(db, stock_symbol)

  stock_prices_query = db.query(models.StockPrice)\
    .filter(models.StockPrice.stock_symbol == stock_symbol)
  
  stock_prices_df = pd.read_sql(stock_prices_query.statement, db.bind)

  return calculate_portfolio_stock(transactions_df, stock_prices_df).to_dict('records')



def calculate_multiple_assets(assets_result: dict):

  # input: { asset_1: asset_1_result, asset_2: asset_2_result }
  # output: combined_asset_result [{date, market_value, cost, ...}, ...]

  merged_df = pd.concat(
    [
      pd.DataFrame(asset_result)[['date', 'cost', 'market_value']].set_index('date')
      for asset_result in assets_result.values()
    ],
    axis=1,
    keys=assets_result.keys()
  ).reset_index()


  merged_df['cost'] = merged_df.xs('cost', axis=1, level=1).sum(axis=1)
  merged_df['market_value'] = merged_df.xs('market_value', axis=1, level=1).sum(axis=1)

  result_df = calculate_return_statistics(merged_df[['date', 'cost', 'market_value']])

  return result_df.to_dict('records')



def get_portfolio_calculation_result(portfolio_id: int, db: Session):

  portfolio_stocks = db.query(models.Portfolio.portfolio_stocks)\
    .filter(models.Portfolio.portfolio_id == portfolio_id)\
    .all()

  portfoliio_stocks_result = {
    portfolio_stock.stock_symbol: get_portfolio_stock_calculation_result(
      portfolio_stock.portfolio_id,
      portfolio_stock.stock,
      db
    )
    for portfolio_stock in portfolio_stocks
  }

  portfolio_result = calculate_multiple_assets(portfoliio_stocks_result)

  return {
    portfolio_result: portfolio_result,
    portfoliio_stocks_result: portfoliio_stocks_result
  }


def get_overall_calculation_result(db: Session):

  portfolios = db.query(models.Portfolio).all()

  portfolios_result = {
    portfolio.portfolio_id: get_portfolio_calculation_result(
      portfolio.portfolio_id,
      db
    ).portfolio_result
    for portfolio in portfolios
  }

  overall_result = calculate_multiple_assets(portfolios_result)

  return {
    overall_result: overall_result,
    portfolios_result: portfolios_result
  }