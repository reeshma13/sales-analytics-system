# sales-analytics-system

## Overview
This project is a Python-based Sales Data Analytics System.  
It reads messy sales transaction files, cleans the data, integrates with external APIs, performs analysis, and generates reports.

## Features
- Read and clean messy sales transaction files
- Handle encoding issues and data quality problems
- Fetch product information from external APIs
- Analyze sales patterns and customer behavior
- Generate comprehensive reports for business decisions

## Project Structure

```text
sales-analytics-system/
  ├── README.md
  ├── main.py
  ├── utils/
  │   ├── file_handler.py
  │   ├── data_processor.py
  │   └── api_handler.py
  ├── data/
  │   └── sales_data.txt (provided)
  ├── output/
  └── requirements.txt
```
## Setup Instructions

1. Clone or download the project folder
2. Install Python 3.9+
3. Install required packages:
 
 
    ```bash
    pip install requests
    ```
    
4. Ensure folder structure exists:
    - data/ --> contains sales_data.txt
    - output/ --> will be created automatically for reports

## How to Run

Run the main script from the project root:

    ```bash
    python main.py
    ```

This will:
1. Read and validate sales data.
2. Align ProductIDs to DummyJSON’s valid range (1–100).
3. Fetch product info from DummyJSON API.
4. Enrich transactions with category, brand, rating.
5. Save enriched data to data/enrichedsalesdata.txt.
6. Generate report in output/sales_report.txt.

---

## API Endpoints Used

Base URL: https://dummyjson.com/products

1. Get ALL products (default 30)
```http
GET https://dummyjson.com/products
```
- Returns first 30 products.
- Response keys: products, total.

2. Get a SINGLE product by ID
```http
GET https://dummyjson.com/products/{id}
```
Example:
```http
GET https://dummyjson.com/products/1
```
- Returns one product object.

3. Get specific number of products
```http
GET https://dummyjson.com/products?limit=100
```
- Returns up to 100 products.
- Used in fetchallproducts().

4. Search products
```http
GET https://dummyjson.com/products/search?q={query}
```
Example:
`http
GET https://dummyjson.com/products/search?q=phone
`
- Returns products matching query.

Sample Product Response
```json
{
  "id": 1,
  "title": "iPhone 9",
  "description": "An apple mobile...",
  "price": 549,
  "category": "smartphones",
  "brand": "Apple",
  "rating": 4.69,
  "stock": 94
}
```

## Verification Steps

1. Verify API Fetch
Run inside Python shell:
Run tem one by one
```python
from utils.api_handler import fetch_all_products, create_product_mapping, enrich_sales_data
api_products = fetch_all_products()
print(len(api_products))   # should be 100
print(api_products[0])     # sample product dict
```

2. Verify Product Mapping

```python
product_mapping = create_product_mapping(api_products)
print(product_mapping[1]) 
```

3. Verify Enrichment
```python
transactions = [{
    'TransactionID': 'T001',
    'Date': '2024-12-01',
    'ProductID': 'P1',
    'ProductName': 'iPhone 9',
    'Quantity': 2,
    'UnitPrice': 549,
    'CustomerID': 'C001',
    'Region': 'North'
}]
enriched = enrich_sales_data(transactions, product_mapping)
print(enriched[0])
```
Expected: API_Match=True with category, brand, rating.

4. Verify Enriched File
Open data/enrichedsalesdata.txt.  
Header should include:

```text
APICategory|APIBrand|APIRating|APIMatch
```
Rows should show enrichment values.

5. Verify Report
Open output/sales_report.txt.  
Check API ENRICHMENT SUMMARY section:

```text
Total Products Enriched: X/Y
Success Rate: Z%
Products not enriched:
  - ...
```

---

🧪 Notes
- DummyJSON only has products with IDs 1–100.  
- If your sales file uses IDs like P101, P110, they must be aligned to 1–100 using the helper function in main.py.  
- Without alignment, enrichment will always fail (API_Match=False).

-
## Expected Output

- When cleaning the data, you should see:

    ```text
    Total records parsed: 80
    Invalid records removed: 10
    Valid records after cleaning: 70
    ```

- Cleaned data will be saved in the **output/** folder.




