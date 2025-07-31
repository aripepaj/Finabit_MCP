from app.services.sales import get_sales
from app.main_ref import mcp

@mcp.tool(name="get_sales", description="Get sales (shitjet) between two ISO dates")
def tool_get_sales(from_date: str, to_date: str):
    return get_sales(from_date, to_date)