from app.database import Base
from sqlalchemy import Column,Integer,String,Boolean,DateTime,func
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True)
    email=Column(String,nullable=False,unique=True)
    password=Column(String,nullable=False)
    is_active=Column(Boolean,default=True)
    created_at=Column(DateTime(timezone=True),server_default=func.now())

    urls=relationship("ShortURL",back_populates="owner")




