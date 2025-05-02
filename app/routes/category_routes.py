from flask import Blueprint, request, jsonify
from app.services.category_service import CategoryService
from app.schemas.category_schema import CategoryCreate, CategoryUpdate
from app.utils.auth_middleware import token_required, role_required
from app.utils.helpers import handle_errors
from pydantic import ValidationError

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
def create_category(current_user):
    """
    Endpoint untuk membuat kategori baru (hanya admin)
    """
    try:
        data = request.json

        # Validasi data dengan Pydantic
        try:
            category_data = CategoryCreate(**data)
        except ValidationError as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Data tidak valid",
                        "errors": e.errors(),
                    }
                ),
                400,
            )

        result, status_code = CategoryService.create_category(category_data)
        return jsonify(result), status_code
    except Exception as e:
        return (
            jsonify({"success": False, "message": f"Terjadi kesalahan: {str(e)}"}),
            500,
        )


@category_bp.route("/<int:category_id>", methods=["PUT"])
@token_required
@role_required("admin")
def update_category(current_user, category_id):
    """
    Endpoint untuk memperbarui kategori (hanya admin)
    """
    try:
        data = request.json

        # Validasi data dengan Pydantic
        try:
            category_data = CategoryUpdate(**data)
        except ValidationError as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Data tidak valid",
                        "errors": e.errors(),
                    }
                ),
                400,
            )

        result, status_code = CategoryService.update_category(
            category_id, category_data
        )
        return jsonify(result), status_code
    except Exception as e:
        return (
            jsonify({"success": False, "message": f"Terjadi kesalahan: {str(e)}"}),
            500,
        )


@category_bp.route("/<int:category_id>", methods=["DELETE"])
@token_required
@role_required("admin")
def delete_category(current_user, category_id):
    """
    Endpoint untuk menghapus kategori (hanya admin)
    """
    try:
        result, status_code = CategoryService.delete_category(category_id)
        return jsonify(result), status_code
    except Exception as e:
        return (
            jsonify({"success": False, "message": f"Terjadi kesalahan: {str(e)}"}),
            500,
        )


@category_bp.route("/seed", methods=["POST"])
@token_required
@role_required("admin")
def seed_categories(current_user):
    """
    Endpoint untuk menambahkan data awal kategori (hanya admin)
    """
    try:
        CategoryService.seed_categories()
        return (
            jsonify(
                {"success": True, "message": "Kategori default berhasil ditambahkan"}
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify({"success": False, "message": f"Terjadi kesalahan: {str(e)}"}),
            500,
        )
