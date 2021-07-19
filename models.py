from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Date, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from calculate import calculatePortfolio
from database import Base


class Portfolio(Base):
    __tablename__ = "portfolios"

    portfolio_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)

    portfolio_stocks = relationship('PortfolioStock', back_populates="portfolio", cascade="all, delete-orphan")

class Stock(Base):
    __tablename__ = "stocks"

    stock_symbol = Column(String, primary_key=True)
    name = Column(String)

    portfolio_stocks = relationship('PortfolioStock', back_populates="stock", cascade="all, delete-orphan")
    stock_close_prices = relationship('StockClosePrice', cascade="all, delete-orphan")

class PortfolioStock(Base):
    __tablename__ = "portfolio_stocks"

    portfolio_id = Column(Integer, ForeignKey('portfolios.portfolio_id'), primary_key=True)
    stock_symbol = Column(String, ForeignKey('stocks.stock_symbol'), primary_key=True)

    portfolio = relationship('Portfolio', back_populates="portfolio_stocks")
    stock = relationship('Stock', back_populates="portfolio_stocks")
    transactions = relationship('Transaction', back_populates="portfolio_stock", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, nullable=False)
    stock_symbol = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    action = Column(String, nullable=False)
    shares = Column(Integer, default=0)
    value = Column(Numeric(10, 3), default=0)
    fee = Column(Numeric(10, 3), default=0)

    portfolio_stock = relationship('PortfolioStock')
    __table_args__ = (ForeignKeyConstraint([portfolio_id, stock_symbol],
                                           [PortfolioStock.portfolio_id, PortfolioStock.stock_symbol]),
                      {})


class StockClosePrice(Base):
    __tablename__ = "stock_close_prices"

    stock_symbol = Column(String, ForeignKey('stocks.stock_symbol'), primary_key=True)
    date = Column(Date, primary_key=True)
    close_price = Column(Numeric(10, 3), nullable=False)

