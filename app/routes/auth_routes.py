from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.utils.auth_middleware import token_required
from app.utils.helpers import handle_errors

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register/buyer", methods=["POST"])
@handle_errors
def register_buyer_route():
    """
    Endpoint untuk registrasi buyer langsung
    """
    data = request.json
    result, status_code = AuthService.register_buyer(data)
    return jsonify(result), status_code


@auth_bp.route("/register/seller", methods=["POST"])
@handle_errors
def register_seller_route():
    """
    Endpoint untuk registrasi seller langsung
    """
    data = request.json
    result, status_code = AuthService.register_seller(data)
    return jsonify(result), status_code


@auth_bp.route("/login", methods=["POST"])
@handle_errors
def login_route():
    """
    Endpoint untuk login dengan email dan password
    """
    data = request.json
    result, status_code = AuthService.login_user(
        data.get("email"), data.get("password")
    )
    return jsonify(result), status_code


@auth_bp.route("/resend-verification", methods=["POST"])
@handle_errors
def resend_verification_route():
    """
    Endpoint untuk mengirim ulang email verifikasi
    """
    data = request.json
    result, status_code = AuthService.resend_verification(data.get("email"))
    return jsonify(result), status_code


@auth_bp.route("/logout", methods=["POST"])
@token_required
@handle_errors
def logout_route(current_user):
    """
    Endpoint untuk logout user
    """
    # Panggil service logout tanpa parameter
    result = AuthService.logout_user()

    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@auth_bp.route("/refresh-token", methods=["POST"])
@handle_errors
def refresh_token_route():
    """
    Endpoint untuk memperbaharui token akses menggunakan refresh token
    """
    data = request.json
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        return jsonify({"success": False, "message": "Refresh token diperlukan"}), 400

    result, status_code = AuthService.refresh_access_token(refresh_token)
    return jsonify(result), status_code


@auth_bp.route("/delete-account", methods=["DELETE"])
@handle_errors
@token_required
def delete_account_route(current_user):
    """
    Endpoint untuk menghapus akun pengguna
    """
    data = request.json
    password = data.get("password")

    result, status_code = AuthService.delete_account(current_user, password)
    return jsonify(result), status_code
