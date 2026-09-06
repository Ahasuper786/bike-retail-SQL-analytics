# Data Dictionary

| Table | Key fields | Purpose |
|---|---|---|
| `customers` | `customer_id` | Customer identity and location attributes |
| `stores` | `store_id` | Retail store attributes |
| `brands` | `brand_id` | Product brand lookup |
| `categories` | `category_id` | Product category lookup |
| `products` | `product_id`, `brand_id`, `category_id` | Product catalogue and list prices |
| `orders` | `order_id`, `customer_id`, `store_id`, `order_date` | Order header table |
| `order_items` | `order_id`, `item_id`, `product_id` | Order-line quantity, price, and discount |

## Derived metric

**Net revenue** = `list_price × (1 - discount) × quantity`

The discount field is interpreted as a proportion between 0 and 1.
