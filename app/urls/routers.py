from fastapi import APIRouter,HTTPException,Depends,Response,Request
from app.database import get_db
from app.core.dependencies import get_current_user
from sqlalchemy.orm import Session
from app.urls.schemas import URLCreate,URLResponse,URLAnalytics
from app.urls.model import ShortURL,URLClick
from app.services.hash_url import base62_encoding
from fastapi.responses import RedirectResponse
from app.core.rate_limit import limiter
from datetime import datetime,timezone
from app.core.redis import redis_client
import json



router=APIRouter(prefix="/api/v1/urls",tags=["URL"])

@router.post("/shorten",response_model=URLResponse)
@limiter.limit("10/minute")
def shorten_url(request:Request,response:Response,info:URLCreate,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    existing=db.query(ShortURL).filter(ShortURL.original_url==str(info.original_url)).filter(ShortURL.user_id==current_user.id).first()

    if existing:
        return existing

    if info.custom_alias:

        RESERVED=["admin","login","register","shorten","docs"]
        if info.custom_alias in RESERVED:
            raise HTTPException(status_code=400,detail="alias is reserved")

        taken=db.query(ShortURL).filter(ShortURL.short_code==info.custom_alias).first()
        if taken:
            raise HTTPException(status_code=400,detail="This alias is not available")


    new_url=ShortURL(original_url=str(info.original_url),
                     short_code=info.custom_alias or "x",
                     user_id=current_user.id,
                     expires_at=info.expires_at)

    db.add(new_url)
    db.flush()


    if not info.custom_alias:
        new_url.short_code=base62_encoding(new_url.id)

    db.commit()
    db.refresh(new_url)
    return new_url

        
@router.get("/{short_code}")
@limiter.limit("60/minute")
def redirect_url(request:Request,short_code:str,db:Session=Depends(get_db)):
    cache_url=redis_client.get(short_code)
    if cache_url:
        return RedirectResponse(url=cache_url)
    
    data=db.query(ShortURL).filter(ShortURL.short_code==short_code,ShortURL.is_active==True).first()
    if not data:
        raise HTTPException(status_code=404,detail="URL not found!")

    if data.expires_at and data.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410,detail="URL validity expired")

    redis_client.setex(short_code,3600,data.original_url)
    newclick=URLClick(
        short_code=data.short_code,
        ip_address=request.client.host,
        country=None
    )
    db.add(newclick)
    data.click_count+=1
    db.commit()

    return RedirectResponse(url=data.original_url)
    
@router.get("/")
@limiter.limit("20/minute")
def get_all_url(request:Request,response:Response,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return db.query(ShortURL).filter(ShortURL.user_id==current_user.id,ShortURL.is_active==True).all()


@router.delete("/{short_code}")
@limiter.limit("5/minute")
def del_url(request:Request,response:Response,short_code:str,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    existing=db.query(ShortURL).filter(ShortURL.short_code==short_code).filter(ShortURL.user_id==current_user.id).first()
    if not existing:
        raise HTTPException(status_code=404,detail="given short code does not exist!")
    existing.is_active=False
    redis_client.delete(short_code)
    db.commit()
    return {"message":"URL deactivated successfully!"}


@router.get("/{short_code}/analytics",response_model=URLAnalytics)
@limiter.limit("10/minute")
def get_analytics(request:Request,response:Response,short_code:str,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    url=db.query(ShortURL).filter(ShortURL.short_code==short_code).first()
    if not url:
        raise HTTPException(status_code=404,detail="url not found")

    clicks=db.query(URLClick).filter(URLClick.short_code==short_code).order_by(URLClick.clicked_at.desc()).limit(5).all()
    return{
        "original_url":url.original_url,
        "short_code":url.short_code,
        "created_at":url.created_at,
        "total_click":url.click_count,
        "is_active":url.is_active,
        "recent_clicks":clicks
    }

    

    
    



