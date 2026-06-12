-- Three slow queries with performance issues

-- Query 1: Function on indexed column prevents index usage
SELECT id, email, name
FROM customers
WHERE LOWER(email) = LOWER('test@example.com');

-- Query 2: SELECT * with correlated subquery instead of JOIN, missing composite index
SELECT *
FROM orders o
WHERE o.customer_id IN (SELECT id FROM customers WHERE country = 'US')
  AND o.order_date >= '2024-01-01';

-- Query 3: OR conditions prevent index usage, plus unnecessary DISTINCT
SELECT DISTINCT p.name, SUM(oi.quantity) as total_qty
FROM order_items oi
JOIN products p ON oi.product_id = p.id
WHERE oi.quantity > 0 OR oi.quantity > 0
GROUP BY p.id, p.name
HAVING total_qty > 10;
