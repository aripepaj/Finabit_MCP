# app/tools/items_tool.py
from app.main_ref import mcp
from app.models.ItemsResponse import ItemsResponse
from app.services.items import get_items

@mcp.tool(
    name="get_items",
    description="Retrieve a paginated list of items plus pagination metadata (total_count, total_pages, current_page)."
)
def tool_get_items(page_number: int = 1, page_size: int = 20) -> ItemsResponse:
    data = get_items(page_number, page_size)
    return ItemsResponse.model_validate(data).model_dump()
