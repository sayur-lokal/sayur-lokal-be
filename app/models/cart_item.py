from app.utils.extensions import db
from app.utils import chrono

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Numeric(12, 2), nullable=False)  # Harga saat ditambahkan ke keranjang
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)  # price * quantity
    
    created_at = db.Column(db.DateTime, default=chrono.now)
    updated_at = db.Column(db.DateTime, default=chrono.now, onupdate=chrono.now)

    # relationships
    cart = db.relationship('Cart', back_populates='cart_items')
    product = db.relationship('Product')