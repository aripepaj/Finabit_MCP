from app.models.Item import Item
from app.repositories.items_repository import fetch_items

def get_items(page_number=1, page_size=20):
    item_dicts = fetch_items()
    items = [Item(**i).model_dump() for i in item_dicts]

    total_count = len(items)
    total_pages = (total_count + page_size - 1) // page_size
    start = (page_number - 1) * page_size
    end = start + page_size
    items_page = items[start:end]

    result = {
        "items": items_page,
        "total_count": total_count,
        "total_pages": total_pages,
        "current_page": page_number,
    }
    return result
