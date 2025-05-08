# from flask import Blueprint, request, jsonify
# from app.services.dashboard_service import DashboardService
# from app.utils.auth_middleware import token_required, role_required
# from app.utils.helpers import create_response,handle_errors

# dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

# @dashboard_bp.route("/seller/summary", methods=["GET"])
# @token_required
# @role_required("seller")
# @handle_errors
# def get_seller_dashboard_summary(current_user):
#     """
#     Endpoint untuk mendapatkan ringkasan dashboard seller
#     """
#     # Mendapatkan seller profile dari current_user
#     seller_profile = current_user.seller_profile
#     if not seller_profile:
#         return create_response(False, "Profil seller tidak ditemukan", status_code=404)

#     # Mendapatkan ringkasan dashboard
#     result = DashboardService.get_seller_dashboard_summary(seller_profile.id)

#     if not result["success"]:
#         return create_response(False, result["message"], status_code=500)

#     return create_response(True, "Ringkasan dashboard berhasil diambil", result["data"])

# @dashboard_bp.route("/seller/daily-sales", methods=["GET"])
# @token_required
# @role_required("seller")
# @handle_errors
# def get_seller_daily_sales(current_user):
#     """
#     Endpoint untuk mendapatkan data penjualan harian seller
#     """
#     # Mendapatkan seller profile dari current_user
#     seller_profile = current_user.seller_profile
#     if not seller_profile:
#         return create_response(False, "Profil seller tidak ditemukan", status_code=404)

#     # Mendapatkan data penjualan harian
#     result = DashboardService.get_seller_daily_sales(seller_profile.id)

#     if not result["success"]:
#         return create_response(False, result["message"], status_code=500)

#     return create_response(True, "Data penjualan harian berhasil diambil", result["data"])

# @dashboard_bp.route("/seller/top-products", methods=["GET"])
# @token_required
# @role_required("seller")
# @handle_errors
# def get_seller_top_products(current_user):
#     """
#     Endpoint untuk mendapatkan data produk terlaris seller
#     """
#     # Mendapatkan seller profile dari current_user
#     seller_profile = current_user.seller_profile
#     if not seller_profile:
#         return create_response(False, "Profil seller tidak ditemukan", status_code=404)

#     # Mendapatkan parameter
#     limit = request.args.get("limit", 5, type=int)

#     # Mendapatkan data produk terlaris
#     result = DashboardService.get_seller_top_products(seller_profile.id, limit)

#     if not result["success"]:
#         return create_response(False, result["message"], status_code=500)

#     return create_response(True, "Data produk terlaris berhasil diambil", result["data"])

# @dashboard_bp.route("/seller/order-status", methods=["GET"])
# @token_required
# @role_required("seller")
# @handle_errors
# def get_seller_order_status(current_user):
#     """
#     Endpoint untuk mendapatkan data status pesanan seller
#     """
#     # Mendapatkan seller profile dari current_user
#     seller_profile = current_user.seller_profile
#     if not seller_profile:
#         return create_response(False, "Profil seller tidak ditemukan", status_code=404)

#     # Mendapatkan data status pesanan
#     result = DashboardService.get_seller_order_status(seller_profile.id)

#     if not result["success"]:
#         return create_response(False, result["message"], status_code=500)

#     return create_response(True, "Data status pesanan berhasil diambil", result["data"])

# @dashboard_bp.route("/seller/inventory-status", methods=["GET"])
# @token_required
# @role_required("seller")
# @handle_errors
# def get_seller_inventory_status(current_user):
#     """
#     Endpoint untuk mendapatkan data status inventaris seller
#     """
#     # Mendapatkan seller profile dari current_user
#     seller_profile = current_user.seller_profile
#     if not seller_profile:
#         return create_response(False, "Profil seller tidak ditemukan", status_code=404)

#     # Mendapatkan data status inventaris
#     result = DashboardService.get_seller_inventory_status(seller_profile.id)

#     if not result["success"]:
#         return create_response(False, result["message"], status_code=500)

#     return create_response(True, "Data status inventaris berhasil diambil", result["data"])

# @dashboard_bp.route("/seller/monthly-revenue", methods=["GET"])
# @token_required
# @role_required("seller")
# @handle_errors
# def get_seller_monthly_revenue(current_user):
#     """
#     Endpoint untuk mendapatkan data pendapatan bulanan seller
#     """
#     # Mendapatkan seller profile dari current_user
#     seller_profile = current_user.seller_profile
#     if not seller_profile:
#         return create_response(False, "Profil seller tidak ditemukan", status_code=404)

#     # Mendapatkan data pendapatan bulanan
#     result = DashboardService.get_seller_monthly_revenue(seller_profile.id)

#     if not result["success"]:
#         return create_response(False, result["message"], status_code=500)

#     return create_response(True, "Data pendapatan bulanan berhasil diambil", result["data"])
