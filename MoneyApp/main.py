
from fastapi import FastAPI

import MoneyApp.models
from MoneyApp.database import engine

from MoneyApp.routers import auth, transactions, admin, user

app = FastAPI()

MoneyApp.models.Base.metadata.create_all(bind=engine) # create database with models

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(admin.router)
app.include_router(user.router)

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