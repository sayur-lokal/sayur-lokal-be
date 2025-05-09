from flask import Blueprint, request, jsonify
from app.utils.auth_middleware import token_required
from app.utils.helpers import handle_errors
from app.services.user_service import UserService

user_bp = Blueprint("user", __name__, url_prefix="/users")

# @user_bp.route("/profile", methods=["GET"])
# @token_required
# @handle_errors
# def get_current_user(current_user):
#     """
#     Endpoint untuk mendapatkan data user yang sedang login
#     """
#     result, status_code = UserService.get_current_user_data(current_user)
#     return jsonify(result), status_code

@user_bp.route("/profile", methods=["GET"])
@token_required
def get_current_user(current_user):
    """
    Endpoint untuk mendapatkan data user yang sedang login
    """
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    logger.debug(f"Current user: {current_user}")
    try:
        result = UserService.get_current_user_data(current_user)
        logger.debug(f"Result from get_current_user_data: {result}")

        if isinstance(result, tuple) and len(result) == 2:
            return jsonify(result[0]), result[1]
        else:
            logger.error(f"Unexpected result format: {result}")
            return jsonify({"success": False, "message": "Format respons tidak valid"}), 500
    except Exception as e:
        logger.exception("Error in get_current_user")
        return jsonify({"success": False, "message": f"Terjadi kesalahan: {str(e)}"}), 500

@user_bp.route("/profile/buyer", methods=["PUT"])
@token_required
@handle_errors
def update_buyer_profile(current_user):
    """
    Endpoint untuk mengupdate profil buyer
    """
    # Cek apakah user adalah buyer
    if not current_user.role or current_user.role.value != "buyer":
        return jsonify({
            "success": False,
            "message": "Akses ditolak. Hanya buyer yang dapat mengakses endpoint ini"
        }), 403

    data = request.json
    result, status_code = UserService.update_buyer_profile(current_user, data)
    return jsonify(result), status_code

@user_bp.route("/profile/seller", methods=["PUT"])
@token_required
@handle_errors
def update_seller_profile(current_user):
    """
    Endpoint untuk mengupdate profil seller
    """
    # Cek apakah user adalah seller
    if not current_user.role or current_user.role.value != "seller":
        return jsonify({
            "success": False,
            "message": "Akses ditolak. Hanya seller yang dapat mengakses endpoint ini"
        }), 403

    data = request.json
    result, status_code = UserService.update_seller_profile(current_user, data)
    return jsonify(result), status_code

@user_bp.route("/profile/picture", methods=["PUT"])
@token_required
@handle_errors
def update_profile_picture(current_user):
    """
    Endpoint untuk mengupdate foto profil (buyer) atau logo (seller)
    """
    data = request.json
    result, status_code = UserService.update_profile_picture(current_user, data)
    return jsonify(result), status_code

@user_bp.route("/password", methods=["PUT"])
@token_required
@handle_errors
def update_password(current_user):
    """
    Endpoint untuk mengupdate password user
    """
    data = request.json
    result, status_code = UserService.update_password(current_user, data)
    return jsonify(result), status_code