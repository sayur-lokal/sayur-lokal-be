from app.utils.helpers import _handle_validation_error
from app.utils.supabase_client import supabase_client
from app.utils.extensions import db
from app.models.user import User, UserRole
from app.models.buyer import BuyerProfile
from app.models.seller import SellerProfile
from app.schemas.profile_schema import BuyerProfileCreate, SellerProfileCreate
from app.schemas.user_schema import UserCreate, UserResponse
from pydantic import ValidationError, EmailStr
from typing import Dict, Any, Tuple


class AuthService:
    @staticmethod
    def register_buyer(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Fungsi untuk registrasi buyer dengan validasi schema
        """
        try:
            # 1. Validasi struktur data dengan Pydantic
            try:
                # Validasi data user
                user_data = UserCreate(
                    email=data.get("email"),
                    password=data.get("password"),
                    full_name=data.get("full_name"),
                )

                # Validasi data profil buyer
                profile_data = BuyerProfileCreate(
                    user_id=0,  # Akan diupdate setelah user dibuat
                    username=data.get("username"),
                    address=data.get("address"),
                    phone_number=data.get("phone_number"),
                    profile_picture_url=data.get("profile_picture_url"),
                    location_lat=data.get("location_lat"),
                    location_lng=data.get("location_lng"),
                )

                # Konversi kembali ke dict untuk penggunaan selanjutnya
                validated_data = {
                    **user_data.model_dump(),
                    **profile_data.model_dump(exclude={"user_id"}),
                }

            except ValidationError as e:
                return _handle_validation_error(e)

            # 2. Validasi bisnis (cek duplikasi)
            # Cek apakah email sudah terdaftar
            existing_user = User.query.filter_by(
                email=validated_data.get("email")
            ).first()
            if existing_user:
                return {
                    "success": False,
                    "message": "Email sudah terdaftar di sistem",
                }, 400

            # Cek apakah username sudah digunakan
            existing_username = BuyerProfile.query.filter_by(
                username=validated_data.get("username")
            ).first()
            if existing_username:
                return {
                    "success": False,
                    "message": "Username sudah digunakan, silakan pilih username lain",
                }, 400

            # 3. Registrasi di Supabase
            try:
                auth_response = supabase_client.auth.sign_up(
                    {
                        "email": validated_data.get("email"),
                        "password": validated_data.get("password"),
                    }
                )

                if hasattr(auth_response, "error") and auth_response.error:
                    return {
                        "success": False,
                        "message": auth_response.error.message,
                    }, 400

                # Simpan UID untuk digunakan nanti
                supabase_uid = auth_response.user.id

            except Exception as supabase_error:
                return {
                    "success": False,
                    "message": f"Error saat mendaftar di Supabase: {str(supabase_error)}",
                }, 500

            # 4. Buat user di database lokal
            try:
                # Mulai transaksi
                db.session.begin_nested()

                new_user = User(
                    email=validated_data.get("email"),
                    supabase_uid=supabase_uid,
                    full_name=validated_data.get("full_name"),
                    role=UserRole.BUYER,
                )

                db.session.add(new_user)
                db.session.flush()  # Flush untuk mendapatkan ID

                # 5. Buat profil buyer
                buyer_profile = BuyerProfile(
                    user_id=new_user.id,
                    username=validated_data.get("username"),
                    address=validated_data.get("address"),
                    phone_number=validated_data.get("phone_number"),
                    profile_picture_url=validated_data.get("profile_picture_url"),
                    location_lat=validated_data.get("location_lat"),
                    location_lng=validated_data.get("location_lng"),
                )

                db.session.add(buyer_profile)
                db.session.commit()

            except Exception as e:
                db.session.rollback()

                # PENTING: Hapus user dari Supabase jika terjadi error
                if supabase_uid:
                    try:
                        # Gunakan admin API untuk menghapus user
                        supabase_client.auth.admin.delete_user(supabase_uid)
                    except Exception as delete_error:
                        # Log error penghapusan, tapi tetap lanjutkan untuk mengembalikan error utama
                        print(
                            f"Error saat menghapus user dari Supabase: {str(delete_error)}"
                        )

                # Jika error terjadi karena duplikasi
                if "duplicate key" in str(e) or "unique constraint" in str(e):
                    return {
                        "success": False,
                        "message": "Email atau username sudah terdaftar di sistem",
                    }, 400

                return {
                    "success": False,
                    "message": f"Terjadi kesalahan: {str(e)}",
                }, 500

            return {
                "success": True,
                "message": "Pendaftaran buyer berhasil, silakan verifikasi email Anda",
                "user_id": new_user.id,
                "supabase_uid": str(supabase_uid),
            }, 201

        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def register_seller(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Fungsi untuk registrasi seller dengan validasi schema
        """
        try:
            # 1. Validasi struktur data dengan Pydantic
            try:
                # Validasi data user
                user_data = UserCreate(
                    email=data.get("email"),
                    password=data.get("password"),
                    full_name=data.get("full_name"),
                )

                # Validasi data profil seller
                profile_data = SellerProfileCreate(
                    user_id=0,  # Akan diupdate setelah user dibuat
                    shop_name=data.get("shop_name"),
                    description=data.get("description"),
                    logo_url=data.get("logo_url"),
                    cover_image_url=data.get("cover_image_url"),
                    location_address=data.get("location_address"),
                    location_lat=data.get("location_lat"),
                    location_lng=data.get("location_lng"),
                    bank_account=data.get("bank_account"),
                    qris_account=data.get("qris_account"),
                    is_supports_cod=data.get("is_supports_cod", True),
                    phone_number=data.get("phone_number"),
                )

                # Konversi kembali ke dict untuk penggunaan selanjutnya
                validated_data = {
                    **user_data.model_dump(),
                    **profile_data.model_dump(exclude={"user_id"}),
                }

            except ValidationError as e:
                return _handle_validation_error(e)

            # 2. Validasi bisnis (cek duplikasi)
            # Cek apakah email sudah terdaftar di database lokal
            existing_user = User.query.filter_by(
                email=validated_data.get("email")
            ).first()
            if existing_user:
                return {
                    "success": False,
                    "message": "Email sudah terdaftar di sistem",
                }, 400

            # Cek apakah nama toko sudah digunakan
            existing_shop = SellerProfile.query.filter_by(
                shop_name=validated_data.get("shop_name")
            ).first()
            if existing_shop:
                return {
                    "success": False,
                    "message": "Nama toko sudah digunakan, silakan pilih nama toko lain",
                }, 400

            # 3. Registrasi di Supabase - SETELAH SEMUA VALIDASI
            try:
                auth_response = supabase_client.auth.sign_up(
                    {
                        "email": validated_data.get("email"),
                        "password": validated_data.get("password"),
                    }
                )

                if hasattr(auth_response, "error") and auth_response.error:
                    return {
                        "success": False,
                        "message": auth_response.error.message,
                    }, 400

                # Simpan UID untuk digunakan nanti
                supabase_uid = auth_response.user.id

                # 4. Buat user di database lokal dalam transaksi
                try:
                    # Mulai transaksi
                    db.session.begin_nested()

                    new_user = User(
                        email=validated_data.get("email"),
                        supabase_uid=supabase_uid,
                        full_name=validated_data.get("full_name"),
                        role=UserRole.SELLER,
                    )

                    db.session.add(new_user)
                    db.session.flush()  # Flush untuk mendapatkan ID

                    # 5. Buat profil seller
                    seller_profile = SellerProfile(
                        user_id=new_user.id,
                        shop_name=validated_data.get("shop_name"),
                        description=validated_data.get("description"),
                        logo_url=validated_data.get("logo_url"),
                        cover_image_url=validated_data.get("cover_image_url"),
                        location_address=validated_data.get("location_address"),
                        location_lat=validated_data.get("location_lat"),
                        location_lng=validated_data.get("location_lng"),
                        bank_account=validated_data.get("bank_account"),
                        qris_account=validated_data.get("qris_account"),
                        is_supports_cod=validated_data.get("is_supports_cod", True),
                        phone_number=validated_data.get("phone_number"),
                    )

                    db.session.add(seller_profile)
                    db.session.commit()

                    return {
                        "success": True,
                        "message": "Pendaftaran seller berhasil, silakan verifikasi email Anda",
                        "user_id": new_user.id,
                        "supabase_uid": str(supabase_uid),
                    }, 201

                except Exception as db_error:
                    db.session.rollback()

                    # PENTING: Hapus user dari Supabase karena gagal menyimpan ke database lokal
                    try:
                        # Gunakan admin API untuk menghapus user
                        supabase_client.auth.admin.delete_user(supabase_uid)
                    except Exception as delete_error:
                        # Log error penghapusan
                        print(
                            f"Error saat menghapus user dari Supabase: {str(delete_error)}"
                        )

                    # Jika error terjadi karena duplikasi
                    if "duplicate key" in str(db_error) or "unique constraint" in str(
                        db_error
                    ):
                        return {
                            "success": False,
                            "message": "Email atau nama toko sudah terdaftar di sistem",
                        }, 400

                    return {
                        "success": False,
                        "message": f"Terjadi kesalahan saat menyimpan data: {str(db_error)}",
                    }, 500

            except Exception as supabase_error:
                return {
                    "success": False,
                    "message": f"Error saat mendaftar di Supabase: {str(supabase_error)}",
                }, 500

        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def login_user(email: str, password: str) -> Tuple[Dict[str, Any], int]:
        """
        Fungsi untuk login user
        """
        try:
            # Validasi input dasar
            if not email:
                return {"success": False, "message": "Email harus diisi"}, 400

            if not password:
                return {"success": False, "message": "Password harus diisi"}, 400

            # Login dengan Supabase
            try:
                auth_response = supabase_client.auth.sign_in_with_password(
                    {"email": email, "password": password}
                )

                if hasattr(auth_response, "error") and auth_response.error:
                    # Jika error karena email belum diverifikasi
                    if "Email not confirmed" in auth_response.error.message:
                        return {
                            "success": False,
                            "message": "Email belum diverifikasi, silakan cek email Anda",
                            "email_verified": False,
                        }, 400

                    # Error login lainnya
                    return {
                        "success": False,
                        "message": "Email atau password salah",
                    }, 401

                # Ambil data user dari database lokal
                user = User.query.filter_by(supabase_uid=auth_response.user.id).first()
                if not user:
                    return {
                        "success": False,
                        "message": "User tidak ditemukan di sistem",
                    }, 404

                # Siapkan response berdasarkan role
                user_data = {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value,
                    "created_at": (
                        user.created_at.isoformat() if user.created_at else None
                    ),
                }

                # Tambahkan data profil sesuai role
                if user.role == UserRole.BUYER and user.buyer_profile:
                    user_data["buyer_profile"] = {
                        "id": user.buyer_profile.id,
                        "username": user.buyer_profile.username,
                        "address": user.buyer_profile.address,
                        "phone_number": user.buyer_profile.phone_number,
                        "profile_picture_url": user.buyer_profile.profile_picture_url,
                        "location_lat": user.buyer_profile.location_lat,
                        "location_lng": user.buyer_profile.location_lng,
                    }
                elif user.role == UserRole.SELLER and user.seller_profile:
                    user_data["seller_profile"] = {
                        "id": user.seller_profile.id,
                        "shop_name": user.seller_profile.shop_name,
                        "description": user.seller_profile.description,
                        "logo_url": user.seller_profile.logo_url,
                        "cover_image_url": user.seller_profile.cover_image_url,
                        "location_address": user.seller_profile.location_address,
                        "location_lat": user.seller_profile.location_lat,
                        "location_lng": user.seller_profile.location_lng,
                        "bank_account": user.seller_profile.bank_account,
                        "qris_account": user.seller_profile.qris_account,
                        "is_supports_cod": user.seller_profile.is_supports_cod,
                        "phone_number": user.seller_profile.phone_number,
                    }

                return {
                    "success": True,
                    "message": "Login berhasil",
                    "user": user_data,
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                }, 200

            except Exception as supabase_error:
                return {
                    "success": False,
                    "message": f"Error saat login: {str(supabase_error)}",
                }, 500

        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def resend_verification(email: str) -> Tuple[Dict[str, Any], int]:
        """
        Fungsi untuk mengirim ulang email verifikasi
        """
        try:
            # Validasi input dasar
            if not email:
                return {"success": False, "message": "Email harus diisi"}, 400

            # Cek apakah email terdaftar
            user = User.query.filter_by(email=email).first()
            if not user:
                return {
                    "success": False,
                    "message": "Email tidak terdaftar di sistem",
                }, 404

            # Kirim ulang email verifikasi dengan Supabase
            try:
                supabase_client.auth.resend_email(email=email, type="signup")

                return {
                    "success": True,
                    "message": "Email verifikasi telah dikirim ulang, silakan cek email Anda",
                }, 200

            except Exception as supabase_error:
                return {
                    "success": False,
                    "message": f"Error saat mengirim email verifikasi: {str(supabase_error)}",
                }, 500

        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def logout_user(token: str = None) -> Dict[str, Any]:
        """
        Fungsi untuk logout user

        Args:
            token: Token akses yang akan diinvalidasi (opsional)

        Returns:
            Dictionary berisi status dan pesan
        """
        try:
            # Lakukan logout dari Supabase tanpa token
            # Ini akan menghapus sesi di sisi klien
            supabase_client.auth.sign_out()

            return {"success": True, "message": "Logout berhasil"}

        except Exception as e:
            return {"success": False, "message": f"Error saat logout: {str(e)}"}

    def refresh_access_token(refresh_token: str) -> Tuple[Dict[str, Any], int]:
        """
        Fungsi untuk memperbaharui access token menggunakan refresh token
        """
        try:
            # Validasi input dasar
            if not refresh_token:
                return {"success": False, "message": "Refresh token harus diisi"}, 400

            # Refresh token dengan Supabase
            try:
                auth_response = supabase_client.auth.refresh_session(refresh_token)

                if hasattr(auth_response, "error") and auth_response.error:
                    return {
                        "success": False,
                        "message": "Refresh token tidak valid atau sudah kadaluarsa",
                    }, 401

                # Ambil data user dari database lokal
                user = User.query.filter_by(supabase_uid=auth_response.user.id).first()
                if not user:
                    return {
                        "success": False,
                        "message": "User tidak ditemukan di sistem",
                    }, 404

                return {
                    "success": True,
                    "message": "Token berhasil diperbaharui",
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                }, 200

            except Exception as supabase_error:
                return {
                    "success": False,
                    "message": f"Error saat refresh token: {str(supabase_error)}",
                }, 500

        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def delete_account(current_user, password: str) -> Tuple[Dict[str, Any], int]:
        """
        Fungsi untuk menghapus akun pengguna

        Args:
            current_user: Objek user yang sedang login
            password: Password untuk konfirmasi penghapusan akun

        Returns:
            Tuple berisi response (dict) dan status code (int)
        """
        try:
            # Validasi input dasar
            if not current_user:
                return {"success": False, "message": "User tidak ditemukan"}, 404

            if not password:
                return {
                    "success": False,
                    "message": "Password harus diisi untuk konfirmasi penghapusan akun",
                }, 400

            # Verifikasi password dengan login ulang ke Supabase
            try:
                auth_response = supabase_client.auth.sign_in_with_password(
                    {"email": current_user.email, "password": password}
                )

                if hasattr(auth_response, "error") and auth_response.error:
                    return {
                        "success": False,
                        "message": "Password salah, penghapusan akun dibatalkan",
                    }, 401

                # Simpan supabase_uid untuk digunakan dalam penghapusan
                supabase_uid = current_user.supabase_uid

                # Mulai transaksi database
                db.session.begin_nested()

                # Hapus data profil sesuai role
                if current_user.role == UserRole.BUYER and current_user.buyer_profile:
                    db.session.delete(current_user.buyer_profile)
                elif (
                    current_user.role == UserRole.SELLER and current_user.seller_profile
                ):
                    db.session.delete(current_user.seller_profile)

                # Hapus user dari database lokal
                db.session.delete(current_user)
                db.session.commit()

                # Hapus user dari Supabase Auth
                try:
                    # Gunakan admin API untuk menghapus user
                    # Pastikan supabase_client memiliki akses admin
                    # Gunakan UUID untuk supabase_uid
                    import uuid

                    # Konversi string ke UUID jika perlu
                    if isinstance(supabase_uid, str):
                        try:
                            supabase_uid = uuid.UUID(supabase_uid)
                        except ValueError:
                            print(f"Invalid UUID format: {supabase_uid}")

                    # Hapus user dari Supabase
                    supabase_client.auth.admin.delete_user(supabase_uid)

                    return {
                        "success": True,
                        "message": "Akun berhasil dihapus dari sistem dan Supabase Auth",
                    }, 200

                except Exception as delete_error:
                    # Log error penghapusan
                    print(
                        f"Error saat menghapus user dari Supabase: {str(delete_error)}"
                    )

                    # Meskipun gagal menghapus dari Supabase, data lokal sudah terhapus
                    return {
                        "success": True,
                        "message": "Akun berhasil dihapus dari sistem, tetapi gagal menghapus dari Supabase Auth",
                        "supabase_error": str(delete_error),
                    }, 200

            except Exception as auth_error:
                db.session.rollback()
                return {
                    "success": False,
                    "message": f"Error saat verifikasi password: {str(auth_error)}",
                }, 500

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500
