from app.utils.extensions import db
from app.utils import chrono

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=chrono.now, nullable=True)
    
    # Relationship
    products = db.relationship('Product', back_populates='category')