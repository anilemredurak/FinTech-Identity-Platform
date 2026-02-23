import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, health
from app.core.config import settings
from app.db.session import init_db

logger = logging.getLogger(__name__)

app = FastAPI(title="FinTech Identity Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])


@app.on_event("startup")
async def on_startup():
    # Initialize DB engine and create tables (simple auto-creation for demo).
    await init_db()
    logger.info("Application startup complete")


@app.get("/alive")
async def alive():
    return {"status": "alive"}
