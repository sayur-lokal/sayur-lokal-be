from functools import wraps
from flask import request, jsonify
from app.utils.supabase_client import supabase_client
from app.models.user import User


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Cek apakah ada header Authorization
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            # Format: "Bearer <token>"
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"success": False, "message": "Token tidak valid"}), 401

        if not token:
            return jsonify({"success": False, "message": "Token tidak ditemukan"}), 401

        try:
            # Verifikasi token dengan Supabase
            user = supabase_client.auth.get_user(token)

            if not user or not user.user:
                return jsonify({"success": False, "message": "Token tidak valid"}), 401

            # Ambil user dari database lokal
            current_user = User.query.filter_by(supabase_uid=user.user.id).first()

            if not current_user:
                return (
                    jsonify({"success": False, "message": "User tidak ditemukan"}),
                    404,
                )

            # Tambahkan user ke request
            kwargs["current_user"] = current_user

            return f(*args, **kwargs)

        except Exception as e:
            return (
                jsonify({"success": False, "message": f"Terjadi kesalahan: {str(e)}"}),
                401,
            )

    return decorated


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Pastikan current_user ada di kwargs (dari token_required)
            if "current_user" not in kwargs:
                return (
                    jsonify({"success": False, "message": "Autentikasi diperlukan"}),
                    401,
                )

            current_user = kwargs["current_user"]

            # Periksa role pengguna
            if not current_user.role or current_user.role.value != role:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": f"Akses ditolak. Hanya {role} yang dapat mengakses endpoint ini",
                        }
                    ),
                    403,
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator
