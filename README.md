# Sistem Supply Chain Management - Modul Retail

## Deskripsi Umum
Modul **Retail** bertanggung jawab untuk mengelola transaksi dan pemesanan produk yang dilakukan oleh toko (retail) kepada supplier. Sistem ini melibatkan proses login, manajemen keranjang belanja, pemesanan barang dari pemasok, dan pelacakan status pesanan. Sistem berinteraksi dengan modul **Supplier** dan **Distributor** melalui RESTful API.

---

## Fitur dan Endpoint API yang Tersedia

### 1. Fitur Login/Registrasi

#### a. Registrasi:
- **Endpoint**: `POST /api/register`
- **Deskripsi**: Digunakan untuk membuat akun baru bagi pengguna retail.
- **Request**:
    ```json
    {
      "username": "retailuser",
      "password": "password123"
    }
    ```
- **Response**:
    ```json
    {
      "message": "Account successfully created!"
    }
    ```

#### b. Login:
- **Endpoint**: `POST /api/login`
- **Deskripsi**: Digunakan untuk otentikasi pengguna retail yang sudah terdaftar.
- **Request**:
    ```json
    {
      "username": "retailuser",
      "password": "password123"
    }
    ```
- **Response**:
    ```json
    {
      "token": "JWT_TOKEN",
      "message": "Login successful"
    }
    ```

---

### 2. Fitur Beranda - Transaksi

#### a. Menambahkan Produk ke Keranjang:
- **Endpoint**: `POST /api/cart/add`
- **Deskripsi**: Menambah produk yang dipilih ke dalam keranjang belanja.
- **Request**:
    ```json
    {
      "product_id": "123",
      "quantity": 100
    }
    ```
- **Response**:
    ```json
    {
      "message": "Product added to cart",
      "cart": {
        "items": [
          {
            "product_id": "123",
            "name": "Sepeda Ontel B",
            "quantity": 100,
            "total_price": 1200000000000
          }
        ]
      }
    }
    ```

#### b. Melihat Keranjang Belanja:
- **Endpoint**: `GET /api/cart`
- **Deskripsi**: Mendapatkan daftar produk yang ada di keranjang belanja saat ini.
- **Response**:
    ```json
    {
      "cart": {
        "items": [
          {
            "product_id": "123",
            "name": "Sepeda Ontel B",
            "quantity": 100,
            "total_price": 1200000000000
          }
        ]
      }
    }
    ```

#### c. Simpan dan Checkout Produk:
- **Endpoint**: `POST /api/cart/checkout`
- **Deskripsi**: Melakukan checkout dari keranjang belanja dan memulai proses pemesanan ke pemasok.
- **Request**:
    ```json
    {
      "cart": {
        "items": [
          {
            "product_id": "123",
            "quantity": 100
          }
        ]
      }
    }
    ```
- **Response**:
    ```json
    {
      "message": "Checkout successful",
      "order_id": "ORD123",
      "total_price": 1200000000000
    }
    ```

---

### 3. Fitur Pemesanan dan Gudang

#### a. Melihat Data Produk di Gudang:
- **Endpoint**: `GET /api/warehouse`
- **Deskripsi**: Mendapatkan informasi stok produk yang tersedia di gudang.
- **Response**:
    ```json
    {
      "warehouse": [
        {
          "product_id": "123",
          "product_name": "Sepeda Ontel B",
          "stock": 500
        }
      ]
    }
    ```

#### b. Melakukan Pemesanan ke Supplier:
- **Endpoint**: `POST /api/orders`
- **Deskripsi**: Retail dapat melakukan pemesanan ke pemasok (supplier) melalui fitur ini.
- **Request**:
    ```json
    {
      "supplier_id": "SUP123",
      "items": [
        {
          "product_id": "123",
          "quantity": 1
        }
      ],
      "distributor_id": "DIST123"
    }
    ```
- **Response**:
    ```json
    {
      "message": "Order submitted successfully",
      "order_id": "ORD123"
    }
    ```

---

### 4. Fitur Pelacakan Pemesanan

#### a. Melihat Daftar Pemesanan:
- **Endpoint**: `GET /api/orders`
- **Deskripsi**: Mendapatkan daftar pemesanan yang sudah dilakukan oleh retail.
- **Response**:
    ```json
    {
      "orders": [
        {
          "order_id": "ORD123",
          "date": "2024-09-28",
          "items": [
            {
              "product_name": "Sepeda Ontel B",
              "quantity": 1
            }
          ],
          "distributor": "DIST123",
          "total_price": 150000,
          "status": "Pending"
        }
      ]
    }
    ```

#### b. Konfirmasi Pemesanan:
- **Endpoint**: `POST /api/orders/confirm`
- **Deskripsi**: Retail dapat mengonfirmasi pesanan yang sudah diterima dari distributor.
- **Request**:
    ```json
    {
      "order_id": "ORD123",
      "confirmation": true
    }
    ```
- **Response**:
    ```json
    {
      "message": "Order confirmed"
    }
    ```

#### c. Melihat Nomor Resi Pengiriman:
- **Endpoint**: `GET /api/shipment/{order_id}/tracking`
- **Deskripsi**: Mendapatkan nomor resi pengiriman dan status pengiriman dari distributor.
- **Response**:
    ```json
    {
      "tracking_number": "RESI123456",
      "status": "Shipped"
    }
    ```

---

### 5. Interaksi dengan Modul Lain

#### a. Interaksi Retail dengan Supplier
- Retail mendapatkan informasi produk dari Supplier menggunakan **GET /api/products**.
- Setelah memilih produk, Retail mengirimkan draft pesanan ke Supplier menggunakan **POST /api/draft-order**.
- Supplier memproses pesanan dan mengirimkan informasi harga ongkir yang didapatkan dari Distributor ke Retail menggunakan **GET /api/shipping-fee**.

#### b. Interaksi Retail dengan Distributor
- Retail mengirimkan detail pengiriman ke Distributor melalui Supplier menggunakan **POST /api/shipment**.
- Distributor memberikan nomor resi pengiriman yang akan dikirim kembali oleh Supplier ke Retail menggunakan **GET /api/tracking-number**.
  
---

### 6. Teknologi yang Digunakan
- **Backend**: Python (Flask)
- **Database**: Firebase
- **Frontend**: HTML, CSS, JavaScript
- **API Integrasi**: -
