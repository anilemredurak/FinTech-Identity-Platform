from datetime import datetime, timedelta
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RefreshToken, AuditLog
from app.security.jwt import create_access_token, make_refresh_token, hash_token
from app.core.config import settings


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_refresh_token(self, user_id: int) -> tuple[str, RefreshToken]:
        raw = make_refresh_token()
        token_hash = hash_token(raw)
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS)
        db_token = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.db.add(db_token)
        await self.db.commit()
        await self.db.refresh(db_token)
        return raw, db_token

    async def rotate_refresh_token(self, old_token_hash: str, user_id: int) -> tuple[str, RefreshToken] | None:
        # Revoke old token and issue new one atomically
        q = await self.db.execute(select(RefreshToken).where(RefreshToken.token_hash == old_token_hash, RefreshToken.revoked == False))
        token = q.scalars().first()
        if not token or token.user_id != user_id:
            return None
        token.revoked = True
        raw, new_db_token = await self.create_refresh_token(user_id)
        return raw, new_db_token

    async def revoke_refresh_token(self, token_hash: str):
        q = await self.db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
        token = q.scalars().first()
        if token:
            token.revoked = True
            await self.db.commit()

    async def prune_expired(self):
        # Delete expired tokens (optional housekeeping)
        await self.db.execute(delete(RefreshToken).where(RefreshToken.expires_at < datetime.utcnow()))
        await self.db.commit()

    async def audit(self, user_id: int | None, event: str, ip: str | None = None, ua: str | None = None):
        log = AuditLog(user_id=user_id, event=event, ip_address=ip, user_agent=ua)
        self.db.add(log)
        await self.db.commit()
