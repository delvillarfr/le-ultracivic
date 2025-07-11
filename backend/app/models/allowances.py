from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class AllowanceStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    RETIRED = "RETIRED"


class Allowance(SQLModel, table=True):
    __tablename__ = "allowances"

    serial_number: str = Field(primary_key=True, max_length=32)
    status: AllowanceStatus = Field(default=AllowanceStatus.AVAILABLE, index=True)
    order_id: Optional[str] = Field(default=None, max_length=36)
    timestamp: Optional[datetime] = Field(default=None, index=True)
    wallet: Optional[str] = Field(default=None, max_length=42)
    message: Optional[str] = Field(default=None, max_length=100)
    tx_hash: Optional[str] = Field(default=None, max_length=66)
    reward_tx_hash: Optional[str] = Field(default=None, max_length=66)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
