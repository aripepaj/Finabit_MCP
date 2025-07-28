from app.repositories.purchase_service import get_purchases_for_date
from app.services.formatters import format_purchases_data  # assuming formatters.py exists

def get_purchases(from_date, to_date):
    purchases = get_purchases_for_date(from_date, to_date)
    return format_purchases_data(purchases, from_date, to_date)