
import asyncio
import aiosqlite

from database import DATABASE_NAME, init_db


async def seed_data():
    await init_db()

    data_alat_tulis = [
        ("Buku Tulis", "Buku", 5000, 100),
        ("Pulpen", "Alat Tulis", 3000, 100),
        ("Pensil 2B", "Alat Tulis", 2500, 100),
        ("Penghapus", "Alat Tulis", 2000, 100),
        ("Penggaris 30 cm", "Perlengkapan", 4000, 100),
        ("Spidol", "Alat Tulis", 7000, 100),
        ("Stabilo", "Alat Tulis", 6000, 100),
        ("Map Plastik", "Perlengkapan", 3500, 100),
        ("Kertas HVS", "Kertas", 45000, 100),
        ("Pensil Warna", "Alat Gambar", 15000, 100)
    ]

    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON")

        cursor = await db.execute(
            "SELECT COUNT(*) FROM alat_tulis"
        )
        jumlah_data = (await cursor.fetchone())[0]

        if jumlah_data == 0:
            await db.executemany(
                """
                INSERT INTO alat_tulis
                (nama, kategori, harga, stok)
                VALUES (?, ?, ?, ?)
                """,
                data_alat_tulis
            )

            await db.commit()
            print("Berhasil menambahkan 10 data alat tulis.")

        else:
            print("Data alat tulis sudah tersedia. Seed dilewati.")


if __name__ == "__main__":
    asyncio.run(seed_data())
