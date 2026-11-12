
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
    description="REST API untuk pengelolaan alat tulis dan transaksi",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs"
)


@app.get("/", include_in_schema=False)
async def home():
    return {
        "pesan": "Selamat Datang di Toko Alat Tulis"
    }


app.include_router(resource_router)
app.include_router(transaction_router)
