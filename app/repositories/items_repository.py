from typing import List, Dict
from app.core.db import get_db_connection

def fetch_items() -> List[Dict]:
    items = []
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC spGetItemsAll_API")
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            item = dict(zip(columns, row))
            items.append(item)
    except Exception as ex:
        print(f"Error fetching all items: {ex}")
    finally:
        cursor.close()
        conn.close()
    return items
