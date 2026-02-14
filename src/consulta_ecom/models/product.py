from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

class ProductSchema(BaseModel):
    title: str
    price: Optional[float] = None
    url: str
    image: Optional[str] = None
    source: str
    page: int
    created_at: datetime = Field(default_factory=datetime.now)