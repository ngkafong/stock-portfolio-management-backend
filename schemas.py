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

    class Config:
        orm_mode = True



class TransactionCreate(TransactionBase):
    pass



class Transaction(TransactionBase):
    transaction_id: int


class TransactionUpdate(TransactionBase):
    pass



class PortfolioBase(BaseModel):
    title: str



class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(PortfolioBase):
    pass



class Portfolio(BaseModel):
    portfolio_id: int
    title: str
    calculation_results: List[dict] = []
    class Config:
        orm_mode = True

class PortfolioStockBase(BaseModel):
    portfolio_id: int
    stock_symbol: str

class PortfolioStockCreate(PortfolioStockBase):
    pass