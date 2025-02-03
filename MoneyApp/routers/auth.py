from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from jose.constants import ALGORITHMS
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from MoneyApp.database import SessionLocal
from MoneyApp.models import Users
from passlib.context import CryptContext
from jose import jwt, JWTError

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# JWT
SECRETE_KEY = "450b0965a4985a8fdbddae85d9f8ccad9c9a5b6668c457662beb201f3e902fee"
ALGORITHM = "HS256"

# db dependency
def get_db():
    db = SessionLocal()
    try:
        yield db # return all
    finally:
        db.close() # then close when finish

# Type of db dependency
db_dependency = Annotated[Session, Depends(get_db)]

# Hashed password
bcrypt_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

# Bearer for check JWT by sending to tokenUrl
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

# Request Body
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str = Field(description="admin/user")

# Token class response
class Token(BaseModel):
    access_token: str
    token_type: str

# LoginRequest
class LoginRequest(BaseModel):
    username: str
    password: str


# Authenticate user
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user

# Create Access Token
def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp":expires})
    return jwt.encode(encode,SECRETE_KEY,ALGORITHM)

# Check current user
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRETE_KEY,algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None or user_role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials.")
        return {"username":username,"id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials.")


# Endpoints
@router.post("/create",status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True
    )
    db.add(create_user_model)
    db.commit()


@router.post("/token",response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm,Depends()], db: db_dependency):
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials.")
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return Token(access_token=token,token_type="Bearer")


@router.post("/get/token",response_model=Token)
async def login_get_token(login_request: LoginRequest, db: db_dependency):
    user = authenticate_user(login_request.username,login_request.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials.")
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return Token(access_token=token, token_type="Bearer")

