# app/repositories/items_repository.py
import requests
from typing import Any, Dict
from app.core.config import settings
from requests.auth import HTTPBasicAuth
from app.repositories.user_repository import _get_creds  # stored creds

def fetch_items(page_number: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Calls GET {server_api_url}/Items/GetAllItems and returns:
    { items: [...], total_count: int, total_pages: int, current_page: int }
    """
    endpoint = f"{settings.server_api_url.rstrip('/')}/api/Items/GetAllItems"
    params = {"pageNumber": page_number, "pageSize": page_size}

    username, password = _get_creds()
    if not username or not password:
        raise RuntimeError("No saved credentials for Basic authentication.")

    try:
        resp = requests.get(
            endpoint,
            params=params,
            auth=HTTPBasicAuth(username, password),
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        
        return {
            "items": data.get("items", []),
            "total_count": data.get("total_count", len(data.get("items", []))),
            "total_pages": data.get("total_pages", 1),
            "current_page": data.get("current_page", page_number),
        }
    except Exception as e:
        print(f"Error fetching items from API: {e}")
        return {
            "items": [],
            "total_count": 0,
            "total_pages": 0,
            "current_page": page_number
        }