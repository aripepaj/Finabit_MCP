from app.main_ref import mcp
from app.repositories.purchases_repository import fetch_purchases

@mcp.tool(name="get_purchases", description="Get purchases between two ISO dates")
def tool_get_purchases(from_date: str, to_date: str):
    return fetch_purchases(from_date, to_date, 1)