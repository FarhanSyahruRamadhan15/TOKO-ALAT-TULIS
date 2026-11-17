
import asyncio

import aiosqlite
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    status
)

from database import DATABASE_NAME, get_db
from models import TransactionCreate

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

# Menghindari pemrosesan bersamaan dalam satu proses aplikasi
stock_lock = asyncio.Lock()


# Memproses transaksi di background
async def process_transaction(transaction_id: int):
    async with stock_lock:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            try:
                db.row_factory = aiosqlite.Row

                # Memulai transaksi database
                await db.execute("BEGIN IMMEDIATE")

                # Mengambil data transaksi
                cursor = await db.execute(
                    "SELECT * FROM transactions WHERE id = ?",
                    (transaction_id,)
                )

                transaction = await cursor.fetchone()

                if transaction is None:
                    await db.rollback()
                    return

                if transaction["status"] != "pending":
                    await db.rollback()
                    return

                # Mengubah status menjadi processing
                await db.execute(
                    """
                    UPDATE transactions
                    SET status = 'processing'
                    WHERE id = ?
                    """,
                    (transaction_id,)
                )

                # Simulasi proses transaksi
                await asyncio.sleep(0.1)

                # Mengurangi stok jika stok mencukupi
                cursor = await db.execute(
                    """
                    UPDATE alat_tulis
                    SET stok = stok - ?
                    WHERE id = ? AND stok >= ?
                    """,
                    (
                        transaction["jumlah"],
                        transaction["alat_tulis_id"],
                        transaction["jumlah"]
                    )
                )

                # Menentukan status transaksi
                if cursor.rowcount == 1:
                    final_status = "completed"
                else:
                    final_status = "failed"

                # Memperbarui status akhir transaksi
                await db.execute(
                    """
                    UPDATE transactions
                    SET status = ?
                    WHERE id = ?
                    """,
                    (final_status, transaction_id)
                )

                await db.commit()

            except aiosqlite.Error:
                await db.rollback()
                raise

            except Exception:
                await db.rollback()
                raise


# POST: Membuat transaksi baru
@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def create_transaction(
    data: TransactionCreate,
    background_tasks: BackgroundTasks,
    db: aiosqlite.Connection = Depends(get_db)
):
    # Memastikan barang tersedia
    cursor = await db.execute(
        "SELECT id FROM alat_tulis WHERE id = ?",
        (data.alat_tulis_id,)
    )

    alat_tulis = await cursor.fetchone()

    if alat_tulis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alat tulis tidak ditemukan"
        )

    # Membuat transaksi dengan status pending
    try:
        cursor = await db.execute(
            """
            INSERT INTO transactions (
                alat_tulis_id,
                jumlah,
                status
            )
            VALUES (?, ?, 'pending')
            """,
            (data.alat_tulis_id, data.jumlah)
        )

        await db.commit()

        transaction_id = cursor.lastrowid

    except aiosqlite.Error:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal membuat transaksi"
        )

    # Menjalankan pemrosesan di background
    background_tasks.add_task(
        process_transaction,
        transaction_id
    )

    return {
        "pesan": "Transaksi berhasil diterima",
        "transaction_id": transaction_id,
        "status": "pending"
    }


# GET: Menampilkan semua transaksi
@router.get("/")
async def get_transactions(
    status_filter: str = Query(
        default=None,
        alias="status",
        pattern="^(pending|processing|completed|failed)$"
    ),
    db: aiosqlite.Connection = Depends(get_db)
):
    if status_filter:
        cursor = await db.execute(
            """
            SELECT * FROM transactions
            WHERE status = ?
            ORDER BY id DESC
            """,
            (status_filter,)
        )
    else:
        cursor = await db.execute(
            """
            SELECT * FROM transactions
            ORDER BY id DESC
            """
        )

    data = await cursor.fetchall()

    return [dict(row) for row in data]


# GET: Menampilkan transaksi berdasarkan ID
@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: int,
    db: aiosqlite.Connection = Depends(get_db)
):
    if transaction_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID transaksi harus lebih dari 0"
        )

    cursor = await db.execute(
        """
        SELECT * FROM transactions
        WHERE id = ?
        """,
        (transaction_id,)
    )

    data = await cursor.fetchone()

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaksi tidak ditemukan"
        )

    return dict(data)
