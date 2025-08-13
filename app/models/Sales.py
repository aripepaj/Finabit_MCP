# app/models/sales.py

from pydantic import BaseModel
from datetime import datetime

class Sales(BaseModel):
    ID: int | None = None
    Data: datetime | None = None
    Numri: str | None = None
    ID_Konsumatorit: int | None = None
    Konsumatori: str | None = None
    Komercialisti: str | None = None
    Statusi_Faturimit: str | None = None
    Shifra: str | None = None
    Emertimi: str | None = None
    Njesia_Artik: str | None = None
    Sasia: float | None = 0
    Cmimi: float | None = 0
    InvoiceNo: str | None = None
    Value: float | None = 0
    PartnerID: str | None = None
    TransactionDate: datetime | None = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
