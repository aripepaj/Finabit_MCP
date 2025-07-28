from app.repositories.items_service import get_items as get_items_data
from app.services.formatters import format_items_data

def get_items(page_number=1, page_size=20):
    result = get_items_data(page_number, page_size)
    return format_items_data(result)