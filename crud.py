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


def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransactionUpdate):
    db.query(models.Transaction)\
        .filter(models.Transaction.transaction_id == transaction_id)\
        .update(transaction.dict())
    db.commit()
    return db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).first()

def delete_transaction(db: Session, transaction_id: int):
    delete_result = db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).delete()
    db.commit()
    return delete_result