# Toko Alat Tulis API

REST API untuk pengelolaan data alat tulis dan transaksi pembelian menggunakan FastAPI dan SQLite. API ini mendukung operasi CRUD, pemrosesan transaksi secara asynchronous, serta pengujian performa dan race condition.

## Teknologi

- Python 3.10+
- FastAPI
- SQLite
- aiosqlite
- Uvicorn
- Locust
- HTTPX

## Fitur

1. Menampilkan seluruh data alat tulis.
2. Menampilkan detail alat tulis berdasarkan ID.
3. Menambahkan data alat tulis.
4. Memperbarui data alat tulis.
5. Menghapus data alat tulis.
6. Membuat dan memantau transaksi pembelian.
7. Memproses transaksi menggunakan background task.
8. Mengamankan pengurangan stok menggunakan `asyncio.Lock` dan SQL stock guard.
9. Menguji race condition pada transaksi bersamaan.
10. Melakukan pengujian beban menggunakan Locust.

## Struktur Project

```text
TOKO_ALAT TULIS/
│
├── .venv/
├── routes/
│   ├── __init__.py
│   ├── resource.py
│   └── transaction.py
│
├── main.py
├── database.py
├── models.py
├── seed.py
├── test_race.py
├── locustfile.py
├── requirements.txt
├── README.md
├── .gitignore
└── toko_alat_tulis.db
```

## Arsitektur Sistem

Sistem menggunakan arsitektur REST API dengan FastAPI sebagai backend dan SQLite sebagai database.

Komponen utama:

1. **Client:** Mengirimkan permintaan melalui Swagger UI atau HTTP client.
2. **FastAPI:** Menerima dan mengelola permintaan API.
3. **Routes:** Mengatur endpoint alat tulis dan transaksi.
4. **Models:** Mengatur validasi data yang diterima.
5. **Database:** Mengelola koneksi dan operasi penyimpanan menggunakan aiosqlite.
6. **SQLite:** Menyimpan data alat tulis, stok, dan transaksi.

## Instalasi

### 1. Membuat Virtual Environment

```bash
python -m venv .venv
```

### 2. Mengaktifkan Virtual Environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Menginstal Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Menambahkan Data Awal

Jalankan perintah:

```bash
python seed.py
```

Program akan menambahkan 10 data alat tulis apabila tabel masih kosong.

## Menjalankan API

Aktifkan virtual environment, kemudian jalankan:

```bash
python -m uvicorn main:app --reload
```

Server berjalan pada:

```text
http://127.0.0.1:8000
```

Dokumentasi API dapat diakses melalui Swagger UI:

http://127.0.0.1:8000/docs

## Pengujian API (Black Box Testing)

Pengujian dilakukan melalui Swagger UI dengan menguji fungsi setiap endpoint.

| Metode | Fungsi | Tujuan |
|---|---|---|
| GET | Menampilkan seluruh alat tulis | Memastikan data berhasil ditampilkan |
| GET | Menampilkan detail alat tulis | Memastikan pencarian berdasarkan ID |
| POST | Menambahkan alat tulis | Memastikan data berhasil disimpan |
| PUT | Memperbarui alat tulis | Memastikan perubahan data berhasil |
| DELETE | Menghapus alat tulis | Memastikan data berhasil dihapus |
| POST | Membuat transaksi | Memastikan transaksi dapat dibuat |
| GET | Memantau transaksi | Memastikan status transaksi dapat dilihat |

Hasil pengujian dibandingkan dengan keluaran yang diharapkan untuk memastikan setiap fungsi berjalan dengan benar.

## Pengujian Race Condition

Pengujian dilakukan untuk mengetahui apakah sistem mampu menangani dua transaksi yang mengakses stok secara bersamaan.

Pastikan server FastAPI sedang berjalan, kemudian buka terminal kedua dan jalankan:

```bash
python test_race.py
```

Skenario pengujian:

- Menggunakan alat tulis dengan ID 1.
- Stok awal disiapkan sebanyak 1 unit.
- Dua transaksi dikirim secara bersamaan.
- Sistem diharapkan hanya menerima satu transaksi yang berhasil mengurangi stok.
- Stok tidak boleh menjadi negatif.

## Pengujian Load Testing

Pengujian beban dilakukan menggunakan Locust untuk mengetahui kemampuan API dalam menangani permintaan dari banyak pengguna secara bersamaan.

### 1. Menjalankan FastAPI (Terminal 1)

```powershell
cd "C:\UTS PAK NORMAN\TOKO_ALAT TULIS"
.\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload
```

### 2. Menjalankan Locust (Terminal 2)

Pastikan Terminal 1 tetap berjalan, kemudian buka terminal kedua:

```powershell
cd "C:\UTS PAK NORMAN\TOKO_ALAT TULIS"
.\.venv\Scripts\Activate.ps1
python -m locust -f locustfile.py --host http://127.0.0.1:8000
```

### 3. Membuka Dashboard Locust

Akses melalui browser:

http://localhost:8089

Masukkan konfigurasi pengujian:

- Number of users: 10
- Spawn rate: 2
- Host: http://127.0.0.1:8000

Kemudian klik **Start** untuk memulai pengujian.

### 4. Parameter Hasil Pengujian

Beberapa parameter yang diamati:

- **Request Count:** Jumlah permintaan yang dikirim.
- **Failure Count:** Jumlah permintaan yang gagal.
- **Average Response Time:** Rata-rata waktu respons API.
- **Requests per Second (RPS):** Jumlah permintaan yang diproses setiap detik.
- **95% Response Time:** Waktu respons yang mencakup 95% permintaan.

## Database

Database menggunakan SQLite dengan library aiosqlite.

Tabel utama terdiri dari:

- `alat_tulis`: Menyimpan data alat tulis, kategori, harga, dan stok.
- `transactions`: Menyimpan data transaksi pembelian dan status pemrosesannya.

## Alur Sistem

1. Client mengirimkan permintaan ke API.
2. FastAPI menerima permintaan melalui endpoint yang sesuai.
3. Routes memproses permintaan berdasarkan fungsi yang dipanggil.
4. Models melakukan validasi data.
5. Database mengelola operasi pembacaan atau perubahan data.
6. SQLite menyimpan atau mengembalikan data.
7. FastAPI mengirimkan respons kepada client.

Untuk transaksi, sistem juga menjalankan proses pemrosesan secara asynchronous dan melakukan pengamanan stok agar transaksi bersamaan tidak menyebabkan stok menjadi negatif.