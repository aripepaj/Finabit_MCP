import requests
from datetime import datetime
from typing import List, Optional, Dict, Any
from config import server_api_url

def fetch_sales(
    from_date: str,
    to_date: str,
    transaction_type_id: int,
    item_id: Optional[str] = None,
    item_name: Optional[str] = None,
    partner_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Call the remote TransactionsList API endpoint
    
    Args:
        from_date: Start date in string format
        to_date: End date in string format
        transaction_type_id: Type of transaction
        item_id: Optional item ID filter
        item_name: Optional item name filter
        partner_name: Optional partner name filter
    
    Returns:
        List of transaction orders
    """
    
    endpoint = f"{server_api_url}/TransactionsList"
    
    params = {
        "FromDate": from_date,
        "ToDate": to_date,
        "TransactionTypeID": transaction_type_id
    }
    
    if item_id:
        params["ItemID"] = item_id
    if item_name:
        params["ItemName"] = item_name
    if partner_name:
        params["PartnerName"] = partner_name
    
    try:
        response = requests.get(endpoint, params=params, timeout=30)
        response.raise_for_status() 
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling TransactionsList API: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []