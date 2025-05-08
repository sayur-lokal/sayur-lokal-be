from app.utils.extensions import db
from app.utils import chrono

class WalletTransaction(db.Model):
    __tablename__ = "wallet_transactions"
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallets.id"), nullable=True)
    
    transaction_type = db.Column(db.String(50), nullable=True)  # deposit, withdrawal, payment
    amount = db.Column(db.Numeric(12, 2), nullable=True)
    status = db.Column(db.String(50), nullable=True)  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=chrono.now, nullable=True)
    
    # relationships
    wallet = db.relationship("Wallet", back_populates="transactions")
