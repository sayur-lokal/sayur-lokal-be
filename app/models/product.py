from app.utils.extensions import db
from app.utils import chrono


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(
        db.Integer, db.ForeignKey("seller_profiles.id"), nullable=True
    )
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    name = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)
    stock = db.Column(db.Integer, nullable=True)
    product_image_url = db.Column(db.String(255), nullable=True)
    # image_url = db.Column(db.JSON)  # Array of image URLs
    discount = db.Column(db.Float, default=0)  # Persentase diskon (0-100)

    created_at = db.Column(db.DateTime, default=chrono.now, nullable=True)
    updated_at = db.Column(
        db.DateTime, default=chrono.now, onupdate=chrono.now, nullable=True
    )

    # Relationships
    seller = db.relationship("SellerProfile", back_populates="products")
    category = db.relationship("Category", back_populates="products")
    ratings = db.relationship("Rating", back_populates="product")
    order_items = db.relationship("OrderItem", back_populates="product")
