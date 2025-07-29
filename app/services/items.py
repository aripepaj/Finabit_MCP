from app.repositories.items_repository import fetch_items
from app.services.formatters import format_items_data

def get_items(page_number=1, page_size=20):
    items = fetch_items()
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
    return format_items_data(result)
