from pydantic import BaseModel, field_validator

class Item(BaseModel):
    Id: int
    ItemID: str
    ItemName: str
    UnitName: str
    UnitID: int
    ItemGroupID: int
    ItemGroup: str
    Taxable: int
    Active: int
    Dogana: int
    Akciza: int
    Color: str
    PDAItemName: str
    VATValue: float
    AkcizaValue: float
    MaximumQuantity: float
    Coefficient: float
    barcode1: str
    barcode2: str
    SalesPrice2: float
    SalesPrice3: float
    Origin: str
    Category: str
    PLU: str
    ItemTemplate: str
    Weight: float
    Author: str
    Publisher: str
    CustomField1: str
    CustomField2: str
    CustomField3: str
    CustomField4: str
    CustomField5: str
    CustomField6: str
    Barcode3: str
    NettoBruttoWeight: float
    BrutoWeight: float
    MaxDiscount: float
    ShifraProdhuesit: str
    Prodhuesi: str

    @field_validator(
        'VATValue', 'AkcizaValue', 'MaximumQuantity', 'Coefficient', 
        'SalesPrice2', 'SalesPrice3', 'Weight', 'NettoBruttoWeight', 
        'BrutoWeight', 'MaxDiscount', mode='before'
    )
    def parse_floats(cls, v):
        if v in (None, ''):
            return 0.0
        return float(v)
