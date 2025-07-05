from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

class User(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    full_name: str
    role: str  # ADMIN, MERCHANT, USER
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    currency: str
    status: str
    is_fraudulent: bool
    created_at: datetime
    updated_at: datetime
    history: List[str]

class PaginatedResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[TransactionResponse]
