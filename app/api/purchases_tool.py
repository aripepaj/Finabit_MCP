from app.main_ref import mcp
from app.services.purchases import get_purchases

@mcp.tool(name="get_purchases", description="Get purchases between two ISO dates")
def tool_get_purchases(from_date: str, to_date: str):
    return get_purchases(from_date, to_date)