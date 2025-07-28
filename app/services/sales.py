from app.repositories.sales_service import get_sales_for_date
from app.services.formatters import format_sales_data 

def get_sales(from_date, to_date):
    sales = get_sales_for_date(from_date, to_date)
    return format_sales_data(sales, from_date, to_date)
