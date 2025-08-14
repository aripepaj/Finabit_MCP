from app.main_ref import mcp
from app.services.purchases import get_purchases

@mcp.tool(
    name="get_purchases",
    description=(
        "Retrieve purchase (blerjet) records filtered by a date range, "
        "with optional filters for transaction type, item ID, item name, and partner name."
    )
)
def tool_get_purchases(
    from_date: str,
    to_date: str,
    transaction_type_id: int = 1,
    item_id: str = None,
    item_name: str = None,
    partner_name: str = None
):
    return get_purchases(
        from_date,
        to_date,
        transaction_type_id=transaction_type_id,
        item_id=item_id,
        item_name=item_name,
        partner_name=partner_name
    )
