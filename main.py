from typing import List

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from sqlalchemy.orm import Session

import crud
import models
import schemas
import calculate
import financeapi
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://23.94.100.114/",
    "http://localhost:8080",
    "https://ngkafong.github.io/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["Accept", "Content-Type"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
@repeat_every(seconds=60 * 60 * 3)
def update_all_stock_history():
    db = SessionLocal()
    financeapi.update_all_stock_price_history(db)
    db.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/overall")
def getOverall(db: Session = Depends(get_db)):
    return calculate.get_overall_calculation_result(db=db)

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

@app.get("/portfolios/{portfolio_id}", response_model=schemas.PortfolioWithCalculationResult)
def getPortfolio(portfolio_id: int, db: Session = Depends(get_db)):
    return crud.get_portfolio(db=db, portfolio_id=portfolio_id)

@app.post("/portfolios", response_model=schemas.Portfolio)
def newPortfolio(portfolio: schemas.PortfolioCreate, db: Session = Depends(get_db)):
    return crud.create_portfolio(db=db, portfolio=portfolio)


@app.get("/stocks", response_model=List[schemas.Stock])
def getStocks(db: Session = Depends(get_db)):
    return crud.get_stocks(db)

@app.get("/portfolio-stocks", response_model=List[schemas.PortfolioStock])
def getPortfolioStocks(db: Session = Depends(get_db)):
    return crud.get_portfolio_stocks(db)


@app.get("/portfolio-stocks/{portfolio_id},{stock_symbol}", response_model=schemas.PortfolioStockWithCalculationResult)
def getPortfolioStock(portfolio_id: int, stock_symbol: str, db: Session = Depends(get_db)):
    return crud.get_portfolio_stock(db, portfolio_id, stock_symbol)