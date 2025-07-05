from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID_BUT_NOT_RETIRED = "paid_but_not_retired"
    COMPLETED = "completed"
    ERROR = "error"


class RetirementRequest(BaseModel):
    num_allowances: int = Field(..., ge=1, le=99, description="Number of allowances to retire")
    message: Optional[str] = Field(None, max_length=100, description="Custom retirement message")
    wallet: str = Field(..., description="User's wallet address")

    @validator('wallet')
    def validate_wallet_address(cls, v):
        if not v.startswith('0x') or len(v) != 42:
            raise ValueError('Invalid wallet address format')
        return v.lower()


class RetirementResponse(BaseModel):
    order_id: UUID
    message: str = "Allowances reserved successfully"


class ConfirmPaymentRequest(BaseModel):
    order_id: UUID
    tx_hash: str = Field(..., description="Transaction hash of the payment")

    @validator('tx_hash')
    def validate_tx_hash(cls, v):
        if not v.startswith('0x') or len(v) != 66:
            raise ValueError('Invalid transaction hash format')
        return v.lower()


class ConfirmPaymentResponse(BaseModel):
    message: str = "Payment confirmation received"
    status: str = "processing"


class OrderStatusResponse(BaseModel):
    order_id: UUID
    status: OrderStatus
    serial_numbers: Optional[List[str]] = None
    message: Optional[str] = None
    tx_hash: Optional[str] = None
    reward_tx_hash: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None