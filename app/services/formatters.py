def format_sales_data(sales, from_date, to_date):
    if not sales:
        return f"No sales found between {from_date} and {to_date}."

    reply = f"Found {len(sales)} sale(s) for the period {from_date} to {to_date}:\n\n"
    for i, sale in enumerate(sales, 1):
        reply += (
            f"**Sale {i}:**\n"
            f"- ID: {sale.get('ID', '')}\n"
            f"- Invoice No: {sale.get('Numri', '')}\n"
            f"- Date: {sale.get('Data', '')}\n"
            f"- Customer ID: {sale.get('ID_Konsumatorit', '')}\n"
            f"- Customer: {sale.get('Konsumatori', '')}\n"
            f"- Salesman: {sale.get('Komercialisti', '')}\n"
            f"- Status: {sale.get('Statusi_Faturimit', '')}\n"
            f"- Code: {sale.get('Shifra', '')}\n"
            f"- Product: {sale.get('Emertimi', '')}\n"
            f"- Unit: {sale.get('Njesia_Artik', '')}\n"
            f"- Quantity: {sale.get('Sasia', '')}\n"
            f"- Unit Price: {sale.get('Cmimi', '')}\n"
        )
        if 'Value' in sale:
            reply += f"- Total Value: {sale.get('Value', '')}\n"
        reply += "\n"
    return reply

def format_purchases_data(purchases, from_date, to_date):
    if not purchases:
        return f"No purchases found between {from_date} and {to_date}."

    reply = f"Found {len(purchases)} purchase(s) for the period {from_date} to {to_date}:\n\n"
    for i, sale in enumerate(sales, 1):
        reply += (
            f"**Sale {i}:**\n"
            f"- ID: {sale.get('ID', '')}\n"
            f"- Invoice No: {sale.get('Numri', '')}\n"
            f"- Date: {sale.get('Data', '')}\n"
            f"- Customer ID: {sale.get('ID_Konsumatorit', '')}\n"
            f"- Customer: {sale.get('Konsumatori', '')}\n"
            f"- Salesman: {sale.get('Komercialisti', '')}\n"
            f"- Status: {sale.get('Statusi_Faturimit', '')}\n"
            f"- Code: {sale.get('Shifra', '')}\n"
            f"- Product: {sale.get('Emertimi', '')}\n"
            f"- Unit: {sale.get('Njesia_Artik', '')}\n"
            f"- Quantity: {sale.get('Sasia', '')}\n"
            f"- Unit Price: {sale.get('Cmimi', '')}\n"
        )
        if 'Value' in sale:
            reply += f"- Total Value: {sale.get('Value', '')}\n"
        reply += "\n"
    return reply

def format_items_data(result):
    items = result.get('items', [])
    total_count = result.get('total_count', 0)
    total_pages = result.get('total_pages', 0)
    current_page = result.get('current_page', 1)

    if not items:
        return "No items found in the inventory."

    reply = f"**Items Inventory** (Page {current_page} of {total_pages})\n"
    reply += f"Showing {len(items)} of {total_count} total items:\n\n"

    for i, item in enumerate(items, 1):
        reply += (
            f"**Item {i}:**\n"
            f"- ID: {item.get('ID', '')}\n"
            f"- ItemID: {item.get('ItemID', '')}\n"
            f"- Name: {item.get('ItemName', '')}\n"
            f"- Unit Name: {item.get('UnitName', '')}\n"
            f"- Unit ID: {item.get('UnitID', '')}\n"
            f"- Item Group ID: {item.get('ItemGroupID', '')}\n"
            f"- Item Group: {item.get('ItemGroup', '')}\n"
            f"- Taxable: {item.get('Taxable', '')}\n"
            f"- Active: {item.get('Active', '')}\n"
            f"- Dogana: {item.get('Dogana', '')}\n"
            f"- Akciza: {item.get('Akciza', '')}\n"
            f"- Color: {item.get('Color', '')}\n"
            f"- PDA Item Name: {item.get('PDAItemName', '')}\n"
            f"- VAT Value: {item.get('VATValue', '')}\n"
            f"- Akciza Value: {item.get('AkcizaValue', '')}\n"
            f"- Maximum Quantity: {item.get('MaximumQuantity', '')}\n"
            f"- Coefficient: {item.get('Coefficient', '')}\n"
            f"- Barcode1: {item.get('barcode1', '')}\n"
            f"- Barcode2: {item.get('barcode2', '')}\n"
            f"- Sales Price2: {item.get('SalesPrice2', '')}\n"
            f"- Sales Price3: {item.get('SalesPrice3', '')}\n"
            f"- Origin: {item.get('Origin', '')}\n"
            f"- Category: {item.get('Category', '')}\n"
            f"- PLU: {item.get('PLU', '')}\n"
            f"- Item Template: {item.get('ItemTemplate', '')}\n"
            f"- Weight: {item.get('Weight', '')}\n"
            f"- Author: {item.get('Author', '')}\n"
            f"- Publisher: {item.get('Publisher', '')}\n"
            f"- Custom Field 1: {item.get('CustomField1', '')}\n"
            f"- Custom Field 2: {item.get('CustomField2', '')}\n"
            f"- Custom Field 3: {item.get('CustomField3', '')}\n"
            f"- Custom Field 4: {item.get('CustomField4', '')}\n"
            f"- Custom Field 5: {item.get('CustomField5', '')}\n"
            f"- Custom Field 6: {item.get('CustomField6', '')}\n"
            f"- Barcode3: {item.get('Barcode3', '')}\n"
            f"- Netto Brutto Weight: {item.get('NettoBruttoWeight', '')}\n"
            f"- Bruto Weight: {item.get('BrutoWeight', '')}\n"
            f"- Max Discount: {item.get('MaxDiscount', '')}\n"
            f"- Shifra Prodhuesit: {item.get('ShifraProdhuesit', '')}\n"
            f"- Prodhuesi: {item.get('Prodhuesi', '')}\n"
        )
        reply += "\n"
    
    if total_pages > 1:
        reply += f"\n*Use `page_number` to view other pages (1–{total_pages})*"

    return reply