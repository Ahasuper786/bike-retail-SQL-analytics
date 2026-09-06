-- Net revenue formula used throughout:
-- list_price * (1 - discount) * quantity

-- 1. Store performance
SELECT
    s.store_name,
    COUNT(DISTINCT o.order_id) AS orders,
    SUM(oi.quantity) AS units,
    ROUND(SUM(oi.list_price * (1 - oi.discount) * oi.quantity), 2) AS revenue
FROM orders o
JOIN stores s ON s.store_id = o.store_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY s.store_id, s.store_name
ORDER BY revenue DESC;

-- 2. Top products by revenue
SELECT
    p.product_id,
    p.product_name,
    SUM(oi.quantity) AS units,
    COUNT(DISTINCT oi.order_id) AS orders,
    ROUND(SUM(oi.list_price * (1 - oi.discount) * oi.quantity), 2) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name
ORDER BY revenue DESC
LIMIT 10;

-- 3. Category performance
SELECT
    c.category_name,
    SUM(oi.quantity) AS units,
    ROUND(SUM(oi.list_price * (1 - oi.discount) * oi.quantity), 2) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN categories c ON c.category_id = p.category_id
GROUP BY c.category_id, c.category_name
ORDER BY revenue DESC;

-- 4. Brand performance
SELECT
    b.brand_name,
    SUM(oi.quantity) AS units,
    ROUND(SUM(oi.list_price * (1 - oi.discount) * oi.quantity), 2) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN brands b ON b.brand_id = p.brand_id
GROUP BY b.brand_id, b.brand_name
ORDER BY revenue DESC;

-- 5. Annual performance. Dates are stored as DD/MM/YYYY in the source data.
SELECT
    substr(o.order_date, 7, 4) AS year,
    COUNT(DISTINCT o.order_id) AS orders,
    SUM(oi.quantity) AS units,
    ROUND(SUM(oi.list_price * (1 - oi.discount) * oi.quantity), 2) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY year
ORDER BY year;

-- 6. Customer repeat-order distribution
SELECT
    customer_id,
    COUNT(*) AS order_count
FROM orders
GROUP BY customer_id
ORDER BY order_count DESC, customer_id;
