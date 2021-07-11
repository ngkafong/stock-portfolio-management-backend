from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)

    transactions = relationship('Transaction', back_populates="portfolio")
    calculation_result_filename = Column(String)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'))
    action = Column(String)
    stock = Column(String)
    shares = Column(Integer, default=0)
    value = Column(Numeric(10, 3), default=0)

    portfolio = relationship('Portfolio', back_populates="transactions")


class Stock(Base):
    __tablename__ = "stocks"

    symbol = Column(String, primary_key=True)
    data_filename = Column(String, nullable=True)
    calculation_result_filename = Column(String, nullable=True)
