from app.repositories.purchases_repository import fetch_purchases
from app.services.formatters import format_purchases_data  # assuming formatters.py exists

def get_purchases(from_date, to_date):
    purchases = fetch_purchases(from_date, to_date, 1)
    return format_purchases_data(purchases, from_date, to_date)