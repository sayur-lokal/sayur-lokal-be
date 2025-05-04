from app.utils.extensions import db
# from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID

class BuyerProfile(db.Model):
    __tablename__ = "buyer_profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=True)

    username = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    location_lat = db.Column(db.Float, nullable=True)
    location_lng = db.Column(db.Float, nullable=True)
    
    # Relationship
    user = db.relationship("User", back_populates="buyer_profile")