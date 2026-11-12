
import asyncio
import time
import statistics
import math
import httpx


BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/alat-tulis/"
TOTAL_REQUESTS = 100
CONCURRENCY = 10


async def benchmark():
    latencies = []
    success = 0
    failed = 0
    semaphore = asyncio.Semaphore(CONCURRENCY)

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=10
    ) as client:

        # Pemanasan awal, tidak dihitung dalam hasil
        for _ in range(5):
            await client.get(ENDPOINT)

        async def send_request():
            nonlocal success, failed

            async with semaphore:
                start = time.perf_counter()

                try:
                    response = await client.get(ENDPOINT)
                    elapsed = time.perf_counter() - start
                    latencies.append(elapsed * 1000)

                    if response.status_code == 200:
                        success += 1
                    else:
                        failed += 1

                except httpx.RequestError:
                    failed += 1

        start_all = time.perf_counter()

        await asyncio.gather(
            *[send_request() for _ in range(TOTAL_REQUESTS)]
        )

        total_time = time.perf_counter() - start_all

    print("\n===== HASIL BENCHMARK TOKO ALAT TULIS =====")
    print(f"Total Request       : {TOTAL_REQUESTS}")
    print(f"Concurrency         : {CONCURRENCY}")
    print(f"Berhasil            : {success}")
    print(f"Gagal               : {failed}")
    print(f"Total Waktu         : {total_time:.3f} detik")

    if latencies:
        sorted_latency = sorted(latencies)
        p95_index = math.ceil(0.95 * len(sorted_latency)) - 1

        print(
            f"Rata-rata Respons   : "
            f"{statistics.mean(latencies):.2f} ms"
        )
        print(
            f"Median Respons      : "
            f"{statistics.median(latencies):.2f} ms"
        )
        print(
            f"P95 Respons         : "
            f"{sorted_latency[p95_index]:.2f} ms"
        )
        print(
            f"Throughput          : "
            f"{success / total_time:.2f} request/detik"
        )


if __name__ == "__main__":
    asyncio.run(benchmark())
