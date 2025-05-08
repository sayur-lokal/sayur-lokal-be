from flask import Blueprint, request, jsonify
from app.services.product_service import ProductService
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductDetailResponse
from app.utils.auth_middleware import token_required, role_required
from app.utils.helpers import handle_errors
from app.models.seller import SellerProfile
from pydantic import ValidationError

# Membuat blueprint untuk produk
product_bp = Blueprint("product", __name__, url_prefix="/products")


def create_response(success, message, data=None, status_code=200, total=None, pagination=None):
    """Fungsi helper untuk membuat response yang konsisten"""
    response = {"success": success, "message": message}

    if data is not None:
        if isinstance(data, list):
            response["total"] = len(data)
            response["data"] = [item.model_dump() for item in data]
        else:
            response["data"] = data.model_dump()
    elif total is not None:
        response["total"] = total
        response["data"] = []

    # Tambahkan informasi pagination jika ada
    if pagination is not None:
        response["pagination"] = pagination

    return jsonify(response), status_code


def get_seller_profile(current_user):
    """Fungsi helper untuk mendapatkan profil seller dari user yang login"""
    seller_profile = SellerProfile.query.filter_by(user_id=current_user.id).first()

    if not seller_profile:
        return None, (
            jsonify(
                {
                    "success": False,
                    "message": "Profil seller tidak ditemukan. Pastikan Anda telah melengkapi profil seller.",
                }
            ),
            400,
        )

    return seller_profile, None


@product_bp.route("", methods=["POST"])
@token_required
@role_required("seller")
@handle_errors
def create_product(current_user):
    """
    Endpoint untuk membuat produk baru.
    Hanya seller yang dapat membuat produk.
    """
    try:
        # Mendapatkan seller profile
        seller_profile, error_response = get_seller_profile(current_user)
        if error_response:
            return error_response

        # Mendapatkan data dari request
        data = request.json
        data["seller_id"] = seller_profile.id

        # Validasi data dengan Pydantic
        product_data = ProductCreate.model_validate(data)
        product = ProductService.create_product(product_data)

        return create_response(True, "Produk berhasil dibuat", product, 201)
    except ValidationError as e:
        return jsonify({
            "success": False,
            "message": "Validasi data gagal",
            "errors": e.errors()
        }), 400


@product_bp.route("", methods=["GET"])
@handle_errors
def get_all_products_item():
    """
    Endpoint untuk mendapatkan daftar semua produk.
    Dapat difilter berdasarkan kategori, seller, dan rentang harga.
    """
    # Mendapatkan parameter query
    filters = {
        "category_id": request.args.get("category_id", type=int),
        "seller_id": request.args.get("seller_id", type=int),
        "price_min": request.args.get("price_min", type=float),
        "price_max": request.args.get("price_max", type=float),
        "name": request.args.get("name", type=str),
        "page": request.args.get("page", 1, type=int),
        "per_page": request.args.get("per_page", 10, type=int),
    }

    # Mendapatkan daftar produk
    result = ProductService.get_all_products(**filters)

    return create_response(
        True,
        "Daftar produk berhasil diambil",
        result["products"],
        pagination=result["pagination"]
    )

@product_bp.route("/<int:product_id>", methods=["GET"])
@handle_errors
def get_product(product_id):
    """
    Endpoint untuk mendapatkan detail produk berdasarkan ID.
    """
    product = ProductService.get_product_with_details(product_id)

    if not product:
        return create_response(
            False, f"Produk dengan ID {product_id} tidak ditemukan", status_code=404
        )

    return jsonify({
        "success": True,
        "message": "Detail produk berhasil diambil",
        "data": product
    }), 200


@product_bp.route("/category/<int:category_id>", methods=["GET"])
@handle_errors
def get_products_by_category(category_id):
    """
    Endpoint untuk mendapatkan semua produk berdasarkan kategori
    Dapat difilter berdasarkan rentang harga dan nama produk
    """
    filters = {
        "category_id": category_id,
        "price_min": request.args.get("price_min", type=float),
        "price_max": request.args.get("price_max", type=float),
        "name": request.args.get("name", type=str),
        "page": request.args.get("page", 1, type=int),
        "per_page": request.args.get("per_page", 10, type=int),
    }

    result = ProductService.get_all_products(**filters)

    if not result["products"]:
        return create_response(
            True,
            f"Tidak ada produk dalam kategori dengan ID {category_id}",
            data=[],
            total=0,
            pagination=result["pagination"]
        )

    return create_response(
        True,
        f"Daftar produk untuk kategori ID {category_id} berhasil diambil",
        result["products"],
        pagination=result["pagination"]
    )


