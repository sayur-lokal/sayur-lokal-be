# Sayur-Lokal API

API untuk aplikasi Sayur-lokal, sebuah platform jual beli produk lokal yang ramah lingkungan.

## Base URL

- Production: `https://fsse-oct24-group-k-gfp-be.onrender.com`
- Local Development: `http://localhost:5000`

---

## Authentication

- `POST /auth/register/buyer` - Registrasi sebagai buyer
- `POST /auth/register/seller` - Registrasi sebagai seller
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user (butuh token)
- `POST /auth/resend-verification` - Kirim ulang email verifikasi

\*\*

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

## Ratings & Reviews

- `POST /ratings` - Buat rating (buyer only)
- `GET /ratings/product/{product_id}` - Lihat semua rating produk
- `GET /ratings/buyer` - Lihat semua rating yang dibuat buyer

---

## Wallet

- `GET /wallet/balance` - Lihat saldo
- `GET /wallet/transactions` - Riwayat transaksi
- `POST /wallet/topup` - Top up saldo
- `POST /wallet/withdraw` - Tarik saldo (seller only)

---

## Admin

- `GET /admin/users` - Lihat semua user
- `PUT /admin/users/{user_id}/status` - Update status user
- `GET /admin/sellers` - Lihat semua seller
- `PUT /admin/sellers/{seller_id}/verify` - Verifikasi seller
- `GET /admin/withdrawals` - Lihat semua permintaan tarik saldo
- `PUT /admin/withdrawals/{withdrawal_id}` - Proses penarikan

---

## Auth Header

Untuk endpoint yang membutuhkan autentikasi, gunakan header:
