"""Load the Olist CSVs into DuckDB, run every query in sql/, and save results to outputs/."""
from pathlib import Path

import duckdb

ROOT = Path(__file__).parent
DATA = ROOT / "data"
TABLES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    for table, file in TABLES.items():
        con.execute(f"CREATE TABLE {table} AS SELECT * FROM read_csv_auto('{DATA / file}', header=true)")
    return con


def main() -> None:
    con = connect()
    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    for sql_file in sorted((ROOT / "sql").glob("*.sql")):
        df = con.execute(sql_file.read_text()).df()
        df.to_csv(out / f"{sql_file.stem}.csv", index=False)
        print(f"\n=== {sql_file.stem} ({len(df)} rows) ===")
        print(df.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
