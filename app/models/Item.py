from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

class Item(BaseModel):
    ItemID: Optional[str] = Field(default=None, alias="itemID")
    ItemName: Optional[str] = Field(default=None, alias="itemName")
    UnitName: Optional[str] = Field(default=None, alias="unitName")
    UnitID: Optional[int] = Field(default=None, alias="unitID")
    ItemGroupID: Optional[int] = Field(default=None, alias="itemGroupID")
    ItemGroup: Optional[str] = Field(default=None, alias="itemGroup")
    Taxable: Optional[bool] = Field(default=None, alias="taxable")
    Active: Optional[bool] = Field(default=None, alias="active")
    Dogana: Optional[bool] = Field(default=None, alias="dogana")
    Akciza: Optional[bool] = Field(default=None, alias="akciza")
    Color: Optional[str] = Field(default=None, alias="color")
    PDAItemName: Optional[str] = Field(default=None, alias="pdaItemName")
    VATValue: Optional[float] = Field(default=None, alias="vatValue")
    AkcizaValue: Optional[float] = Field(default=None, alias="akcizaValue")
    MaximumQuantity: Optional[float] = Field(default=None, alias="maximumQuantity")
    Coefficient: Optional[float] = Field(default=None, alias="coefficient")
    SalesPrice2: Optional[float] = Field(default=None, alias="salesPrice2")
    SalesPrice3: Optional[float] = Field(default=None, alias="salesPrice3")
    Origin: Optional[str] = Field(default=None, alias="origin")
    Category: Optional[str] = Field(default=None, alias="category")
    PLU: Optional[str] = Field(default=None, alias="plu")
    ItemTemplate: Optional[str] = Field(default=None, alias="itemTemplate")
    Weight: Optional[float] = Field(default=None, alias="weight")
    Author: Optional[str] = Field(default=None, alias="author")
    Publisher: Optional[str] = Field(default=None, alias="publisher")
    CustomField1: Optional[str] = Field(default=None, alias="customField1")
    CustomField2: Optional[str] = Field(default=None, alias="customField2")
    CustomField3: Optional[str] = Field(default=None, alias="customField3")
    CustomField4: Optional[str] = Field(default=None, alias="customField4")
    CustomField5: Optional[str] = Field(default=None, alias="customField5")
    CustomField6: Optional[str] = Field(default=None, alias="customField6")
    Barcode3: Optional[str] = Field(default=None, alias="barcode3")
    NettoBruttoWeight: Optional[float] = Field(default=None, alias="nettoBruttoWeight")
    BrutoWeight: Optional[float] = Field(default=None, alias="brutoWeight")
    MaxDiscount: Optional[float] = Field(default=None, alias="maxDiscount")
    ShifraProdhuesit: Optional[str] = Field(default=None, alias="shifraProdhuesit")
    Prodhuesi: Optional[str] = Field(default=None, alias="prodhuesi")
    Id: Optional[int] = Field(default=None, alias="id")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"
    )

    @field_validator(
        "VATValue", "AkcizaValue", "MaximumQuantity",
        "Coefficient", "SalesPrice2", "SalesPrice3",
        "Weight", "NettoBruttoWeight", "BrutoWeight",
        "MaxDiscount", mode="before"
    )
    def parse_optional_float(cls, v):
        if v is None:
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None
