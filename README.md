
# Toko Alat Tulis API

REST API untuk pengelolaan data alat tulis dan transaksi pembelian menggunakan FastAPI dan SQLite.

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
2. Menampilkan detail alat tulis.
3. Menambahkan data alat tulis.
4. Memperbarui data alat tulis.
5. Menghapus data alat tulis.
6. Membuat dan memantau transaksi.
7. Memproses transaksi menggunakan background task.
8. Mengamankan pengurangan stok dengan asyncio.Lock dan SQL stock guard.
9. Pengujian race condition.
10. Pengujian beban menggunakan Locust.

## Struktur Project

```text
TOKO_ALAT TULIS/
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
│
└── routes/
    ├── __init__.py
    ├── resource.py
    └── transaction.py
```

## Instalasi

Buat virtual environment:

```bash
python -m venv .venv
```

Aktifkan virtual environment pada Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instal library:

```bash
pip install -r requirements.txt
```

## Menambahkan Data Awal

Jalankan perintah:

```bash
python seed.py
```

Program akan menambahkan 10 data alat tulis jika tabel masih kosong.

## Menjalankan API

Jalankan server:

```bash
uvicorn main:app --reload
```

Buka dokumentasi API melalui browser:

```text
http://127.0.0.1:8000/docs
```

## Pengujian Race Condition

Pastikan server sedang berjalan, kemudian buka terminal lain dan jalankan:

```bash
python test_race.py
```

Pengujian mengirimkan dua transaksi secara bersamaan ketika stok alat tulis ID 1 hanya tersisa satu.

## Pengujian Load Testing

Pastikan server sedang berjalan, kemudian jalankan:

```bash
locust -f locustfile.py --host http://127.0.0.1:8000
```

Buka halaman Locust:

```text
http://localhost:8089
```

Masukkan jumlah pengguna dan jumlah pengguna yang bertambah setiap detik, kemudian mulai pengujian.

## Database

Database menggunakan SQLite dengan library aiosqlite. Tabel utama terdiri dari:

- `alat_tulis`: menyimpan data alat tulis dan stok.
- `transactions`: menyimpan data transaksi pembelian dan status pemrosesannya.
