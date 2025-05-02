from app.utils.supabase_client import supabase_client
from app.utils.extensions import db
from app.models.user import User, UserRole
from app.models.buyer import BuyerProfile
from app.models.seller import SellerProfile


class AuthService:
    def register_buyer(data):
        """
        Fungsi untuk registrasi buyer
        """
        try:
            # Validasi data terlebih dahulu
            validation_errors = []

            # Cek apakah email sudah terdaftar di database lokal
            existing_user = User.query.filter_by(email=data.get("email")).first()
            if existing_user:
                return {
                    "success": False,
                    "message": "Email sudah terdaftar di sistem",
                }, 400

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

            # Jika ada error validasi, kembalikan error
            if validation_errors:
                return {
                    "success": False,
                    "message": "Validasi gagal",
                    "errors": validation_errors,
                }, 400

            # 1. Registrasi di Supabase
            try:
                auth_response = supabase_client.auth.sign_up(
                    {"email": data.get("email"), "password": data.get("password")}
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

            # 2. Buat user di database lokal
            try:
                # Mulai transaksi
                db.session.begin_nested()

                new_user = User(
                    email=data.get("email"),
                    supabase_uid=supabase_uid,
                    full_name=data.get("full_name"),
                    role=UserRole.BUYER,
                )

                db.session.add(new_user)
                db.session.flush()  # Flush untuk mendapatkan ID

                # 3. Buat profil buyer
                buyer_profile = BuyerProfile(
                    user_id=new_user.id,
                    username=data.get("username"),
                    address=data.get("address"),
                    phone_number=data.get("phone_number"),
                    location_lat=data.get("location_lat"),
                    location_lng=data.get("location_lng"),
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

    def register_seller(data):
        """
        Fungsi untuk registrasi seller
        """
        try:
            # Validasi data terlebih dahulu
            validation_errors = []

            # Cek apakah email sudah terdaftar di database lokal
            existing_user = User.query.filter_by(email=data.get("email")).first()
            if existing_user:
                return {
                    "success": False,
                    "message": "Email sudah terdaftar di sistem",
                }, 400

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

            # Jika ada error validasi, kembalikan error
            if validation_errors:
                return {
                    "success": False,
                    "message": "Validasi gagal",
                    "errors": validation_errors,
                }, 400

            # 1. Registrasi di Supabase (hanya dilakukan setelah validasi berhasil)
            try:
                auth_response = supabase_client.auth.sign_up(
                    {"email": data.get("email"), "password": data.get("password")}
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

            # 2. Buat user di database lokal
            try:
                # Mulai transaksi
                db.session.begin_nested()

                new_user = User(
                    email=data.get("email"),
                    supabase_uid=supabase_uid,
                    full_name=data.get("full_name"),
                    role=UserRole.SELLER,
                )

                db.session.add(new_user)
                db.session.flush()  # Flush untuk mendapatkan ID

                # 3. Buat profil seller
                seller_profile = SellerProfile(
                    user_id=new_user.id,
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

                db.session.add(seller_profile)
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
                        "message": "Email sudah terdaftar di sistem",
                    }, 400

                return {
                    "success": False,
                    "message": f"Terjadi kesalahan: {str(e)}",
                }, 500

            return {
                "success": True,
                "message": "Pendaftaran seller berhasil, silakan verifikasi email Anda",
                "user_id": new_user.id,
                "supabase_uid": str(supabase_uid),
            }, 201

        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    def login_user(email, password):
        """
        Fungsi untuk login user
        """
        if not email or not password:
            return {"success": False, "message": "Email dan password harus diisi"}, 400

        try:
            # Login dengan Supabase
            auth_response = supabase_client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            # Cek apakah login berhasil
            if hasattr(auth_response, "error") and auth_response.error:
                return {
                    "success": False,
                    "message": f"Login gagal: {auth_response.error.message}",
                }, 401

            # Ambil data user dari database lokal
            user = User.query.filter_by(email=email).first()

            if not user:
                return {
                    "success": False,
                    "message": "User tidak ditemukan di sistem",
                }, 404

            # Siapkan response data
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

            return response_data, 200

        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    def resend_verification_email(email):
        """
        Fungsi untuk mengirim ulang email verifikasi
        """
        try:
            # Pastikan email adalah string, bukan dictionary
            if isinstance(email, dict):
                email = email.get("email")

            # Kirim ulang email verifikasi melalui Supabase
            # Ganti resend() dengan resend_signup_email()
            supabase_client.auth.resend({"email": email, "type": "signup"})

            return {
                "success": True,
                "message": "Email verifikasi telah dikirim ulang. Silakan periksa kotak masuk Anda.",
            }, 200

        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    def logout_user():
        """
        Fungsi untuk logout user
        """
        try:
            response = supabase_client.auth.sign_out()

            # Periksa response
            if hasattr(response, "error") and response.error:
                return {
                    "success": False,
                    "message": f"Logout gagal: {response.error.message}",
                }

            return {"success": True, "message": "Logout berhasil"}
        except Exception as e:
            return {
                "success": False,
                "message": f"Terjadi kesalahan saat logout: {str(e)}",
            }
