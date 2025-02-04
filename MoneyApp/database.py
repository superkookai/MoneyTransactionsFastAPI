from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# sqlite
# SQLALCHEMY_DATABASE_URL = "sqlite:///./moneyapp.db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

# Postgresql
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/MoneyAppDatabase"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base = declarative_base()