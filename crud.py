from sqlalchemy.orm import Session
import models
import schemas
import json

def get_portfolio(db: Session, portfolio_id: int):
    return db.query(models.Portfolio).filter(models.Portfolio.portfolio_id == portfolio_id).first()


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

    return db_transaction

def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransactionUpdate):
    db.query(models.Transaction)\
        .filter(models.Transaction.transaction_id == transaction_id)\
        .update(transaction.dict())
    db.commit()

    if db_transaction.portfolio_stock is None:
        portfolio_stock = schemas.PortfolioStockCreate.parse_obj(transaction.dict())
        create_portfolio_stock(db, portfolio_stock)

    return db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).first()

def delete_transaction(db: Session, transaction_id: int):
    delete_result = db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).delete()
    db.commit()
    return delete_result