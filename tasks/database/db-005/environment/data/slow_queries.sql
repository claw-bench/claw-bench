-- Query 1: function on indexed column
SELECT id, email, name
FROM customers
WHERE LOWER(email) = 'test@example.com';

-- Query 2: SELECT * plus subquery
SELECT *
FROM orders
WHERE customer_id IN (
    SELECT id FROM customers WHERE country = 'US'
)
AND order_date >= '2024-01-01';

-- Query 3: OR plus unnecessary DISTINCT
SELECT DISTINCT p.name, SUM(oi.quantity) AS total_qty
FROM order_items oi
JOIN products p ON oi.product_id = p.id
WHERE oi.quantity > 0 OR oi.quantity IS NOT NULL
GROUP BY p.id, p.name;
