from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Date
from sqlalchemy.orm import relationship

from database import Base


class Portfolio(Base):
    __tablename__ = "portfolios"

    portfolio_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)

    portfolio_stocks = relationship('PortfolioStock', back_populates="portfolio")

class Stock(Base):
    __tablename__ = "stocks"

    stock_symbol = Column(String, primary_key=True)

    portfolio_stocks = relationship('PortfolioStock', back_populates="stock")
    stock_close_prices = relationship('StockClosePrice')

class PortfolioStock(Base):
    __table__ = "portfolio_stocks"

    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), primary_key=True)
    stock_symbol = Column(String, ForeignKey('stocks.id'), primary_key=True)

    portfolio = relationship('Portfolio', back_populates="portfolio_stocks")
    stock = relationship('Stock', back_populates="portfolio_stocks")
    transactions = relationship('Transaction', back_populates="portfolio_stock")


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'))
    stock_symbol = Column(String, ForeignKey('stocks.stock_symbol'))
    transaction_date = Column(Date)
    action = Column(String)
    shares = Column(Integer, default=0)
    value = Column(Numeric(10, 3), default=0)
    fee = Column(Numeric(10, 3), default=0)


class StockClosePrice(Base):
    __tablename__ = "stock_close_prices"

    stock_symbol = Column(String, ForeignKey('stock'), primary_key=True)
    date = Column(Date, primary_key=True)

