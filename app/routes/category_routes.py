from flask import Blueprint, request, jsonify
from app.services.category_service import CategoryService
from app.utils.auth_middleware import token_required, role_required
from app.utils.helpers import handle_errors

category_bp = Blueprint("category", __name__, url_prefix="/categories")


@category_bp.route("", methods=["GET"])
@handle_errors
def get_all_categories():
    """
    Endpoint untuk mendapatkan semua kategori
    """
    result, status_code = CategoryService.get_all_categories()
    return jsonify(result), status_code


@category_bp.route("/<int:category_id>", methods=["GET"])
@handle_errors
def get_category_by_id(category_id):
    """
    Endpoint untuk mendapatkan detail kategori berdasarkan ID
    """
    result, status_code = CategoryService.get_category_by_id(category_id)
    return jsonify(result), status_code


@category_bp.route("/<int:category_id>/products", methods=["GET"])
@handle_errors
def get_category_with_products(category_id):
    """
    Endpoint untuk mendapatkan detail kategori beserta produk-produknya
    """
    result, status_code = CategoryService.get_category_with_products(category_id)
    return jsonify(result), status_code


@category_bp.route("", methods=["POST"])
@token_required
@role_required("admin")
@handle_errors
def create_category(current_user):
    """
    Endpoint untuk membuat kategori baru (hanya admin)
    """
    data = request.json
    result, status_code = CategoryService.create_category(data)
    return jsonify(result), status_code


@category_bp.route("/<int:category_id>", methods=["PUT", "DELETE"])
@token_required
@role_required("admin")
@handle_errors
def manage_category(current_user, category_id):
    """
    Endpoint untuk memperbarui atau menghapus kategori (hanya admin)
    """
    if request.method == "PUT":
        data = request.json
        result, status_code = CategoryService.update_category(category_id, data)
    else:  # DELETE
        result, status_code = CategoryService.delete_category(category_id)

    return jsonify(result), status_code