@product_bp.route("/seller/<int:seller_id>", methods=["GET"])
@handle_errors
def get_products_by_seller(seller_id):
    """
    Endpoint untuk mendapatkan semua produk berdasarkan seller
    Dapat difilter berdasarkan rentang harga
    """
    filters = {
        "seller_id": seller_id,
        "price_min": request.args.get("price_min", type=float),
        "price_max": request.args.get("price_max", type=float),
        "name": request.args.get("name", type=str),
        "page": request.args.get("page", 1, type=int),
        "per_page": request.args.get("per_page", 10, type=int),
    }

    result = ProductService.get_all_products(**filters)

    if not result["products"]:
        return create_response(
            True,
            f"Tidak ada produk dari seller dengan ID {seller_id}",
            data=[],
            total=0,
            pagination=result["pagination"]
        )

    return create_response(
        True,
        f"Daftar produk untuk seller ID {seller_id} berhasil diambil",
        result["products"],
        pagination=result["pagination"]
    )


@product_bp.route("/price-range", methods=["GET"])
@handle_errors
def get_products_by_price_range():
    """
    Endpoint untuk mendapatkan produk berdasarkan rentang harga
    """
    price_min = request.args.get("price_min", type=float)
    price_max = request.args.get("price_max", type=float)
    name = request.args.get("name", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    if price_min is None and price_max is None:
        return create_response(
            False,
            "Minimal satu parameter harga (min atau max) harus diisi",
            status_code=400,
        )

    result = ProductService.get_all_products(
        price_min=price_min,
        price_max=price_max,
        name=name,
        page=page,
        per_page=per_page
    )

    if not result["products"]:
        return create_response(
            True,
            "Tidak ada produk dalam rentang harga yang ditentukan",
            data=[],
            total=0,
            pagination=result["pagination"]
        )

    return create_response(
        True,
        "Daftar produk berdasarkan rentang harga berhasil diambil",
        result["products"],
        pagination=result["pagination"]
    )


@product_bp.route("/search", methods=["GET"])
@handle_errors
def search_products():
    """
    Endpoint untuk mencari produk berdasarkan nama
    """
    name = request.args.get("q", type=str)

    if not name:
        return create_response(
            False, "Parameter pencarian (q) harus diisi", status_code=400
        )

    filters = {
        "name": name,
        "price_min": request.args.get("price_min", type=float),
        "price_max": request.args.get("price_max", type=float),
        "category_id": request.args.get("category_id", type=int),
        "page": request.args.get("page", 1, type=int),
        "per_page": request.args.get("per_page", 10, type=int),
    }

    result = ProductService.get_all_products(**filters)

    if not result["products"]:
        return create_response(
            True,
            f"Tidak ada produk yang cocok dengan pencarian '{name}'",
            data=[],
            total=0,
            pagination=result["pagination"]
        )

    return create_response(
        True,
        f"Hasil pencarian untuk '{name}'",
        result["products"],
        pagination=result["pagination"]
    )


@product_bp.route("/<int:product_id>", methods=["PUT", "DELETE"])
@token_required
@role_required("seller")
@handle_errors
def manage_product(current_user, product_id):
    """
    Endpoint untuk memperbarui atau menghapus produk berdasarkan ID.
    Hanya seller yang memiliki produk yang dapat memperbarui atau menghapus.
    """
    try:
        # Memeriksa apakah produk ada
        product = ProductService.get_product_by_id(product_id)
        if not product:
            return create_response(
                False, f"Produk dengan ID {product_id} tidak ditemukan", status_code=404
            )

        # Mendapatkan seller profile
        seller_profile, error_response = get_seller_profile(current_user)
        if error_response:
            return error_response

        # Memeriksa kepemilikan produk
        if product.seller_id != seller_profile.id:
            action = "memperbarui" if request.method == "PUT" else "menghapus"
            return create_response(
                False,
                f"Anda tidak memiliki izin untuk {action} produk ini",
                status_code=403,
            )

        if request.method == "PUT":
            # Memperbarui produk dengan validasi Pydantic
            product_data = ProductUpdate.model_validate(request.json)
            updated_product = ProductService.update_product(product_id, product_data)
            return create_response(True, "Produk berhasil diperbarui", updated_product)
        else:  # DELETE
            # Menghapus produk
            success = ProductService.delete_product(product_id)
            if not success:
                return create_response(False, "Gagal menghapus produk", status_code=500)
            return create_response(True, "Produk berhasil dihapus")
    except ValidationError as e:
        return jsonify({
            "success": False,
            "message": "Validasi data gagal",
            "errors": e.errors()
        }), 400