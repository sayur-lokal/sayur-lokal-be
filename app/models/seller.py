from app.utils.extensions import db

class SellerProfile(db.Model):
    __tablename__ = 'seller_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=True)

    shop_name = db.Column(db.String(100), nullable=True)
    
    description = db.Column(db.Text, nullable=True)
    logo_url = db.Column(db.String(255), nullable=True)
    cover_image_url = db.Column(db.String(255), nullable=True)
    location_address = db.Column(db.String(255), nullable=True)
    location_lat = db.Column(db.Float, nullable=True)
    location_lng = db.Column(db.Float, nullable=True)
    
    is_verified = db.Column(db.Boolean, default=False, nullable=True)  # by admin
    is_eco_friendly = db.Column(db.Boolean, default=False, nullable=True)
    
    bank_account = db.Column(db.String(255), nullable=True)  # No Rekening untuk withdrawal
    qris_account = db.Column(db.String(255), nullable=True)  # QRIS (optional)
    is_supports_cod = db.Column(db.Boolean, default=True, nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)

    # Relationships
    products = db.relationship('Product', back_populates='seller')
    user = db.relationship("User", back_populates="seller_profile")
    orders = db.relationship("Order", back_populates="seller", foreign_keys="Order.seller_id")