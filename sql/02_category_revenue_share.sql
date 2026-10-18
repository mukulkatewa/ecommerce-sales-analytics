-- Revenue by product category with share and cumulative share (Pareto) using window functions
WITH cat AS (
    SELECT
        COALESCE(t.product_category_name_english, 'unknown') AS category,
        SUM(oi.price)                                         AS revenue
    FROM order_items oi
    JOIN orders o   ON o.order_id = oi.order_id AND o.order_status = 'delivered'
    JOIN products p ON p.product_id = oi.product_id
    LEFT JOIN category_translation t ON t.product_category_name = p.product_category_name
    GROUP BY 1
)
SELECT
    RANK() OVER (ORDER BY revenue DESC)                                  AS rank,
    category,
    ROUND(revenue, 2)                                                    AS revenue,
    ROUND(100.0 * revenue / SUM(revenue) OVER (), 2)                     AS share_pct,
    ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC
                                     ROWS UNBOUNDED PRECEDING)
          / SUM(revenue) OVER (), 2)                                     AS cumulative_share_pct
FROM cat
ORDER BY revenue DESC;
