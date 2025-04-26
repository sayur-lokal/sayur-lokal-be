from app.utils import chrono
from app.utils.extensions import db

class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'))

    transaction_type = db.Column(db.String(50))  # topup, withdraw, payment, refund
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(50))  # pending, verified, rejected
    # proof_url = db.Column(db.String(255), nullable=True)  # URL bukti transfer, pembayaran, dll.
    created_at = db.Column(db.DateTime, default=chrono.now)

    wallet = db.relationship('Wallet', back_populates='transactions')