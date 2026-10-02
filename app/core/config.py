from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL:str
    SECRET_KEY:str
    ALGORITHM:str="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int=5
    REFRESH_TOKEN_EXPIRE_DAYS:int=1
    GOOGLE_CLIENT_ID:str
    GOOGLE_SECRET_KEY:str
    GOOGLE_REDIRECT_URI:str

    class Config():
        env_file=".env"

settings=Settings()
