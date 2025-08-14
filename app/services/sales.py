# app/services/sales.py
from typing import List, Any
from app.models.Sales import Sales
from app.repositories.sales_repository import fetch_sales

def get_sales(
    from_date,
    to_date,
    transaction_type_id=2,
    item_id=None,
    item_name=None,
    partner_name=None
) -> List[dict]:
    api_result = fetch_sales(
        from_date,
        to_date,
        transaction_type_id,
        item_id=item_id,
        item_name=item_name,
        partner_name=partner_name
    )

    raw_list = api_result if isinstance(api_result, list) else api_result.get("items", [])

    sales = [Sales.model_validate(s).model_dump() for s in raw_list]
    return sales
