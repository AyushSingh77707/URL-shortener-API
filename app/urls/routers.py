from fastapi import APIRouter,HTTPException,Depends,Response,Request
from app.database import get_db
from app.core.dependencies import get_current_user
from sqlalchemy.orm import Session
from app.urls.schemas import URLCreate,URLResponse,URLAnalytics
from app.urls.model import ShortURL
from app.services.hash_url import base62_encoding
from fastapi.responses import RedirectResponse
from app.core.rate_limit import limiter



router=APIRouter(prefix="/api/v1/urls",tags=["URL"])

@router.post("/shorten",response_model=URLResponse)
@limiter.limit("2/minute")
def shorten_url(request:Request,response:Response,info:URLCreate,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    existing=db.query(ShortURL).filter(ShortURL.original_url==info.original_url).filter(ShortURL.user_id==current_user.id).first()

    if existing:
        return existing

    new_url=ShortURL(original_url=info.original_url,
                     short_code="x",
                     user_id=current_user.id)

    db.add(new_url)
    db.flush()

    new_url.short_code=base62_encoding(new_url.id)

    db.commit()
    db.refresh(new_url)
    return new_url
    
    
@router.get("/{short_code}")
def redirect_url(short_code:str,db:Session=Depends(get_db)):
    data=db.query(ShortURL).filter(ShortURL.short_code==short_code,ShortURL.is_active==True).first()
    if not data:
        raise HTTPException(status_code=404,detail="URL not found!")
    
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
    



