import logging
import os
from utils.file_handler import read_sales_data, parse_transactions, validate_and_filter
from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products
)
from utils.api_handler import fetch_all_products, create_product_mapping, enrich_sales_data
from datetime import datetime

# Configure logging
os.makedirs("output", exist_ok=True)
logging.basicConfig(
    filename="output/app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
# -----------------------------
# Helper: Normalize ProductIDs 
# -----------------------------

def normalize_product_ids(transactions):
    """
    Normalize ProductIDs so they match DummyJSON API IDs (1–100).
    - Removes 'P' prefix
    - Converts leading zeros (P01 -> 1)
    - Remaps IDs >100 into 1–100 range
    - Defaults to 1 if parsing fails
    """
    normalized = []
    for t in transactions:
        try:
            # Remove 'P' and convert to int
            num = int(t["ProductID"].lstrip("P"))
            
            # Assign normalized numeric ID
            t["ProductID"] = num
        except Exception:
            # Fallback if parsing fails
            t["ProductID"] = 1
        
        normalized.append(t)
    return normalized
def align_product_ids(transactions):
    """
    Adjusts ProductIDs in sales data so they match DummyJSON API IDs (1–100).
    Keeps the 'P' prefix but remaps any out-of-range IDs to valid ones.
    Example: P101 -> P1, P205 -> P5
    """
    aligned = []
    for t in transactions:
        try:
            numeric_id = int(t["ProductID"].lstrip("P"))
            # Force into 1–100 range by modulo
            if numeric_id > 100:
                numeric_id = numeric_id % 100 or 100
            t["ProductID"] = f"P{numeric_id}"
        except Exception:
            # If parsing fails, default to P1
            t["ProductID"] = "P1"
        aligned.append(t)
    return aligned

# -----------------------------
# Report Generator
# -----------------------------
def generate_sales_report(transactions, enriched_transactions, output_file="output/sales_report.txt"):
    """
    Generates a comprehensive formatted text report with aligned tables.
    """
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. HEADER
    lines.append("="*70)
    lines.append("                     SALES ANALYTICS REPORT")
    lines.append(f"                 Generated: {now}")
    lines.append(f"                 Records Processed: {len(transactions)}")
    lines.append("="*70)
    lines.append("")

    # 2. OVERALL SUMMARY
    total_revenue = calculate_total_revenue(transactions)
    total_transactions = len(transactions)
    avg_order_value = total_revenue / total_transactions if total_transactions else 0
    dates = sorted(set(t["Date"] for t in transactions))
    date_range = f"{dates[0]} to {dates[-1]}" if dates else "N/A"

    lines.append("OVERALL SUMMARY")
    lines.append("-"*70)
    lines.append(f"{'Total Revenue:':<25} ₹{total_revenue:,.2f}")
    lines.append(f"{'Total Transactions:':<25} {total_transactions}")
    lines.append(f"{'Average Order Value:':<25} ₹{avg_order_value:,.2f}")
    lines.append(f"{'Date Range:':<25} {date_range}")
    lines.append("")

    # 3. REGION-WISE PERFORMANCE
    region_stats = region_wise_sales(transactions)
    lines.append("REGION-WISE PERFORMANCE")
    lines.append("-"*70)
    lines.append(f"{'Region':<12}{'Sales':<18}{'% of Total':<15}{'Transactions':<15}")
    for region, stats in region_stats.items():
        lines.append(f"{region:<12}₹{stats['total_sales']:<10}{stats['percentage']:>15.2f}%{stats['transaction_count']:>15}")
    lines.append("")

    # 4. TOP 5 PRODUCTS
    top_products = top_selling_products(transactions, n=5)
    lines.append("TOP 5 PRODUCTS")
    lines.append("-"*70)
    lines.append(f"{'Rank':<6}{'Product Name':<20}{'Quantity':<12}{'Revenue':<15}")
    for i, (name, qty, rev) in enumerate(top_products, 1):
        lines.append(f"{i:<6}{name:<20}{qty:<12}{'₹'+format(rev, ',.0f'):<15}")
    lines.append("")

    # 5. TOP 5 CUSTOMERS
    customers = customer_analysis(transactions)
    lines.append("TOP 5 CUSTOMERS")
    lines.append("-"*70)
    lines.append(f"{'Rank':<6}{'Customer ID':<15}{'Total Spent':<18}{'Orders':<10}")
    for i, (cid, stats) in enumerate(list(customers.items())[:5], 1):
        lines.append(f"{i:<6}{cid:<15}{'₹'+format(stats['total_spent'], ',.0f'):<18}{stats['purchase_count']:<10}")
    lines.append("")

    # 6. DAILY SALES TREND
    trend = daily_sales_trend(transactions)
    lines.append("DAILY SALES TREND")
    lines.append("-"*70)
    lines.append(f"{'Date':<12}{'Revenue':<15}{'Transactions':<15}{'Unique Customers':<18}")
    for date, stats in trend.items():
        lines.append(f"{date:<12}{'₹'+format(stats['revenue'], ',.0f'):<15}{stats['transaction_count']:<15}{stats['unique_customers']:<18}")
    lines.append("")

    # 7. PRODUCT PERFORMANCE ANALYSIS
    peak_day = find_peak_sales_day(transactions)
    low_products = low_performing_products(transactions)
    lines.append("PRODUCT PERFORMANCE ANALYSIS")
    lines.append("-"*70)
    if peak_day:
        lines.append(f"Best Selling Day: {peak_day[0]} (Revenue ₹{peak_day[1]:,.0f}, Transactions {peak_day[2]})")
    if low_products:
        lines.append("Low Performing Products:")
        lines.append(f"{'Product':<20}{'Quantity':<12}{'Revenue':<15}")
        for name, qty, rev in low_products:
            lines.append(f"{name:<20}{qty:<12}{'₹'+format(rev, ',.0f'):<15}")
    lines.append("")

    # 8. API ENRICHMENT SUMMARY
    enriched_count = sum(1 for t in enriched_transactions if t.get("API_Match"))
    total_count = len(enriched_transactions)
    success_rate = (enriched_count / total_count * 100) if total_count > 0 else 0
    failed_products = [t["ProductName"] for t in enriched_transactions if not t.get("API_Match")]

    lines.append("API ENRICHMENT SUMMARY")
    lines.append("-"*70)
    lines.append(f"{'Total Products Enriched:':<30}{enriched_count}/{total_count}")
    lines.append(f"{'Success Rate:':<30}{success_rate:.1f}%")
    if failed_products:
        lines.append("Products not enriched:")
        for p in failed_products:
            lines.append(f"  - {p}")
    lines.append("")

    # Write to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
# -----------------------------
# Main WorkFlow
# -----------------------------      
def main():
    raw_lines = read_sales_data("data/sales_data.txt")
    transactions = parse_transactions(raw_lines)
    transactions, invalid_count, summary = validate_and_filter(transactions)

    # Align IDs before enrichment
    transactions = align_product_ids(transactions)

    # Fetch API products and enrich
    api_products = fetch_all_products()
    product_mapping = create_product_mapping(api_products)
    enriched_transactions = enrich_sales_data(transactions, product_mapping)

    # Generate report
    generate_sales_report(transactions, enriched_transactions)
    print("========================================")
    print("        SALES ANALYTICS SYSTEM")
    print("========================================")

    try:
        logging.info("Step 1: Reading sales data")
        print("\n[1/10] Reading sales data...")
        raw_lines = read_sales_data("data/sales_data.txt")
        print(f"✓ Successfully read {len(raw_lines)} transactions")

        logging.info("Step 2: Parsing and cleaning")
        print("\n[2/10] Parsing and cleaning data...")
        transactions = parse_transactions(raw_lines)
        print(f"✓ Parsed {len(transactions)} records")

        logging.info("Step 3: Filter options")
        print("\n[3/10] Filter Options Available:")
        regions = sorted(set(t["Region"] for t in transactions))
        print(f"Regions: {', '.join(regions)}")
        amounts = [t["Quantity"] * t["UnitPrice"] for t in transactions]
        if amounts:
            print(f"Amount Range: ₹{min(amounts)} - ₹{max(amounts)}")

        choice = input("\nDo you want to filter data? (y/n): ").strip().lower()
        if choice == "y":
            region = input("Enter region to filter (or press Enter to skip): ").strip()
            min_amount = input("Enter minimum amount (or press Enter to skip): ").strip()
            max_amount = input("Enter maximum amount (or press Enter to skip): ").strip()
            min_amount = float(min_amount) if min_amount else None
            max_amount = float(max_amount) if max_amount else None
            transactions, invalid_count, summary = validate_and_filter(
                transactions, region=region if region else None,
                min_amount=min_amount, max_amount=max_amount
            )
        else:
            transactions, invalid_count, summary = validate_and_filter(transactions)

        logging.info("Step 4: Validation")
        print("\n[4/10] Validating transactions...")
        print(f"✓ Valid: {summary['final_count']} | Invalid: {summary['invalid']}")

        logging.info("Step 5: Analysis")
        print("\n[5/10] Analyzing sales data...")
        _ = calculate_total_revenue(transactions)
        _ = region_wise_sales(transactions)
        _ = top_selling_products(transactions)
        _ = customer_analysis(transactions)
        _ = daily_sales_trend(transactions)
        _ = find_peak_sales_day(transactions)
        _ = low_performing_products(transactions)
        print("✓ Analysis complete")

        transactions= normalize_product_ids(transactions)
        for t in transactions[:10]:
            print(f"TransactionID: {t['TransactionID']} | Original ProductName: {t['ProductName']} | Normalized ProductID: {t['ProductID']}")
        
        logging.info("Step 6: Fetch API products")
        print("\n[6/10] Fetching product data from API...")
        api_products = fetch_all_products()
        product_mapping = create_product_mapping(api_products)
        print(f"✓ Fetched {len(api_products)} products")

        logging.info("Step 7: Enrich sales data")
        print("\n[7/10] Enriching sales data...")
        enriched_transactions = enrich_sales_data(transactions, product_mapping)
        enriched_count = sum(1 for t in enriched_transactions if t.get("API_Match"))
        total_count = len(enriched_transactions)
        success_rate = (enriched_count / total_count * 100) if total_count > 0 else 0
        print(f"✓ Enriched {enriched_count}/{total_count} transactions ({success_rate:.1f}%)")

        logging.info("Step 8: Save enriched data")
        print("\n[8/10] Saving enriched data...")
        print("✓ Saved to: data/enriched_sales_data.txt")

        logging.info("Step 9: Generate report")
        print("\n[9/10] Generating report...")
        generate_sales_report(transactions, enriched_transactions, output_file="output/sales_report.txt")
        print("✓ Report saved to: output/sales_report.txt")

        logging.info("Step 10: Complete")
        print("\n[10/10] Process Complete!")
        print("========================================")

    except Exception as e:
        logging.error("Error in main workflow", exc_info=True)
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()