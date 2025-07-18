import pyodbc

MSSQL_CONN_STR = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.199.30;DATABASE=FINA;UID=fina;PWD=Fina-10;TrustServerCertificate=yes;"

def get_sales_for_date(date):
    """Get shitjet (sales) for the given date."""
    return _get_transactions(date, transaction_type=2)

def get_purchases_for_date(date):
    """Get blerjet (purchases) for the given date."""
    return _get_transactions(date, transaction_type=1)

def _get_transactions(date, transaction_type):
    with pyodbc.connect(MSSQL_CONN_STR) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT InvoiceNo, Value, PartnerID, TransactionDate
            FROM dbo.tblTransactions
            WHERE TransactionTypeID = ? AND CAST(TransactionDate AS DATE) = ?
            """,
            transaction_type, date
        )
        return cursor.fetchall()
