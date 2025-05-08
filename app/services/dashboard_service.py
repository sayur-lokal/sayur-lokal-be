from app.models.seller import SellerProfile
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from sqlalchemy import func, extract, desc
from datetime import datetime, timedelta
from app.utils.extensions import db
from typing import Dict, Any
import logging

class DashboardService:
    @staticmethod
    def get_seller_dashboard_summary(seller_id: int) -> Dict[str, Any]:
        """
        Mendapatkan ringkasan dashboard untuk seller.

        Args:
            seller_id: ID dari seller

        Returns:
            Dictionary berisi data ringkasan dashboard
        """
        try:
            # Validasi seller_id
            if not isinstance(seller_id, int) or seller_id <= 0:
                return {
                    "success": False,
                    "message": "ID seller harus berupa bilangan bulat positif"
                }

            # Cek apakah seller ada
            seller = SellerProfile.query.get(seller_id)
            if not seller:
                return {
                    "success": False,
                    "message": f"Seller dengan ID {seller_id} tidak ditemukan"
                }

            # Total produk
            total_products = db.session.query(
                func.count(Product.id)
            ).filter(
                Product.seller_id == seller_id
            ).scalar() or 0

            # Produk dengan stok rendah (kurang dari 10)
            low_stock_products = db.session.query(
                func.count(Product.id)
            ).filter(
                Product.seller_id == seller_id,
                Product.stock < 10
            ).scalar() or 0

            # Total pesanan
            total_orders = db.session.query(
                func.count(Order.id.distinct())
            ).join(
                OrderItem, Order.id == OrderItem.order_id
            ).join(
                Product, OrderItem.product_id == Product.id
            ).filter(
                Product.seller_id == seller_id
            ).scalar() or 0

            # Pesanan baru (belum diproses)
            new_orders = db.session.query(
                func.count(Order.id.distinct())
            ).join(
                OrderItem, Order.id == OrderItem.order_id
            ).join(
                Product, OrderItem.product_id == Product.id
            ).filter(
                Product.seller_id == seller_id,
                Order.status == 'paid'
            ).scalar() or 0

            # Total pendapatan
            total_revenue = db.session.query(
                func.sum(OrderItem.quantity * OrderItem.price)
            ).join(
                Order, OrderItem.order_id == Order.id
            ).join(
                Product, OrderItem.product_id == Product.id
            ).filter(
                Product.seller_id == seller_id,
                Order.status.in_(['completed', 'delivered', 'paid'])
            ).scalar() or 0

            return {
                "success": True,
                "data": {
                    "totalProducts": int(total_products),
                    "lowStockProducts": int(low_stock_products),
                    "totalOrders": int(total_orders),
                    "newOrders": int(new_orders),
                    "totalRevenue": float(total_revenue)
                }
            }

        except Exception as e:
            logging.error(f"Error in get_seller_dashboard_summary: {str(e)}")
            return {
                "success": False,
                "message": f"Gagal mendapatkan ringkasan dashboard: {str(e)}"
            }

    @staticmethod
    def get_seller_daily_sales(seller_id: int) -> Dict[str, Any]:
        """
        Mendapatkan data penjualan harian untuk dashboard seller.

        Args:
            seller_id: ID dari seller

        Returns:
            Dictionary berisi data penjualan harian
        """
        try:
            # Validasi seller_id
            if not isinstance(seller_id, int) or seller_id <= 0:
                return {
                    "success": False,
                    "message": "ID seller harus berupa bilangan bulat positif"
                }

            # Cek apakah seller ada
            seller = SellerProfile.query.get(seller_id)
            if not seller:
                return {
                    "success": False,
                    "message": f"Seller dengan ID {seller_id} tidak ditemukan"
                }

            # Mendapatkan data 7 hari terakhir
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=6)

            # Membuat daftar semua hari dalam rentang
            days = []
            day_names = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
            current_date = start_date

            while current_date <= end_date:
                days.append({
                    "date": current_date,
                    "name": day_names[current_date.weekday()]
                })
                current_date += timedelta(days=1)

            # Query untuk mendapatkan total penjualan per hari
            sales_data = db.session.query(
                func.date(Order.created_at).label('date'),
                func.sum(OrderItem.quantity * OrderItem.price).label('sales')
            ).join(
                OrderItem, Order.id == OrderItem.order_id
            ).join(
                Product, OrderItem.product_id == Product.id
            ).filter(
                Product.seller_id == seller_id,
                Order.status.in_(['completed', 'delivered', 'paid']),
                func.date(Order.created_at) >= start_date,
                func.date(Order.created_at) <= end_date
            ).group_by(
                func.date(Order.created_at)
            ).all()

            # Konversi hasil query ke dictionary untuk pencarian yang lebih mudah
            sales_dict = {str(item.date): float(item.sales) for item in sales_data}

            # Format data sesuai dengan format yang diinginkan
            result = []
            for day in days:
                date_str = str(day["date"])
                result.append({
                    "name": day["name"],
                    "sales": sales_dict.get(date_str, 0)
                })

            return {
                "success": True,
                "data": result
            }

        except Exception as e:
            logging.error(f"Error in get_seller_daily_sales: {str(e)}")
            return {
                "success": False,
                "message": f"Gagal mendapatkan data penjualan harian: {str(e)}"
            }

    @staticmethod
    def get_seller_top_products(seller_id: int, limit: int = 5) -> Dict[str, Any]:
        """
        Mendapatkan produk terlaris untuk seller.

        Args:
            seller_id: ID dari seller
            limit: Jumlah produk yang akan ditampilkan

        Returns:
            Dictionary berisi data produk terlaris
        """
        try:
            # Validasi seller_id
            if not isinstance(seller_id, int) or seller_id <= 0:
                return {
                    "success": False,
                    "message": "ID seller harus berupa bilangan bulat positif"
                }

            # Validasi limit
            if not isinstance(limit, int) or limit <= 0:
                limit = 5

            # Cek apakah seller ada
            seller = SellerProfile.query.get(seller_id)
            if not seller:
                return {
                    "success": False,
                    "message": f"Seller dengan ID {seller_id} tidak ditemukan"
                }

            # Query untuk mendapatkan produk terlaris
            top_products = db.session.query(
                Product.name,
                func.sum(OrderItem.quantity).label('units')
            ).join(
                OrderItem, Product.id == OrderItem.product_id
            ).join(
                Order, OrderItem.order_id == Order.id
            ).filter(
                Product.seller_id == seller_id,
                Order.status.in_(['completed', 'delivered', 'paid'])
            ).group_by(
                Product.name
            ).order_by(
                func.sum(OrderItem.quantity).desc()
            ).limit(limit).all()

            # Format data sesuai dengan format yang diinginkan
            result = [{"name": product.name, "units": int(product.units)} for product in top_products]

            # Jika tidak ada data, berikan beberapa data dummy
            if not result:
                dummy_products = [
                    {"name": "Sayur Bayam", "units": 0},
                    {"name": "Beras Organik", "units": 0},
                    {"name": "Cabai Segar", "units": 0},
                    {"name": "Tomat Lokal", "units": 0},
                    {"name": "Keripik Singkong", "units": 0}
                ]
                result = dummy_products[:limit]

            return {
                "success": True,
                "data": result
            }

        except Exception as e:
            logging.error(f"Error in get_seller_top_products: {str(e)}")
            return {
                "success": False,
                "message": f"Gagal mendapatkan data produk terlaris: {str(e)}"
            }

    @staticmethod
    def get_seller_order_status(seller_id: int) -> Dict[str, Any]:
        """
        Mendapatkan jumlah pesanan berdasarkan status untuk dashboard seller.

        Args:
            seller_id: ID dari seller

        Returns:
            Dictionary berisi data status pesanan
        """
        try:
            # Validasi seller_id
            if not isinstance(seller_id, int) or seller_id <= 0:
                return {
                    "success": False,
                    "message": "ID seller harus berupa bilangan bulat positif"
                }

            # Cek apakah seller ada
            seller = SellerProfile.query.get(seller_id)
            if not seller:
                return {
                    "success": False,
                    "message": f"Seller dengan ID {seller_id} tidak ditemukan"
                }

            # Status yang mungkin dalam sistem dan pemetaannya ke UI
            status_mapping = {
                "pending": "Baru",
                "paid": "Baru",
                "processing": "Dikemas",
                "shipped": "Dikirim",
                "delivered": "Selesai",
                "completed": "Selesai",
                "cancelled": "Dibatalkan"
            }

            # Query untuk mendapatkan jumlah pesanan per status
            order_status = db.session.query(
                Order.status,
                func.count(Order.id.distinct()).label('count')
            ).join(
                OrderItem, Order.id == OrderItem.order_id
            ).join(
                Product, OrderItem.product_id == Product.id
            ).filter(
                Product.seller_id == seller_id
            ).group_by(
                Order.status
            ).all()

            # Inisialisasi hasil dengan semua status yang mungkin
            result_dict = {
                "Baru": 0,
                "Dikemas": 0,
                "Dikirim": 0,
                "Selesai": 0,
                "Dibatalkan": 0
            }

            # Isi hasil dengan data dari query
            for status in order_status:
                if status.status in status_mapping:
                    ui_status = status_mapping[status.status]
                    result_dict[ui_status] += status.count

            # Format data sesuai dengan format yang diinginkan
            result = [{"name": status, "value": count} for status, count in result_dict.items()]

            return {
                "success": True,
                "data": result
            }

        except Exception as e:
            logging.error(f"Error in get_seller_order_status: {str(e)}")
            return {
                "success": False,
                "message": f"Gagal mendapatkan data status pesanan: {str(e)}"
            }

    @staticmethod
    def get_seller_inventory_status(seller_id: int) -> Dict[str, Any]:
        """
        Mendapatkan status inventaris untuk dashboard seller.

        Args:
            seller_id: ID dari seller

        Returns:
            Dictionary berisi data status inventaris
        """
        try:
            # Validasi seller_id
            if not isinstance(seller_id, int) or seller_id <= 0:
                return {
                    "success": False,
                    "message": "ID seller harus berupa bilangan bulat positif"
                }

            # Cek apakah seller ada
            seller = SellerProfile.query.get(seller_id)
            if not seller:
                return {
                    "success": False,
                    "message": f"Seller dengan ID {seller_id} tidak ditemukan"
                }

            # Query untuk mendapatkan jumlah produk berdasarkan status stok
            stock_status = db.session.query(
                func.count(Product.id).label('count'),
                func.case(
                    [(Product.stock == 0, "Habis")],
                    [(Product.stock < 10, "Rendah")],
                    else_="Cukup"
                ).label('status')
            ).filter(
                Product.seller_id == seller_id
            ).group_by(
                func.case(
                    [(Product.stock == 0, "Habis")],
                    [(Product.stock < 10, "Rendah")],
                    else_="Cukup"
                )
            ).all()

            # Inisialisasi hasil dengan semua status yang mungkin
            result_dict = {
                "Habis": 0,
                "Rendah": 0,
                "Cukup": 0
            }

            # Isi hasil dengan data dari query
            for item in stock_status:
                result_dict[item.status] = item.count

            # Format data sesuai dengan format yang diinginkan
            result = [{"name": status, "value": count} for status, count in result_dict.items()]

            return {
                "success": True,
                "data": result
            }

        except Exception as e:
            logging.error(f"Error in get_seller_inventory_status: {str(e)}")
            return {
                "success": False,
                "message": f"Gagal mendapatkan data status inventaris: {str(e)}"
            }

    @staticmethod
    def get_seller_monthly_revenue(seller_id: int) -> Dict[str, Any]:
        """
        Mendapatkan pendapatan bulanan untuk dashboard seller.

        Args:
            seller_id: ID dari seller

        Returns:
            Dictionary berisi data pendapatan bulanan
        """
        try:
            # Validasi seller_id
            if not isinstance(seller_id, int) or seller_id <= 0:
                return {
                    "success": False,
                    "message": "ID seller harus berupa bilangan bulat positif"
                }

            # Cek apakah seller ada
            seller = SellerProfile.query.get(seller_id)
            if not seller:
                return {
                    "success": False,
                    "message": f"Seller dengan ID {seller_id} tidak ditemukan"
                }

            # Mendapatkan data 6 bulan terakhir
            today = datetime.now()
            end_month = today.replace(day=1)

            # Membuat daftar 6 bulan terakhir
            months = []
            month_names = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

            for i in range(5, -1, -1):
                month = (end_month.month - i - 1) % 12 + 1
                year = end_month.year - ((end_month.month - i - 1) // 12)
                months.append({
                    "month": month,
                    "year": year,
                    "name": month_names[month - 1]
                })

            # Query untuk mendapatkan total pendapatan per bulan
            revenue_data = db.session.query(
                extract('year', Order.created_at).label('year'),
                extract('month', Order.created_at).label('month'),
                func.sum(OrderItem.quantity * OrderItem.price).label('revenue')
            ).join(
                OrderItem, Order.id == OrderItem.order_id
            ).join(
                Product, OrderItem.product_id == Product.id
            ).filter(
                Product.seller_id == seller_id,
                Order.status.in_(['completed', 'delivered', 'paid']),
                Order.created_at >= datetime(months[0]["year"], months[0]["month"], 1),
                Order.created_at < datetime(today.year, today.month, 1) + timedelta(days=31)
            ).group_by(
                extract('year', Order.created_at),
                extract('month', Order.created_at)
            ).all()

            # Konversi hasil query ke dictionary untuk pencarian yang lebih mudah
            revenue_dict = {(int(item.year), int(item.month)): float(item.revenue) for item in revenue_data}

            # Format data sesuai dengan format yang diinginkan
            result = []
            for month in months:
                key = (month["year"], month["month"])
                result.append({
                    "name": f"{month['name']} {month['year']}",
                    "revenue": revenue_dict.get(key, 0)
                })

            return {
                "success": True,
                "data": result
            }

        except Exception as e:
            logging.error(f"Error in get_seller_monthly_revenue: {str(e)}")
            return {
                "success": False,
                "message": f"Gagal mendapatkan data pendapatan bulanan: {str(e)}"
            }