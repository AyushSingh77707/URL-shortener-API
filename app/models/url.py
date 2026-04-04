from app.database import Base
from sqlalchemy import Column,Integer,String,Boolean,DateTime,func,ForeignKey
from sqlalchemy.orm import relationship

class URL(Base):
    __tablename__="urls"
    id=Column(Integer,primary_key=True,index=True)
    original_url=Column(String,nullable=False)
    short_code=Column(String,unique=True,nullable=False,index=True)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    is_active=Column(Boolean,default=True)
    click_count=Column(Integer,default=0)
    created_at=Column(DateTime(timezone=True),server_default=func.now())

    owner=relationship("User",back_populates="urls")