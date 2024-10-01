# Sistem Supply Chain Management - Modul Retail | PedalXPress

## Anggota | Kelompok 8
- 162112133009 | Diaz Arvinda Ardian
- 162112133028 | Denis Muhammad Jethro
- 164221010 | Aqila Hana Winanggoro
- 164221016 | Jihan Ashifa Hakim
- 164221079 | Patricia Dewinta Wahyu Krisnayanti

## Deskripsi Umum
Modul **Retail** bertanggung jawab untuk mengelola transaksi dan pemesanan produk yang dilakukan oleh toko (retail) kepada supplier. Sistem ini melibatkan proses login, manajemen keranjang belanja, pemesanan barang dari pemasok, dan pelacakan status pesanan. Sistem berinteraksi dengan Modul **Supplier** dan **Distributor** melalui RESTful API.

## Link Github Project:
https://github.com/diazarvinda/iak_kelompok8

---

## Fitur dan Endpoint API yang Tersedia

### Overview
API ini menyediakan endpoint untuk mengelola transaksi, data stok, pesanan, dan lainnya. Dibangun menggunakan Flask dan terintegrasi dengan Firebase untuk penyimpanan data.

### Endpoints:

### 1. User Authentication

#### a. Login
- **URL:** `/`
- **Method:** `GET`, `POST`
- **Deskripsi:** Menampilkan halaman login dan menangani login pengguna.
- **Contoh Request:**
  ```http
  GET /
  ```

#### b. Register
- **URL:** `/register`
- **Method:** `GET`, `POST`
- **Deskripsi:** Menampilkan halaman registrasi dan menangani pendaftaran pengguna.
- **Contoh Request:**
  ```http
  POST /register
  Content-Type: application/x-www-form-urlencoded

  email=user@example.com&password=securepassword
  ```

#### c. Logout
- **URL:** `/logout`
- **Method:** `GET`
- **Deskripsi:** Logout pengguna dan menghapus sesi.
- **Contoh Request:**
  ```http
  GET /logout
  ```

### 2. Transactions

#### a. Get Transactions Data
- **URL:** `/api/get/transaction_data`
- **Method:** `GET`
- **Deskripsi:** Mengambil semua data transaksi.
- **Contoh Request:**
  ```http
  GET /api/get/transaction_data
  ```
- **Contoh Response:**
  ```json
    {
      "-O83UToeNuy6veE5b0qj": {
        "date": "2024-10-01 02:52:35",
        "items": [
          {
            "item": "Sepeda Ontel - SIGMA",
            "price": 15000000,
            "quantity": 3,
            "totalPrice": 45000000
          }
        ],
        "total_price": 45000000,
        "transaction_id": "0c0b0099-709a-4c4e-8ba6-8cc48e2d339d"
      }
    }
  ```

#### b. Save Transaction
- **URL:** `/api/save_transaction`
- **Method:** `POST`
- **Deskripsi:** Menyimpan transaksi baru.
- **Contoh Request:**
  ```http
  POST /api/save_transaction
  Content-Type: application/json

  {
    "items": [
      {"item": "Sepeda Ontel - ALPHA", "price": 500, "quantity": 2}
    ]
  }
  ```
- **Contoh Response:**
  ```json
  {
    "message": "Semua transaksi berhasil disimpan!"
  }
  ```

### 3. Stock Data

#### a. Get Stock Data
- **URL:** `/api/get/stock_data`
- **Method:** `GET`
- **Deskripsi:** Mengambil semua data stok.
- **Contoh Request:**
  ```http
  GET /api/get/stock_data
  ```
- **Contoh Response:**
  ```json
  {
    "PROD001": {"product_name": "Part A", "quantity": 10},
    "PROD002": {"product_name": "Part B", "quantity": 5}
  }
  ```

#### b. Get Supplier Stock
- **URL:** `/api/get/supplier_stock/<supplier>`
- **Method:** `GET`
- **Deskripsi:** Mengambil data stok dari supplier tertentu.
- **Contoh Request:**
  ```http
  GET /api/get/supplier_stock/SUP01
  ```
- **Contoh Response:**
  ```json
     {
        "berat": "0.50",
        "harga": "300000.00",
        "id_produk": "3-PRO",
        "linkgambar": "https://standert.de/cdn/shop/files/Kreissage-RS-Road-Bike-Frameset-Navy_500x500@2x.webp?v=1697787188",
        "nama_produk": "Speed",
        "stock": 49
     },
  ```

