from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.schemas.auth import RegisterIn, LoginIn, TokenResponse, RefreshIn
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.security.jwt import create_access_token, hash_token
from app.security.jwks import get_jwks
from app.core.config import settings
from app.db.models import User, RefreshToken

router = APIRouter()


@router.post("/register", status_code=201)
async def register(payload: RegisterIn, db: AsyncSession = Depends(get_db), request: Request = None):
    svc = UserService(db)
    q = await db.execute(select(User).where(User.email == payload.email))
    if q.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await svc.create_user(payload.email, payload.password)
    auth = AuthService(db)
    await auth.audit(user.id, "register", request.client.host if request else None)
    return {"id": user.id, "email": user.email}


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginIn, db: AsyncSession = Depends(get_db), request: Request = None):
    usersvc = UserService(db)
    user = await usersvc.authenticate(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_access_token(subject=str(user.id))
    auth = AuthService(db)
    raw_refresh, db_token = await auth.create_refresh_token(user.id)
    await auth.audit(user.id, "login", request.client.host if request else None)
    return TokenResponse(access_token=access, expires_in=settings.ACCESS_TOKEN_EXPIRE_SECONDS, refresh_token=raw_refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshIn, db: AsyncSession = Depends(get_db), request: Request = None):
    auth = AuthService(db)
    token_hash = hash_token(payload.refresh_token)
    q = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    token = q.scalars().first()
    if not token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user_id = token.user_id
    revoked = token.revoked
    expires_at = token.expires_at
    if revoked:
        raise HTTPException(status_code=401, detail="Revoked token")
    if expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Expired token")
    # Rotate
    result = await auth.rotate_refresh_token(token_hash, user_id)
    if not result:
        raise HTTPException(status_code=401, detail="Cannot rotate token")
    raw_new, new_db_token = result
    access = create_access_token(subject=str(user_id))
    await auth.audit(user_id, "refresh", request.client.host if request else None)
    return TokenResponse(access_token=access, expires_in=settings.ACCESS_TOKEN_EXPIRE_SECONDS, refresh_token=raw_new)


@router.post("/logout")
async def logout(payload: RefreshIn, db: AsyncSession = Depends(get_db), request: Request = None):
    auth = AuthService(db)
    await auth.revoke_refresh_token(hash_token(payload.refresh_token))
    await auth.audit(None, "logout", request.client.host if request else None)
    return {"ok": True}


@router.get("/.well-known/jwks.json")
async def jwks():
    return get_jwks()
