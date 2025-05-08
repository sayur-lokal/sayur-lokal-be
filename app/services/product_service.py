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
                product_image_url=product_data.product_image_url,
                discount=product_data.discount or 0,
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
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
    ) -> dict:
        """
        Mendapatkan daftar produk dengan filter opsional dan pagination.
        """
        query = Product.query

        # Filter berdasarkan kategori
        if category_id:
            query = query.filter(Product.category_id == category_id)

        # Filter berdasarkan seller
        if seller_id:
            query = query.filter(Product.seller_id == seller_id)

        # Filter berdasarkan harga minimum
        if price_min is not None:
            query = query.filter(Product.price >= price_min)

        # Filter berdasarkan harga maksimum
        if price_max is not None:
            query = query.filter(Product.price <= price_max)

        # Filter berdasarkan nama produk (pencarian parsial)
        if name is not None:
            query = query.filter(Product.name.ilike(f"%{name}%"))


        # Hitung total produk yang sesuai dengan filter
        total_products = query.count()

        # Terapkan pagination
        paginated_products = query.paginate(page=page, per_page=per_page, error_out=False)

        # Konversi hasil ke format response
        product_list = [ProductResponse.model_validate(product) for product in paginated_products.items]

        # Buat response dengan informasi pagination
        return {
            "products": product_list,
            "pagination": {
                "total_items": total_products,
                "total_pages": paginated_products.pages,
                "current_page": page,
                "per_page": per_page,
                "has_next": paginated_products.has_next,
                "has_prev": paginated_products.has_prev,
                "next_page": paginated_products.next_num,
                "prev_page": paginated_products.prev_num
            }
        }

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
                # Validasi category_id
                category = Category.query.get(product_data.category_id)
                if not category:
                    raise Exception(
                        f"Kategori dengan ID {product_data.category_id} tidak ditemukan"
                    )
                product.category_id = product_data.category_id

            if product_data.product_image_url is not None:
                product.product_image_url = product_data.product_image_url

            if product_data.discount is not None:
                product.discount = product_data.discount

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
        Menghapus produk berdasarkan ID (hard delete).
        """
        try:
            product = Product.query.get(product_id)
            if not product:
                return False

            db.session.delete(product)
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

    @staticmethod
    def get_product_with_details(product_id: int):
        """
        Mendapatkan produk dengan detail tambahan seperti nama seller dan kategori.
        """
        try:
            product = Product.query.get(product_id)
            if not product:
                return None

            # Ambil data seller dan kategori
            seller = SellerProfile.query.get(product.seller_id)
            category = Category.query.get(product.category_id)

            # Buat response dengan data tambahan
            product_data = ProductResponse.model_validate(product)

            # Hitung harga setelah diskon
            final_price = product.price
            if product.discount > 0:
                final_price = product.price - (product.price * product.discount / 100)

            # Buat response detail
            return {
                **product_data.model_dump(),
                "seller_name": seller.shop_name if seller else None,
                "category_name": category.name if category else None,
                "final_price": float(final_price)
            }
        except Exception as e:
            raise Exception(f"Gagal mendapatkan detail produk: {str(e)}")