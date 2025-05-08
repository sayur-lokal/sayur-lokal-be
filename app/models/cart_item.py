from app.utils.extensions import db
from app.utils import chrono

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    
    quantity = db.Column(db.Integer, default=1, nullable=True)
    price = db.Column(db.Numeric(12, 2), nullable=True)  # Harga saat ditambahkan ke keranjang
    subtotal = db.Column(db.Numeric(12, 2), nullable=True)  # price * quantity
    
    created_at = db.Column(db.DateTime, default=chrono.now, nullable=True)
    updated_at = db.Column(db.DateTime, default=chrono.now, onupdate=chrono.now, nullable=True)

    # relationships
    cart = db.relationship('Cart', back_populates='cart_items')
    product = db.relationship('Product')