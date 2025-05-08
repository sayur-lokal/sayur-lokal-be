from app.models.rating import Rating
from app.models.order import Order, OrderStatus
from app.schemas.rating_schema import RatingCreate, RatingResponse, RatingUpdate
from app.utils.extensions import db
from typing import Dict, Any, Tuple

def create_rating(current_user, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Membuat rating baru untuk produk

    Args:
        current_user: User yang sedang login
        data: Data rating yang akan dibuat

    Returns:
        Tuple berisi response (dict) dan status code (int)
    """
    try:
        # Validasi bahwa user adalah pembeli
        if not current_user or not current_user.buyer_profile:
            return {
                "success": False,
                "message": "Hanya pembeli yang dapat memberikan rating"
            }, 403

        # Validasi bahwa order ada dan milik pembeli ini
        order = Order.query.filter_by(
            id=data.get("order_id"),
            buyer_id=current_user.id
        ).first()

        if not order:
            return {
                "success": False,
                "message": "Order tidak ditemukan atau bukan milik Anda"
            }, 404

        # Validasi bahwa order sudah selesai (COMPLETED)
        if order.status != OrderStatus.COMPLETED.value:
            return {
                "success": False,
                "message": "Anda hanya dapat memberikan rating untuk order yang sudah selesai"
            }, 400

        # Validasi bahwa produk ada dalam order
        product_in_order = False
        for item in order.order_items:
            if item.product_id == data.get("product_id"):
                product_in_order = True
                break

        if not product_in_order:
            return {
                "success": False,
                "message": "Produk tidak ditemukan dalam order ini"
            }, 400

        # Cek apakah sudah pernah memberikan rating untuk produk ini dalam order ini
        existing_rating = Rating.query.filter_by(
            buyer_id=current_user.id,
            product_id=data.get("product_id"),
            order_id=data.get("order_id")
        ).first()

        if existing_rating:
            return {
                "success": False,
                "message": "Anda sudah memberikan rating untuk produk ini dalam order ini"
            }, 400

        # Buat rating baru
        new_rating = Rating(
            buyer_id=current_user.id,
            product_id=data.get("product_id"),
            order_id=data.get("order_id"),
            rating=data.get("rating"),
            comment=data.get("comment")
        )

        db.session.add(new_rating)
        db.session.commit()

        # Siapkan response
        rating_response = RatingResponse.model_validate(new_rating)

        return {
            "success": True,
            "message": "Rating berhasil dibuat",
            "rating": rating_response.model_dump()
        }, 201

    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

def update_rating(current_user, rating_id: int, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Mengupdate rating yang sudah ada

    Args:
        current_user: User yang sedang login
        rating_id: ID rating yang akan diupdate
        data: Data rating yang akan diupdate

    Returns:
        Tuple berisi response (dict) dan status code (int)
    """
    try:
        # Validasi bahwa user adalah pembeli
        if not current_user or not current_user.buyer_profile:
            return {
                "success": False,
                "message": "Hanya pembeli yang dapat mengupdate rating"
            }, 403

        # Cari rating yang akan diupdate
        rating = Rating.query.filter_by(
            id=rating_id,
            buyer_id=current_user.id
        ).first()

        if not rating:
            return {
                "success": False,
                "message": "Rating tidak ditemukan atau bukan milik Anda"
            }, 404

        # Update rating
        if "rating" in data and data["rating"] is not None:
            rating.rating = data["rating"]

        if "comment" in data and data["comment"] is not None:
            rating.comment = data["comment"]

        db.session.commit()

        # Siapkan response
        rating_response = RatingResponse.model_validate(rating)

        return {
            "success": True,
            "message": "Rating berhasil diupdate",
            "rating": rating_response.model_dump()
        }, 200

    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

def delete_rating(current_user, rating_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Menghapus rating

    Args:
        current_user: User yang sedang login
        rating_id: ID rating yang akan dihapus

    Returns:
        Tuple berisi response (dict) dan status code (int)
    """
    try:
        # Validasi bahwa user adalah pembeli
        if not current_user or not current_user.buyer_profile:
            return {
                "success": False,
                "message": "Hanya pembeli yang dapat menghapus rating"
            }, 403

        # Cari rating yang akan dihapus
        rating = Rating.query.filter_by(
            id=rating_id,
            buyer_id=current_user.id
        ).first()

        if not rating:
            return {
                "success": False,
                "message": "Rating tidak ditemukan atau bukan milik Anda"
            }, 404

        # Hapus rating
        db.session.delete(rating)
        db.session.commit()

        return {
            "success": True,
            "message": "Rating berhasil dihapus"
        }, 200

    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500