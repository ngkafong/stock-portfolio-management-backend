from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class TransactionBase(BaseModel):
    portfolio_id: int
    stock_symbol: str
    action: str
    date: date
    shares: Optional[int]
    value: Optional[float]
    fee: Optional[float]



class TransactionCreate(TransactionBase):
    pass



class Transaction(TransactionBase):
    transaction_id: int
    class Config:
        orm_mode = True


class TransactionUpdate(TransactionBase):
    pass


class PortfolioStockBase(BaseModel):
    portfolio_id: int
    stock_symbol: str

class PortfolioStockCreate(PortfolioStockBase):
    pass

class PortfolioStock(PortfolioStockBase):
    class Config:
        orm_mode = True

class PortfolioStockWithCalculationResult(PortfolioStockBase):
    calculation_results: List[dict]



class PortfolioBase(BaseModel):
    title: str



class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(PortfolioBase):
    pass



class Portfolio(PortfolioBase):
    portfolio_id: int
    portfolio_stocks: List[PortfolioStock]
    class Config:
        orm_mode = True


class PortfolioWithCalculationResult(Portfolio):
    calculation_results: List[dict]
    portfolio_stocks: List[PortfolioStockWithCalculationResult]


class StockBase(BaseModel):
    stock_symbol: str


class StockCreate(StockBase):
    pass


class Stock(StockBase):
    class Config:
        orm_mode = True



class StockPrice(BaseModel):
    stock_symbol: str
    date: date
    price: float

