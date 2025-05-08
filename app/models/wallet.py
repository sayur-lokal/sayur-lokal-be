from app.utils.extensions import db

class Wallet(db.Model):
    __tablename__ = "wallets"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=True)
    balance = db.Column(db.Numeric(12, 2), default=0.00, nullable=True)
    
    # relationships
    user = db.relationship("User", back_populates="wallet")
    transactions = db.relationship("WalletTransaction", back_populates="wallet", cascade="all, delete-orphan")