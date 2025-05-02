# from pydantic import BaseModel, Field
# from typing import Optional
# from datetime import datetime
# from enum import Enum

# class TransactionTypeEnum(str, Enum):
#     DEPOSIT = "deposit"
#     WITHDRAWAL = "withdrawal"
#     PAYMENT = "payment"
#     REFUND = "refund"

# class WalletBase(BaseModel):
#     user_id: int

# class WalletCreate(WalletBase):
#     balance: float = Field(default=0.0, ge=0)

# class WalletUpdate(BaseModel):
#     balance: Optional[float] = Field(default=None, ge=0)

# class WalletResponse(WalletBase):
#     id: int
#     balance: float
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         from_attributes = True

# class TransactionBase(BaseModel):
#     wallet_id: int
#     amount: float = Field(gt=0)
#     transaction_type: TransactionTypeEnum
#     description: Optional[str] = None

# class TransactionCreate(TransactionBase):
#     pass

# class TransactionResponse(TransactionBase):
#     id: int
#     created_at: datetime

#     class Config:
#         from_attributes = True
