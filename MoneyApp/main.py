import datetime
from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Path
from starlette import status

import models
from models import Transactions
from database import engine, SessionLocal

app = FastAPI()

models.Base.metadata.create_all(bind=engine) # create database with models

# db dependency
def get_db():
    db = SessionLocal()
    try:
        yield db # return all
    finally:
        db.close() # then close when finish

# Type of db dependency
db_dependency = Annotated[Session, Depends(get_db)]

# Request Body
class TransactionRequest(BaseModel):
    category: str = Field(description="food/transport/entertainment/utilities")
    type: str = Field(description="income/expense")
    amount: float = Field(gt=0)
    description: str = Field(min_length=5, max_length=100)
    date: datetime.date


# Endpoints
@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency): # inject get_db
    return db.query(Transactions).all()


@app.get("/transaction/{transaction_id}", status_code=status.HTTP_200_OK)
async def read_transaction(db: db_dependency, transaction_id: int = Path(gt=0)):
    transaction_model = db.query(Transactions).filter(Transactions.id == transaction_id).first()
    if transaction_model is not None:
        return transaction_model
    raise HTTPException(status_code=404,detail=f"Transaction {transaction_id} not found")


@app.post("/transaction",status_code=status.HTTP_201_CREATED)
async def create_transaction(db: db_dependency, transaction_request: TransactionRequest):
    transaction_model = Transactions(**transaction_request.model_dump())
    db.add(transaction_model)
    db.commit()


@app.put("/transaction/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_transaction(db: db_dependency,
                             transaction_request: TransactionRequest,
                             transaction_id: int = Path(gt=0)):
    transaction_model = db.query(Transactions).filter(Transactions.id == transaction_id).first()
    if transaction_model is None:
        raise HTTPException(status_code=404,detail=f"Transaction {transaction_id} not found")

    transaction_model.category = transaction_request.category
    transaction_model.type = transaction_request.type
    transaction_model.amount = transaction_request.amount
    transaction_model.description = transaction_request.description
    transaction_model.date = transaction_request.date

    db.add(transaction_model)
    db.commit()


@app.delete("/transaction/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(db: db_dependency, transaction_id: int = Path(gt=0)):
    transaction_model = db.query(Transactions).filter(Transactions.id == transaction_id).first()
    if transaction_model is None:
        raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")

    db.query(Transactions).filter(Transactions.id == transaction_id).delete()
    db.commit()


# def insertTransactionsManually():
#     # Insert data to transactions table
#     transactions = [
#     models.Transactions(
#         category=models.CategoryEnum.FOOD,
#         type=models.TypeEnum.EXPENSE,
#         amount=75.50,
#         description="Lunch at a restaurant",
#         date=datetime.date.today()),
#     models.Transactions(
#         category=models.CategoryEnum.TRANSPORT,
#         type=models.TypeEnum.EXPENSE,
#         amount=47.0,
#         description="BTS to Onnut",
#         date=datetime.date(2025,1,15)),
#     models.Transactions(
#         category=models.CategoryEnum.ENTERTAINMENT,
#         type=models.TypeEnum.EXPENSE,
#         amount=100.0,
#         description="See Movie",
#         date=datetime.date(2025,1,7))
#     ]
#     session = SessionLocal()
#     for trans in transactions:
#         session.add(trans)
#         session.commit()