from app.main_ref import mcp
from app.services.items import get_items

@mcp.tool(name="get_items", description="Get paginated list of items")
def tool_get_items(page_number: int = 1, page_size: int = 20):
    return get_items(page_number, page_size)