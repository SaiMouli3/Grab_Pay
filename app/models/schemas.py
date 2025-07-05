from pydantic import BaseModel, Field
from typing import Dict, Any

class TransactionAmount(BaseModel):
    value: int
    currency: str

class Transaction(BaseModel):
    capture_id: str = Field(..., alias='captureId')
    request_id: str = Field(..., alias='requestId')
    charge_id: str = Field(..., alias='chargeId')
    status: str
    amount: TransactionAmount
    metadata: Dict[str, Any]
    created_at: str = Field(..., alias='createdAt')
    updated_at: str = Field(..., alias='updatedAt')
