from app.utils.extensions import db
# from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum
from app.utils import chrono

class UserRole(Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    supabase_uid = db.Column(UUID(as_uuid=True), unique=True, nullable=False)  # dari Supabase
    email = db.Column(db.String(120), unique=True, nullable=False)
    # password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    role = db.Column(db.Enum(UserRole), nullable=True)
    is_suspended = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=chrono.now)
    updated_at = db.Column(db.DateTime, default=chrono.now, onupdate=chrono.now)

    # Relationships
    buyer_profile = db.relationship("BuyerProfile", back_populates="user", uselist=False)
    seller_profile = db.relationship("SellerProfile", back_populates="user", uselist=False)
    wallet = db.relationship("Wallet", back_populates="user", uselist=False)
    orders = db.relationship("Order", back_populates="buyer", foreign_keys="Order.buyer_id")
    ratings = db.relationship("Rating", back_populates="buyer")
