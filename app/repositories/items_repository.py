from typing import List, Dict
from app.core.db import engine

def fetch_items() -> List[Dict]:
    items = []
    conn = engine.raw_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("EXEC spGetItemsAll_API")
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            item = dict(zip(columns, row))
            items.append(item)
        cursor.close()
    except Exception as ex:
        print(f"Error fetching all items: {ex}")
    finally:
        conn.close()
    return items
