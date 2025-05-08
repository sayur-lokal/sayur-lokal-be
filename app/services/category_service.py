from pydantic import ValidationError
from app.models.category import Category
from app.schemas.category_schema import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryWithProductsResponse,
)
from app.utils.extensions import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Dict, Any, Tuple, List, Optional, Union
import datetime
from app.utils.helpers import _handle_validation_error


class CategoryService:

    @staticmethod
    def create_category(data: Union[Dict[str, Any], CategoryCreate]) -> Tuple[Dict[str, Any], int]:
        """
        Membuat kategori baru berdasarkan data yang diberikan.

        Args:
            data: Data kategori dalam bentuk dict atau objek CategoryCreate

        Returns:
            Tuple berisi response (dict) dan status code (int)
        """
        try:
            # Validasi data dengan Pydantic
            try:
                if isinstance(data, dict):
                    category_data = CategoryCreate(**data)
                else:
                    category_data = data
            except ValidationError as e:
                return _handle_validation_error(e)

            # Cek apakah kategori dengan nama yang sama sudah ada (case insensitive)
            existing_category = Category.query.filter(
                db.func.lower(Category.name) == db.func.lower(category_data.name)
            ).first()

            if existing_category:
                return {
                    "success": False,
                    "message": f"Kategori dengan nama '{category_data.name}' sudah ada",
                }, 400

            # Membuat instance kategori baru
            new_category = Category(name=category_data.name)

            # Menyimpan ke database
            db.session.add(new_category)
            db.session.commit()

            # Mengembalikan data kategori yang telah dibuat
            category_response = CategoryResponse.model_validate(new_category)
            category_response.product_count = 0  # Kategori baru belum memiliki produk

            return {
                "success": True,
                "message": "Kategori berhasil dibuat",
                "data": category_response.model_dump(),
            }, 201
        except IntegrityError as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Gagal membuat kategori: Nama kategori harus unik",
            }, 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Gagal membuat kategori: {str(e)}",
            }, 500
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def get_all_categories(
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[Dict[str, Any], int]:
        """
        Mendapatkan daftar semua kategori dengan opsi pengurutan dan pencarian.

        Args:
            sort_by: Field untuk pengurutan ('name', 'created_at', 'product_count')
            sort_order: Arah pengurutan ('asc' atau 'desc')
            search: Kata kunci pencarian untuk nama kategori

        Returns:
            Tuple berisi response (dict) dan status code (int)
        """
        try:
            # Buat query dasar
            query = Category.query

            # Terapkan filter pencarian jika ada
            if search:
                query = query.filter(Category.name.ilike(f"%{search}%"))

            # Ambil semua kategori yang sesuai filter
            categories = query.all()

            # Siapkan hasil dengan jumlah produk
            result = []
            for category in categories:
                category_response = CategoryResponse.model_validate(category)
                category_response.product_count = (
                    len(category.products) if hasattr(category, "products") else 0
                )
                result.append(category_response.model_dump())

            # Terapkan pengurutan
            if sort_by:
                reverse = sort_order and sort_order.lower() == 'desc'

                if sort_by == 'name':
                    result.sort(key=lambda x: x['name'], reverse=reverse)
                elif sort_by == 'created_at':
                    result.sort(key=lambda x: x['created_at'], reverse=reverse)
                elif sort_by == 'product_count':
                    result.sort(key=lambda x: x.get('product_count', 0), reverse=reverse)

            return {
                "success": True,
                "message": "Daftar kategori berhasil diambil",
                "data": result,
                "total": len(result)
            }, 200
        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def get_category_by_id(category_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Mendapatkan detail kategori berdasarkan ID.

        Args:
            category_id: ID kategori yang akan diambil

        Returns:
            Tuple berisi response (dict) dan status code (int)
        """
        try:
            # Validasi ID
            if not isinstance(category_id, int) or category_id <= 0:
                return {
                    "success": False,
                    "message": "ID kategori harus berupa bilangan bulat positif",
                }, 400

            category = Category.query.get(category_id)

            if not category:
                return {
                    "success": False,
                    "message": f"Kategori dengan ID {category_id} tidak ditemukan",
                }, 404

            # Menambahkan jumlah produk
            category_response = CategoryResponse.model_validate(category)
            category_response.product_count = (
                len(category.products) if hasattr(category, "products") else 0
            )

            return {
                "success": True,
                "message": "Detail kategori berhasil diambil",
                "data": category_response.model_dump(),
            }, 200
        except ValueError as e:
            return {"success": False, "message": str(e)}, 400
        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def get_category_with_products(category_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Mendapatkan detail kategori beserta produk-produknya berdasarkan ID.

        Args:
            category_id: ID kategori yang akan diambil

        Returns:
            Tuple berisi response (dict) dan status code (int)
        """
        try:
            # Validasi ID
            if not isinstance(category_id, int) or category_id <= 0:
                return {
                    "success": False,
                    "message": "ID kategori harus berupa bilangan bulat positif",
                }, 400

            category = Category.query.get(category_id)

            if not category:
                return {
                    "success": False,
                    "message": f"Kategori dengan ID {category_id} tidak ditemukan",
                }, 404

            # Menggunakan skema yang menyertakan produk
            category_with_products = CategoryWithProductsResponse.model_validate(
                category
            )

            # Pastikan product_count sesuai dengan jumlah produk
            category_with_products.product_count = len(category_with_products.products)

            return {
                "success": True,
                "message": "Detail kategori dan produk berhasil diambil",
                "data": category_with_products.model_dump(),
            }, 200
        except ValueError as e:
            return {"success": False, "message": str(e)}, 400
        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def update_category(
        category_id: int, data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], int]:
        """
        Memperbarui kategori berdasarkan ID dan data yang diberikan.

        Args:
            category_id: ID kategori yang akan diperbarui
            data: Data kategori yang akan diperbarui

        Returns:
            Tuple berisi response (dict) dan status code (int)
        """
        try:
            # Validasi ID
            if not isinstance(category_id, int) or category_id <= 0:
                return {
                    "success": False,
                    "message": "ID kategori harus berupa bilangan bulat positif",
                }, 400

            # Validasi data dengan Pydantic
            try:
                # Hanya validasi field yang ada
                update_data = {k: v for k, v in data.items() if v is not None}
                category_data = CategoryUpdate(**update_data)
            except ValidationError as e:
                return _handle_validation_error(e)

            category = Category.query.get(category_id)

            if not category:
                return {
                    "success": False,
                    "message": f"Kategori dengan ID {category_id} tidak ditemukan",
                }, 404

            # Cek apakah nama baru sudah digunakan oleh kategori lain (case insensitive)
            if category_data.name and category_data.name.lower() != category.name.lower():
                existing_category = Category.query.filter(
                    db.func.lower(Category.name) == db.func.lower(category_data.name)
                ).first()

                if existing_category and existing_category.id != category_id:
                    return {
                        "success": False,
                        "message": f"Kategori dengan nama '{category_data.name}' sudah ada",
                    }, 400

            # Memperbarui atribut kategori jika ada dalam data
            if category_data.name is not None:
                category.name = category_data.name

            # Memperbarui waktu update
            category.updated_at = datetime.datetime.utcnow()

            db.session.commit()

            # Menambahkan jumlah produk
            category_response = CategoryResponse.model_validate(category)
            category_response.product_count = (
                len(category.products) if hasattr(category, "products") else 0
            )

            return {
                "success": True,
                "message": "Kategori berhasil diperbarui",
                "data": category_response.model_dump(),
            }, 200
        except IntegrityError:
            db.session.rollback()
            return {
                "success": False,
                "message": "Gagal memperbarui kategori: Nama kategori harus unik",
            }, 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Gagal memperbarui kategori: {str(e)}",
            }, 500
        except ValueError as e:
            return {"success": False, "message": str(e)}, 400
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def delete_category(category_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Menghapus kategori berdasarkan ID.

        Args:
            category_id: ID kategori yang akan dihapus

        Returns:
            Tuple berisi response (dict) dan status code (int)
        """
        try:
            # Validasi ID
            if not isinstance(category_id, int) or category_id <= 0:
                return {
                    "success": False,
                    "message": "ID kategori harus berupa bilangan bulat positif",
                }, 400

            category = Category.query.get(category_id)

            if not category:
                return {
                    "success": False,
                    "message": f"Kategori dengan ID {category_id} tidak ditemukan",
                }, 404

            # Cek apakah kategori memiliki produk
            if hasattr(category, "products") and len(category.products) > 0:
                return {
                    "success": False,
                    "message": f"Kategori tidak dapat dihapus karena masih memiliki {len(category.products)} produk",
                    "product_count": len(category.products)
                }, 400

            # Hapus kategori
            db.session.delete(category)
            db.session.commit()

            return {
                "success": True,
                "message": "Kategori berhasil dihapus",
                "deleted_id": category_id
            }, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Gagal menghapus kategori: {str(e)}",
            }, 500
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def bulk_delete_categories(category_ids: List[int]) -> Tuple[Dict[str, Any], int]:
        """
        Menghapus beberapa kategori sekaligus berdasarkan daftar ID.

        Args:
            category_ids: Daftar ID kategori yang akan dihapus

        Returns:
            Tuple berisi response (dict) dan status code (int)
        """
        try:
            # Validasi input
            if not isinstance(category_ids, list) or not category_ids:
                return {
                    "success": False,
                    "message": "Daftar ID kategori harus berupa array yang tidak kosong",
                }, 400

            # Validasi semua ID adalah integer positif
            invalid_ids = [id for id in category_ids if not isinstance(id, int) or id <= 0]
            if invalid_ids:
                return {
                    "success": False,
                    "message": f"ID kategori harus berupa bilangan bulat positif: {invalid_ids}",
                }, 400

            # Ambil semua kategori yang akan dihapus
            categories = Category.query.filter(Category.id.in_(category_ids)).all()
            found_ids = [category.id for category in categories]

            # Cek kategori yang tidak ditemukan
            not_found_ids = [id for id in category_ids if id not in found_ids]
            if not_found_ids:
                return {
                    "success": False,
                    "message": f"Beberapa kategori tidak ditemukan: {not_found_ids}",
                    "not_found_ids": not_found_ids
                }, 404

            # Cek kategori yang memiliki produk
            categories_with_products = []
            for category in categories:
                if hasattr(category, "products") and len(category.products) > 0:
                    categories_with_products.append({
                        "id": category.id,
                        "name": category.name,
                        "product_count": len(category.products)
                    })

            if categories_with_products:
                return {
                    "success": False,
                    "message": "Beberapa kategori tidak dapat dihapus karena masih memiliki produk",
                    "categories_with_products": categories_with_products
                }, 400

            # Hapus semua kategori yang valid
            for category in categories:
                db.session.delete(category)

            db.session.commit()

            return {
                "success": True,
                "message": f"Berhasil menghapus {len(categories)} kategori",
                "deleted_ids": found_ids
            }, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Gagal menghapus kategori: {str(e)}",
            }, 500
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500