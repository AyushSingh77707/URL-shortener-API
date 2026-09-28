from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import Optional

class UserRegister(BaseModel):
    email:EmailStr
    password:str

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class UserResponse(BaseModel):
    id:int
    email:EmailStr
    created_at: datetime

class RefreshToken(BaseModel):
    refresh_token:str

    class Config:
        from_attributes=True

class TokenResponse(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str="bearer"