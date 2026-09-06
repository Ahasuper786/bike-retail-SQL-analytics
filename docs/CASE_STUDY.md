# Case Study

## Context

The source data describes a bicycle retailer through seven relational tables covering customers, stores, products, brands, categories, orders, and order lines.

## Goal

Turn a database coursework exercise into a compact business analytics project that answers commercially useful questions with reproducible SQL and Python.

## Approach

1. Rebuilt the schema with primary keys, foreign keys, constraints, and a composite key for order lines.
2. Loaded the source CSVs into SQLite.
3. Defined net revenue as `list_price * (1 - discount) * quantity`.
4. Used SQL to analyse stores, products, categories, brands, customers, and time trends.
5. Used pandas for validation, secondary metrics, and exportable recruiter-friendly result tables.
6. Added tests for revenue logic and database integrity checks.

## Key findings

- Total net revenue was approximately **$7.69M** across **1,615 orders**.
- Baldwin Bikes generated roughly **67.8% of revenue**, driven by the largest order volume.
- Rowlett Bikes had the highest average order value at approximately **$4,986**.
- Trek Slash 8 27.5 - 2016 was the highest-revenue product at approximately **$555.6K**.
- Mountain Bikes were the highest-revenue category at approximately **$2.72M**.
- Revenue increased by approximately **42.0% from 2016 to 2017**.
- Only about **9.1% of customers** placed more than one order, suggesting limited repeat purchasing in the observed data.

## Professional improvements over the coursework version

The original notebook subtracted the discount value directly from list price. Because the discount column contains proportions such as `0.20` and `0.07`, the portfolio version treats them as percentage discounts and uses the conventional formula `price × (1 - discount) × quantity`.

The redesigned schema also avoids uniqueness constraints on foreign keys that would incorrectly imply one order per customer or store, and it models order lines using `(order_id, item_id)` as a composite primary key.

## Limitations

- The raw dataset provenance/license was not established from the coursework files, so raw files are not redistributed.
- Customer contact fields look like personal data; public outputs are restricted to aggregate, non-identifying results.
- This is descriptive analytics, not causal inference or demand forecasting.
