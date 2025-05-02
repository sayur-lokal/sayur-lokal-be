from app.models.category import Category
from app.models.product import Product
from app.models.seller import SellerProfile
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from app.utils.extensions import db, supabase
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
import uuid
import datetime


class ProductService:
    @staticmethod
    def create_product(product_data: ProductCreate) -> ProductResponse:
        """
        Membuat produk baru berdasarkan data yang diberikan.
        """
        try:
            # Validasi seller_id
            seller = SellerProfile.query.get(product_data.seller_id)
            if not seller:
                raise Exception(
                    f"Seller dengan ID {product_data.seller_id} tidak ditemukan"
                )

            # Validasi category_id
            category = Category.query.get(product_data.category_id)
            if not category:
                raise Exception(
                    f"Kategori dengan ID {product_data.category_id} tidak ditemukan"
                )

            # Membuat instance produk baru
            new_product = Product(
                name=product_data.name,
                description=product_data.description,
                price=product_data.price,
                stock=product_data.stock,
                category_id=product_data.category_id,
                seller_id=product_data.seller_id,
                image_url=product_data.image_url,
                # is_active=True,
            )

            # Menyimpan ke database
            db.session.add(new_product)
            db.session.commit()

            # Mengembalikan data produk yang telah dibuat
            return ProductResponse.model_validate(new_product)
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Gagal membuat produk: {str(e)}")

    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[ProductResponse]:
        """
        Mendapatkan produk berdasarkan ID.
        """
        product = Product.query.get(product_id)
        if not product:
            return None
        return ProductResponse.model_validate(product)

    @staticmethod
    def get_all_products(
        category_id: Optional[int] = None,
        seller_id: Optional[int] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        name: Optional[str] = None,
        # is_active: bool = True,
    ) -> List[ProductResponse]:
        """
        Mendapatkan daftar produk dengan filter opsional.
        """
        query = Product.query

        # Filter berdasarkan kategori
        if category_id:
            query = query.filter(Product.category_id == category_id)

        # Filter berdasarkan seller
        if seller_id:
            query = query.filter(Product.seller_id == seller_id)

        # Filter berdasarkan status aktif
        # if is_active is not None:
        #     query = query.filter(Product.is_active == is_active)

        # Filter berdasarkan harga minimum
        if price_min is not None:
            query = query.filter(Product.price >= price_min)

        # Filter berdasarkan harga maksimum
        if price_max is not None:
            query = query.filter(Product.price <= price_max)

        # Filter berdasarkan nama produk (pencarian parsial)
        if name is not None:
            query = query.filter(Product.name.ilike(f"%{name}%"))

        products = query.all()
        return [ProductResponse.model_validate(product) for product in products]

    @staticmethod
    def update_product(
        product_id: int, product_data: ProductUpdate
    ) -> Optional[ProductResponse]:
        """
        Memperbarui produk berdasarkan ID dan data yang diberikan.
        """
        try:
            product = Product.query.get(product_id)
            if not product:
                return None

            # Memperbarui atribut produk jika ada dalam data
            if product_data.name is not None:
                product.name = product_data.name

            if product_data.description is not None:
                product.description = product_data.description

            if product_data.price is not None:
                product.price = product_data.price

            if product_data.stock is not None:
                product.stock = product_data.stock

            if product_data.category_id is not None:
                product.category_id = product_data.category_id

            if product_data.image_url is not None:
                product.image_url = product_data.image_url

            # if product_data.is_active is not None:
            #     product.is_active = product_data.is_active

            # Memperbarui waktu update
            product.updated_at = datetime.datetime.utcnow()

            db.session.commit()
            return ProductResponse.model_validate(product)
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Gagal memperbarui produk: {str(e)}")

    @staticmethod
    def delete_product(product_id: int) -> bool:
        """
        Menghapus produk berdasarkan ID (soft delete dengan mengubah is_active menjadi False).
        """
        try:
            product = Product.query.get(product_id)
            if not product:
                return False

            # Soft delete
            # product.is_active = False
            product.updated_at = datetime.datetime.utcnow()

            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Gagal menghapus produk: {str(e)}")

    @staticmethod
    def upload_product_image(file_data, file_name: str) -> str:
        """
        Mengunggah gambar produk ke Supabase Storage dan mengembalikan URL.
        """
        try:
            # Membuat nama file unik
            unique_filename = f"{uuid.uuid4()}_{file_name}"

            # Mengunggah file ke Supabase
            response = supabase.storage.from_("product-images").upload(
                unique_filename, file_data
            )

            # Mendapatkan URL publik
            image_url = supabase.storage.from_("product-images").get_public_url(
                unique_filename
            )

            return image_url
        except Exception as e:
            raise Exception(f"Gagal mengunggah gambar: {str(e)}")
