from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"])  # health check used by CI
async def health():
    return {"status": "ok"}
