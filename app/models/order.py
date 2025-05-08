from app.utils.extensions import db
from app.utils import chrono
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    PROCESSED = "processed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seller_id = db.Column( db.Integer, db.ForeignKey("seller_profiles.id"), nullable=False)

    total_price = db.Column(db.Numeric(12, 2), nullable=True)
    status = db.Column(db.String(20))  # pending, paid, shipped, delivered, cancelled
    payment_method = db.Column(db.String(50))  # cod, qris, transfer, wallet
    is_paid = db.Column(db.Boolean, default=False)
    # payment_proof_url = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=chrono.now)
    updated_at = db.Column(db.DateTime, default=chrono.now, onupdate=chrono.now)

    # relationships
    buyer = db.relationship("User", back_populates="orders", foreign_keys=[buyer_id])
    seller = db.relationship("SellerProfile", back_populates="orders", foreign_keys=[seller_id])
    order_items = db.relationship("OrderItem", back_populates="order", cascade="all,delete-orphan")
    ratings = db.relationship("Rating", back_populates="order", cascade="all,delete-orphan")