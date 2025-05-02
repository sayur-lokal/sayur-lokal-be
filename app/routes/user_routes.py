from flask import Blueprint, jsonify
from app.utils.auth_middleware import token_required, role_required
from app.services.user_service import UserService
from app.utils.helpers import handle_errors

user_bp = Blueprint("user", __name__, url_prefix="/users")


@user_bp.route("/me", methods=["GET"])
@token_required
@handle_errors
def get_current_user(current_user):
    """
    Endpoint untuk mendapatkan data user yang sedang login
    """
    result, status_code = UserService.get_current_user_data(current_user)
    return jsonify(result), status_code
