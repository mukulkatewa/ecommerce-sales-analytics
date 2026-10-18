-- How many customers ever order more than once?
WITH per_customer AS (
    SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS orders
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1
)
SELECT
    COUNT(*)                                               AS customers,
    SUM(CASE WHEN orders > 1 THEN 1 ELSE 0 END)            AS repeat_customers,
    ROUND(100.0 * AVG(CASE WHEN orders > 1 THEN 1 ELSE 0 END), 2) AS repeat_rate_pct
FROM per_customer;
