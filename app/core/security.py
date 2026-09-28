import uuid
from app.core.config import settings
from passlib.context import CryptContext
from jose import jwt,JWTError
from datetime import datetime,timezone,timedelta
from fastapi import HTTPException

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_pwd(password:str)->str:
    return pwd_context.hash(password)

def verify_pwd(plain:str,hashed:str)->bool:
    return pwd_context.verify(plain,hashed)


def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire,"jti":str(uuid.uuid4()),"type":"access"})
    return jwt.encode(to_encode,settings.SECRET_KEY,settings.ALGORITHM)

def create_refresh_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire,"jti":str(uuid.uuid4()),"type":"refresh"})
    return jwt.encode(to_encode,settings.SECRET_KEY,settings.ALGORITHM)

def verify_token(token:str,expected_type:str="access")->dict:
    try:
        payload=jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
    except JWTError as e:
        raise HTTPException(status_code=401,detail="invalid or expire token!")

    if payload.get("type")!=expected_type:
        raise HTTPException(status_code=401,detail="wrong token type")
    return payload




