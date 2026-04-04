from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import verify_pwd,verify_token,create_access_token,hash_pwd
from app.models.users import User

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    payload=verify_token(token)
    if not payload:
        raise HTTPException(status_code=401,detail="invalid token")
    user=db.query(User).filter(User.id==int(payload.get("sub"))).first()
    if not user:
        raise HTTPException(status_code=404,detail="user not found!")
    return user
