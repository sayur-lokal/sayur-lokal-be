from flask import Blueprint, request, jsonify
from app.services.product_service import ProductService
from app.schemas.product_schema import ProductCreate, ProductUpdate
from app.utils.auth_middleware import token_required, role_required
from app.utils.helpers import handle_errors

# Membuat blueprint untuk produk
product_bp = Blueprint("product", __name__, url_prefix="/products")


@product_bp.route("", methods=["POST"])
@token_required
@role_required("seller")
@handle_errors
def create_product(current_user):
    """
    Endpoint untuk membuat produk baru.
    Hanya seller yang dapat membuat produk.
    """
    # Mendapatkan data dari request
    data = request.json

    # Mendapatkan seller_profile_id dari user yang login
    from app.models.seller import SellerProfile

    seller_profile = SellerProfile.query.filter_by(user_id=current_user.id).first()

    if not seller_profile:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Profil seller tidak ditemukan. Pastikan Anda telah melengkapi profil seller.",
                }
            ),
            400,
        )

    # Menambahkan seller_id ke data (menggunakan ID dari seller_profile)
    data["seller_id"] = seller_profile.id

    # Validasi data menggunakan schema
    product_data = ProductCreate(**data)

    # Membuat produk baru
    product = ProductService.create_product(product_data)

    return (
        jsonify(
            {
                "success": True,
                "message": "Produk berhasil dibuat",
                "data": product.model_dump(),
            }
        ),
        201,
    )


@product_bp.route("", methods=["GET"])
@handle_errors
def get_all_products():
    """
    Endpoint untuk mendapatkan daftar semua produk.
    Dapat difilter berdasarkan kategori, seller, dan rentang harga.
    """
    # Mendapatkan parameter query
    category_id = request.args.get("category_id", type=int)
    seller_id = request.args.get("seller_id", type=int)
    price_min = request.args.get("price_min", type=float)
    price_max = request.args.get("price_max", type=float)
    name = request.args.get("name", type=str)

    # Mendapatkan daftar produk
    products = ProductService.get_all_products(
        category_id=category_id,
        seller_id=seller_id,
        price_min=price_min,
        price_max=price_max,
        name=name,
    )

    return (
        jsonify(
            {
                "success": True,
                "message": "Daftar produk berhasil diambil",
                "total": len(products),
                "data": [product.model_dump() for product in products],
            }
        ),
        200,
    )


@product_bp.route("/<int:product_id>", methods=["GET"])
@handle_errors
def get_product(product_id):
    """
    Endpoint untuk mendapatkan detail produk berdasarkan ID.
    """
    # Mendapatkan produk berdasarkan ID
    product = ProductService.get_product_by_id(product_id)

    if not product:
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Produk dengan ID {product_id} tidak ditemukan",
                }
            ),
            404,
        )

    return (
        jsonify(
            {
                "success": True,
                "message": "Detail produk berhasil diambil",
                "data": product.model_dump(),
            }
        ),
        200,
    )


@product_bp.route("/category/<int:category_id>", methods=["GET"])
@handle_errors
def get_products_by_category(category_id):
    """
    Endpoint untuk mendapatkan semua produk berdasarkan kategori
    Dapat difilter berdasarkan rentang harga dan nama produk
    """
    # Mendapatkan parameter query
    price_min = request.args.get("price_min", type=float)
    price_max = request.args.get("price_max", type=float)
    name = request.args.get("name", type=str)

    products = ProductService.get_all_products(
        category_id=category_id, price_min=price_min, price_max=price_max, name=name
    )

    if not products:
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Tidak ada produk dalam kategori dengan ID {category_id}",
                    "total": 0,
                    "data": [],
                }
            ),
            200,
        )

    return (
        jsonify(
            {
                "success": True,
                "message": f"Daftar produk untuk kategori ID {category_id} berhasil diambil",
                "total": len(products),
                "data": [product.model_dump() for product in products],
            }
        ),
        200,
    )


@product_bp.route("/seller/<int:seller_id>", methods=["GET"])
@handle_errors
def get_products_by_seller(seller_id):
    """
    Endpoint untuk mendapatkan semua produk berdasarkan seller
    Dapat difilter berdasarkan rentang harga
    """
    # Mendapatkan parameter query
    price_min = request.args.get("price_min", type=float)
    price_max = request.args.get("price_max", type=float)
    name = request.args.get("name", type=str)

    products = ProductService.get_all_products(
        seller_id=seller_id, price_min=price_min, price_max=price_max, name=name
    )

    if not products:
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Tidak ada produk dari seller dengan ID {seller_id}",
                    "total": 0,
                    "data": [],
                }
            ),
            200,
        )

    return (
        jsonify(
            {
                "success": True,
                "message": f"Daftar produk untuk seller ID {seller_id} berhasil diambil",
                "total": len(products),
                "data": [product.model_dump() for product in products],
            }
        ),
        200,
    )


