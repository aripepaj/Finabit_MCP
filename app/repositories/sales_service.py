import requests
from app.core.config import settings

API_BASE_URL = settings.API_BASE_URL

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
        
        self.InvoiceNo = self.Numri
        self.Value = self.Cmimi * self.Sasia if self.Cmimi and self.Sasia else 0
        self.PartnerID = self.Konsumatori
        self.TransactionDate = self.Data

def get_sales_for_date(from_date, to_date):
    params = {"FromDate": from_date, "ToDate": to_date, "TransactionTypeID": 2}
    try:
        resp = requests.get(f"{API_BASE_URL}Transactions/TransactionsList", params=params, timeout=10)
        resp.raise_for_status()
        transactions = resp.json()
        return [Order(t) for t in transactions]
    except Exception as e:
        print(f"[get_sales_for_date] Error: {e}")
        return []