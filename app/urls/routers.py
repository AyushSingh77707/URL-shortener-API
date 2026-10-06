from fastapi import APIRouter,HTTPException,Depends,Response,Request
from app.database import get_db
from app.core.dependencies import get_current_user
from sqlalchemy.orm import Session
from app.urls.schemas import URLCreate,URLResponse,URLAnalytics
from app.urls.model import ShortURL
from app.services.hash_url import base62_encoding
from fastapi.responses import RedirectResponse
from app.core.rate_limit import limiter
from datetime import datetime,timezone



router=APIRouter(prefix="/api/v1/urls",tags=["URL"])

@router.post("/shorten",response_model=URLResponse)
@limiter.limit("2/minute")
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
def redirect_url(short_code:str,db:Session=Depends(get_db)):
    data=db.query(ShortURL).filter(ShortURL.short_code==short_code,ShortURL.is_active==True).first()
    if not data:
        raise HTTPException(status_code=404,detail="URL not found!")

    if data.expires_at and data.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410,detail="URL validity expired")
    
    data.click_count+=1
    db.commit()

    return RedirectResponse(url=data.original_url)
    
@router.get("/")
@limiter.limit("10/minute")
def get_all_url(request:Request,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return db.query(ShortURL).filter(ShortURL.user_id==current_user.id,ShortURL.is_active==True).all()


@router.delete("/{short_code}")
@limiter.limit("5/minute")
def del_url(request:Request,short_code:str,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    existing=db.query(ShortURL).filter(ShortURL.short_code==short_code).first()
    if not existing:
        raise HTTPException(status_code=404,detail="given short code does not exist!")
    existing.is_active=False
    db.commit()
    return {"message":"URL deleted successfully!"}


@router.get("/{short_code}/analytics",response_model=URLAnalytics)
@limiter.limit("5/minute")
def get_analytics(request:Request,short_code:str,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    url=db.query(ShortURL).filter(ShortURL.short_code==short_code).first()
    if not url:
        raise HTTPException(status_code=404,detail="url not found!")
    return{
        "total_click":url.click_count,
        "short_code":url.short_code,
        "original_url":url.original_url,
        "created_at":url.created_at

    }
    

    
    



