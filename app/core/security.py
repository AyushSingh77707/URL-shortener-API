from app.core.config import settings
from passlib.context import CryptContext
from jose import jwt,JWTError
from datetime import datetime,timezone,timedelta
from fastapi import HTTPException

pwd_context=CryptContext(schemes="bcrypt",deprecated="auto")

def hash_pwd(password:str):
    return pwd_context.hash(password)

def verify_pwd(plain:str,hashed:str):
    return pwd_context.verify(plain,hashed)

def create_access_token(data:dict):
    to_encode=data.copy
    expire=datetime.now(timezone.utc)+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,settings.SECRET_KEY,settings.ALGORITHM)

def verify_token(token:str)->dict:
    try:
        payload=jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401,detail="invalid or expire token!")




