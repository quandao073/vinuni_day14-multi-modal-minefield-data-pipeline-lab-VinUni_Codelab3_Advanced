from bs4 import BeautifulSoup

# ==========================================
# ROLE 2 (assigned to Người 1): ETL — HTML
# ==========================================
# Task: Extract product data from the HTML table, ignoring boilerplate.

def parse_html_catalog(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    # ------------------------------------------

    # Find the main product table by id
    table = soup.find("table", id="main-catalog")
    if table is None:
        print("[HTML] Could not find table with id='main-catalog'")
        return []

    # Read header row to get column names
    headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]

    documents = []
    rows = table.find("tbody").find_all("tr")

    for idx, row in enumerate(rows, start=1):
        cells = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cells) != len(headers):
            print(f"[HTML] Skipping row {idx}: column count mismatch")
            continue

        # Map header → value for readability
        row_data = dict(zip(headers, cells))

        product_id   = row_data.get("Mã SP", f"SP-{idx:03d}")
        product_name = row_data.get("Tên sản phẩm", "")
        category     = row_data.get("Danh mục", "")
        raw_price    = row_data.get("Giá niêm yết", "")
        raw_stock    = row_data.get("Tồn kho", "0")
        rating       = row_data.get("Đánh giá", "")

        # --- Price cleaning ---
        price_value = _parse_price(raw_price)

        # --- Stock cleaning (reject negatives) ---
        try:
            stock = int(raw_stock)
        except (ValueError, TypeError):
            stock = 0

        # Build UnifiedDocument-compatible dict
        doc = {
            "document_id": f"html-{product_id}",
            "content": (
                f"Product: {product_name} | Category: {category} | "
                f"Price: {price_value} | Stock: {stock} | Rating: {rating}"
            ),
            "source_type": "HTML",
            "author": "VinShop",
            "timestamp": None,
            "source_metadata": {
                "original_file": "product_catalog.html",
                "product_id": product_id,
                "product_name": product_name,
                "category": category,
                "price_raw": raw_price,
                "price_parsed": price_value,
                "stock": stock,
                "rating": rating,
            },
        }
        documents.append(doc)

    print(f"[HTML] Extracted {len(documents)} products from catalog.")
    return documents


def _parse_price(raw: str):
    """
    Parse Vietnamese-style price strings.
    Returns a float (VND) when possible, or None for 'N/A' / 'Liên hệ'.
    """
    if not raw:
        return None

    cleaned = raw.strip()

    # Prices like "N/A" or "Liên hệ" → unknown
    if cleaned.upper() == "N/A" or "liên hệ" in cleaned.lower():
        return None

    # Remove currency suffix like " VND"
    cleaned = cleaned.replace("VND", "").strip()

    # Remove thousand-separator commas: "28,500,000" → "28500000"
    cleaned = cleaned.replace(",", "")

    try:
        return float(cleaned)
    except ValueError:
        return None
