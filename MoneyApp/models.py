import enum
from MoneyApp.database import Base
from sqlalchemy import Column, Integer, Double, Date, String, Enum, Boolean, ForeignKey


# Users Model
class RoleEnum(str, enum.Enum):  # Store as String in DB
    ADMIN = "admin"
    USER = "user"

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(RoleEnum),nullable=False)

# Transactions Model
class CategoryEnum(str, enum.Enum):  # Store as String in DB
    FOOD = "food"
    TRANSPORT = "transport"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"

class TypeEnum(str, enum.Enum):  # Store as String in DB
    INCOME = "income"
    EXPENSE = "expense"

class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(Integer,primary_key=True,index=True)
    category = Column(Enum(CategoryEnum), nullable=False)
    type = Column(Enum(TypeEnum), nullable=False)
    amount = Column(Double, nullable=False)
    description = Column(String)
    date = Column(Date, nullable=False)
    owner_id = Column(Integer,ForeignKey("users.id"))



