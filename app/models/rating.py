from app.utils import chrono
from app.utils.extensions import db

class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=chrono.now)

    # relationships
    product = db.relationship('Product', back_populates='ratings')
    buyer = db.relationship('User', back_populates='ratings')