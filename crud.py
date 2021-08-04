from sqlalchemy.orm import Session
import models
import schemas
import json
import calculate

def delete_garbage_stock(db: Session):
    garbage_stocks = db.query(models.Stock).filter(models.Stock.portfolio_stocks==None).all()
    for garbage_stock in garbage_stocks:
        db.delete(garbage_stock)
    db.commit()
    return

def delete_garbage_portfolio_stock(db: Session):
    garbage_portfolio_stocks = db.query(models.PortfolioStock).filter(models.PortfolioStock.transactions==None).all()
    for garbage_portfolio_stock in garbage_portfolio_stocks:
        db.delete(garbage_portfolio_stock)
    db.commit()
    return

def get_overall(db: Session):

    calculation_results = calculate.get_overall_calculation_result(db)

    db_portfolios = db.query(models.Portfolio).all()

    return {
        "calculation_results": calculation_results["overall_result"],
        "portfolios": [{
            **(portfolio.__dict__),
            "calculation_results": calculation_results["portfolios_result"][portfolio.portfolio_id]
        } for portfolio in db_portfolios]
    }

def get_portfolio(db: Session, portfolio_id: int):

    calculation_results = calculate.get_portfolio_calculation_result(portfolio_id, db)

    db_portfolio = db.query(models.Portfolio).filter(models.Portfolio.portfolio_id == portfolio_id).first()

    return {
        **(db_portfolio.__dict__),
        "calculation_results": calculation_results["portfolio_result"],
        "portfolio_stocks": [{
            **(portfolio_stock.__dict__),
            "calculation_results": calculation_results["portfolio_stocks_result"][portfolio_stock.stock_symbol]
        } for portfolio_stock in db_portfolio.portfolio_stocks]
    }

def get_portfolios(db: Session):
    return db.query(models.Portfolio).all()


def create_portfolio(db: Session, portfolio: schemas.PortfolioCreate):
    db_portfolio = models.Portfolio(**portfolio.dict())
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio


def get_transaction(db: Session, transaction_id: int):
    return db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).first()


def get_transactions(db: Session):
    return db.query(models.Transaction).all()

def create_stock(db: Session, stock: schemas.StockCreate):
    db_stock = models.Stock(**stock.dict())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

def create_portfolio_stock(db: Session, portfolio_stock: schemas.PortfolioStockCreate):
    db_portfolio_stock = models.PortfolioStock(**portfolio_stock.dict())
    db.add(db_portfolio_stock)
    db.commit()
    db.refresh(db_portfolio_stock)
    return db_portfolio_stock

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    if db_transaction.portfolio_stock is None:
        portfolio_stock = schemas.PortfolioStockCreate.parse_obj(transaction.dict())
        create_portfolio_stock(db, portfolio_stock)

    if db_transaction.portfolio_stock.stock is None:
        stock = schemas.StockCreate.parse_obj(transaction.dict())
        create_stock(db, stock)

    return db_transaction


def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransactionUpdate):
    db_transaction = models.Transaction(transaction_id = transaction_id, **transaction.dict())
    db_transaction = db.merge(db_transaction)
    db.commit()

    if db_transaction.portfolio_stock is None:
        portfolio_stock = schemas.PortfolioStockCreate.parse_obj(transaction.dict())
        create_portfolio_stock(db, portfolio_stock)

    if db_transaction.portfolio_stock.stock is None:
        stock = schemas.StockCreate.parse_obj(transaction.dict())
        create_stock(db, stock)

    delete_garbage_portfolio_stock(db)
    delete_garbage_stock(db)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int):
    delete_transaction = db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).first()
    db.delete(delete_transaction)
    db.commit()
    delete_garbage_portfolio_stock(db)
    delete_garbage_stock(db)
    return delete_transaction

def get_portfolio_stocks(db: Session):
    return db.query(models.PortfolioStock).all()


def get_portfolio_stock(db: Session, portfolio_id: int, stock_symbol: str):

    calculation_results = calculate\
        .get_portfolio_stock_calculation_result(portfolio_id, stock_symbol, db)

    db_portfolio_stock = db.query(models.PortfolioStock)\
        .filter(
            (models.PortfolioStock.portfolio_id == portfolio_id) &
            (models.PortfolioStock.stock_symbol == stock_symbol)
        )\
        .first()


    return {
        **(db_portfolio_stock.__dict__),
        "calculation_results": calculation_results
    }

def get_stocks(db: Session):
    return db.query(models.Stock).all()