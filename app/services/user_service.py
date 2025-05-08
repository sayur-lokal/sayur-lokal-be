from datetime import datetime
from typing import Any, Dict, Tuple
import re
from app.models.user import User
from app.schemas.user_schema import UserResponse, PasswordChangeSchema
from app.schemas.profile_schema import BuyerProfileResponse, SellerProfileResponse, BuyerProfileUpdate, SellerProfileUpdate
from app.utils.extensions import db
from app.utils.supabase_client import supabase_client
from pydantic import ValidationError


class UserService:
    @staticmethod
    def get_current_user_data(current_user):
        """
        Service untuk mendapatkan data user yang sedang login

        Args:
            current_user: Objek user yang sedang login

        Returns:
            Tuple berisi response (dict) dan status code (int)
        """
        try:
            if not current_user:
                return {"success": False, "message": "User tidak ditemukan"}, 404

            # Buat dictionary dari objek User
            user_dict = {
                "id": current_user.id,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "role": current_user.role.value if current_user.role else None,
                "created_at": current_user.created_at,
            }

            # Konversi user ke response schema
            try:
                user_data = UserResponse.model_validate(user_dict)
            except ValidationError as e:
                return {
                    "success": False,
                    "message": "Validasi data user gagal",
                    "errors": [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]
                }, 400

            response_data = {
                "success": True,
                "user": user_data.model_dump()
            }

            # Tambahkan data profil sesuai role
            if (
                current_user.role
                and current_user.role.value == "buyer"
                and current_user.buyer_profile
            ):
                # Buat dictionary dari profil buyer
                buyer_profile_dict = {
                    "id": current_user.buyer_profile.id,
                    "user_id": current_user.id,
                    "username": current_user.buyer_profile.username,
                    "address": current_user.buyer_profile.address,
                    "phone_number": current_user.buyer_profile.phone_number,
                    "profile_picture_url": current_user.buyer_profile.profile_picture_url,
                    "location_lat": current_user.buyer_profile.location_lat,
                    "location_lng": current_user.buyer_profile.location_lng,
                    # Tambahkan created_at dan updated_at jika ada
                    "created_at": getattr(current_user.buyer_profile, 'created_at', None),
                    "updated_at": getattr(current_user.buyer_profile, 'updated_at', None)
                }

                # Hapus nilai None jika field tidak wajib
                buyer_profile_dict = {k: v for k, v in buyer_profile_dict.items() if v is not None}

                try:
                    buyer_profile_data = BuyerProfileResponse.model_validate(buyer_profile_dict)
                    response_data["buyer_profile"] = buyer_profile_data.model_dump()
                except ValidationError as e:
                    return {
                        "success": False,
                        "message": "Validasi data profil buyer gagal",
                        "errors": [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]
                    }, 400

            elif (
                current_user.role
                and current_user.role.value == "seller"
                and current_user.seller_profile
            ):
                # Buat dictionary dari profil seller
                seller_profile_dict = {
                    "id": current_user.seller_profile.id,
                    "user_id": current_user.id,
                    "shop_name": current_user.seller_profile.shop_name,
                    "description": current_user.seller_profile.description,
                    "logo_url": current_user.seller_profile.logo_url,
                    "cover_image_url": current_user.seller_profile.cover_image_url,
                    "location_address": current_user.seller_profile.location_address,
                    "location_lat": current_user.seller_profile.location_lat,
                    "location_lng": current_user.seller_profile.location_lng,
                    "bank_account": current_user.seller_profile.bank_account,
                    "qris_account": current_user.seller_profile.qris_account,
                    "is_supports_cod": bool(current_user.seller_profile.is_supports_cod),  # Pastikan boolean
                    "phone_number": current_user.seller_profile.phone_number,
                    # Tambahkan created_at dan updated_at jika ada
                    "created_at": getattr(current_user.seller_profile, 'created_at', datetime.now()),
                    "updated_at": getattr(current_user.seller_profile, 'updated_at', datetime.now())
                }

                # Hapus nilai None jika field tidak wajib
                seller_profile_dict = {k: v for k, v in seller_profile_dict.items() if v is not None}

                try:
                    seller_profile_data = SellerProfileResponse.model_validate(seller_profile_dict)
                    response_data["seller_profile"] = seller_profile_data.model_dump()
                except ValidationError as e:
                    return {
                        "success": False,
                        "message": "Validasi data profil seller gagal",
                        "errors": [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]
                    }, 400

            # Jika user adalah admin, tambahkan info admin langsung
            elif current_user.role and current_user.role.value == "admin":
                response_data["admin_info"] = {
                    "email": current_user.email,
                    "role": "admin",
                    "created_at": (
                        current_user.created_at.isoformat()
                        if current_user.created_at
                        else None
                    ),
                }

            return response_data, 200

        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def update_buyer_profile(current_user, data):
        """
        Service untuk mengupdate profil buyer

        Args:
            current_user: Objek user yang sedang login
            data: Data profil yang akan diupdate

        Returns:
            Tuple berisi response (dict) dan status code (int)
        """
        try:
            # Validasi role user
            if not current_user or not current_user.buyer_profile:
                return {
                    "success": False,
                    "message": "Profil buyer tidak ditemukan"
                }, 404

            # Validasi data menggunakan schema
            try:
                # Hapus None values untuk menghindari validasi field yang tidak diisi
                profile_data = {k: v for k, v in data.items() if v is not None}
                validated_data = BuyerProfileUpdate(**profile_data)
            except ValidationError as e:
                errors = [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]
                return {
                    "success": False,
                    "message": "Validasi data gagal",
                    "errors": errors
                }, 400

            # Cek apakah username sudah digunakan (jika username diubah)
            if data.get("username") and data["username"] != current_user.buyer_profile.username:
                existing_username = User.query.join(User.buyer_profile).filter(
                    User.buyer_profile.has(username=data["username"]),
                    User.id != current_user.id
                ).first()

                if existing_username:
                    return {
                        "success": False,
                        "message": "Username sudah digunakan, silakan pilih username lain"
                    }, 400

            # Update profil buyer
            buyer_profile = current_user.buyer_profile

            # Update field yang ada di data
            for field, value in validated_data.model_dump(exclude_unset=True).items():
                setattr(buyer_profile, field, value)

            db.session.commit()

            # Siapkan response
            try:
                updated_profile = BuyerProfileResponse(
                    id=buyer_profile.id,
                    user_id=current_user.id,
                    username=buyer_profile.username,
                    address=buyer_profile.address,
                    phone_number=buyer_profile.phone_number,
                    profile_picture_url=buyer_profile.profile_picture_url,
                    location_lat=buyer_profile.location_lat,
                    location_lng=buyer_profile.location_lng,
                    created_at=buyer_profile.created_at,
                    updated_at=buyer_profile.updated_at
                )
            except ValidationError as e:
                db.session.rollback()
                return {
                    "success": False,
                    "message": "Validasi data hasil update gagal",
                    "errors": [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]
                }, 400

            return {
                "success": True,
                "message": "Profil berhasil diperbarui",
                "buyer_profile": updated_profile.model_dump()
            }, 200

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def update_seller_profile(current_user, data):
        """
        Service untuk mengupdate profil seller

        Args:
            current_user: Objek user yang sedang login
            data: Data profil yang akan diupdate

        Returns:
            Tuple berisi response (dict) dan status code (int)
        """
        try:
            # Validasi role user
            if not current_user or not current_user.seller_profile:
                return {
                    "success": False,
                    "message": "Profil seller tidak ditemukan"
                }, 404

            # Validasi data menggunakan schema
            try:
                # Hapus None values untuk menghindari validasi field yang tidak diisi
                profile_data = {k: v for k, v in data.items() if v is not None}
                validated_data = SellerProfileUpdate(**profile_data)
            except ValidationError as e:
                errors = [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]
                return {
                    "success": False,
                    "message": "Validasi data gagal",
                    "errors": errors
                }, 400

            # Cek apakah shop_name sudah digunakan (jika shop_name diubah)
            if data.get("shop_name") and data["shop_name"] != current_user.seller_profile.shop_name:
                existing_shop = User.query.join(User.seller_profile).filter(
                    User.seller_profile.has(shop_name=data["shop_name"]),
                    User.id != current_user.id
                ).first()

                if existing_shop:
                    return {
                        "success": False,
                        "message": "Nama toko sudah digunakan, silakan pilih nama toko lain"
                    }, 400

            # Update profil seller
            seller_profile = current_user.seller_profile

            # Update field yang ada di data
            for field, value in validated_data.model_dump(exclude_unset=True).items():
                setattr(seller_profile, field, value)

            db.session.commit()

            # Siapkan response
            try:
                updated_profile = SellerProfileResponse(
                    id=seller_profile.id,
                    user_id=current_user.id,
                    shop_name=seller_profile.shop_name,
                    description=seller_profile.description,
                    logo_url=seller_profile.logo_url,
                    cover_image_url=seller_profile.cover_image_url,
                    location_address=seller_profile.location_address,
                    location_lat=seller_profile.location_lat,
                    location_lng=seller_profile.location_lng,
                    bank_account=seller_profile.bank_account,
                    qris_account=seller_profile.qris_account,
                    is_supports_cod=seller_profile.is_supports_cod,
                    phone_number=seller_profile.phone_number,
                    created_at=seller_profile.created_at,
                    updated_at=seller_profile.updated_at
                )
            except ValidationError as e:
                db.session.rollback()
                return {
                    "success": False,
                    "message": "Validasi data hasil update gagal",
                    "errors": [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]
                }, 400

            return {
                "success": True,
                "message": "Profil toko berhasil diperbarui",
                "seller_profile": updated_profile.model_dump()
            }, 200

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def update_profile_picture(current_user, data):
        """
        Service untuk mengupdate foto profil (untuk buyer) atau logo (untuk seller)

        Args:
            current_user: Objek user yang sedang login
            data: Data URL gambar yang akan diupdate

        Returns:
            Tuple berisi response (dict) dan status code (int)
        """
        try:
            if not current_user:
                return {"success": False, "message": "User tidak ditemukan"}, 404

            image_url = data.get("image_url")
            if not image_url:
                return {
                    "success": False,
                    "message": "URL gambar harus diisi"
                }, 400

            # Validasi URL gambar
            if len(image_url) > 255:
                return {
                    "success": False,
                    "message": "URL gambar tidak boleh lebih dari 255 karakter"
                }, 400

            # Validasi format URL gambar
            if not image_url.startswith(('http://', 'https://')):
                return {
                    "success": False,
                    "message": "URL gambar harus dimulai dengan http:// atau https://"
                }, 400

            # Update sesuai role
            if current_user.role.value == "buyer" and current_user.buyer_profile:
                current_user.buyer_profile.profile_picture_url = image_url
                db.session.commit()
                return {
                    "success": True,
                    "message": "Foto profil berhasil diperbarui",
                    "profile_picture_url": image_url
                }, 200

            elif current_user.role.value == "seller" and current_user.seller_profile:
                current_user.seller_profile.logo_url = image_url
                db.session.commit()
                return {
                    "success": True,
                    "message": "Logo toko berhasil diperbarui",
                    "logo_url": image_url
                }, 200

            else:
                return {
                    "success": False,
                    "message": "Profil tidak ditemukan"
                }, 404

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def reset_password(email: str) -> Tuple[Dict[str, Any], int]:
        """
        Fungsi untuk mengirim email reset password

        Args:
            email: Email user yang akan direset passwordnya

        Returns:
            Tuple berisi response (dict) dan status code (int)
        """
        try:
            # Validasi input dasar
            if not email:
                return {
                    "success": False,
                    "message": "Email harus diisi"
                }, 400

            # Validasi format email
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return {
                    "success": False,
                    "message": "Format email tidak valid"
                }, 400

            # Cek apakah email terdaftar
            user = User.query.filter_by(email=email).first()
            if not user:
                # Untuk keamanan, kita tetap mengembalikan sukses meskipun email tidak ditemukan
                # Ini untuk mencegah enumeration attack
                return {
                    "success": True,
                    "message": "Jika email terdaftar, instruksi reset password akan dikirim"
                }, 200

            # Kirim email reset password dengan Supabase
            try:
                supabase_client.auth.reset_password_email(email)

                return {
                    "success": True,
                    "message": "Email reset password telah dikirim, silakan cek email Anda"
                }, 200

            except Exception as supabase_error:
                return {
                    "success": False,
                    "message": f"Error saat mengirim email reset password: {str(supabase_error)}"
                }, 500

        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def change_password(current_user, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Fungsi untuk mengubah password user

        Args:
            current_user: Objek user yang sedang login
            data: Data password yang akan diubah

        Returns:
            Tuple berisi response (dict) dan status code (int)
        """
        try:
            if not current_user:
                return {"success": False, "message": "User tidak ditemukan"}, 404

            # Validasi data dengan schema
            try:
                validated_data = PasswordChangeSchema(
                    current_password=data.get("current_password"),
                    new_password=data.get("new_password"),
                    confirm_password=data.get("confirm_password")
                )
            except ValidationError as e:
                errors = [f"{error['loc'][0]}: {error['msg']}" for error in e.errors()]
                return {
                    "success": False,
                    "message": "Validasi data gagal",
                    "errors": errors
                }, 400

            current_password = validated_data.current_password
            new_password = validated_data.new_password

            # Validasi password baru tidak sama dengan password lama
            if current_password == new_password:
                return {
                    "success": False,
                    "message": "Password baru tidak boleh sama dengan password lama"
                }, 400

            # Ubah password dengan Supabase
            try:
                # Login ulang untuk memverifikasi password lama
                auth_response = supabase_client.auth.sign_in_with_password({
                    "email": current_user.email,
                    "password": current_password
                })

                if hasattr(auth_response, "error") and auth_response.error:
                    return {
                        "success": False,
                        "message": "Password lama salah"
                    }, 401

                # Update password
                supabase_client.auth.update_user(
                    {"password": new_password},
                    auth_response.session.access_token
                )

                return {
                    "success": True,
                    "message": "Password berhasil diubah"
                }, 200

            except Exception as supabase_error:
                return {
                    "success": False,
                    "message": f"Error saat mengubah password: {str(supabase_error)}"
                }, 500

        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500
