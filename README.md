# URL Shortener API

A production-oriented **URL shortening SaaS backend** built with FastAPI. Users can register, sign in with email/password or Google, create short links (including custom aliases and expiry), and inspect click analytics.

This project is structured like a real backend service: layered modules, JWT auth with token revocation, Redis caching, Postgres persistence, Alembic migrations, rate limiting, and Docker Compose for local deployment.

---

![FastAPI](https://img.shields.io/badge/FastAPI-0.141-green)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)

## Features

| Area | What it does |
| --- | --- |
| URL shortening | Create short codes via Base62 encoding of the row ID |
| Custom aliases | Optional vanity codes with reserved-word checks |
| Redirects | Resolve a short code and send a 302 redirect |
| Caching | Redis lookup on the hot redirect path (`SETEX` + cache invalidation on delete) |
| Analytics | Click count plus recent click records (IP, timestamp) |
| Link expiry | Optional `expires_at`; expired links return HTTP 410 |
| Soft delete | Deactivate a link and drop it from Redis |
| Auth | Register / login with bcrypt passwords |
| JWT | Short-lived access tokens + refresh tokens (`jti`, `type`, `exp`) |
| Logout | Redis token blacklist until JWT expiry |
| OAuth 2.0 | Google login via Authlib + OpenID Connect discovery |
| PKCE | S256 code challenge/verifier stored in the session |
| Rate limiting | Per-route SlowAPI limits keyed by client IP |
| CORS | Configured for local frontends (`localhost:5173`, `localhost:3000`) |
| Docker | App + PostgreSQL 16 + Redis 7, migrations on startup |

---

## Tech stack

- **API:** FastAPI, Uvicorn, Starlette (sessions, CORS)
- **Validation:** Pydantic v2 (`EmailStr`, `AnyHttpUrl`, response models)
- **ORM:** SQLAlchemy 2.x (`Mapped`, `mapped_column`, relationships)
- **Database:** PostgreSQL (psycopg)
- **Migrations:** Alembic
- **Cache / sessions:** Redis
- **Auth:** python-jose (JWT), Passlib + bcrypt, OAuth2PasswordBearer
- **OAuth:** Authlib (Google OIDC)
- **Rate limiting:** SlowAPI (fixed-window)
- **Config:** pydantic-settings + `.env`
- **Containers:** Docker, Docker Compose

---

## Skills demonstrated

This section maps **what the code actually does** to backend skills you can talk about in interviews or on a resume.

### REST API design (FastAPI)

- Versioned URL routes under `/api/v1/urls`
- Auth routes under `/auth` with OpenAPI tags
- Typed request/response models (`UserRegister`, `URLCreate`, `URLAnalytics`, etc.)
- Correct HTTP usage: 401/403/404/410, `RedirectResponse`, bearer auth headers
- Dependency injection (`Depends`) for DB sessions and the current user

### Authentication & authorization

- Email/password registration with **bcrypt** hashing (`passlib`)
- Login issues **access + refresh JWTs**
- Tokens include `sub`, `exp`, unique `jti`, and `type` (`access` vs `refresh`)
- Refresh flow **rotates** the refresh token (old `jti` is blacklisted)
- Logout blacklists both access and refresh tokens
- Protected URL endpoints require a valid, non-blacklisted access token
- OAuth users can have a **nullable password** (Google-only accounts)

### OAuth 2.0 / OpenID Connect

- Google registered through Authlib using `.well-known/openid-configuration`
- Scopes: `openid email profile`
- Starlette **session middleware** holds the PKCE verifier across redirect
- Callback exchanges the code, reads `userinfo`, and upserts the user

### PKCE (OAuth security)

- Cryptographically random `code_verifier` (`secrets.token_urlsafe`)
- SHA-256 digest, Base64URL-encoded `code_challenge` (S256)
- Challenge sent on authorize; verifier sent on token exchange

### Security practices

- Secrets and DB URLs loaded from environment variables, not hardcoded
- `.env` excluded from git
- JWT type checks so a refresh token cannot be used as an access token
- Redis blacklist keyed by `jti` with TTL matching remaining token lifetime
- Rate limits on register, login, shorten, redirect, list, delete, and analytics
- Reserved aliases (`admin`, `login`, `register`, …) to avoid path collisions
- CORS allowlist for local SPA origins

### Data modeling (SQLAlchemy 2)

- `User` 1—N `ShortURL` 1—N `URLClick`
- Typed mappings, timezone-aware timestamps, unique indexed `short_code`
- Foreign keys to `users.id` and `urls.short_code`
- Connection pool (`pool_size`, `max_overflow`, `pool_pre_ping`)
- FastAPI `yield` session pattern (`get_db`) so connections always close

### Database migrations (Alembic)

Schema evolved in versioned steps rather than ad-hoc SQL:

1. Users and URLs tables
2. Nullable password + OAuth-friendly user fields
3. `expires_at` on URLs
4. `clicks` table for analytics

`alembic/env.py` imports models so autogenerate sees current metadata. Compose runs `alembic upgrade head` before Uvicorn.

### Caching (Redis)

- Redirect path: `GET` from Redis first; on miss, query Postgres and `SETEX` for 1 hour
- Soft-delete: `DELETE` the short-code key so stale redirects cannot be served
- Token blacklist: `SET` with TTL derived from JWT `exp`

### Algorithms

- **Base62-style short codes** from the auto-increment ID (offset applied so codes are not tiny sequential strings)
- Optional **custom alias** instead of generated codes
- Idempotent shorten: same user + same original URL returns the existing row

### Rate limiting & abuse control

- Global default: 100 requests/minute per IP
- Stricter limits on sensitive routes (e.g. register `3/minute;5/day`, login `5/minute`)
- SlowAPI middleware + `RateLimitExceeded` handler
- Rate-limit headers enabled for clients

### Configuration & 12-factor style

- `pydantic-settings` `Settings` class: `DATABASE_URL`, `SECRET_KEY`, JWT timings, Google OAuth credentials
- Redis host via `REDIS_HOST` (defaults to localhost for non-Docker runs)

### Containerization & local ops

- Multi-stage-style slim **Python 3.12** image with Postgres client libs
- Compose services: API, Postgres 16 (volume + healthcheck), Redis 7
- App waits for a healthy database, migrates, then serves on port 8000

### API product features (SaaS-style)

- Per-user link ownership
- Custom aliases
- Link expiry (HTTP 410 Gone)
- Click tracking (`click_count` + `clicks` rows with IP)
- Analytics endpoint returning totals and recent clicks
- Soft deactivation instead of hard deletes

---

## Architecture

```
Client (SPA / curl)
        │
        ▼
FastAPI (Uvicorn)
  ├── Auth router     → JWT / Google OAuth / blacklist
  ├── URL router      → shorten, list, delete, analytics, redirect
  ├── PostgreSQL      → users, urls, clicks
  └── Redis           → redirect cache + token blacklist
```

**Hot path (redirect):** Redis → (miss) Postgres → cache write → increment clicks → 302.

**Auth path:** verify JWT type and `jti` → Redis blacklist check → load `User`.

---

## Project structure

```
url_shortener/
├── app/
│   ├── main.py                 # App factory, middleware, routers
│   ├── database.py             # Engine, session, DeclarativeBase
│   ├── auth/                   # Users, JWT login, Google OAuth
│   ├── urls/                   # Shorten, redirect, analytics
│   ├── core/                   # Config, security, OAuth, Redis, rate limit
│   └── services/               # Base62, PKCE, token blacklist
├── alembic/                    # Schema migrations
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## API reference

Base URL (local): `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

### Health

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/` | No | Health check |

### Authentication (`/auth`)

| Method | Path | Auth | Rate limit | Description |
| --- | --- | --- | --- | --- |
| POST | `/auth/register` | No | 3/min; 5/day | Create account |
| POST | `/auth/login` | No | 5/min | Email/password → JWT pair |
| POST | `/auth/refresh` | Refresh body | — | Rotate tokens |
| POST | `/auth/logout` | Bearer + refresh | — | Blacklist both tokens |
| GET | `/auth/google/login` | No | — | Start Google OAuth + PKCE |
| GET | `/auth/google/callback` | No | — | OAuth callback → JWT pair |

**Register body**

```json
{ "email": "you@example.com", "password": "your-password" }
```

**Login / token response**

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer"
}
```

### URLs (`/api/v1/urls`)

Protected routes expect:

```http
Authorization: Bearer <access_token>
```

| Method | Path | Auth | Rate limit | Description |
| --- | --- | --- | --- | --- |
| POST | `/api/v1/urls/shorten` | Yes | 10/min | Create short link |
| GET | `/api/v1/urls/` | Yes | 20/min | List the current user’s active links |
| GET | `/api/v1/urls/{short_code}` | No | 60/min | Redirect (cached) |
| GET | `/api/v1/urls/{short_code}/analytics` | Yes | 10/min | Clicks + recent events |
| DELETE | `/api/v1/urls/{short_code}` | Yes | 5/min | Soft-delete + cache drop |

**Shorten body**

```json
{
  "original_url": "https://example.com/very/long/path",
  "custom_alias": "docs",
  "expires_at": null
}
```

`custom_alias` and `expires_at` are optional. If the same user already shortened that URL, the existing row is returned.

---

## Getting started

### Prerequisites

- Docker and Docker Compose **or**
- Python 3.12, PostgreSQL 16, Redis 7

### Environment

Create a `.env` in the project root:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/postgres
SECRET_KEY=change-me-to-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=5
REFRESH_TOKEN_EXPIRE_DAYS=1
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_SECRET_KEY=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
REDIS_HOST=redis
```

For a local (non-Docker) run, point `DATABASE_URL` at `localhost` and set `REDIS_HOST=127.0.0.1`.

### Run with Docker

```bash
docker compose up --build
```

The API starts on [http://localhost:8000](http://localhost:8000). Compose waits for Postgres, runs `alembic upgrade head`, then starts Uvicorn.

### Run locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Example flow

```bash
# 1. Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"secret123"}'

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"secret123"}'

# 3. Shorten (use the access_token from step 2)
curl -X POST http://localhost:8000/api/v1/urls/shorten \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"original_url":"https://fastapi.tiangolo.com"}'

# 4. Open the short URL in a browser
# GET http://localhost:8000/api/v1/urls/<short_code>
```

---

## Summary

> Designed and built a FastAPI URL-shortening SaaS API with JWT (access/refresh, rotation, Redis blacklist), Google OAuth 2.0 + PKCE, PostgreSQL/SQLAlchemy 2 models, Alembic migrations, Redis-backed redirect cache, SlowAPI rate limiting, click analytics, and Docker Compose deployment.

---


