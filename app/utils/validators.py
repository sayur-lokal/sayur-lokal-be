from typing import Dict, Any, List, Tuple
from app.models.user import User
from app.models.buyer import BuyerProfile
from app.models.seller import SellerProfile
import logging

# Konfigurasi logging
logger = logging.getLogger(__name__)


class UserValidator:

    @staticmethod
    def validate_buyer_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validasi data registrasi buyer

        Args:
            data: Dictionary berisi data registrasi

        Returns:
            Dictionary berisi status validasi dan error (jika ada)
        """
        validation_errors = []

        # Cek apakah email sudah terdaftar di database lokal
        existing_user = User.query.filter_by(email=data.get("email")).first()
        if existing_user:
            validation_errors.append("Email sudah terdaftar di sistem")
            return {"valid": False, "errors": validation_errors}

        # Cek apakah username sudah digunakan
        if data.get("username"):
            existing_username = BuyerProfile.query.filter_by(
                username=data.get("username")
            ).first()
            if existing_username:
                validation_errors.append(
                    "Username sudah digunakan, silakan pilih username lain"
                )

        # Validasi field-field wajib
        required_fields = ["email", "password", "username"]
        for field in required_fields:
            if not data.get(field):
                validation_errors.append(f"Field {field} wajib diisi")

        # Validasi format email
        if data.get("email") and "@" not in data.get("email"):
            validation_errors.append("Format email tidak valid")

        # Validasi password
        if data.get("password") and len(data.get("password")) < 8:
            validation_errors.append("Password minimal 8 karakter")

        # Validasi username
        if data.get("username"):
            # Validasi panjang username
            if len(data.get("username")) < 3:
                validation_errors.append("Username minimal 3 karakter")

            # Validasi karakter username (hanya alfanumerik dan underscore)
            import re

            if not re.match(r"^[a-zA-Z0-9_]+$", data.get("username")):
                validation_errors.append(
                    "Username hanya boleh berisi huruf, angka, dan underscore"
                )

        # Validasi location_lat dan location_lng (jika ada)
        if data.get("location_lat") is not None:
            try:
                float(data.get("location_lat"))
            except (ValueError, TypeError):
                validation_errors.append("Format location_lat tidak valid")

        if data.get("location_lng") is not None:
            try:
                float(data.get("location_lng"))
            except (ValueError, TypeError):
                validation_errors.append("Format location_lng tidak valid")

        return {"valid": len(validation_errors) == 0, "errors": validation_errors}

    @staticmethod
    def validate_seller_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validasi data registrasi seller

        Args:
            data: Dictionary berisi data registrasi

        Returns:
            Dictionary berisi status validasi dan error (jika ada)
        """
        validation_errors = []

        # Cek apakah email sudah terdaftar di database lokal
        existing_user = User.query.filter_by(email=data.get("email")).first()
        if existing_user:
            validation_errors.append("Email sudah terdaftar di sistem")
            return {"valid": False, "errors": validation_errors}

        # Cek apakah nama toko sudah digunakan
        if data.get("shop_name"):
            existing_shop = SellerProfile.query.filter_by(
                shop_name=data.get("shop_name")
            ).first()
            if existing_shop:
                validation_errors.append(
                    "Nama toko sudah digunakan, silakan pilih nama toko lain"
                )

        # Validasi field-field wajib
        required_fields = [
            "email",
            "password",
            "shop_name",
            "location_address",
            "phone_number",
        ]
        for field in required_fields:
            if not data.get(field):
                validation_errors.append(f"Field {field} wajib diisi")

        # Validasi format email
        if data.get("email") and "@" not in data.get("email"):
            validation_errors.append("Format email tidak valid")

        # Validasi password
        if data.get("password") and len(data.get("password")) < 8:
            validation_errors.append("Password minimal 8 karakter")

        # Validasi nama toko
        if data.get("shop_name"):
            if len(data.get("shop_name")) < 3:
                validation_errors.append("Nama toko minimal 3 karakter")

        # Validasi nomor telepon
        if data.get("phone_number"):
            import re

            if not re.match(r"^[0-9+\-\s]+$", data.get("phone_number")):
                validation_errors.append("Format nomor telepon tidak valid")

        # Validasi location_lat dan location_lng (jika ada)
        if data.get("location_lat") is not None:
            try:
                float(data.get("location_lat"))
            except (ValueError, TypeError):
                validation_errors.append("Format location_lat tidak valid")

        if data.get("location_lng") is not None:
            try:
                float(data.get("location_lng"))
            except (ValueError, TypeError):
                validation_errors.append("Format location_lng tidak valid")

        return {"valid": len(validation_errors) == 0, "errors": validation_errors}

    def prepare_login_response(user, auth_response) -> Dict[str, Any]:
        """
        Menyiapkan response data untuk login

        Args:
            user: User model dari database lokal
            auth_response: Response dari Supabase auth

        Returns:
            Dictionary berisi data response
        """
        response_data = {
            "success": True,
            "message": "Login berhasil",
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value if user.role else None,
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
        }

        # Tambahkan data profil jika ada
        if user.role and user.role.value == "buyer" and user.buyer_profile:
            response_data["profile"] = {
                "username": user.buyer_profile.username,
                "profile_id": str(user.buyer_profile.id),
            }
        elif user.role and user.role.value == "seller" and user.seller_profile:
            response_data["profile"] = {
                "shop_name": user.seller_profile.shop_name,
                "profile_id": user.seller_profile.id,
            }

        return response_data
