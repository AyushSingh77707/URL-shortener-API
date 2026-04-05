import random
import string
from sqlalchemy.orm import Session
from app.models.url import ShortURL

def generate_short_code(lenght:int=6)->str:
    character=string.ascii_letters+string.digits
    return ''.join(random.choices(character,k=lenght))

def create_unique_short_code(db:Session)->str:
    while True:
        code=generate_short_code()   

        existing=db.query(ShortURL).filter(ShortURL.short_code==code).first()
        if not existing:
            return code 





