from typing import List

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import crud
import models
import schemas
import financeapi
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def initialize():
    db = SessionLocal()
    if db.query(models.Stock).first() is None:
        financeapi.update_stock_list(db)
    db.close()
    return


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/transactions")
def getTransaction(db: Session = Depends(get_db)):
    return crud.get_transactions(db=db)

@app.get("/transactions/{transaction_id}")
def getTransaction(transaction_id: int, db: Session = Depends(get_db)):
    return crud.get_transaction(db=db, transaction_id=transaction_id)


@app.post("/transactions", response_model=schemas.Transaction)
def newTransaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db=db, transaction=transaction)


@app.put("/transactions/{transaction_id}", response_model=schemas.Transaction)
def updateTransaction(transaction_id: int, transaction: schemas.TransactionUpdate, db: Session = Depends(get_db)):
    return crud.update_transaction(db, transaction_id, transaction)

@app.delete("/transactions/{transaction_id}")
def deleteTransaction(transaction_id: int, db: Session = Depends(get_db)):
    return crud.delete_transaction(db=db, transaction_id=transaction_id)


@app.get("/portfolios", response_model=List[schemas.Portfolio])
def getPortfolios(db: Session = Depends(get_db)):
    return crud.get_portfolios(db=db)

@app.get("/portfolios/{portfolio_id}", response_model=schemas.Portfolio)
def getPortfolio(portfolio_id: int, db: Session = Depends(get_db)):
    return crud.get_portfolio(db=db, portfolio_id=portfolio_id)

@app.post("/portfolios", response_model=schemas.Portfolio)
def newPortfolio(portfolio: schemas.PortfolioCreate, db: Session = Depends(get_db)):
    return crud.create_portfolio(db=db, portfolio=portfolio)


@app.get("/stocks/{search_str}", response_model=List[schemas.Stock])
def getStocks(search_str: str, db: Session = Depends(get_db)):
    return crud.search_stocks(db, search_str)