@product_bp.route("/price-range", methods=["GET"])
@handle_errors
def get_products_by_price_range():
    """
    Endpoint untuk mendapatkan produk berdasarkan rentang harga
    """
    # Mendapatkan parameter query
    price_min = request.args.get("price_min", type=float)
    price_max = request.args.get("price_max", type=float)
    name = request.args.get("name", type=str)

    if price_min is None and price_max is None:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Minimal satu parameter harga (min atau max) harus diisi",
                }
            ),
            400,
        )

    products = ProductService.get_all_products(
        price_min=price_min, price_max=price_max, name=name
    )

    if not products:
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Tidak ada produk dalam rentang harga yang ditentukan",
                    "total": 0,
                    "data": [],
                }
            ),
            200,
        )

    return (
        jsonify(
            {
                "success": True,
                "message": "Daftar produk berdasarkan rentang harga berhasil diambil",
                "total": len(products),
                "data": [product.model_dump() for product in products],
            }
        ),
        200,
    )


@product_bp.route("/search", methods=["GET"])
@handle_errors
def search_products():
    """
    Endpoint untuk mencari produk berdasarkan nama
    """
    name = request.args.get("q", type=str)
    price_min = request.args.get("price_min", type=float)
    price_max = request.args.get("price_max", type=float)
    category_id = request.args.get("category_id", type=int)

    if not name:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Parameter pencarian (q) harus diisi",
                }
            ),
            400,
        )

    products = ProductService.get_all_products(
        name=name, price_min=price_min, price_max=price_max, category_id=category_id
    )

    if not products:
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Tidak ada produk yang cocok dengan pencarian '{name}'",
                    "total": 0,
                    "data": [],
                }
            ),
            200,
        )

    return (
        jsonify(
            {
                "success": True,
                "message": f"Hasil pencarian untuk '{name}'",
                "total": len(products),
                "data": [product.model_dump() for product in products],
            }
        ),
        200,
    )


@product_bp.route("/<int:product_id>", methods=["PUT"])
@token_required
@role_required("seller")
@handle_errors
def update_product(current_user, product_id):
    """
    Endpoint untuk memperbarui produk berdasarkan ID.
    Hanya seller yang memiliki produk yang dapat memperbarui.
    """
    # Memeriksa apakah produk ada dan milik seller yang sedang login
    product = ProductService.get_product_by_id(product_id)

    if not product:
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Produk dengan ID {product_id} tidak ditemukan",
                }
            ),
            404,
        )

    if product.seller_id != current_user.id:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Anda tidak memiliki izin untuk memperbarui produk ini",
                }
            ),
            403,
        )

    # Mendapatkan data dari request
    data = request.json

    # Validasi data menggunakan schema
    product_data = ProductUpdate(**data)

    # Memperbarui produk
    updated_product = ProductService.update_product(product_id, product_data)

    return (
        jsonify(
            {
                "success": True,
                "message": "Produk berhasil diperbarui",
                "data": updated_product.model_dump(),
            }
        ),
        200,
    )


@product_bp.route("/<int:product_id>", methods=["DELETE"])
@token_required
@role_required("seller")
@handle_errors
def delete_product(current_user, product_id):
    """
    Endpoint untuk menghapus produk berdasarkan ID (soft delete).
    Hanya seller yang memiliki produk yang dapat menghapus.
    """
    # Memeriksa apakah produk ada dan milik seller yang sedang login
    product = ProductService.get_product_by_id(product_id)

    if not product:
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Produk dengan ID {product_id} tidak ditemukan",
                }
            ),
            404,
        )

    if product.seller_id != current_user.id:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Anda tidak memiliki izin untuk menghapus produk ini",
                }
            ),
            403,
        )

    # Menghapus produk (soft delete)
    success = ProductService.delete_product(product_id)

    if not success:
        return jsonify({"success": False, "message": "Gagal menghapus produk"}), 500

    return jsonify({"success": True, "message": "Produk berhasil dihapus"}), 200


@product_bp.route("/upload-image", methods=["POST"])
@token_required
@role_required("seller")
@handle_errors
def upload_product_image(current_user):
    """
    Endpoint untuk mengunggah gambar produk.
    """
    if "image" not in request.files:
        return (
            jsonify({"success": False, "message": "Tidak ada file yang diunggah"}),
            400,
        )

    file = request.files["image"]

    if file.filename == "":
        return (
            jsonify({"success": False, "message": "Tidak ada file yang dipilih"}),
            400,
        )

    # Memeriksa ekstensi file
    allowed_extensions = {"png", "jpg", "jpeg", "gif"}
    if (
        "." not in file.filename
        or file.filename.rsplit(".", 1)[1].lower() not in allowed_extensions
    ):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Format file tidak didukung. Gunakan PNG, JPG, JPEG, atau GIF",
                }
            ),
            400,
        )

    # Mengunggah gambar
    image_url = ProductService.upload_product_image(file.read(), file.filename)

    return (
        jsonify(
            {
                "success": True,
                "message": "Gambar berhasil diunggah",
                "data": {"image_url": image_url},
            }
        ),
        200,
    )
