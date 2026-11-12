
import aiosqlite

DATABASE_NAME = "toko_alat_tulis.db"


async def get_db():
    async with aiosqlite.connect(DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def init_db():
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS alat_tulis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                kategori TEXT NOT NULL,
                harga REAL NOT NULL CHECK (harga >= 0),
                stok INTEGER NOT NULL DEFAULT 0 CHECK (stok >= 0)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alat_tulis_id INTEGER NOT NULL,
                jumlah INTEGER NOT NULL CHECK (jumlah > 0),
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (alat_tulis_id) REFERENCES alat_tulis(id)
            )
        """)

        await db.commit()
