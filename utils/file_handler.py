def read_sales_data(filename):
    """
    Reads sales data from file handling encoding issues

    Returns: list of raw lines (strings)

    Expected Output Format:
    ['T001|2024-12-01|P101|Laptop|2|45000|C001|North', ...]
    """
    encodings = ['utf-8', 'latin-1', 'cp1252']
    lines = []

    for enc in encodings:
        try:
            with open(filename, 'r', encoding=enc, errors='ignore') as f:
                lines = f.readlines()
                break
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return []
        except UnicodeDecodeError:
            continue  # try next encoding

    # Remove header row and empty lines
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("TransactionID"):  # skip header
            continue
        cleaned_lines.append(line)

    return cleaned_lines


def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries

    Returns: list of dictionaries with keys:
    ['TransactionID', 'Date', 'ProductID', 'ProductName',
     'Quantity', 'UnitPrice', 'CustomerID', 'Region']
    """
    transactions = []

    for line in raw_lines:
        fields = line.split("|")

        # Expect exactly 8 fields
        if len(fields) != 8:
            continue

        transaction_id, date, product_id, product_name, quantity, unit_price, customer_id, region = fields

        # Clean product name (remove commas)
        product_name = product_name.replace(",", "")

        # Clean numeric fields
        try:
            quantity = int(quantity.replace(",", ""))
            unit_price = float(unit_price.replace(",", ""))
        except ValueError:
            continue

        transaction = {
            "TransactionID": transaction_id.strip(),
            "Date": date.strip(),
            "ProductID": product_id.strip(),
            "ProductName": product_name.strip(),
            "Quantity": quantity,
            "UnitPrice": unit_price,
            "CustomerID": customer_id.strip(),
            "Region": region.strip()
        }

        transactions.append(transaction)

    return transactions


def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters

    Returns: tuple (valid_transactions, invalid_count, filter_summary)
    """
    valid_transactions = []
    invalid_count = 0

    # Validation
    for t in transactions:
        if (t["Quantity"] <= 0 or
            t["UnitPrice"] <= 0 or
            not t["TransactionID"].startswith("T") or
            not t["ProductID"].startswith("P") or
            not t["CustomerID"].startswith("C") or
            not t["Region"]):
            invalid_count += 1
            continue
        valid_transactions.append(t)

    # Filtering
    total_input = len(transactions)
    filtered_by_region = 0
    filtered_by_amount = 0

    # Show available regions
    regions = sorted(set(t["Region"] for t in valid_transactions))
    print(f"Available regions: {regions}")

    # Show transaction amount range
    amounts = [t["Quantity"] * t["UnitPrice"] for t in valid_transactions]
    if amounts:
        print(f"Transaction amount range: Min={min(amounts)}, Max={max(amounts)}")

    # Apply region filter
    if region:
        before = len(valid_transactions)
        valid_transactions = [t for t in valid_transactions if t["Region"] == region]
        filtered_by_region = before - len(valid_transactions)
        print(f"Records after region filter: {len(valid_transactions)}")

    # Apply amount filters
    if min_amount is not None:
        before = len(valid_transactions)
        valid_transactions = [t for t in valid_transactions if t["Quantity"] * t["UnitPrice"] >= min_amount]
        filtered_by_amount += before - len(valid_transactions)
        print(f"Records after min_amount filter: {len(valid_transactions)}")

    if max_amount is not None:
        before = len(valid_transactions)
        valid_transactions = [t for t in valid_transactions if t["Quantity"] * t["UnitPrice"] <= max_amount]
        filtered_by_amount += before - len(valid_transactions)
        print(f"Records after max_amount filter: {len(valid_transactions)}")

    filter_summary = {
        "total_input": total_input,
        "invalid": invalid_count,
        "filtered_by_region": filtered_by_region,
        "filtered_by_amount": filtered_by_amount,
        "final_count": len(valid_transactions)
    }

    return valid_transactions, invalid_count, filter_summary