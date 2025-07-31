
from app.models.Sales import Sales
from app.repositories.sales_repository import fetch_sales

def get_sales(from_date, to_date):
    sales_dicts = fetch_sales(from_date, to_date, 2)
    sales = [Sales(**s).model_dump() for s in sales_dicts]
    return sales