from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine=create_engine(settings.DATABASE_URL)
SessionLocal=sessionmaker(bind=engine)
Base=declarative_base()

def get_db():
    session=SessionLocal()
    try:
        yield session
    finally:
        session.close()