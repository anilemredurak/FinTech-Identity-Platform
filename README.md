# FinTech Identity Platform (FastAPI)

Production-grade identity service demonstrating secure JWT (RS256) authentication, refresh token rotation, JWKS, Redis rate-limiting, audit logging, and clean architecture.

Highlights
- JWT access tokens signed with RS256
- Refresh tokens stored hashed in DB with rotation support
- JWKS endpoint for public keys
- Redis-based basic rate-limiting
- Async SQLAlchemy 2.0 with PostgreSQL
- Docker + docker-compose for local deployment
- Pytest test suite and GitHub Actions CI

Quick start

1. Copy .env.example to .env and fill values (or use default development values):

```bash
cp .env.example .env
# generate keys or use the provided dev keys under secrets/
docker compose up --build
```

Run tests locally:

```bash
pip install -r requirements.txt
pytest -q
```

Architecture overview and security notes are in the repository documentation.
