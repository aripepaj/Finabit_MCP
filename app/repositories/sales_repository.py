from typing import List, Dict
from app.core.db import get_db_connection

def fetch_sales(from_date: str, to_date: str, tran_type_id: int) -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        EXEC spTransactionsList_API ?, ?, ?
    """, (from_date, to_date, tran_type_id))
    columns = [column[0] for column in cursor.description]
    sales = []
    for row in cursor.fetchall():
        sales.append(dict(zip(columns, row)))
    cursor.close()
    conn.close()
    return sales
