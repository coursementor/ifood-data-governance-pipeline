{{
  config(
    materialized='table',
    tags=['gold', 'orders', 'daily', 'summary'],
    description='Daily aggregated orders metrics for business intelligence and reporting'
  )
}}

/*
Gold Layer - Daily Orders Summary
Business-ready aggregated data providing daily insights into order performance,
delivery metrics, and business KPIs for stakeholders and analytics.
*/

WITH silver_orders AS (
  SELECT * FROM {{ ref('silver_orders') }}
),

daily_aggregations AS (
  SELECT
    order_date,
    day_name,
    day_type,
    
    -- Volume metrics
    COUNT(*) AS total_orders,
    COUNT(CASE WHEN order_status = 'DELIVERED' THEN 1 END) AS delivered_orders,
    COUNT(CASE WHEN order_status = 'CANCELLED' THEN 1 END) AS cancelled_orders,
    COUNT(CASE WHEN order_status IN ('PENDING', 'CONFIRMED', 'PREPARING', 'READY_FOR_PICKUP', 'IN_DELIVERY') THEN 1 END) AS active_orders,
    
    -- Financial metrics
    SUM(total_amount) AS total_revenue,
    SUM(net_order_value) AS total_net_revenue,
    SUM(delivery_fee) AS total_delivery_fees,
    SUM(discount_amount) AS total_discounts,
    
    AVG(total_amount) AS avg_order_value,
    AVG(net_order_value) AS avg_net_order_value,
    PERCENTILE_CONT(total_amount, 0.5) AS median_order_value,
    
    -- Delivery performance metrics
    COUNT(CASE WHEN delivery_performance = 'ON_TIME' THEN 1 END) AS on_time_deliveries,
    COUNT(CASE WHEN delivery_performance = 'SLIGHTLY_DELAYED' THEN 1 END) AS slightly_delayed_deliveries,
    COUNT(CASE WHEN delivery_performance = 'DELAYED' THEN 1 END) AS delayed_deliveries,
    COUNT(CASE WHEN delivery_performance = 'SEVERELY_DELAYED' THEN 1 END) AS severely_delayed_deliveries,
    
    AVG(delivery_delay_minutes) AS avg_delivery_delay_minutes,
    PERCENTILE_CONT(delivery_delay_minutes, 0.5) AS median_delivery_delay_minutes,
    PERCENTILE_CONT(delivery_delay_minutes, 0.95) AS p95_delivery_delay_minutes,
    
    -- Channel and platform metrics
    COUNT(CASE WHEN channel = 'APP' THEN 1 END) AS app_orders,
    COUNT(CASE WHEN channel = 'WEBSITE' THEN 1 END) AS website_orders,
    COUNT(CASE WHEN channel = 'PHONE' THEN 1 END) AS phone_orders,
    COUNT(CASE WHEN channel = 'WHATSAPP' THEN 1 END) AS whatsapp_orders,
    
    COUNT(CASE WHEN platform = 'IOS' THEN 1 END) AS ios_orders,
    COUNT(CASE WHEN platform = 'ANDROID' THEN 1 END) AS android_orders,
    COUNT(CASE WHEN platform = 'WEB' THEN 1 END) AS web_orders,
    
    -- Payment method metrics
    COUNT(CASE WHEN payment_method = 'CREDIT_CARD' THEN 1 END) AS credit_card_orders,
    COUNT(CASE WHEN payment_method = 'PIX' THEN 1 END) AS pix_orders,
    COUNT(CASE WHEN payment_method = 'CASH' THEN 1 END) AS cash_orders,
    COUNT(CASE WHEN payment_method = 'DEBIT_CARD' THEN 1 END) AS debit_card_orders,
    
    -- Meal period analysis
    COUNT(CASE WHEN meal_period = 'BREAKFAST' THEN 1 END) AS breakfast_orders,
    COUNT(CASE WHEN meal_period = 'LUNCH' THEN 1 END) AS lunch_orders,
    COUNT(CASE WHEN meal_period = 'DINNER' THEN 1 END) AS dinner_orders,
    COUNT(CASE WHEN meal_period = 'OTHER' THEN 1 END) AS other_time_orders,
    
    -- Order size analysis
    COUNT(CASE WHEN order_size_category = 'small' THEN 1 END) AS small_orders,
    COUNT(CASE WHEN order_size_category = 'medium' THEN 1 END) AS medium_orders,
    COUNT(CASE WHEN order_size_category = 'large' THEN 1 END) AS large_orders,
    COUNT(CASE WHEN order_size_category = 'extra_large' THEN 1 END) AS extra_large_orders,
    
    -- Discount analysis
    COUNT(CASE WHEN has_discount THEN 1 END) AS orders_with_discount,
    AVG(CASE WHEN has_discount THEN discount_percentage END) AS avg_discount_percentage,
    
    -- Data quality metrics
    AVG(data_quality_score) AS avg_data_quality_score,
    COUNT(CASE WHEN data_quality_score = 100 THEN 1 END) AS perfect_quality_orders,
    COUNT(CASE WHEN data_quality_score < 75 THEN 1 END) AS low_quality_orders,
    
    -- Unique counts
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT restaurant_id) AS unique_restaurants,
    
    -- Processing metadata
    MAX(silver_processed_at) AS latest_silver_processing,
    COUNT(DISTINCT batch_id) AS processed_batches
    
  FROM silver_orders
  WHERE order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)  -- Last 90 days
  GROUP BY order_date, day_name, day_type
),

