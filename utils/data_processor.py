# utils/data_processor.py

from collections import defaultdict

# -------------------------------
# Task 2.1: Sales Summary Calculator
# -------------------------------

def calculate_total_revenue(transactions):
    """
    Calculates total revenue from all transactions

    Returns: float (total revenue)
    Example: 1545000.50
    """
    return sum(t["Quantity"] * t["UnitPrice"] for t in transactions)


def region_wise_sales(transactions):
    """
    Analyzes sales by region

    Returns: dictionary with region statistics
    Format:
    {
        'North': {
            'total_sales': 450000.0,
            'transaction_count': 15,
            'percentage': 29.13
        },
        ...
    }
    """
    region_stats = defaultdict(lambda: {"total_sales": 0.0, "transaction_count": 0})
    total_revenue = calculate_total_revenue(transactions)

    # Aggregate by region
    for t in transactions:
        amount = t["Quantity"] * t["UnitPrice"]
        region_stats[t["Region"]]["total_sales"] += amount
        region_stats[t["Region"]]["transaction_count"] += 1

    # Add percentage and sort by total_sales
    result = {}
    for region, stats in region_stats.items():
        percentage = (stats["total_sales"] / total_revenue * 100) if total_revenue > 0 else 0
        result[region] = {
            "total_sales": stats["total_sales"],
            "transaction_count": stats["transaction_count"],
            "percentage": round(percentage, 2)
        }

    # Sort by total_sales descending
    sorted_result = dict(sorted(result.items(), key=lambda x: x[1]["total_sales"], reverse=True))
    return sorted_result


def top_selling_products(transactions, n=5):
    """
    Finds top n products by total quantity sold

    Returns: list of tuples
    Format:
    [
        ('Laptop', 45, 2250000.0),
        ('Mouse', 38, 19000.0),
        ...
    ]
    """
    product_stats = defaultdict(lambda: {"quantity": 0, "revenue": 0.0})

    for t in transactions:
        amount = t["Quantity"] * t["UnitPrice"]
        product_stats[t["ProductName"]]["quantity"] += t["Quantity"]
        product_stats[t["ProductName"]]["revenue"] += amount

    # Convert to list of tuples
    products = [(p, stats["quantity"], stats["revenue"]) for p, stats in product_stats.items()]

    # Sort by quantity descending
    products.sort(key=lambda x: x[1], reverse=True)

    return products[:n]


def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns

    Returns: dictionary of customer statistics
    Format:
    {
        'C001': {
            'total_spent': 95000.0,
            'purchase_count': 3,
            'avg_order_value': 31666.67,
            'products_bought': ['Laptop', 'Mouse', 'Keyboard']
        },
        ...
    }
    """
    customer_stats = defaultdict(lambda: {"total_spent": 0.0, "purchase_count": 0, "products": set()})

    for t in transactions:
        amount = t["Quantity"] * t["UnitPrice"]
        cid = t["CustomerID"]
        customer_stats[cid]["total_spent"] += amount
        customer_stats[cid]["purchase_count"] += 1
        customer_stats[cid]["products"].add(t["ProductName"])

    # Finalize stats
    result = {}
    for cid, stats in customer_stats.items():
        avg_order_value = stats["total_spent"] / stats["purchase_count"] if stats["purchase_count"] > 0 else 0
        result[cid] = {
            "total_spent": stats["total_spent"],
            "purchase_count": stats["purchase_count"],
            "avg_order_value": round(avg_order_value, 2),
            "products_bought": sorted(list(stats["products"]))
        }

    # Sort by total_spent descending
    sorted_result = dict(sorted(result.items(), key=lambda x: x[1]["total_spent"], reverse=True))
    return sorted_result


# -------------------------------
# Task 2.2: Date-based Analysis
# -------------------------------

def daily_sales_trend(transactions):
    """
    Analyzes sales trends by date

    Returns: dictionary sorted by date
    Format:
    {
        '2024-12-01': {
            'revenue': 125000.0,
            'transaction_count': 8,
            'unique_customers': 6
        },
        ...
    }
    """
    date_stats = defaultdict(lambda: {"revenue": 0.0, "transaction_count": 0, "customers": set()})

    for t in transactions:
        amount = t["Quantity"] * t["UnitPrice"]
        date_stats[t["Date"]]["revenue"] += amount
        date_stats[t["Date"]]["transaction_count"] += 1
        date_stats[t["Date"]]["customers"].add(t["CustomerID"])

    result = {}
    for date, stats in date_stats.items():
        result[date] = {
            "revenue": stats["revenue"],
            "transaction_count": stats["transaction_count"],
            "unique_customers": len(stats["customers"])
        }

    # Sort chronologically by date
    sorted_result = dict(sorted(result.items(), key=lambda x: x[0]))
    return sorted_result


def find_peak_sales_day(transactions):
    """
    Identifies the date with highest revenue
    Returns: tuple (date, revenue, transaction_count)
    """
    trend = daily_sales_trend(transactions)
    if not trend:
        return None

    peak_date, peak_stats = max(trend.items(), key=lambda x: x[1]["revenue"])
    return (peak_date, peak_stats["revenue"], peak_stats["transaction_count"])


# -------------------------------
# Task 2.3: Product Performance
# -------------------------------

def low_performing_products(transactions, threshold=10):
    """
    Identifies products with low sales

    Returns: list of tuples
    Format:
    [
        ('Webcam', 4, 12000.0),
        ('Headphones', 7, 10500.0),
        ...
    ]
    """
    product_stats = defaultdict(lambda: {"quantity": 0, "revenue": 0.0})

    for t in transactions:
        amount = t["Quantity"] * t["UnitPrice"]
        product_stats[t["ProductName"]]["quantity"] += t["Quantity"]
        product_stats[t["ProductName"]]["revenue"] += amount

    # Filter products below threshold
    low_products = [(p, stats["quantity"], stats["revenue"]) 
                    for p, stats in product_stats.items() if stats["quantity"] < threshold]

    # Sort by quantity ascending
    low_products.sort(key=lambda x: x[1])
    return low_products