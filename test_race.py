
import asyncio
import aiosqlite
import httpx

from database import DATABASE_NAME


BASE_URL = "http://127.0.0.1:8000"


async def test_race_condition():
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON")

        # Cari barang pertama yang tersedia
        cursor = await db.execute(
            "SELECT id, nama FROM alat_tulis ORDER BY id LIMIT 1"
        )
        barang = await cursor.fetchone()

        if barang is None:
            print("Tidak ada data alat tulis.")
            return

        alat_tulis_id = barang[0]
        nama_barang = barang[1]

        # Atur stok menjadi 1
        await db.execute(
            "UPDATE alat_tulis SET stok = 1 WHERE id = ?",
            (alat_tulis_id,)
        )
        await db.commit()

    print(f"Menguji barang: {nama_barang}")
    print(f"ID barang: {alat_tulis_id}")
    print("Stok awal: 1")

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=15
    ) as client:

        # Kirim dua transaksi secara bersamaan
        response1, response2 = await asyncio.gather(
            client.post(
                "/transactions/",
                json={
                    "alat_tulis_id": alat_tulis_id,
                    "jumlah": 1
                }
            ),
            client.post(
                "/transactions/",
                json={
                    "alat_tulis_id": alat_tulis_id,
                    "jumlah": 1
                }
            )
        )

        print("\nHASIL PERMINTAAN:")
        print("Transaksi 1:", response1.status_code, response1.json())
        print("Transaksi 2:", response2.status_code, response2.json())

        # Tunggu background task selesai
        await asyncio.sleep(2)

        # Periksa stok terakhir
        stok_response = await client.get(
            f"/alat-tulis/{alat_tulis_id}"
        )

        data_stok = stok_response.json()
        print("\nSTOK TERAKHIR:")
        print(data_stok)

        # Periksa daftar transaksi
        transaksi_response = await client.get("/transactions/")
        daftar_transaksi = transaksi_response.json()

        print("\nSTATUS TRANSAKSI:")

        for transaksi in daftar_transaksi:
            if transaksi["alat_tulis_id"] == alat_tulis_id:
                print(
                    f"ID: {transaksi['id']} | "
                    f"Jumlah: {transaksi['jumlah']} | "
                    f"Status: {transaksi['status']}"
                )

        # Validasi hasil pengujian
        if data_stok["stok"] == 0:
            print("\nBERHASIL: Stok tidak menjadi minus.")
        else:
            print("\nPERIKSA: Stok akhir tidak sesuai harapan.")


if __name__ == "__main__":
    asyncio.run(test_race_condition())
