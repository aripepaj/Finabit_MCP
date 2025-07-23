from service.sales_service import get_sales_for_date, format_sales_data

def get_sales(from_date, to_date):
    """
    Tool interface: call the service with date range, return formatted results.
    """
    sales = get_sales_for_date(from_date, to_date)
    return format_sales_data(sales, from_date, to_date)
