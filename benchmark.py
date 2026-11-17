
import asyncio
import argparse
import statistics
import time

import httpx


async def send_request(client, url, semaphore):
    async with semaphore:
        start = time.perf_counter()

        try:
            response = await client.get(url)
            elapsed = (time.perf_counter() - start) * 1000

            return {
                "success": response.is_success,
                "status": response.status_code,
                "time": elapsed
            }

        except httpx.HTTPError as error:
            elapsed = (time.perf_counter() - start) * 1000

            return {
                "success": False,
                "status": str(error),
                "time": elapsed
            }


async def run_benchmark(url, total_requests, concurrency):
    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(timeout=10.0) as client:
        print("\nMemulai benchmark...")
        print(f"URL         : {url}")
        print(f"Total       : {total_requests}")
        print(f"Concurrency : {concurrency}\n")

        start = time.perf_counter()

        tasks = [
            send_request(client, url, semaphore)
            for _ in range(total_requests)
        ]

        results = await asyncio.gather(*tasks)

        duration = time.perf_counter() - start

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    response_times = sorted(r["time"] for r in results)

    average = statistics.mean(response_times)
    minimum = min(response_times)
    maximum = max(response_times)

    p95_index = max(0, int(len(response_times) * 0.95) - 1)
    p95 = response_times[p95_index]

    rps = total_requests / duration if duration > 0 else 0

    print("========== HASIL BENCHMARK ==========")
    print(f"Total Request       : {total_requests}")
    print(f"Request Berhasil    : {len(successful)}")
    print(f"Request Gagal       : {len(failed)}")
    print(f"Total Waktu         : {duration:.2f} detik")
    print(f"Rata-rata Response  : {average:.2f} ms")
    print(f"Response Tercepat   : {minimum:.2f} ms")
    print(f"Response Terlambat  : {maximum:.2f} ms")
    print(f"P95 Response Time   : {p95:.2f} ms")
    print(f"Requests per Second : {rps:.2f} RPS")
    print("=====================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Benchmark Toko Alat Tulis API"
    )

    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000/alat-tulis/",
        help="Endpoint API yang akan diuji"
    )

    parser.add_argument(
        "--requests",
        type=int,
        default=100,
        help="Jumlah request"
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Jumlah request bersamaan"
    )

    args = parser.parse_args()

    if args.requests < 1 or args.concurrency < 1:
        parser.error("Requests dan concurrency harus lebih dari 0")

    asyncio.run(
        run_benchmark(
            args.url,
            args.requests,
            args.concurrency
        )
    )