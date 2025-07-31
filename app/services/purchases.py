from app.models.Purchases import Purchases
from app.repositories.purchases_repository import fetch_purchases

def get_purchases(from_date, to_date):
    purchases_dicts = fetch_purchases(from_date, to_date, 1)
    purchases = [Purchases(**s).model_dump() for s in purchases_dicts]
    return purchases