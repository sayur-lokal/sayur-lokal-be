from app.utils.extensions import db

class SellerProfile(db.Model):
    __tablename__ = 'seller_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)

    shop_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(255))
    cover_image_url = db.Column(db.String(255))
    location_address = db.Column(db.String(255))
    location_lat = db.Column(db.Float)
    location_lng = db.Column(db.Float)
    is_verified = db.Column(db.Boolean, default=False)  # by admin
    is_eco_friendly = db.Column(db.Boolean, default=False)
    
    bank_account = db.Column(db.String(255))  # No Rekening untuk withdrawal
    qris_account = db.Column(db.String(255))  # QRIS (optional)
    is_supports_cod = db.Column(db.Boolean, default=True)
    phone_number = db.Column(db.String(20))

    # Relationships
    products = db.relationship('Product', back_populates='seller')
    user = db.relationship("User", back_populates="seller_profile")
    orders = db.relationship("Order", back_populates="seller", foreign_keys="Order.seller_id")