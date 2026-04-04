from fastapi import FastAPI
from fastapi_cache import FastAPICache
from redis import asyncio as aioredis
from fastapi_cache.backends.redis import RedisBackend
from app.models.url import ShortURL
from app.models.users import User
from app.routers import auth

app=FastAPI(title="URL Shortener API",description="URL Shortener SaaS API",version="1.0.0")

app.include_router(auth.router)

@app.on_event("startup")
async def startup():
    redis=aioredis.from_url("redis://localhost:6379")
    FastAPICache.init(RedisBackend(redis),prefix="cache")

@app.get("/")
def health_check():
    return{"message":"api is running !"}