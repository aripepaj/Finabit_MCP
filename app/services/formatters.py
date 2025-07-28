def format_sales_data(sales, from_date, to_date):
    if not sales:
        return f"No sales found between {from_date} and {to_date}."
    
    reply = f"Found {len(sales)} sale(s) for the period {from_date} to {to_date}:\n\n"
    for i, sale in enumerate(sales, 1):
        reply += (
            f"**Sale {i}:**\n"
            f"- Invoice No: {sale.Numri}\n"
            f"- Date: {sale.Data}\n"
            f"- Customer: {sale.Konsumatori}\n"
            f"- Product: {sale.Emertimi}\n"
            f"- Quantity: {sale.Sasia} {sale.Njesia_Artik}\n"
            f"- Unit Price: {sale.Cmimi}\n"
            f"- Total Value: {sale.Value}\n"
            f"- Status: {sale.Statusi_Faturimit}\n\n"
        )
    return reply

def format_purchases_data(purchases, from_date, to_date):
    if not purchases:
        return f"No purchases found between {from_date} and {to_date}."

    reply = f"Found {len(purchases)} purchase(s) for the period {from_date} to {to_date}:\n\n"
    for i, p in enumerate(purchases, 1):
        reply += (
            f"**Purchase {i}:**\n"
            f"- Invoice No: {p.Numri}\n"
            f"- Date: {p.Data}\n"
            f"- Supplier: {p.Konsumatori}\n"
            f"- Product: {p.Emertimi}\n"
            f"- Quantity: {p.Sasia} {p.Njesia_Artik}\n"
            f"- Unit Price: {p.Cmimi}\n"
            f"- Total Value: {p.Value}\n"
            f"- Status: {p.Statusi_Faturimit}\n\n"
        )
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
            f"- ID: {item.ItemID}\n"
            f"- Name: {item.ItemName}\n"
            f"- Quantity: {item.Quantity} {item.UnitName or item.UnitDescription or ''}\n"
            f"- Sales Price: {item.SalesPrice}\n"
            f"- Cost Price: {item.CostPrice}\n"
            f"- Location: {item.LocationName}\n"
            f"- Group: {item.ItemGroup}\n"
            f"- Producer: {item.Prodhuesi}\n"
        )
        if item.Barcode:
            reply += f"- Barcode: {item.Barcode}\n"
        if item.Color:
            reply += f"- Color: {item.Color}\n"
        if item.Weight:
            reply += f"- Weight: {item.Weight}\n"

        reply += f"- Active: {'Yes' if item.Active else 'No'}\n"
        reply += f"- Service: {'Yes' if item.IsService else 'No'}\n\n"

    if total_pages > 1:
        reply += f"\n*Use `page_number` to view other pages (1–{total_pages})*"

    return reply