import requests
from app.core.config import settings

API_BASE_URL = settings.API_BASE_URL

class ItemLookup:
    def __init__(self, data):
        self.ItemID = data.get('ItemID')
        self.ItemName = data.get('ItemName')
        self.Quantity = data.get('Quantity')
        self.SalesPrice = data.get('SalesPrice')
        self.CostPrice = data.get('CostPrice')
        self.UnitName = data.get('UnitName')
        self.UnitDescription = data.get('UnitDescription')
        self.LocationName = data.get('LocationName')
        self.ItemGroup = data.get('ItemGroup')
        self.Prodhuesi = data.get('Prodhuesi')
        self.Barcode = data.get('Barcode')
        self.Active = data.get('Active')
        self.IsService = data.get('IsService')
        self.Color = data.get('Color')
        self.Weight = data.get('Weight')

def get_items(page_number=1, page_size=20):
    params = {"pageNumber": page_number, "pageSize": page_size}
    try:
        resp = requests.get(f"{API_BASE_URL}Items/GetAllItems", params=params, timeout=10)
        resp.raise_for_status()
        response_data = resp.json()

        total_count = response_data.get('TotalCount', 0)
        total_pages = response_data.get('TotalPages', 0)
        items_data = response_data.get('Items', [])

        items = [ItemLookup(item_data) for item_data in items_data]

        return {
            'items': items,
            'total_count': total_count,
            'total_pages': total_pages,
            'current_page': page_number,
            'page_size': page_size
        }

    except Exception as e:
        print(f"[get_items] Error: {e}")
        return {
            'items': [],
            'total_count': 0,
            'total_pages': 0,
            'current_page': page_number,
            'page_size': page_size
        }
