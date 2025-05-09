from flask import Blueprint, request, jsonify
from app.services.rating_service import create_rating, update_rating, delete_rating
from app.utils.auth_middleware import token_required,role_required
from app.models.rating import Rating
from app.utils.helpers import handle_errors

rating_bp = Blueprint('rating', __name__, url_prefix='/ratings')

@rating_bp.route('', methods=['POST'])
@token_required
@role_required('buyer')
@handle_errors
def create_rating_endpoint(current_user):
    """
    Endpoint untuk membuat rating baru

    Request body:
    {
        "product_id": 1,
        "order_id": 1,
        "rating": 5,
        "comment": "Produk sangat bagus dan segar!"
    }
    """
    data = request.json
    response, status_code = create_rating(current_user, data)
    return jsonify(response), status_code

@rating_bp.route('/<int:rating_id>', methods=['PUT', 'PATCH'])
@token_required
@role_required('buyer')
@handle_errors
def update_rating_endpoint(current_user, rating_id):
    """
    Endpoint untuk mengupdate rating yang sudah ada

    Request body:
    {
        "rating": 4,
        "comment": "Produk bagus tapi pengiriman agak lama"
    }
    """
    data = request.json
    response, status_code = update_rating(current_user, rating_id, data)
    return jsonify(response), status_code

@rating_bp.route('/<int:rating_id>', methods=['DELETE'])
@token_required
@handle_errors
def delete_rating_endpoint(current_user, rating_id):
    """
    Endpoint untuk menghapus rating
    """
    response, status_code = delete_rating(current_user, rating_id)
    return jsonify(response), status_code

@rating_bp.route('/product/<int:product_id>', methods=['GET'])
@handle_errors
def get_product_ratings(product_id):
    """
    Endpoint untuk mendapatkan semua rating untuk produk tertentu
    """
    ratings = Rating.query.filter_by(product_id=product_id).all()

    if not ratings:
        return jsonify({
            "success": True,
            "message": "Belum ada rating untuk produk ini",
            "ratings": []
        }), 200

    # Hitung rata-rata rating
    total_rating = sum(r.rating for r in ratings)
    avg_rating = total_rating / len(ratings) if ratings else 0

    # Format response dengan data yang diperlukan saja
    ratings_response = [{
        "id": r.id,
        "buyer_id": r.buyer_id,
        "product_id": r.product_id,
        "order_id": r.order_id,
        "rating": r.rating,
        "comment": r.comment,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None
    } for r in ratings]

    return jsonify({
        "success": True,
        "message": "Rating berhasil diambil",
        "ratings": ratings_response,
        "total_ratings": len(ratings),
        "average_rating": round(avg_rating, 1)
    }), 200

@rating_bp.route('/user', methods=['GET'])
@token_required
@handle_errors
def get_user_ratings(current_user):
    """
    Endpoint untuk mendapatkan semua rating yang diberikan oleh user yang sedang login
    """
    # Validasi bahwa user adalah pembeli
    if not current_user or not current_user.buyer_profile:
        return jsonify({
            "success": False,
            "message": "Hanya pembeli yang dapat melihat rating mereka"
        }), 403

    ratings = Rating.query.filter_by(buyer_id=current_user.id).all()

    if not ratings:
        return jsonify({
            "success": True,
            "message": "Anda belum memberikan rating",
            "ratings": []
        }), 200

    # Format response dengan data yang diperlukan saja
    ratings_response = [{
        "id": r.id,
        "product_id": r.product_id,
        "order_id": r.order_id,
        "rating": r.rating,
        "comment": r.comment,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None
    } for r in ratings]

    return jsonify({
        "success": True,
        "message": "Rating berhasil diambil",
        "ratings": ratings_response
    }), 200

@rating_bp.route('/<int:rating_id>', methods=['GET'])
@handle_errors
def get_rating_detail(rating_id):
    """
    Endpoint untuk mendapatkan detail rating berdasarkan ID
    """
    rating = Rating.query.get(rating_id)

    if not rating:
        return jsonify({
            "success": False,
            "message": "Rating tidak ditemukan"
        }), 404

    # Format response dengan data yang diperlukan saja
    rating_response = {
        "id": rating.id,
        "buyer_id": rating.buyer_id,
        "product_id": rating.product_id,
        "order_id": rating.order_id,
        "rating": rating.rating,
        "comment": rating.comment,
        "created_at": rating.created_at.isoformat() if rating.created_at else None,
        "updated_at": rating.updated_at.isoformat() if rating.updated_at else None
    }

    return jsonify({
        "success": True,
        "message": "Rating berhasil diambil",
        "rating": rating_response
    }), 200