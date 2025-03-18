# data_handler.py
import json

def load_product_data():
    """
    Load product data from scraped_product_data.json.
    """
    try:
        with open("scraped_product_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_product_data(product_data):
    """
    Save product data to scraped_product_data.json.
    """
    output_file = "scraped_product_data.json"
    existing_data = load_product_data()

    product_exists = False
    for i, item in enumerate(existing_data):
        if item.get("Title") == product_data.get("Title"):
            existing_data[i] = product_data
            product_exists = True
            print(f"✅ Updated existing product: {product_data.get('Title')}")
            break

    if not product_exists:
        existing_data.append(product_data)
        print(f"✅ Added new product: {product_data.get('Title')}")

    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)