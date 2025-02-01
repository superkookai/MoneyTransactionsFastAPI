import enum
from database import Base
from sqlalchemy import Column, Integer, Double, Date, String, Enum

# Define Enums
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

