from flask import Blueprint, request, jsonify
from app.services.order_service import OrderService
from app.utils.auth_middleware import token_required, role_required
from app.utils.helpers import handle_errors
from pydantic import ValidationError

order_bp = Blueprint("order", __name__, url_prefix="/orders")


@order_bp.route("", methods=["POST"])
@token_required
@role_required("buyer")
@handle_errors
def create_order(current_user):
    """
    Endpoint untuk membuat pesanan baru (hanya buyer)
    """
    data = request.json

    # Teruskan data dan current_user ke service
    result, status_code = OrderService.create_order(data, current_user)
    return jsonify(result), status_code

@order_bp.route("/<int:order_id>", methods=["GET"])
@token_required
@role_required("buyer")
@handle_errors
def get_order(current_user, order_id):
    """
    Endpoint untuk mendapatkan detail pesanan (buyer atau seller yang terkait)
    """
    # Dapatkan pesanan terlebih dahulu
    result, status_code = OrderService.get_order_by_id(order_id)

    if status_code == 200 and result["success"]:
        order_data = result["data"]

        # Cek apakah pengguna adalah buyer dari pesanan ini
        is_buyer = current_user.id == order_data["buyer_id"]

        # Cek apakah pengguna adalah seller dari pesanan ini
        is_seller = False
        if current_user.role.value == "seller" and hasattr(
            current_user, "seller_profile"
        ):
            is_seller = current_user.seller_profile.id == order_data["seller_id"]

        # Jika bukan buyer atau seller yang terkait, tolak akses
        if not is_buyer and not is_seller:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Anda tidak memiliki akses ke pesanan ini",
                    }
                ),
                403,
            )

    return jsonify(result), status_code


@order_bp.route("/buyer", methods=["GET"])
@token_required
@role_required("buyer")
@handle_errors
def get_buyer_orders(current_user):
    """
    Endpoint untuk mendapatkan daftar pesanan buyer (hanya buyer)
    """
    result, status_code = OrderService.get_buyer_orders(current_user.id)
    return jsonify(result), status_code


@order_bp.route("/seller", methods=["GET"])
@token_required
@role_required("seller")
@handle_errors
def get_seller_orders(current_user):
    """
    Endpoint untuk mendapatkan daftar pesanan seller (hanya seller)
    """
    # Dapatkan seller_id dari profil seller
    seller_id = (
        current_user.seller_profile.id
        if hasattr(current_user, "seller_profile")
        else None
    )

    if not seller_id:
        return (
            jsonify({"success": False, "message": "Profil seller tidak ditemukan"}),
            404,
        )

    result, status_code = OrderService.get_seller_orders(seller_id)
    return jsonify(result), status_code


@order_bp.route("/<int:order_id>/status", methods=["PUT"])
@token_required
@handle_errors
def update_order_status(current_user, order_id):
    """
    Endpoint untuk memperbarui status pesanan (buyer atau seller yang terkait)
    """
    try:
        data = request.json

        # Dapatkan pesanan untuk cek akses
        order_result, _ = OrderService.get_order_by_id(order_id)

        if not order_result["success"]:
            return jsonify(order_result), 404

        order = order_result["data"]

        # Cek apakah pengguna berhak memperbarui pesanan ini
        if current_user.role.value == "seller":
            # Seller hanya bisa memperbarui pesanan miliknya
            seller_id = (
                current_user.seller_profile.id
                if hasattr(current_user, "seller_profile")
                else None
            )
            if not seller_id or order["seller_id"] != seller_id:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Anda tidak memiliki akses ke pesanan ini",
                        }
                    ),
                    403,
                )
        elif current_user.role.value == "buyer":
            # Buyer hanya bisa memperbarui pesanan miliknya
            if current_user.id != order["buyer_id"]:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Anda tidak memiliki akses ke pesanan ini",
                        }
                    ),
                    403,
                )
        else:
            # Jika bukan buyer atau seller, tolak akses
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Anda tidak memiliki akses ke pesanan ini",
                    }
                ),
                403,
            )

        result, status_code = OrderService.update_order_status(order_id, data)
        return jsonify(result), status_code

    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Terjadi kesalahan: {str(e)}",
                }
            ),
            500,
        )


@order_bp.route("/<int:order_id>/cancel", methods=["POST"])
@token_required
@role_required("buyer")
@handle_errors
def cancel_order(current_user, order_id):
    """
    Endpoint untuk membatalkan pesanan (hanya buyer)
    """
    # Dapatkan pesanan untuk cek akses
    order_result, _ = OrderService.get_order_by_id(order_id)

    if not order_result["success"]:
        return jsonify(order_result), 404

    order = order_result["data"]

    # Cek apakah pengguna adalah buyer dari pesanan ini
    if current_user.id != order["buyer_id"]:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Anda hanya dapat membatalkan pesanan milik Anda sendiri",
                }
            ),
            403,
        )

    result, status_code = OrderService.cancel_order(order_id)
    return jsonify(result), status_code

# @order_bp.route("/<int:order_id>/payment-proof", methods=["POST"])
# @token_required
# @role_required("buyer")
# @handle_errors
# def upload_payment_proof(current_user, order_id):
    """
    Endpoint untuk mengunggah bukti pembayaran (hanya buyer)
    """
    # Dapatkan pesanan untuk cek akses
    order_result, _ = OrderService.get_order_by_id(order_id)

    if not order_result["success"]:
        return jsonify(order_result), 404

    order = order_result["data"]

    # Cek apakah pengguna adalah buyer dari pesanan ini
    if current_user.id != order["buyer_id"]:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Anda hanya dapat mengunggah bukti pembayaran untuk pesanan milik Anda sendiri",
                }
            ),
            403,
        )

    # Dapatkan URL bukti pembayaran dari request
    data = request.json
    payment_proof_url = data.get("payment_proof_url")

    if not payment_proof_url:
        return (
            jsonify({"success": False, "message": "URL bukti pembayaran wajib diisi"}),
            400,
        )

    result, status_code = OrderService.upload_payment_proof(order_id, payment_proof_url)
    return jsonify(result), status_code