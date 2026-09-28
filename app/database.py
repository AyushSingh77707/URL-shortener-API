from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker


engine=create_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_timeout=30
)

class Base(DeclarativeBase):
    pass

Session=sessionmaker(bind=engine,autoflush=False,autocommit=False,expire_on_commit=False)

def get_db():
    db=Session()
    try:
        yield db
    finally:
        db.close()


