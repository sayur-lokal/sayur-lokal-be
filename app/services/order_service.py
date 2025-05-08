from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.utils.extensions import db
from app.schemas.order_schema import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderBriefResponse,
    OrderStatusEnum,
)
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
from pydantic import ValidationError
from app.utils.helpers import _handle_validation_error


class OrderService:

    @staticmethod
    def create_order(
        data: Dict[str, Any], current_user
    ) -> Tuple[Dict[str, Any], int]:
        """
        Membuat pesanan baru berdasarkan data yang diberikan dan user yang sedang login.
        """
        try:
            # Validasi data dengan Pydantic
            try:
                order_data = OrderCreate(**data)
            except ValidationError as e:
                return _handle_validation_error(e)

            # Validasi role user
            if current_user.role.value != "buyer":
                return {
                    "success": False,
                    "message": "Hanya buyer yang dapat membuat pesanan",
                }, 403

            # Validasi stok produk terlebih dahulu dan hitung total price
            total_price = Decimal("0.0")
            validated_items = []

            for item in order_data.items:
                product = Product.query.get(item.product_id)
                if not product:
                    return {
                        "success": False,
                        "message": f"Produk dengan ID {item.product_id} tidak ditemukan",
                    }, 404

                if product.stock < item.quantity:
                    return {
                        "success": False,
                        "message": f"Stok produk {product.name} tidak mencukupi. Tersedia: {product.stock}, diminta: {item.quantity}",
                    }, 400

                # Gunakan harga dari database, bukan dari input
                item_price = Decimal(str(product.price))
                item_total = item_price * item.quantity
                total_price += item_total

                # Simpan item dengan harga yang benar dari database
                validated_items.append(
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price": item_price,
                    }
                )

            # Mulai transaksi
            db.session.begin_nested()

            # Buat pesanan baru dengan total price yang dihitung dan buyer_id dari current_user
            new_order = Order(
                buyer_id=current_user.id,  # Gunakan ID dari current_user
                seller_id=order_data.seller_id,
                total_price=total_price,
                status=order_data.status,
                payment_method=order_data.payment_method,
                is_paid=order_data.is_paid,
            )

            db.session.add(new_order)
            db.session.flush()  # Flush untuk mendapatkan ID

            # Buat item pesanan dan kurangi stok produk
            for item_data in validated_items:
                product = Product.query.get(item_data["product_id"])

                # Buat item pesanan dengan harga dari database
                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=item_data["product_id"],
                    quantity=item_data["quantity"],
                    price=item_data["price"],
                )

                # Kurangi stok produk
                product.stock -= item_data["quantity"]

                db.session.add(order_item)

            db.session.commit()

            return {
                "success": True,
                "message": "Pesanan berhasil dibuat",
                "order_id": new_order.id,
                "total_price": float(total_price),
            }, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Gagal membuat pesanan: {str(e)}",
            }, 500
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def get_order_by_id(order_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Mendapatkan pesanan berdasarkan ID.
        """
        try:
            # Validasi parameter
            if not isinstance(order_id, int) or order_id <= 0:
                return {
                    "success": False,
                    "message": "ID pesanan harus berupa bilangan bulat positif",
                }, 400

            order = Order.query.get(order_id)
            if not order:
                return {
                    "success": False,
                    "message": f"Pesanan dengan ID {order_id} tidak ditemukan",
                }, 404

            # Konversi ke response schema
            try:
                order_data = OrderResponse.model_validate(order)
                return {"success": True, "data": order_data.model_dump()}, 200
            except ValidationError as e:
                return _handle_validation_error(e)

        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def get_buyer_orders(buyer_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Mendapatkan daftar pesanan untuk buyer tertentu.
        """
        try:
            # Validasi parameter
            if not isinstance(buyer_id, int) or buyer_id <= 0:
                return {
                    "success": False,
                    "message": "ID buyer harus berupa bilangan bulat positif",
                }, 400

            orders = Order.query.filter_by(buyer_id=buyer_id).all()

            # Konversi ke response schema
            try:
                orders_data = []
                for order in orders:
                    order_data = OrderResponse.model_validate(order)
                    orders_data.append(order_data.model_dump())

                return {
                    "success": True,
                    "data": orders_data,
                    "total_orders": len(orders_data),
                }, 200
            except ValidationError as e:
                return _handle_validation_error(e)

        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def get_seller_orders(seller_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Mendapatkan daftar pesanan untuk seller tertentu.
        """
        try:
            # Validasi parameter
            if not isinstance(seller_id, int) or seller_id <= 0:
                return {
                    "success": False,
                    "message": "ID seller harus berupa bilangan bulat positif",
                }, 400

            orders = Order.query.filter_by(seller_id=seller_id).all()

            # Konversi ke response schema
            try:
                orders_data = []
                for order in orders:
                    order_data = OrderResponse.model_validate(order)
                    orders_data.append(order_data.model_dump())

                return {
                    "success": True,
                    "data": orders_data,
                    "total_orders": len(orders_data),
                }, 200
            except ValidationError as e:
                return _handle_validation_error(e)

        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def update_order_status(
        order_id: int, data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], int]:
        """
        Memperbarui status pesanan.
        """
        try:
            # Validasi parameter
            if not isinstance(order_id, int) or order_id <= 0:
                return {
                    "success": False,
                    "message": "ID pesanan harus berupa bilangan bulat positif",
                }, 400

            # Validasi data dengan Pydantic
            try:
                order_data = OrderUpdate(**data)
            except ValidationError as e:
                return _handle_validation_error(e)

            order = Order.query.get(order_id)
            if not order:
                return {
                    "success": False,
                    "message": f"Pesanan dengan ID {order_id} tidak ditemukan",
                }, 404

            # Validasi perubahan status
            if order_data.status is not None:
                # Cek apakah perubahan status valid
                current_status = OrderStatusEnum(order.status)
                new_status = order_data.status

                # Validasi alur status pesanan
                if current_status == OrderStatusEnum.CANCELLED and new_status != OrderStatusEnum.CANCELLED:
                    return {
                        "success": False,
                        "message": "Pesanan yang sudah dibatalkan tidak dapat diubah statusnya",
                    }, 400

                if current_status == OrderStatusEnum.DELIVERED and new_status != OrderStatusEnum.DELIVERED:
                    return {
                        "success": False,
                        "message": "Pesanan yang sudah diterima tidak dapat diubah statusnya",
                    }, 400

                # Validasi alur status: PENDING -> PAID -> SHIPPED -> DELIVERED
                if (current_status == OrderStatusEnum.PENDING and
                    new_status not in [OrderStatusEnum.PAID, OrderStatusEnum.CANCELLED]):
                    return {
                        "success": False,
                        "message": "Pesanan dengan status PENDING hanya dapat diubah menjadi PAID atau CANCELLED",
                    }, 400

                if (current_status == OrderStatusEnum.PAID and
                    new_status not in [OrderStatusEnum.SHIPPED, OrderStatusEnum.CANCELLED]):
                    return {
                        "success": False,
                        "message": "Pesanan dengan status PAID hanya dapat diubah menjadi SHIPPED atau CANCELLED",
                    }, 400

                if (current_status == OrderStatusEnum.SHIPPED and
                    new_status != OrderStatusEnum.DELIVERED):
                    return {
                        "success": False,
                        "message": "Pesanan dengan status SHIPPED hanya dapat diubah menjadi DELIVERED",
                    }, 400

                order.status = new_status.value

            # Update is_paid jika disediakan
            if order_data.is_paid is not None:
                # Jika mengubah status menjadi sudah dibayar, pastikan status pesanan minimal PAID
                if order_data.is_paid and order.status == OrderStatusEnum.PENDING.value:
                    order.status = OrderStatusEnum.PAID.value

                # Jika mengubah status menjadi belum dibayar, pastikan status pesanan adalah PENDING
                if not order_data.is_paid and order.status != OrderStatusEnum.PENDING.value:
                    return {
                        "success": False,
                        "message": "Pesanan dengan status selain PENDING tidak dapat diubah menjadi belum dibayar",
                    }, 400

                order.is_paid = order_data.is_paid

            db.session.commit()

            # Konversi ke response schema
            try:
                updated_order = OrderResponse.model_validate(order)
                return {
                    "success": True,
                    "message": "Status pesanan berhasil diperbarui",
                    "data": updated_order.model_dump(),
                }, 200
            except ValidationError as e:
                return _handle_validation_error(e)

        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Gagal memperbarui status pesanan: {str(e)}",
            }, 500
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def cancel_order(order_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Membatalkan pesanan dan mengembalikan stok produk.
        """
        try:
            # Validasi parameter
            if not isinstance(order_id, int) or order_id <= 0:
                return {
                    "success": False,
                    "message": "ID pesanan harus berupa bilangan bulat positif",
                }, 400

            order = Order.query.get(order_id)
            if not order:
                return {
                    "success": False,
                    "message": f"Pesanan dengan ID {order_id} tidak ditemukan",
                }, 404

            # Cek apakah pesanan masih bisa dibatalkan (hanya status PENDING atau PAID)
            if order.status not in [OrderStatusEnum.PENDING.value, OrderStatusEnum.PAID.value]:
                return {
                    "success": False,
                    "message": f"Pesanan dengan status {order.status} tidak dapat dibatalkan",
                }, 400

            # Mulai transaksi
            db.session.begin_nested()

            # Kembalikan stok produk
            for item in order.order_items:
                product = Product.query.get(item.product_id)
                if product:
                    product.stock += item.quantity

            # Ubah status pesanan menjadi CANCELLED
            order.status = OrderStatusEnum.CANCELLED.value

            # Jika pesanan sudah dibayar, tandai untuk refund (dalam sistem nyata)
            needs_refund = order.is_paid

            # Pesanan yang dibatalkan tidak bisa dalam status dibayar
            order.is_paid = False

            db.session.commit()

            response_data = {
                "success": True,
                "message": "Pesanan berhasil dibatalkan",
                "needs_refund": needs_refund
            }

            if needs_refund:
                response_data["refund_message"] = "Pembayaran akan dikembalikan dalam 3-5 hari kerja"

            return response_data, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Gagal membatalkan pesanan: {str(e)}",
            }, 500
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def get_orders_by_status(status: str) -> Tuple[Dict[str, Any], int]:
        """
        Mendapatkan daftar pesanan berdasarkan status.
        """
        try:
            # Validasi status
            try:
                valid_status = OrderStatusEnum(status)
            except ValueError:
                return {
                    "success": False,
                    "message": f"Status '{status}' tidak valid. Status yang valid: {', '.join([s.value for s in OrderStatusEnum])}",
                }, 400

            orders = Order.query.filter_by(status=valid_status.value).all()

            # Konversi ke response schema
            try:
                orders_data = []
                for order in orders:
                    order_data = OrderBriefResponse.model_validate(order)
                    # Tambahkan jumlah item
                    order_data_dict = order_data.model_dump()
                    order_data_dict["items_count"] = len(order.order_items)
                    orders_data.append(order_data_dict)

                return {
                    "success": True,
                    "data": orders_data,
                    "total_orders": len(orders_data),
                }, 200
            except ValidationError as e:
                return _handle_validation_error(e)

        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def get_order_statistics() -> Tuple[Dict[str, Any], int]:
        """
        Mendapatkan statistik pesanan (jumlah per status).
        """
        try:
            stats = {}

            # Hitung jumlah pesanan untuk setiap status
            for status in OrderStatusEnum:
                count = Order.query.filter_by(status=status.value).count()
                stats[status.value] = count

            # Hitung total pesanan
            total_orders = Order.query.count()

            # Hitung total nilai pesanan yang sudah dibayar
            from sqlalchemy import func
            paid_orders_value = db.session.query(func.sum(Order.total_price)).filter(
                Order.is_paid == True
            ).scalar() or 0

            return {
                "success": True,
                "data": {
                    "status_counts": stats,
                    "total_orders": total_orders,
                    "total_paid_value": float(paid_orders_value)
                }
            }, 200

        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500