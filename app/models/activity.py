from app.utils import chrono
from app.utils.extensions import db
from datetime import datetime

class Activity(db.Model):
    """Model untuk aktivitas seller"""
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("seller_profiles.id"), nullable=True)
    activity_type = db.Column(db.String(50), nullable=True)  # order, product, promotion, etc.
    description = db.Column(db.String(255), nullable=True)
    reference_id = db.Column(db.Integer, nullable=True)  # ID referensi (order_id, product_id, etc.)
    created_at = db.Column(db.DateTime, default=chrono.now, nullable=True)


    # Relasi
    seller = db.relationship("SellerProfile", backref=db.backref("activities", lazy=True))

    def __repr__(self):
        return f"<Activity {self.id}: {self.activity_type} - {self.description}>"
