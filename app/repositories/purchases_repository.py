from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.db import SessionLocal

def fetch_purchases(from_date: str, to_date: str, tran_type_id: int):
    try:
        with SessionLocal() as session:
            result = session.execute(
                text("EXEC spTransactionsList_API :from_date, :to_date, :tran_type_id"),
                {"from_date": from_date, "to_date": to_date, "tran_type_id": tran_type_id}
            )
            columns = result.keys()
            sales = [dict(zip(columns, row)) for row in result.fetchall()]
            return sales
    except Exception as e:
        print("SQL ERROR:", e)
        raise