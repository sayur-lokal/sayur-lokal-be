from app.utils import chrono
from app.utils.extensions import db


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)

    quantity = db.Column(db.Integer, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)

    created_at = db.Column(db.DateTime, default=chrono.now)

    # relationships
    order = db.relationship("Order", back_populates="order_items")
    product = db.relationship("Product", back_populates="order_items")
