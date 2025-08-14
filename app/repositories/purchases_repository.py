import requests
from typing import List, Optional, Dict, Any
from app.core.config import settings
from requests.auth import HTTPBasicAuth
from app.repositories.user_repository import _get_creds 

def fetch_purchases(
    from_date: str,
    to_date: str,
    transaction_type_id: int,
    item_id: Optional[str] = None,
    item_name: Optional[str] = None,
    partner_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Call the remote PurchasesList API endpoint using Basic Auth creds from keyring.
    """
    endpoint = f"{settings.server_api_url}/api/Transactions/TransactionsList"

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

    username, password = _get_creds()
    if not username or not password:
        raise RuntimeError("No saved credentials for Basic authentication.")

    try:
        response = requests.get(
            endpoint,
            params=params,
            auth=HTTPBasicAuth(username, password),  
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling PurchasesList API: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []