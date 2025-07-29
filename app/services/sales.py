from app.repositories.sales_repository import fetch_sales
from app.services.formatters import format_sales_data 

def get_sales(from_date, to_date):
    sales = fetch_sales(from_date, to_date, 2)
    return format_sales_data(sales, from_date, to_date)
