from fastapi import FastAPI,HTTPException,Depends
from app.database import get_db
from fastapi_cache import FastAPICache
from redis import asyncio as aioredis
from fastapi_cache.backends.redis import RedisBackend
from sqlalchemy.orm import Session
from app.models.url import ShortURL
from app.models.users import User
from app.routers import auth,urls

from fastapi.responses import RedirectResponse



from app.core.rate_limit import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi import Request



app=FastAPI(title="URL Shortener API",description="URL Shortener SaaS API",version="1.0.0")

#Rate limiter add
app.state.limiter=limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)

app.include_router(auth.router)
app.include_router(urls.router)


@app.on_event("startup")
async def startup():
    redis=aioredis.from_url("redis://localhost:6379")
    FastAPICache.init(RedisBackend(redis),prefix="cache")


@app.get("/")
def health_check():
    return{"message":"URL Shortener api is running !"}

@app.get("/{short_code}")
def redirect_url(short_code:str,db:Session=Depends(get_db)):
    data=db.query(ShortURL).filter(ShortURL.short_code==short_code,ShortURL.is_active==True).first()
    if not data:
        raise HTTPException(status_code=404,detail="URL not found!")
    
    data.click_count+=1
    db.commit()

    return RedirectResponse(url=data.original_url)



