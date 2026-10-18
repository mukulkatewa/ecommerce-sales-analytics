-- Payment method mix and average installments
SELECT
    payment_type,
    COUNT(DISTINCT order_id)                                        AS orders,
    ROUND(100.0 * COUNT(DISTINCT order_id)
          / SUM(COUNT(DISTINCT order_id)) OVER (), 2)               AS pct_orders,
    ROUND(SUM(payment_value), 2)                                    AS total_value,
    ROUND(AVG(payment_installments), 2)                             AS avg_installments
FROM order_payments
WHERE payment_type <> 'not_defined'
GROUP BY 1
ORDER BY orders DESC;
