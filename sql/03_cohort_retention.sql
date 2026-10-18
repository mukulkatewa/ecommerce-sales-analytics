-- Monthly acquisition cohorts: % of customers who purchase again N months after their first order (CTEs)
WITH purchases AS (
    SELECT c.customer_unique_id,
           DATE_TRUNC('month', o.order_purchase_timestamp) AS month
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
),
first_purchase AS (
    SELECT customer_unique_id, MIN(month) AS cohort_month
    FROM purchases
    GROUP BY 1
),
activity AS (
    SELECT DISTINCT
        f.cohort_month,
        p.customer_unique_id,
        DATEDIFF('month', f.cohort_month, p.month) AS month_number
    FROM purchases p
    JOIN first_purchase f USING (customer_unique_id)
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) AS customers
    FROM first_purchase
    GROUP BY 1
)
SELECT
    a.cohort_month,
    s.customers                                       AS cohort_size,
    a.month_number,
    COUNT(*)                                          AS active_customers,
    ROUND(100.0 * COUNT(*) / s.customers, 2)          AS retention_pct
FROM activity a
JOIN cohort_size s USING (cohort_month)
WHERE a.cohort_month BETWEEN DATE '2017-01-01' AND DATE '2018-06-01'
  AND a.month_number <= 12
GROUP BY 1, 2, 3
ORDER BY 1, 3;
