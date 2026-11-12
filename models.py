
from pydantic import BaseModel, Field


class AlatTulisCreate(BaseModel):
    nama: str = Field(..., min_length=1)
    kategori: str = Field(..., min_length=1)
    harga: float = Field(..., ge=0)
    stok: int = Field(..., ge=0)


class AlatTulisUpdate(BaseModel):
    nama: str = Field(..., min_length=1)
    kategori: str = Field(..., min_length=1)
    harga: float = Field(..., ge=0)
    stok: int = Field(..., ge=0)


class TransactionCreate(BaseModel):
    alat_tulis_id: int = Field(..., gt=0)
    jumlah: int = Field(..., gt=0)
