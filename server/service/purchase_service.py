import requests
from ..tools.config import API_BASE_URL

class Purchase:
    """Represents a purchase from the API"""
    def __init__(self, data):
        self.ID = data.get('ID')
        self.Data = data.get('Data')
        self.Numri = data.get('Numri')  # Invoice number
        self.ID_Konsumatorit = data.get('ID_Konsumatorit')
        self.Konsumatori = data.get('Konsumatori')  # Supplier
        self.Komercialisti = data.get('Komercialisti')
        self.Statusi_Faturimit = data.get('Statusi_Faturimit')
        self.Shifra = data.get('Shifra')  # Product code
        self.Emertimi = data.get('Emertimi')  # Product name
        self.Njesia_Artik = data.get('Njesia_Artik')  # Unit
        self.Sasia = data.get('Sasia')  # Quantity
        self.Cmimi = data.get('Cmimi')  # Price
        
        # For backward compatibility with the formatting function
        self.InvoiceNo = self.Numri
        self.Value = self.Cmimi * self.Sasia if self.Cmimi and self.Sasia else 0
        self.PartnerID = self.Konsumatori
        self.TransactionDate = self.Data

def get_purchases_for_date(from_date, to_date):
    """
    Fetch purchase data from the API for the given date range.
    """
    params = {"FromDate": from_date, "ToDate": to_date}
    try:
        # For purchases, you might need a different endpoint
        # Adjust this URL based on your actual API for purchases
        resp = requests.get(f"{API_BASE_URL}Transactions/PurchasesList", params=params, timeout=10)
        resp.raise_for_status()
        transactions = resp.json()
        
        # Convert raw API data to Purchase objects
        purchases = [Purchase(transaction) for transaction in transactions]
        return purchases
        
    except Exception as e:
        print(f"[get_purchases_for_date] Error: {e}")
        return []

def format_purchases_data(purchases, from_date, to_date):
    """
    Format purchases data for display
    """
    if not purchases:
        return "No purchases found for the specified date range."
    
    reply = f"Found {len(purchases)} purchase(s) for the period {from_date} to {to_date}:\n\n"
    for i, purchase in enumerate(purchases, 1):
        reply += f"**Purchase {i}:**\n"
        reply += f"- Invoice No: {purchase.Numri}\n"
        reply += f"- Date: {purchase.Data}\n"
        reply += f"- Supplier: {purchase.Konsumatori}\n"
        reply += f"- Product: {purchase.Emertimi}\n"
        reply += f"- Quantity: {purchase.Sasia} {purchase.Njesia_Artik}\n"
        reply += f"- Unit Price: {purchase.Cmimi}\n"
        reply += f"- Total Value: {purchase.Cmimi * purchase.Sasia if purchase.Cmimi and purchase.Sasia else 0}\n"
        reply += f"- Status: {purchase.Statusi_Faturimit}\n\n"
    
    return reply
