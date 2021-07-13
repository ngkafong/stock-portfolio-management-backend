from pydantic import BaseModel
from typing import List, Optional


class TransactionBase(BaseModel):
    portfolio_id: int
    action: str
    stock: str
    date: str
    share: Optional[int]
    value: Optional[float]

    class Config:
        orm_mode = True



class TransactionCreate(TransactionBase):
    pass



class Transaction(TransactionBase):
    id: int




class PortfolioBase(BaseModel):
    title: str



class PortfolioCreate(PortfolioBase):
    pass



class Portfolio(BaseModel):
    portfolio_id: int
    title: str
    transactions: List[Transaction] = []
    class Config:
        orm_mode = True