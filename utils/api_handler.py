# utils/api_handler.py
import requests

def fetch_all_products():
    """
    Fetches all products from DummyJSON API

    Returns: list of product dictionaries
    Format:
    [
        {
            'id': 1,
            'title': 'iPhone 9',
            'category': 'smartphones',
            'brand': 'Apple',
            'price': 549,
            'rating': 4.69
        },
        ...
    ]
    """
    url = "https://dummyjson.com/products?limit=100"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        products = data.get("products", [])
        result = []
        for p in products:
            result.append({
                "id": p.get("id"),
                "title": p.get("title"),
                "category": p.get("category"),
                "brand": p.get("brand"),
                "price": p.get("price"),
                "rating": p.get("rating")
            })
        print(f"✓ Successfully fetched {len(result)} products")
        return result
    except Exception as e:
        print(f"❌ Failed to fetch products: {e}")
        return []


def create_product_mapping(api_products):
    """
    Creates a mapping of product IDs to product info

    Parameters: api_products from fetch_all_products()

    Returns: dictionary mapping product IDs to info
    Format:
    {
        1: {'title': 'iPhone 9', 'category': 'smartphones', 'brand': 'Apple', 'rating': 4.69},
        ...
    }
    """
    mapping = {}
    for p in api_products:
        mapping[int(p["id"])] = {
            "title": p.get("title"),
            "category": p.get("category"),
            "brand": p.get("brand"),
            "rating": p.get("rating")
        }
    return mapping


def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transaction data with API product information

    Parameters:
    - transactions: list of transaction dictionaries
    - product_mapping: dictionary from create_product_mapping()

    Returns: list of enriched transaction dictionaries
    Also saves enriched data to 'data/enriched_sales_data.txt'
    """
    enriched = []
    for t in transactions:
        try:
            # Extract numeric ID from ProductID (e.g., P101 -> 101)
            numeric_id = int(t["ProductID"])
            product_info = product_mapping.get(numeric_id)

            if product_info:
                t["API_Category"] = product_info.get("category")
                t["API_Brand"] = product_info.get("brand")
                t["API_Rating"] = product_info.get("rating")
                t["API_Match"] = True
            else:
                t["API_Category"] = None
                t["API_Brand"] = None
                t["API_Rating"] = None
                t["API_Match"] = False
        except Exception:
            t["API_Category"] = None
            t["API_Brand"] = None
            t["API_Rating"] = None
            t["API_Match"] = False

        enriched.append(t)

    # Save to file
    save_enriched_data(enriched, filename="data/enriched_sales_data.txt")
    return enriched


def save_enriched_data(enriched_transactions, filename="data/enriched_sales_data.txt"):
    """
    Saves enriched transactions back to file

    Format:
    TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|CustomerID|Region|API_Category|API_Brand|API_Rating|API_Match
    """
    header = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region",
        "API_Category", "API_Brand", "API_Rating", "API_Match"
    ]

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("|".join(header) + "\n")
            for t in enriched_transactions:
                row = [
                    str(t.get("TransactionID", "")),
                    str(t.get("Date", "")),
                    str(t.get("ProductID", "")),
                    str(t.get("ProductName", "")),
                    str(t.get("Quantity", "")),
                    str(t.get("UnitPrice", "")),
                    str(t.get("CustomerID", "")),
                    str(t.get("Region", "")),
                    str(t.get("API_Category", "")),
                    str(t.get("API_Brand", "")),
                    str(t.get("API_Rating", "")),
                    str(t.get("API_Match", ""))
                ]
                f.write("|".join(row) + "\n")
        print(f"✓ Enriched data saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving enriched data: {e}")