from pydantic import BaseModel,Field,AnyHttpUrl
from typing import Annotated,Optional
from datetime import datetime

class URLCreate(BaseModel):
    original_url: AnyHttpUrl
    expires_at:Optional[str]=None
    custom_alias:Optional[str]=None

class URLResponse(BaseModel):
    id:int
    original_url:str
    short_code:str
    click_count:int
    is_active:bool
    created_at:datetime
    expires_at:datetime

    class Config:
        from_attributes:True

class ClickInfo(BaseModel):
    ip_address:Optional[str]
    country:Optional[str]
    clicked_at:datetime

    class Config:
        from_attributes:True

class URLAnalytics(BaseModel):
    original_url:str
    short_code:str
    created_at:datetime
    total_click:int
    is_active:bool
    recent_clicks:list[ClickInfo]

    class Config:
        from_attributes:True
