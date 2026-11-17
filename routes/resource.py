
import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, Query, status

from database import get_db
from models import AlatTulisCreate, AlatTulisUpdate

router = APIRouter(
    prefix="/alat-tulis",
    tags=["Alat Tulis"]
)


# GET: Menampilkan semua alat tulis
@router.get("/")
async def get_all_alat_tulis(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute(
        """
        SELECT id, nama, kategori, harga, stok
        FROM alat_tulis
        ORDER BY id ASC
        LIMIT ? OFFSET ?
        """,
        (limit, skip)
    )

    data = await cursor.fetchall()

    return [dict(row) for row in data]


# GET: Menampilkan alat tulis berdasarkan ID
@router.get("/{alat_tulis_id}")
async def get_alat_tulis(
    alat_tulis_id: int,
    db: aiosqlite.Connection = Depends(get_db)
):
    if alat_tulis_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="ID alat tulis harus lebih dari 0"
        )

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


# POST: Menambahkan alat tulis
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_alat_tulis(
    data: AlatTulisCreate,
    db: aiosqlite.Connection = Depends(get_db)
):
    try:
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

    except aiosqlite.Error:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Gagal menambahkan alat tulis"
        )


# PUT: Memperbarui seluruh data alat tulis
@router.put("/{alat_tulis_id}")
async def update_alat_tulis(
    alat_tulis_id: int,
    data: AlatTulisUpdate,
    db: aiosqlite.Connection = Depends(get_db)
):
    if alat_tulis_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="ID alat tulis harus lebih dari 0"
        )

    try:
        cursor = await db.execute(
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

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Alat tulis tidak ditemukan"
            )

        await db.commit()

        return {
            "pesan": "Data alat tulis berhasil diperbarui"
        }

    except HTTPException:
        raise

    except aiosqlite.Error:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Gagal memperbarui data alat tulis"
        )


# DELETE: Menghapus alat tulis
@router.delete("/{alat_tulis_id}")
async def delete_alat_tulis(
    alat_tulis_id: int,
    db: aiosqlite.Connection = Depends(get_db)
):
    if alat_tulis_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="ID alat tulis harus lebih dari 0"
        )

    try:
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

        return {
            "pesan": "Alat tulis berhasil dihapus"
        }

    except HTTPException:
        raise

    except aiosqlite.Error:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Gagal menghapus alat tulis"
        )
