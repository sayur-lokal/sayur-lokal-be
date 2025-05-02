from app.models.category import Category
from app.schemas.category_schema import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryWithProductsResponse,
)
from app.utils.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any, Tuple, List
import datetime


class CategoryService:
    @staticmethod
    def create_category(category_data: CategoryCreate) -> Tuple[Dict[str, Any], int]:
        """
        Membuat kategori baru berdasarkan data yang diberikan.
        """
        try:
            # Cek apakah kategori dengan nama yang sama sudah ada
            existing_category = Category.query.filter_by(
                name=category_data.name
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
            return {
                "success": True,
                "message": "Kategori berhasil dibuat",
                "data": CategoryResponse.model_validate(new_category).model_dump(),
            }, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Gagal membuat kategori: {str(e)}",
            }, 500
        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def get_all_categories() -> Tuple[Dict[str, Any], int]:
        """
        Mendapatkan daftar semua kategori.
        """
        try:
            categories = Category.query.all()

            # Menambahkan jumlah produk untuk setiap kategori
            result = []
            for category in categories:
                category_data = CategoryResponse.model_validate(category).model_dump()
                category_data["product_count"] = (
                    len(category.products) if hasattr(category, "products") else 0
                )
                result.append(category_data)

            return {
                "success": True,
                "message": "Daftar kategori berhasil diambil",
                "data": result,
            }, 200
        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def get_category_by_id(category_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Mendapatkan detail kategori berdasarkan ID.
        """
        try:
            category = Category.query.get(category_id)

            if not category:
                return {
                    "success": False,
                    "message": f"Kategori dengan ID {category_id} tidak ditemukan",
                }, 404

            # Menambahkan jumlah produk
            category_data = CategoryResponse.model_validate(category).model_dump()
            category_data["product_count"] = (
                len(category.products) if hasattr(category, "products") else 0
            )

            return {
                "success": True,
                "message": "Detail kategori berhasil diambil",
                "data": category_data,
            }, 200
        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def get_category_with_products(category_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Mendapatkan detail kategori beserta produk-produknya berdasarkan ID.
        """
        try:
            category = Category.query.get(category_id)

            if not category:
                return {
                    "success": False,
                    "message": f"Kategori dengan ID {category_id} tidak ditemukan",
                }, 404

            # Menggunakan skema yang menyertakan produk
            category_with_products = CategoryWithProductsResponse.model_validate(
                category
            ).model_dump()

            return {
                "success": True,
                "message": "Detail kategori dan produk berhasil diambil",
                "data": category_with_products,
            }, 200
        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def update_category(
        category_id: int, category_data: CategoryUpdate
    ) -> Tuple[Dict[str, Any], int]:
        """
        Memperbarui kategori berdasarkan ID dan data yang diberikan.
        """
        try:
            category = Category.query.get(category_id)

            if not category:
                return {
                    "success": False,
                    "message": f"Kategori dengan ID {category_id} tidak ditemukan",
                }, 404

            # Cek apakah nama baru sudah digunakan oleh kategori lain
            if category_data.name and category_data.name != category.name:
                existing_category = Category.query.filter_by(
                    name=category_data.name
                ).first()
                if existing_category and existing_category.id != category_id:
                    return {
                        "success": False,
                        "message": f"Kategori dengan nama '{category_data.name}' sudah ada",
                    }, 400

            # Memperbarui atribut kategori jika ada dalam data
            if category_data.name is not None:
                category.name = category_data.name

            # if category_data.description is not None:
            #     category.description = category_data.description

            # Memperbarui waktu update
            category.updated_at = datetime.datetime.utcnow()

            db.session.commit()

            # Menambahkan jumlah produk
            category_response = CategoryResponse.model_validate(category).model_dump()
            category_response["product_count"] = (
                len(category.products) if hasattr(category, "products") else 0
            )

            return {
                "success": True,
                "message": "Kategori berhasil diperbarui",
                "data": category_response,
            }, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Gagal memperbarui kategori: {str(e)}",
            }, 500
        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    @staticmethod
    def delete_category(category_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Menghapus kategori berdasarkan ID.
        """
        try:
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
                }, 400

            # Hapus kategori
            db.session.delete(category)
            db.session.commit()

            return {"success": True, "message": "Kategori berhasil dihapus"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                "success": False,
                "message": f"Gagal menghapus kategori: {str(e)}",
            }, 500
        except Exception as e:
            return {"success": False, "message": f"Terjadi kesalahan: {str(e)}"}, 500

    # @staticmethod
    # def seed_categories() -> None:
    #     """
    #     Menambahkan data awal kategori.
    #     """
    #     default_categories = [
    #         {
    #             "name": "Elektronik",
    #             "description": "Produk elektronik seperti handphone, laptop, dll",
    #         },
    #         {
    #             "name": "Fashion",
    #             "description": "Produk fashion seperti baju, celana, sepatu, dll",
    #         },
    #         {"name": "Makanan & Minuman", "description": "Produk makanan dan minuman"},
    #         {
    #             "name": "Kesehatan",
    #             "description": "Produk kesehatan dan perawatan tubuh",
    #         },
    #         {
    #             "name": "Rumah Tangga",
    #             "description": "Produk untuk kebutuhan rumah tangga",
    #         },
    #         {
    #             "name": "Olahraga",
    #             "description": "Produk olahraga dan aktivitas luar ruangan",
    #         },
    #         {
    #             "name": "Buku & Alat Tulis",
    #             "description": "Produk buku, alat tulis, dan perlengkapan kantor",
    #         },
    #         {"name": "Mainan & Hobi", "description": "Produk mainan dan hobi"},
    #     ]

    #     try:
    #         for category_data in default_categories:
    #             # Cek apakah kategori sudah ada
    #             existing = Category.query.filter_by(name=category_data["name"]).first()
    #             if not existing:
    #                 new_category = Category(
    #                     name=category_data["name"],
    #                     description=category_data["description"],
    #                 )
    #                 db.session.add(new_category)

    #         db.session.commit()
    #     except SQLAlchemyError as e:
    #         db.session.rollback()
    #         print(f"Gagal menambahkan kategori default: {str(e)}")
    #     except Exception as e:
    #         print(f"Terjadi kesalahan: {str(e)}")