### 4. Orders

#### a. Get Distributor Price
- **URL:** `/api/get/distributor_price`
- **Method:** `POST`
- **Deskripsi:** Mengambil harga dari distributor.
- **Contoh Request:**
  ```http
  POST /api/get/distributor_price

    {
    "id_supplier": "SUP01",  
    "cart": [
        {
            "id_produk": "PROD001",  
            "quantity": 2  
        {
            "id_produk": "PROD002",
            "quantity": 1
        }
    ],
    "id_retail": "RET02",  
    "id_distributor": "DIS01",  
    "total_harga_barang": 500000,  
    "total_berat_barang": 10, 
    "kota_tujuan": "ngawi"  
  }
  ```
- **Contoh Response:**
  ```json
    {
    "harga_pengiriman": 50000,  
    "lama_pengiriman": "3-5 hari", 
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000"  
    }
  ```

#### b. Submit Order
- **URL:** `/api/submit_order`
- **Method:** `POST`
- **Deskripsi:** Mengirimkan pesanan baru.
- **Contoh Request:**
  ```http
  POST /api/submit_order

  {
        "id_supplier": "SUP01",
        "id_log": "123e4567-e89b-12d3-a456-426614174000",  
        "id_distributor": "DIS01",  
        "total_price": 550000,  
        "cart": [
            {
                "supplier": "SUP01",
                "product": "PROD001",
                "quantity": 2,
                "harga": 200000,
                "berat": 5,
                "product_name": "Product 1"
            },
            {
                "supplier": "SUP01",
                "product": "PROD002",
                "quantity": 1,
                "harga": 100000,
                "berat": 5,
                "product_name": "Product 2"
            }
        ]
    }
  ```
- **Contoh Response:**
  ```json
  {
    "message": "Order submitted successfully"
  }
  ```

#### c. Track Order
- **URL:** `/api/track/order`
- **Method:** `POST`
- **Deskripsi:** Melacak pesanan yang ada.
- **Contoh Request:**
  ```http
  POST /api/track/order

  {
    "no_resi": "resi123",
    "id_distributor": "DIS01"
  }
  ```
- **Contoh Response:**
  ```json
  {
    "no_resi": "resi123",
    "status": "Arrived"
  }
  ```

#### d. Confirm Order
- **URL:** `/api/confirm_order`
- **Method:** `POST`
- **Deskripsi:** Mengonfirmasi pesanan dan memperbarui data stok.
- **Contoh Request:**
  ```http
  POST /api/confirm_order
  Content-Type: application/json

  {
    "data_confirm": {
      "no_resi": "resi123",
      "cart": [...]
    }
  }
  ```
- **Contoh Response:**
  ```json
  {
    "message": "Konfirmasi Berhasil"
  }
  ```

#### e. Get Data Pemesanan
- **URL:** `/api/get/pemesanan`
- **Method:** `GET`
- **Deskripsi:** Mengambil semua data pemesanan.
- **Contoh Request:**
  ```http
  GET /api/get/pemesanan
  ```
- **Contoh Response:**
  ```json
  {
    "order_id": {
      "no_resi": "resi123",
      "id_distributor": "DIS01",
      "lama_pengiriman": 3,
      "harga_pengiriman": 100,
      "cart": [...],
      "total_price": 1000,
      "date": "2023-10-01 12:00:00"
    }
  }
  ```

## Teknologi yang Digunakan
- **Backend**: Python (Flask)
- **Database**: Firebase
- **Frontend**: HTML, CSS, JavaScript
- **API Integrasi**: RESTful API

## Cara Kerja Modul dan Interaksi dengan Modul Lain
- Modul Retail akan mengambil data transaksi yang telah dilakukan menggunakan **GET /api/get/transaction_data**.
- Kemudian transaksi disimpan ke dalam histori transaksi menggunakan **POST /api/save_transaction**.
- Modul Retail akan bisa mendapatkan informasi produk dari Modul Supplier menggunakan **GET /api/get/supplier_stock/<supplier>**.
- Setelah memilih produk, Retail melakukan order kepada Supplier menggunakan **POST /api/submit_order**.
- Supplier memproses pesanan dan mengirimkan informasi terkait harga pengiriman dari Distributor ke Retail menggunakan **GET /api/get/distributor_price**.
- Retail akan mendapatkan detail pengiriman dan dapat melacak pengiriman melalui nomor resi menggunakan **POST /api/track/order**.
