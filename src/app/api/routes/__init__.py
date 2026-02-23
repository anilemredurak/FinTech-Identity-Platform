from fastapi import APIRouter

router = APIRouter()

from . import health, auth  # noqa: F401
