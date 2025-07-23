import requests
from ..tools.config import API_BASE_URL

class Order:
    """Represents an order/sale from the API"""
    def __init__(self, data):
        self.ID = data.get('ID')
        self.Data = data.get('Data')
        self.Numri = data.get('Numri')  # Invoice number
        self.ID_Konsumatorit = data.get('ID_Konsumatorit')
        self.Konsumatori = data.get('Konsumatori')  # Customer
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

def get_sales_for_date(from_date, to_date):
    """
    Fetch sales data from the API for the given date range.
    """
    params = {"FromDate": from_date, "ToDate": to_date}
    try:
        # Use the correct API endpoint from your documentation
        resp = requests.get(f"{API_BASE_URL}Transactions/OrdersList", params=params, timeout=10)
        resp.raise_for_status()
        transactions = resp.json()
        
        # Convert raw API data to Order objects
        orders = [Order(transaction) for transaction in transactions]
        return orders
        
    except Exception as e:
        print(f"[get_sales_for_date] Error: {e}")
        return []

def format_sales_data(sales, from_date, to_date):
    """
    Format sales data for display
    """
    if not sales:
        return "No sales found for the specified date range."
    
    reply = f"Found {len(sales)} sale(s) for the period {from_date} to {to_date}:\n\n"
    for i, sale in enumerate(sales, 1):
        reply += f"**Sale {i}:**\n"
        reply += f"- Invoice No: {sale.Numri}\n"
        reply += f"- Date: {sale.Data}\n"
        reply += f"- Customer: {sale.Konsumatori}\n"
        reply += f"- Product: {sale.Emertimi}\n"
        reply += f"- Quantity: {sale.Sasia} {sale.Njesia_Artik}\n"
        reply += f"- Unit Price: {sale.Cmimi}\n"
        reply += f"- Total Value: {sale.Cmimi * sale.Sasia if sale.Cmimi and sale.Sasia else 0}\n"
        reply += f"- Status: {sale.Statusi_Faturimit}\n\n"
    
    return reply