calculated_metrics AS (
  SELECT
    *,
    
    -- Calculated rates and percentages
    SAFE_DIVIDE(delivered_orders, total_orders) * 100 AS delivery_success_rate,
    SAFE_DIVIDE(cancelled_orders, total_orders) * 100 AS cancellation_rate,
    SAFE_DIVIDE(on_time_deliveries, delivered_orders) * 100 AS on_time_delivery_rate,
    
    SAFE_DIVIDE(app_orders, total_orders) * 100 AS app_order_percentage,
    SAFE_DIVIDE(website_orders, total_orders) * 100 AS website_order_percentage,
    
    SAFE_DIVIDE(orders_with_discount, total_orders) * 100 AS discount_usage_rate,
    
    -- Customer metrics
    SAFE_DIVIDE(total_orders, unique_customers) AS avg_orders_per_customer,
    SAFE_DIVIDE(total_revenue, unique_customers) AS avg_revenue_per_customer,
    
    -- Restaurant metrics
    SAFE_DIVIDE(total_orders, unique_restaurants) AS avg_orders_per_restaurant,
    SAFE_DIVIDE(total_revenue, unique_restaurants) AS avg_revenue_per_restaurant,
    
    -- Efficiency metrics
    SAFE_DIVIDE(total_net_revenue, total_revenue) * 100 AS net_revenue_margin,
    SAFE_DIVIDE(total_delivery_fees, total_revenue) * 100 AS delivery_fee_percentage,
    SAFE_DIVIDE(total_discounts, total_revenue) * 100 AS discount_impact_percentage,
    
    -- Quality indicators
    CASE
      WHEN avg_data_quality_score >= 90 THEN 'EXCELLENT'
      WHEN avg_data_quality_score >= 80 THEN 'GOOD'
      WHEN avg_data_quality_score >= 70 THEN 'FAIR'
      ELSE 'POOR'
    END AS daily_data_quality_grade,
    
    -- Business performance indicators
    CASE
      WHEN delivery_success_rate >= 95 AND on_time_delivery_rate >= 85 THEN 'EXCELLENT'
      WHEN delivery_success_rate >= 90 AND on_time_delivery_rate >= 75 THEN 'GOOD'
      WHEN delivery_success_rate >= 85 AND on_time_delivery_rate >= 65 THEN 'FAIR'
      ELSE 'NEEDS_IMPROVEMENT'
    END AS daily_performance_grade
    
  FROM daily_aggregations
),

final AS (
  SELECT
    *,
    
    -- Add trend indicators (comparing to previous day)
    LAG(total_orders) OVER (ORDER BY order_date) AS prev_day_total_orders,
    LAG(total_revenue) OVER (ORDER BY order_date) AS prev_day_total_revenue,
    LAG(delivery_success_rate) OVER (ORDER BY order_date) AS prev_day_delivery_success_rate,
    
    -- Calculate day-over-day changes
    total_orders - LAG(total_orders) OVER (ORDER BY order_date) AS orders_change_from_prev_day,
    total_revenue - LAG(total_revenue) OVER (ORDER BY order_date) AS revenue_change_from_prev_day,
    delivery_success_rate - LAG(delivery_success_rate) OVER (ORDER BY order_date) AS delivery_rate_change_from_prev_day,
    
    -- Add Gold layer metadata
    CURRENT_TIMESTAMP() AS gold_processed_at,
    '{{ invocation_id }}' AS gold_dbt_run_id
    
  FROM calculated_metrics
)

SELECT * FROM final
ORDER BY order_date DESC

-- This model provides comprehensive daily insights for:
-- 1. Business stakeholders (revenue, volume, performance)
-- 2. Operations teams (delivery metrics, channel performance)
-- 3. Data teams (quality metrics, processing status)
-- 4. Product teams (platform usage, user behavior)
