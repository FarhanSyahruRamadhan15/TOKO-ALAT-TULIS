
import asyncio
import aiosqlite
import httpx

from database import DATABASE_NAME


BASE_URL = "http://127.0.0.1:8000"


async def test_race_condition():
    # Atur stok alat tulis ID 1 menjadi 1
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute(
            "UPDATE alat_tulis SET stok = 1 WHERE id = 1"
        )
        await db.commit()

    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Kirim dua transaksi secara bersamaan
        response1, response2 = await asyncio.gather(
            client.post(
                "/transactions/",
                json={"alat_tulis_id": 1, "jumlah": 1}
            ),
            client.post(
                "/transactions/",
                json={"alat_tulis_id": 1, "jumlah": 1}
            )
        )

        print("Transaksi 1:", response1.json())
        print("Transaksi 2:", response2.json())

        # Tunggu background task selesai
        await asyncio.sleep(3)

        # Periksa stok terakhir
        stok_response = await client.get("/alat-tulis/1")
        print("Data stok terakhir:", stok_response.json())

        # Periksa status transaksi
        transaksi_response = await client.get("/transactions/")
        print("Daftar transaksi:", transaksi_response.json())


if __name__ == "__main__":
    asyncio.run(test_race_condition())
