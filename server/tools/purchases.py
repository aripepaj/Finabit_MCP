from service.purchase_service import get_purchases_for_date, format_purchases_data

def get_purchases(from_date, to_date):
    """
    Tool interface: call the service with date range, return formatted results.
    """
    purchases = get_purchases_for_date(from_date, to_date)
    return format_purchases_data(purchases, from_date, to_date)
