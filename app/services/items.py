# app/services/items.py
from typing import Any, Dict
from app.models.Item import Item
from app.repositories.items_repository import fetch_items

def get_items(page_number: int = 1, page_size: int = 20) -> Dict[str, Any]:
    api_result = fetch_items(page_number, page_size)

    items = [Item.model_validate(i).model_dump() for i in api_result.get("items", [])]

    return {
        "items": items,
        "total_count": api_result.get("total_count", 0),
        "total_pages": api_result.get("total_pages", 0),
        "current_page": api_result.get("current_page", page_number),
    }
