from app.utils import chrono
from app.utils.extensions import db

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller_profiles.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=chrono.now)
    updated_at = db.Column(db.DateTime, default=chrono.now, onupdate=chrono.now)

    # Relationships
    seller = db.relationship('SellerProfile', back_populates='products')
    category = db.relationship('Category', back_populates='products')
    ratings = db.relationship('Rating', back_populates='product')
    order_items = db.relationship('OrderItem', back_populates='product')
