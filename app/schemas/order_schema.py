from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentMethodEnum(str, Enum):
    COD = "cod"
    QRIS = "qris"
    TRANSFER = "transfer"
    WALLET = "wallet"


class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0, description="ID produk yang valid")
    quantity: int = Field(gt=0, le=100, description="Jumlah produk (1-100)")

    @field_validator("product_id")
    @classmethod
    def validate_product_id(cls, v):
        if v <= 0:
            raise ValueError("ID produk harus lebih besar dari 0")
        return v

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Jumlah produk harus lebih besar dari 0")
        if v > 100:
            raise ValueError("Jumlah maksimal per item adalah 100")
        return v


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float

    @field_validator("id", "product_id")
    @classmethod
    def validate_ids(cls, v):
        if v <= 0:
            raise ValueError("ID harus lebih besar dari 0")
        return v

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Jumlah produk harus lebih besar dari 0")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("Harga tidak boleh negatif")
        return v

    model_config = {
        "from_attributes": True
    }


class OrderCreate(BaseModel):
    seller_id: int = Field(gt=0, description="ID penjual yang valid")
    payment_method: PaymentMethodEnum = Field(description="Metode pembayaran (cod, qris, transfer, wallet)")
    status: OrderStatusEnum = Field(default=OrderStatusEnum.PENDING, description="Status pesanan")
    is_paid: bool = Field(default=False, description="Status pembayaran")
    items: List[OrderItemCreate] = Field(
        min_length=1,
        max_length=50,  # Batasi maksimal 50 item berbeda dalam satu pesanan
        description="Daftar item pesanan (minimal 1 item, maksimal 50 item)"
    )

    @field_validator("seller_id")
    @classmethod
    def validate_seller_id(cls, v):
        if v <= 0:
            raise ValueError("ID penjual harus lebih besar dari 0")
        return v

    @model_validator(mode='after')
    def validate_unique_products(self):
        # Cek duplikasi produk
        product_ids = [item.product_id for item in self.items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Tidak boleh ada duplikasi produk dalam pesanan")

        # Cek total item tidak melebihi batas
        total_quantity = sum(item.quantity for item in self.items)
        if total_quantity > 1000:
            raise ValueError("Total jumlah produk dalam pesanan tidak boleh melebihi 1000")

        return self

    @model_validator(mode='after')
    def validate_payment_status(self):
        # Jika metode pembayaran adalah COD, status awal harus PENDING
        if self.payment_method == PaymentMethodEnum.COD and self.status != OrderStatusEnum.PENDING:
            raise ValueError("Pesanan dengan metode COD harus berstatus PENDING saat dibuat")

        # Jika is_paid=True, status minimal harus PAID
        if self.is_paid and self.status == OrderStatusEnum.PENDING:
            raise ValueError("Pesanan yang sudah dibayar tidak boleh berstatus PENDING")

        # Validasi status CANCELLED tidak boleh is_paid=True
        if self.is_paid and self.status == OrderStatusEnum.CANCELLED:
            raise ValueError("Pesanan yang dibatalkan tidak boleh berstatus sudah dibayar")

        return self


class OrderUpdate(BaseModel):
    status: Optional[OrderStatusEnum] = Field(
        default=None,
        description="Status pesanan (pending, paid, shipped, delivered, cancelled)"
    )
    is_paid: Optional[bool] = Field(
        default=None,
        description="Status pembayaran"
    )

    @model_validator(mode='after')
    def validate_payment_status_consistency(self):
        # Jika status diubah menjadi PAID, is_paid harus True
        if self.status == OrderStatusEnum.PAID and self.is_paid is False:
            raise ValueError("Status PAID tidak konsisten dengan is_paid=False")

        # Jika is_paid diubah menjadi True, status minimal harus PAID
        if self.is_paid and self.status and self.status == OrderStatusEnum.PENDING:
            raise ValueError("Pesanan yang sudah dibayar tidak boleh berstatus PENDING")

        # Validasi status CANCELLED tidak boleh is_paid=True
        if self.is_paid and self.status == OrderStatusEnum.CANCELLED:
            raise ValueError("Pesanan yang dibatalkan tidak boleh berstatus sudah dibayar")

        return self


class OrderResponse(BaseModel):
    id: int
    buyer_id: int
    seller_id: int
    total_price: float
    status: str
    payment_method: str
    is_paid: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    order_items: List[OrderItemResponse]

    @field_validator("id", "buyer_id", "seller_id")
    @classmethod
    def validate_ids(cls, v):
        if v <= 0:
            raise ValueError("ID harus lebih besar dari 0")
        return v

    @field_validator("total_price")
    @classmethod
    def validate_total_price(cls, v):
        if v < 0:
            raise ValueError("Total harga tidak boleh negatif")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        valid_statuses = [status.value for status in OrderStatusEnum]
        if v not in valid_statuses:
            raise ValueError(f"Status tidak valid. Status yang valid: {', '.join(valid_statuses)}")
        return v

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, v):
        valid_methods = [method.value for method in PaymentMethodEnum]
        if v not in valid_methods:
            raise ValueError(f"Metode pembayaran tidak valid. Metode yang valid: {', '.join(valid_methods)}")
        return v

    model_config = {
        "from_attributes": True
    }


# Skema tambahan untuk respons ringkas (tanpa detail item)
class OrderBriefResponse(BaseModel):
    id: int
    buyer_id: int
    seller_id: int
    total_price: float
    status: str
    payment_method: str
    is_paid: bool
    created_at: datetime
    items_count: int

    @field_validator("id", "buyer_id", "seller_id", "items_count")
    @classmethod
    def validate_ids(cls, v):
        if v <= 0:
            raise ValueError("ID dan jumlah item harus lebih besar dari 0")
        return v

    @field_validator("total_price")
    @classmethod
    def validate_total_price(cls, v):
        if v < 0:
            raise ValueError("Total harga tidak boleh negatif")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        valid_statuses = [status.value for status in OrderStatusEnum]
        if v not in valid_statuses:
            raise ValueError(f"Status tidak valid. Status yang valid: {', '.join(valid_statuses)}")
        return v

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, v):
        valid_methods = [method.value for method in PaymentMethodEnum]
        if v not in valid_methods:
            raise ValueError(f"Metode pembayaran tidak valid. Metode yang valid: {', '.join(valid_methods)}")
        return v

    model_config = {
        "from_attributes": True
    }