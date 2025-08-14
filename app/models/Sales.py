# app/models/Sales.py
from typing import Optional, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime

class Sales(BaseModel):
    ID: Optional[int] = Field(default=None, alias="id")
    Data: Optional[datetime] = Field(default=None, alias="data")
    Numri: Optional[str] = Field(default=None, alias="numri")
    ID_Konsumatorit: Optional[int] = Field(default=None, alias="id_Konsumatorit")
    Konsumatori: Optional[str] = Field(default=None, alias="konsumatori")
    Komercialisti: Optional[str] = Field(default=None, alias="komercialisti")
    Statusi_Faturimit: Optional[str] = Field(default=None, alias="statusi_Faturimit")
    Shifra: Optional[str] = Field(default=None, alias="shifra")
    Emertimi: Optional[str] = Field(default=None, alias="emertimi")
    Njesia_Artik: Optional[str] = Field(default=None, alias="njesia_Artik")
    Sasia: Optional[Union[float, str]] = Field(default=None, alias="sasia")
    Cmimi: Optional[Union[float, str]] = Field(default=None, alias="cmimi")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"
    )

    @field_validator("Sasia", "Cmimi", mode="before")
    def parse_numeric(cls, v):
        if v is None:
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None
