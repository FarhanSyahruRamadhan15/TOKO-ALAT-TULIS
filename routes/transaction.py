
import asyncio

import aiosqlite
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from database import DATABASE_NAME, get_db
from models import TransactionCreate

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

stock_lock = asyncio.Lock()


async def process_transaction(transaction_id: int):
    async with stock_lock:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            db.row_factory = aiosqlite.Row

            cursor = await db.execute(
                "SELECT * FROM transactions WHERE id = ?",
                (transaction_id,)
            )
            transaction = await cursor.fetchone()

            if transaction is None:
                return

            if transaction["status"] != "pending":
                return

            await db.execute(
                "UPDATE transactions SET status = 'processing' WHERE id = ?",
                (transaction_id,)
            )
            await db.commit()

            await asyncio.sleep(0.1)

            cursor = await db.execute(
                "SELECT stok FROM alat_tulis WHERE id = ?",
                (transaction["alat_tulis_id"],)
            )
            alat_tulis = await cursor.fetchone()

            if alat_tulis is None:
                status = "failed"
            else:
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

                status = "completed" if cursor.rowcount == 1 else "failed"

            await db.execute(
                "UPDATE transactions SET status = ? WHERE id = ?",
                (status, transaction_id)
            )
            await db.commit()


@router.post("/", status_code=202)
async def create_transaction(
    data: TransactionCreate,
    background_tasks: BackgroundTasks,
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute(
        "SELECT id FROM alat_tulis WHERE id = ?",
        (data.alat_tulis_id,)
    )

    if await cursor.fetchone() is None:
        raise HTTPException(
            status_code=404,
            detail="Alat tulis tidak ditemukan"
        )

    cursor = await db.execute(
        """
        INSERT INTO transactions (alat_tulis_id, jumlah, status)
        VALUES (?, ?, 'pending')
        """,
        (data.alat_tulis_id, data.jumlah)
    )
    await db.commit()

    transaction_id = cursor.lastrowid

    background_tasks.add_task(
        process_transaction,
        transaction_id
    )

    return {
        "pesan": "Transaksi diterima dan sedang menunggu proses",
        "transaction_id": transaction_id,
        "status": "pending"
    }


@router.get("/")
async def get_transactions(
    status: str = None,
    db: aiosqlite.Connection = Depends(get_db)
):
    if status:
        cursor = await db.execute(
            "SELECT * FROM transactions WHERE status = ? ORDER BY id DESC",
            (status,)
        )
    else:
        cursor = await db.execute(
            "SELECT * FROM transactions ORDER BY id DESC"
        )

    data = await cursor.fetchall()
    return [dict(row) for row in data]


@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: int,
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute(
        "SELECT * FROM transactions WHERE id = ?",
        (transaction_id,)
    )
    data = await cursor.fetchone()

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Transaksi tidak ditemukan"
        )

    return dict(data)
