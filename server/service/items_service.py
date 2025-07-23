import requests
from tools.config import API_BASE_URL

class ItemLookup:
    """Represents an item from the GetAllItems API with pagination"""
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
        self.Prodhuesi = data.get('Prodhuesi')  # Producer
        self.Barcode = data.get('Barcode')
        self.Active = data.get('Active')
        self.IsService = data.get('IsService')
        self.Color = data.get('Color')
        self.Weight = data.get('Weight')

def get_items(page_number=1, page_size=20):
    """
    Fetch items from the GetAllItems API with pagination.
    """
    params = {
        "pageNumber": page_number,
        "pageSize": page_size
    }
    try:
        resp = requests.get(f"{API_BASE_URL}Items/GetAllItems", params=params, timeout=10)
        resp.raise_for_status()
        response_data = resp.json()
        
        # Extract pagination info and items
        total_count = response_data.get('TotalCount', 0)
        total_pages = response_data.get('TotalPages', 0)
        items_data = response_data.get('Items', [])
        
        # Convert raw API data to ItemLookup objects
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

def format_items_data(result):
    """
    Format items data for display
    """
    items = result.get('items', [])
    total_count = result.get('total_count', 0)
    total_pages = result.get('total_pages', 0)
    current_page = result.get('current_page', 1)
    page_size = result.get('page_size', 20)
    
    if not items:
        return "No items found in the inventory."
    
    reply = f"**Items Inventory** (Page {current_page} of {total_pages})\n"
    reply += f"Showing {len(items)} of {total_count} total items:\n\n"
    
    for i, item in enumerate(items, 1):
        reply += f"**Item {i}:**\n"
        reply += f"- ID: {item.ItemID}\n"
        reply += f"- Name: {item.ItemName}\n"
        reply += f"- Quantity: {item.Quantity} {item.UnitName or item.UnitDescription or ''}\n"
        reply += f"- Sales Price: {item.SalesPrice}\n"
        reply += f"- Cost Price: {item.CostPrice}\n"
        reply += f"- Location: {item.LocationName}\n"
        reply += f"- Group: {item.ItemGroup}\n"
        reply += f"- Producer: {item.Prodhuesi}\n"
        if item.Barcode:
            reply += f"- Barcode: {item.Barcode}\n"
        if item.Color:
            reply += f"- Color: {item.Color}\n"
        if item.Weight:
            reply += f"- Weight: {item.Weight}\n"
        reply += f"- Active: {'Yes' if item.Active else 'No'}\n"
        reply += f"- Service: {'Yes' if item.IsService else 'No'}\n"
        reply += "\n"
    
    if total_pages > 1:
        reply += f"\n*Use page_number parameter to view other pages (1-{total_pages})*"
    
    return reply
