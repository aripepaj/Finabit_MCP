# app/services/purchases.py
from typing import List
from app.models.Purchases import Purchases
from app.repositories.purchases_repository import fetch_purchases

def get_purchases(
    from_date, 
    to_date, 
    transaction_type_id=2, 
    item_id=None, 
    item_name=None, 
    partner_name=None
) -> List[dict]:
    api_result = fetch_purchases(
        from_date, 
        to_date, 
        transaction_type_id, 
        item_id=item_id, 
        item_name=item_name, 
        partner_name=partner_name
    )

    # API returns a list, not a paginated dict
    raw_list = api_result if isinstance(api_result, list) else api_result.get("items", [])

    purchases = [Purchases.model_validate(p).model_dump() for p in raw_list]
    return purchases
