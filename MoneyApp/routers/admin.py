import datetime
from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Path, APIRouter
from starlette import status

import MoneyApp.routers.auth
from MoneyApp.models import Transactions, Users
from MoneyApp.database import engine, SessionLocal
from MoneyApp.routers.auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
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

# Endpoints Transactions for Admin
@router.get("/transactions",status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    return db.query(Transactions).all()


@router.delete("/transaction/{transaction_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(user: user_dependency, db: db_dependency, transaction_id: int = Path(gt=0)):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    transaction_model = db.query(Transactions).filter(Transactions.id==transaction_id).first()
    if transaction_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction {transaction_id} not found")

    db.query(Transactions).filter(Transactions.id==transaction_id).delete()
    db.commit()


# Endpoints Users for Admin
@router.get("/users",status_code=status.HTTP_200_OK)
async def read_all_users(user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    return db.query(Users).all()


@router.delete("/user/{user_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")

    transactions = db.query(Transactions).filter(Transactions.owner_id==user_model.id).all()
    if transactions is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transactions for User {user_id} not found")
    for transaction in transactions:
        db.query(Transactions).filter(Transactions.id == transaction.id).delete()
        db.commit()

    db.query(Users).filter(Users.id == user_id).delete()
    db.commit()