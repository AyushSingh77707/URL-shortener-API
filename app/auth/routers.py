from app.database import get_db
from app.auth.schemas import UserRegister,UserLogin,UserResponse,TokenResponse
from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import HTTPException,Depends
from app.auth.models import User
from app.core.security import hash_pwd,verify_pwd,verify_token,create_access_token

from app.core.rate_limit import limiter
from fastapi import Request
from app.core.dependencies import oauth2_scheme
from app.core.security import verify_token
from app.services.token_blacklist import blacklist_token

router=APIRouter(prefix="/auth",tags=["Authentication"])

@router.post("/register",response_model=UserResponse)
@limiter.limit("1/minute")
def register(request:Request,info:UserRegister,db:Session=Depends(get_db)):
    existing_user=db.query(User).filter(User.email==info.email).first()
    if existing_user:
        raise HTTPException(status_code=401,detail="User already exists!")
    hashed=hash_pwd(info.password)
    new_user=User(email=info.email,password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login",response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request:Request,info:UserLogin,db:Session=Depends(get_db)):
    data=db.query(User).filter(User.email==info.email).first()
    if not data:
        raise HTTPException(status_code=404,detail="Email is not registered")
    token=create_access_token(data={
        "sub":str(data.id)
    })
    return{
        "access_token":token,
        "token_type":"bearer"
    }

@router.post("/logout")
def logout_user(token:str=Depends(oauth2_scheme)):
    payload=verify_token(token)
    if not payload:
        raise HTTPException(status_code=401,detail="Invalid Token")
    blacklist_token(payload)
    return {"message":"Logged out successfully"}
    