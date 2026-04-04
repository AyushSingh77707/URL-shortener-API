from fastapi import FastAPI
from fastapi_cache import FastAPICache
from redis import asyncio as aioredis
from fastapi_cache.backends.redis import RedisBackend

app=FastAPI(title="URL Shortener API",description="URL Shortener SaaS API",version="1.0.0")

@app.on_event("startup")
async def startup():
    redis=aioredis.from_url("redis://localhost:6379")
    FastAPICache.init(RedisBackend(redis),prefix="cache")

@app.get("/")
def health_check():
    return{"message":"api is running !"}