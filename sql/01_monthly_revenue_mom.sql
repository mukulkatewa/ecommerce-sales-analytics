-- Monthly revenue, order count, AOV and month-over-month growth (window function: LAG)
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
        COUNT(DISTINCT o.order_id)                      AS orders,
        SUM(oi.price)                                   AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1
)
SELECT
    month,
    orders,
    ROUND(revenue, 2)                                              AS revenue,
    ROUND(revenue / orders, 2)                                     AS aov,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
          / LAG(revenue) OVER (ORDER BY month), 1)                 AS mom_growth_pct
FROM monthly
WHERE month BETWEEN DATE '2017-01-01' AND DATE '2018-08-01'   -- drop sparse edge months
ORDER BY month;
