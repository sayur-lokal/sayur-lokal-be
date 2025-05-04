from app.utils.extensions import db
from app.utils import chrono

class Rating(db.Model):
    __tablename__ = "ratings"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    
    rating = db.Column(db.Integer, nullable=True)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=chrono.now, nullable=True)
    
    # relationships
    product = db.relationship("Product", back_populates="ratings")
    buyer = db.relationship("User", back_populates="ratings")