from fastapi import APIRouter,HTTPException,Depends
from app.database import get_db
from app.core.dependencies import get_current_user
from sqlalchemy.orm import Session
from app.schemas.url import URLCreate,URLResponse,URLAnalytics
from app.services.url_services import create_unique_short_code
from app.models.url import ShortURL

router=APIRouter(prefix="/api/v1/urls",tags=["URL"])

@router.post("/",response_model=URLResponse)
def create_url(info:URLCreate,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    short_code=create_unique_short_code(db)

    new_url=ShortURL(original_url=info.original_url,
                     short_code=short_code,
                     user_id=current_user.id)
    
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    return new_url

@router.get("/")
def get_all_url(db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return db.query(ShortURL).filter(ShortURL.user_id==current_user.id,ShortURL.is_active==True).all()

@router.delete("/{short_code}")
def del_url(short_code:str,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    existing=db.query(ShortURL).filter(ShortURL.short_code==short_code).first()
    if not existing:
        raise HTTPException(status_code=404,detail="given short code does not exist!")
    existing.is_active=False
    db.commit()
    return {"message":"URL deleted successfully!"}

@router.get("/{short_code}/analytics",response_model=URLAnalytics)
def get_analytics(short_code:str,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    url=db.query(ShortURL).filter(ShortURL.short_code==short_code).first()
    if not url:
        raise HTTPException(status_code=404,detail="url not found!")
    return{
        "total_click":url.click_count,
        "short_code":url.short_code,
        "original_url":url.original_url,
        "created_at":url.created_at

    }


