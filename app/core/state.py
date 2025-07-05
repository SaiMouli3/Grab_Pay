from typing import TypedDict, Optional, List, Any
from app.models.schemas import Transaction

class AgentState(TypedDict):
    transaction: Transaction
    is_valid: Optional[bool]
    is_fraudulent: Optional[bool]
    fulfillment_status: Optional[str]
    error_message: Optional[str]
    history: List[str]
