from pydantic import BaseModel,Field
from typing import Annotated
from datetime import datetime

class URLCreate(BaseModel):
    original_url:Annotated[str,Field(title="enter your original url here...")]

class URLResponse(BaseModel):
    id:int
    original_url:str
    short_code:str
    click_count:int
    is_active:bool
    created_at:datetime

    class Config:
        from_attributes:True

class URLAnalytics(BaseModel):
    total_click:int
    short_code:str
    original_url:str
    created_at:datetime