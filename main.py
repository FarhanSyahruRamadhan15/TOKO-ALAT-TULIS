
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import init_db
from routes.resource import router as resource_router
from routes.transaction import router as transaction_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Toko Alat Tulis API",
    description=(
        "REST API untuk pengelolaan data alat tulis, "
        "stok barang, dan transaksi penjualan."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/", tags=["Home"])
async def home():
    return {
        "status": "success",
        "pesan": "Selamat Datang di Toko Alat Tulis API",
        "versi": "1.0.0",
        "dokumentasi": "/docs"
    }


app.include_router(resource_router)
app.include_router(transaction_router)
