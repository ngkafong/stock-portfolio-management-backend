from sqlalchemy.orm import Session
from . import models, schemas

def get_portfolio(db: Session, portfolio_id: int):
    return db.query(models.Portfolio).filter(models.Portfolio.id == portfolio_id).first()


def get_portfolios(db: Session):
    return db.query(models.Portfolio).all()


def create_portfolio(db: Session, portfolio: schemas.PortfolioCreate):
    db_portfolio = models.Portfolio(**portfolio.dict())
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio


def get_transaction(db: Session, transaction_id: int):
    return db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

def get_transactions(db: Session, portolio_id: int):
    return db.query(models.Transaction).filter(models.Transaction.portfolio_id == portolio_id).all()



def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Portfolio(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction