from service.items_service import get_items as get_items_data, format_items_data

def get_items(page_number=1, page_size=20):
    """
    Tool interface: get items with pagination and return formatted results.
    """
    result = get_items_data(page_number, page_size)
    return format_items_data(result)
