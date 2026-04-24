import pandas as pd
import re
from datetime import datetime

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================

def _clean_price(val):
    if pd.isna(val):
        return None
    val = str(val).strip()
    if val in ('N/A', 'NULL', 'Liên hệ', ''):
        return None
    val = val.replace('$', '').replace(',', '').strip()
    # Reject text prices like "five dollars"
    if re.search(r'[a-zA-Z]', val):
        return None
    try:
        price = float(val)
        return None if price < 0 else price
    except ValueError:
        return None


def _clean_date(val):
    if pd.isna(val):
        return None
    val = str(val).strip()
    # Remove ordinal suffixes: 1st, 2nd, 3rd, 4th...
    val = re.sub(r'(\d+)(st|nd|rd|th)\b', r'\1', val)
    formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%d-%m-%Y',
        '%B %d %Y',
        '%d %b %Y',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(val, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None


def process_sales_csv(file_path):
    # --- FILE READING (Handled for students) ---
    df = pd.read_csv(file_path)
    # ------------------------------------------

    # Remove duplicate rows based on 'id', keep first occurrence
    df = df.drop_duplicates(subset='id', keep='first')

    # Clean price column
    df['price'] = df['price'].apply(_clean_price)

    # Normalize date to YYYY-MM-DD
    df['date_of_sale'] = df['date_of_sale'].apply(_clean_date)

    results = []
    for _, row in df.iterrows():
        price = None if pd.isna(row['price']) else row['price']
        currency = str(row.get('currency', '')).strip()
        stock = row.get('stock_quantity')

        price_str = f"{price} {currency}" if price is not None else "price unknown"
        doc = {
            "document_id": f"csv-{int(row['id'])}",
            "content": (
                f"{row['product_name']} ({row['category']}). "
                f"Price: {price_str}. "
                f"Sold on: {row['date_of_sale']}."
            ),
            "source_type": "CSV",
            "author": str(row.get('seller_id', 'Unknown')),
            "timestamp": row['date_of_sale'],
            "source_metadata": {
                "product_name": str(row['product_name']),
                "category": str(row['category']),
                "price": price,
                "currency": currency,
                "seller_id": str(row.get('seller_id', '')),
                "stock_quantity": None if pd.isna(stock) else int(stock),
            },
        }
        results.append(doc)

    return results
