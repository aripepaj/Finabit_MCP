import pyodbc
from app.core.config import settings

def get_db_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={settings.db_server};"
        f"DATABASE={settings.db_name};"
        f"UID={settings.db_user};"
        f"PWD={settings.db_password};"
        "TrustServerCertificate=Yes;"
    )
    return pyodbc.connect(conn_str)