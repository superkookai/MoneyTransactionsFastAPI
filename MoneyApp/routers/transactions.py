import datetime
from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Path, APIRouter
from starlette import status

import MoneyApp.routers.auth
from MoneyApp.models import Transactions
from MoneyApp.database import engine, SessionLocal
from MoneyApp.routers.auth import get_current_user

router = APIRouter(
    prefix="/transaction",
    tags=["Transaction"]
)

# db dependency
def get_db():
    db = SessionLocal()
    try:
        yield db # return all
    finally:
        db.close() # then close when finish

# db dependency
db_dependency = Annotated[Session, Depends(get_db)]

# user dependency
user_dependency = Annotated[dict, Depends(get_current_user)]

# Request Body
class TransactionRequest(BaseModel):
    category: str = Field(description="food/transport/entertainment/utilities")
    type: str = Field(description="income/expense")
    amount: float = Field(gt=0)
    description: str = Field(min_length=5, max_length=100)
    date: datetime.date


# Endpoints
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency): # inject get_db
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    return db.query(Transactions).filter(Transactions.owner_id==user.get("id")).all()


@router.get("/get/{transaction_id}", status_code=status.HTTP_200_OK)
async def read_transaction(user: user_dependency, db: db_dependency, transaction_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    transaction_model = (db.query(Transactions).filter(Transactions.owner_id == user.get("id"))
                         .filter(Transactions.id == transaction_id).first())
    if transaction_model is not None:
        return transaction_model
    raise HTTPException(status_code=404,detail=f"Transaction {transaction_id} not found")


@router.post("/create",status_code=status.HTTP_201_CREATED)
async def create_transaction(user: user_dependency, db: db_dependency, transaction_request: TransactionRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    transaction_model = Transactions(**transaction_request.model_dump(),owner_id=user.get("id"))
    db.add(transaction_model)
    db.commit()


@router.put("/update/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_transaction(user: user_dependency,
                             db: db_dependency,
                             transaction_request: TransactionRequest,
                             transaction_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    transaction_model = (db.query(Transactions).filter(Transactions.owner_id == user.get("id"))
                         .filter(Transactions.id == transaction_id).first())
    if transaction_model is None:
        raise HTTPException(status_code=404,detail=f"Transaction {transaction_id} not found")

    transaction_model.category = transaction_request.category
    transaction_model.type = transaction_request.type
    transaction_model.amount = transaction_request.amount
    transaction_model.description = transaction_request.description
    transaction_model.date = transaction_request.date

    db.add(transaction_model)
    db.commit()


@router.delete("/delete/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(user: user_dependency, db: db_dependency, transaction_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    transaction_model = (db.query(Transactions).filter(Transactions.owner_id == user.get("id"))
                         .filter(Transactions.id == transaction_id).first())

    if transaction_model is None:
        raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")

    (db.query(Transactions).filter(Transactions.owner_id == user.get("id"))
     .filter(Transactions.id == transaction_id).delete())
    db.commit()
