from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import verify_pwd,verify_token,create_access_token,hash_pwd
from app.auth.models import User
from app.services.token_blacklist import is_blacklisted

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    credential_exc=HTTPException(status_code=401,detail="Could not validate credentials",headers={"WWW-Authentication":"Bearer"})

    payload=verify_token(token)
    if not payload:
        raise HTTPException(status_code=401,detail="invalid token")

    user_id=payload.get("sub")
    jti=payload.get("jti")
    if not user_id or not jti:
        raise credential_exc
    if is_blacklisted(jti):
        raise credential_exc



    user=db.query(User).filter(User.id==int(payload.get("sub"))).first()
    if not user:
        raise credential_exc
    return user
