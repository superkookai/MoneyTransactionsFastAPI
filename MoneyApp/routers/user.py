import datetime
from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Path, APIRouter
from starlette import status

import MoneyApp.routers.auth
from MoneyApp.models import Transactions, Users
from MoneyApp.database import engine, SessionLocal
from MoneyApp.routers.auth import get_current_user, bcrypt_context

router = APIRouter(
    prefix="/user",
    tags=["User"]
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

# Change Password Request
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

# Endpoints
@router.get("/current",status_code=status.HTTP_200_OK)
async def get_current_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.put("/change_password",status_code=status.HTTP_201_CREATED)
async def change_password(user: user_dependency, db: db_dependency, change_request: ChangePasswordRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not bcrypt_context.verify(change_request.old_password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Old Password not correct")

    user_model.hashed_password = bcrypt_context.hash(change_request.new_password)
    db.add(user_model)
    db.commit()
