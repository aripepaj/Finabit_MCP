from app.models.Sales import Sales
from app.repositories.sales_repository import fetch_sales

def get_sales(
    from_date, 
    to_date, 
    transaction_type_id=2, 
    item_id=None, 
    item_name=None, 
    partner_name=None
):
    sales_dicts = fetch_sales(
        from_date, 
        to_date, 
        transaction_type_id, 
        item_id=item_id, 
        item_name=item_name, 
        partner_name=partner_name
    )
    sales = [Sales(**s).model_dump() for s in sales_dicts]
    return sales
