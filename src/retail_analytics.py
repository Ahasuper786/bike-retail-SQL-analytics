from __future__ import annotations

import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RESULTS = ROOT / "results"
DB_PATH = ROOT / "retail.db"

TABLES = [
    "brands",
    "categories",
    "customers",
    "stores",
    "products",
    "orders",
    "order_items",
]


def net_revenue(list_price, discount, quantity):
    """Return net line revenue after a percentage discount."""
    return list_price * (1 - discount) * quantity


def require_source_files() -> None:
    missing = [name for name in TABLES if not (RAW / f"{name}.csv").exists()]
    if missing:
        raise FileNotFoundError(
            "Missing source files in data/raw/: " + ", ".join(f"{x}.csv" for x in missing)
        )


def build_database() -> sqlite3.Connection:
    require_source_files()
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    schema = (ROOT / "sql" / "schema.sql").read_text(encoding="utf-8")
    conn.executescript(schema)

    for table in TABLES:
        df = pd.read_csv(RAW / f"{table}.csv")
        df.to_sql(table, conn, if_exists="append", index=False)

    violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    if violations:
        raise ValueError(f"Foreign-key violations detected: {violations[:5]}")
    return conn


def query_df(conn: sqlite3.Connection, sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn)


def run_analysis(conn: sqlite3.Connection) -> None:
    RESULTS.mkdir(exist_ok=True)

    store = query_df(
        conn,
        """
        SELECT s.store_name,
               COUNT(DISTINCT o.order_id) AS orders,
               SUM(oi.quantity) AS units,
               SUM(oi.list_price * (1 - oi.discount) * oi.quantity) AS revenue
        FROM orders o
        JOIN stores s ON s.store_id = o.store_id
        JOIN order_items oi ON oi.order_id = o.order_id
        GROUP BY s.store_id, s.store_name
        ORDER BY revenue DESC
        """,
    )

    top_products = query_df(
        conn,
        """
        SELECT p.product_id, p.product_name,
               COUNT(DISTINCT oi.order_id) AS orders,
               SUM(oi.quantity) AS units,
               SUM(oi.list_price * (1 - oi.discount) * oi.quantity) AS revenue
        FROM order_items oi
        JOIN products p ON p.product_id = oi.product_id
        GROUP BY p.product_id, p.product_name
        ORDER BY revenue DESC
        LIMIT 10
        """,
    )

    category = query_df(
        conn,
        """
        SELECT c.category_name,
               COUNT(DISTINCT oi.order_id) AS orders,
               SUM(oi.quantity) AS units,
               SUM(oi.list_price * (1 - oi.discount) * oi.quantity) AS revenue
        FROM order_items oi
        JOIN products p ON p.product_id = oi.product_id
        JOIN categories c ON c.category_id = p.category_id
        GROUP BY c.category_id, c.category_name
        ORDER BY revenue DESC
        """,
    )

    brand = query_df(
        conn,
        """
        SELECT b.brand_name,
               COUNT(DISTINCT oi.order_id) AS orders,
               SUM(oi.quantity) AS units,
               SUM(oi.list_price * (1 - oi.discount) * oi.quantity) AS revenue
        FROM order_items oi
        JOIN products p ON p.product_id = oi.product_id
        JOIN brands b ON b.brand_id = p.brand_id
        GROUP BY b.brand_id, b.brand_name
        ORDER BY revenue DESC
        """,
    )

    monthly = query_df(
        conn,
        """
        SELECT substr(o.order_date, 7, 4) AS year,
               substr(o.order_date, 4, 2) AS month,
               COUNT(DISTINCT o.order_id) AS orders,
               SUM(oi.quantity) AS units,
               SUM(oi.list_price * (1 - oi.discount) * oi.quantity) AS revenue
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        GROUP BY year, month
        ORDER BY year, month
        """,
    )
    monthly["year_month"] = monthly["year"] + "-" + monthly["month"]

    yearly = query_df(
        conn,
        """
        SELECT substr(o.order_date, 7, 4) AS year,
               COUNT(DISTINCT o.order_id) AS orders,
               SUM(oi.quantity) AS units,
               SUM(oi.list_price * (1 - oi.discount) * oi.quantity) AS revenue
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        GROUP BY year
        ORDER BY year
        """,
    )
    yearly["revenue_growth_pct"] = yearly["revenue"].pct_change() * 100

    order_totals = query_df(
        conn,
        """
        SELECT o.order_id, s.store_name,
               SUM(oi.list_price * (1 - oi.discount) * oi.quantity) AS revenue
        FROM orders o
        JOIN stores s ON s.store_id = o.store_id
        JOIN order_items oi ON oi.order_id = o.order_id
        GROUP BY o.order_id, s.store_name
        """,
    )
    aov = order_totals.groupby("store_name", as_index=False)["revenue"].mean().rename(
        columns={"revenue": "average_order_value"}
    )
    store = store.merge(aov, on="store_name")
    store["revenue_share_pct"] = store["revenue"] / store["revenue"].sum() * 100

    repeat = query_df(
        conn,
        "SELECT customer_id, COUNT(*) AS order_count FROM orders GROUP BY customer_id",
    )

    weighted_discount = query_df(
        conn,
        """
        SELECT SUM(discount * list_price * quantity) / SUM(list_price * quantity) AS value
        FROM order_items
        """,
    ).iloc[0, 0]

    key_metrics = pd.DataFrame(
        {
            "metric": [
                "Total revenue",
                "Orders",
                "Units sold",
                "Unique customers",
                "Average order value",
                "Weighted average discount",
                "Repeat-customer rate",
            ],
            "value": [
                store["revenue"].sum(),
                int(order_totals["order_id"].nunique()),
                int(store["units"].sum()),
                int(repeat["customer_id"].nunique()),
                order_totals["revenue"].mean(),
                weighted_discount,
                (repeat["order_count"] > 1).mean(),
            ],
        }
    )

    outputs = {
        "key_metrics.csv": key_metrics,
        "store_performance.csv": store,
        "top_products.csv": top_products,
        "category_performance.csv": category,
        "brand_performance.csv": brand,
        "monthly_performance.csv": monthly,
        "yearly_performance.csv": yearly,
    }
    for filename, frame in outputs.items():
        frame.to_csv(RESULTS / filename, index=False)


if __name__ == "__main__":
    connection = build_database()
    try:
        run_analysis(connection)
        print(f"Analysis complete. Results written to {RESULTS}")
    finally:
        connection.close()
