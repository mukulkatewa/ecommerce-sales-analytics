#!/usr/bin/env bash
# Downloads the Olist Brazilian E-Commerce dataset (public, from Olist's GitHub) into data/
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p data
BASE=https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets
for f in olist_customers_dataset olist_order_items_dataset olist_order_payments_dataset \
         olist_order_reviews_dataset olist_orders_dataset olist_products_dataset \
         olist_sellers_dataset product_category_name_translation; do
  curl -sfL -o "data/$f.csv" "$BASE/$f.csv"
done
echo "Downloaded to data/"
