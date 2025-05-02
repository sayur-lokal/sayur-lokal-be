from app.utils.extensions import db
from app.utils import chrono

class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    total_amount = db.Column(db.Numeric(12, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=chrono.now)
    updated_at = db.Column(db.DateTime, default=chrono.now, onupdate=chrono.now)

    # relationships
    buyer = db.relationship('User', backref='cart', uselist=False)
    cart_items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')