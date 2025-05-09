# Sayur-Lokal API

API untuk aplikasi Sayur-lokal, sebuah platform jual beli produk lokal yang ramah lingkungan.

## Base URL

- Production: `[https://sayur-lokal-be.onrender.com/](https://sayur-lokal-be.onrender.com/)`
- Local Development: `http://localhost:5000`
- API Documentation: `[https://documenter.getpostman.com](https://documenter.getpostman.com/view/18837078/2sB2j978ZD#fe4e1328-19a2-4ca1-b1ac-e6f627be134a)`

---

## Authentication

- `POST /auth/register/buyer` - Registrasi sebagai buyer
- `POST /auth/register/seller` - Registrasi sebagai seller
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user (butuh token)
- `POST /auth/resend-verification` - Kirim ulang email verifikasi

---

## User Profile

- `GET /user/profile` - Lihat profil user (token)
- `PUT /user/profile/buyer` - Update profil buyer
- `PUT /user/profile/seller` - Update profil seller
- `PUT /user/profile/picture` - Update foto profil
- `PUT /user/password` - Ganti password

---

## Products

- `GET /products` - Lihat semua produk
- `GET /products/{product_id}` - Detail produk
- `POST /products` - Tambah produk (seller only)
- `PUT /products/{product_id}` - Update produk (seller only)
- `DELETE /products/{product_id}` - Hapus produk (seller only)
- `GET /products/category/{category_id}` - Produk berdasarkan kategori
- `GET /products/seller/{seller_id}` - Produk berdasarkan seller
- `GET /products/price-range` - Filter harga
- `GET /products/search` - Cari produk

---

## Categories

- `GET /categories` - Lihat semua kategori
- `GET /categories/{category_id}` - Detail kategori dan produk
- `POST /categories` - Tambah kategori (admin only)
- `PUT /categories/{category_id}` - Update kategori (admin only)
- `DELETE /categories/{category_id}` - Hapus kategori (admin only)

---

## Orders

- `POST /orders` - Buat order (buyer only)
- `GET /orders/buyer` - Lihat order buyer
- `GET /orders/seller` - Lihat order seller
- `GET /orders/{order_id}` - Detail order
- `PUT /orders/{order_id}/status` - Update status (seller only)
- `PUT /orders/{order_id}/cancel` - Batalkan order (buyer only)

---

## Auth Header

Untuk endpoint yang membutuhkan autentikasi, gunakan header:
