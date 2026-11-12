
from fastapi import APIRouter, Depends, HTTPException
import aiosqlite

from database import get_db
from models import AlatTulisCreate, AlatTulisUpdate

router = APIRouter(
    prefix="/alat-tulis",
    tags=["Alat Tulis"]
)


@router.get("/")
async def get_all_alat_tulis(
    skip: int = 0,
    limit: int = 10,
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute(
        "SELECT * FROM alat_tulis LIMIT ? OFFSET ?",
        (limit, skip)
    )
    data = await cursor.fetchall()

    return [dict(row) for row in data]


@router.get("/{alat_tulis_id}")
async def get_alat_tulis(
    alat_tulis_id: int,
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute(
        "SELECT * FROM alat_tulis WHERE id = ?",
        (alat_tulis_id,)
    )
    data = await cursor.fetchone()

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Alat tulis tidak ditemukan"
        )

    return dict(data)


@router.post("/", status_code=201)
async def create_alat_tulis(
    data: AlatTulisCreate,
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute(
        """
        INSERT INTO alat_tulis (nama, kategori, harga, stok)
        VALUES (?, ?, ?, ?)
        """,
        (data.nama, data.kategori, data.harga, data.stok)
    )
    await db.commit()

    return {
        "pesan": "Alat tulis berhasil ditambahkan",
        "id": cursor.lastrowid
    }


@router.put("/{alat_tulis_id}")
async def update_alat_tulis(
    alat_tulis_id: int,
    data: AlatTulisUpdate,
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute(
        "SELECT id FROM alat_tulis WHERE id = ?",
        (alat_tulis_id,)
    )

    if await cursor.fetchone() is None:
        raise HTTPException(
            status_code=404,
            detail="Alat tulis tidak ditemukan"
        )

    await db.execute(
        """
        UPDATE alat_tulis
        SET nama = ?, kategori = ?, harga = ?, stok = ?
        WHERE id = ?
        """,
        (
            data.nama,
            data.kategori,
            data.harga,
            data.stok,
            alat_tulis_id
        )
    )
    await db.commit()

    return {"pesan": "Data alat tulis berhasil diperbarui"}


@router.delete("/{alat_tulis_id}")
async def delete_alat_tulis(
    alat_tulis_id: int,
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute(
        "DELETE FROM alat_tulis WHERE id = ?",
        (alat_tulis_id,)
    )

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Alat tulis tidak ditemukan"
        )

    await db.commit()

    return {"pesan": "Alat tulis berhasil dihapus"}
