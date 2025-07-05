from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# You can change this to another DB like PostgreSQL if needed
from pathlib import Path

# Get absolute path to database file
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR}/transactions.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    capture_id = Column(String, unique=True, index=True)
    request_id = Column(String, unique=True, index=True)
    charge_id = Column(String, unique=True, index=True)
    status = Column(String)
    amount_value = Column(Integer)  # Stored in cents
    amount_currency = Column(String)
    transaction_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_valid = Column(Boolean)
    is_fraudulent = Column(Boolean)
    fulfillment_status = Column(String)
    error_message = Column(String)
    history = Column(JSON)

    def __repr__(self):
        return f"<Transaction(capture_id='{self.capture_id}', status='{self.status}')>"
