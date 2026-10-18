-- Revenue, AOV and late-delivery rate by customer state, ranked (RANK window function)
SELECT
    RANK() OVER (ORDER BY SUM(oi.price) DESC)                       AS revenue_rank,
    c.customer_state                                                AS state,
    COUNT(DISTINCT o.order_id)                                      AS orders,
    ROUND(SUM(oi.price), 2)                                         AS revenue,
    ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id), 2)            AS aov,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
                                      THEN o.order_id END)
          / COUNT(DISTINCT o.order_id), 2)                          AS late_delivery_pct
FROM orders o
JOIN customers c   ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY revenue_rank;
