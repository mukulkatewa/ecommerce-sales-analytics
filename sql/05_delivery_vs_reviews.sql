-- Impact of late delivery on customer review score
WITH delivered AS (
    SELECT
        o.order_id,
        CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
             THEN 'late' ELSE 'on_time' END AS delivery_status,
        DATEDIFF('day', o.order_purchase_timestamp, o.order_delivered_customer_date) AS delivery_days
    FROM orders o
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
),
reviews AS (
    SELECT order_id, AVG(review_score) AS review_score
    FROM order_reviews
    GROUP BY 1
)
SELECT
    d.delivery_status,
    COUNT(*)                                                    AS orders,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)          AS pct_of_orders,
    ROUND(AVG(d.delivery_days), 1)                              AS avg_delivery_days,
    ROUND(AVG(r.review_score), 2)                               AS avg_review_score,
    ROUND(100.0 * AVG(CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END), 2) AS pct_negative_reviews
FROM delivered d
JOIN reviews r USING (order_id)
GROUP BY 1
ORDER BY 1;
