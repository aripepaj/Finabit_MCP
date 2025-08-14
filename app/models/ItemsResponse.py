# app/models/items_response.py
from typing import List
from pydantic import BaseModel, ConfigDict
from app.models.Item import Item

class ItemsResponse(BaseModel):
    items: List[Item]
    total_count: int
    total_pages: int
    current_page: int

    model_config = ConfigDict(extra="ignore")