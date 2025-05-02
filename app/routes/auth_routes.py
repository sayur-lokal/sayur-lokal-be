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
    result, status_code = AuthService.resend_verification_email(data.get("email"))
    return jsonify(result), status_code


@auth_bp.route("/logout", methods=["POST"])
@token_required
@handle_errors
def logout_route(current_user):
    """
    Endpoint untuk logout user
    """
    try:
        # Panggil service logout tanpa parameter
        result = AuthService.logout_user()

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        return (
            jsonify({"success": False, "message": f"Terjadi kesalahan: {str(e)}"}),
            500,
        )
