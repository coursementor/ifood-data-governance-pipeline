{{
  config(
    materialized='table',
    tags=['silver', 'orders', 'cleaned'],
    description='Cleaned and standardized orders data with PII masking and data quality enhancements'
  )
}}

/*
Silver Layer - Cleaned Orders Data
This model applies data cleansing, standardization, PII masking, and enrichment
to the bronze orders data, making it ready for business consumption.
*/

WITH bronze_orders AS (
  SELECT * FROM {{ ref('bronze_orders') }}
),

cleaned_orders AS (
  SELECT
    -- Identifiers (no changes)
    order_id,
    customer_id,
    restaurant_id,
    
    -- Timestamps (validated and cleaned)
    order_timestamp,
    estimated_delivery_time,
    actual_delivery_time,
    
    -- Status standardization
    CASE status
      WHEN 'pending' THEN 'PENDING'
      WHEN 'confirmed' THEN 'CONFIRMED'
      WHEN 'preparing' THEN 'PREPARING'
      WHEN 'ready_for_pickup' THEN 'READY_FOR_PICKUP'
      WHEN 'in_delivery' THEN 'IN_DELIVERY'
      WHEN 'delivered' THEN 'DELIVERED'
      WHEN 'cancelled' THEN 'CANCELLED'
      ELSE 'UNKNOWN'
    END AS order_status,
    
    CASE cancellation_reason
      WHEN 'customer_request' THEN 'CUSTOMER_REQUEST'
      WHEN 'restaurant_unavailable' THEN 'RESTAURANT_UNAVAILABLE'
      WHEN 'payment_failed' THEN 'PAYMENT_FAILED'
      WHEN 'delivery_failed' THEN 'DELIVERY_FAILED'
      WHEN 'system_error' THEN 'SYSTEM_ERROR'
      ELSE NULL
    END AS cancellation_reason,
    
    -- Financial fields (validated)
    CASE 
      WHEN total_amount < 0 THEN 0
      WHEN total_amount > {{ var('max_order_value') }} THEN {{ var('max_order_value') }}
      ELSE total_amount
    END AS total_amount,
    
    CASE 
      WHEN delivery_fee < 0 THEN 0
      ELSE delivery_fee
    END AS delivery_fee,
    
    CASE 
      WHEN discount_amount < 0 THEN 0
      ELSE discount_amount
    END AS discount_amount,
    
    -- PII Masking (conditional based on variable)
    {% if var('enable_pii_masking') %}
      {% if var('mask_cpf') %}
        {{ mask_cpf('customer_cpf') }} AS customer_cpf_masked,
      {% else %}
        customer_cpf AS customer_cpf_masked,
      {% endif %}
      
      {% if var('mask_phone') %}
        {{ mask_phone('customer_phone') }} AS customer_phone_masked,
      {% else %}
        customer_phone AS customer_phone_masked,
      {% endif %}
      
      {% if var('mask_email') %}
        {{ mask_email('customer_email') }} AS customer_email_masked,
      {% else %}
        customer_email AS customer_email_masked,
      {% endif %}
    {% else %}
      customer_cpf AS customer_cpf_masked,
      customer_phone AS customer_phone_masked,
      customer_email AS customer_email_masked,
    {% endif %}
    
    -- Delivery address (structured)
    delivery_address,
    
    -- Order items (validated JSON)
    items,
    
    -- Metadata standardization
    UPPER(channel) AS channel,
    UPPER(platform) AS platform,
    UPPER(payment_method) AS payment_method,
    
    -- System fields
    created_at,
    updated_at,
    data_source,
    batch_id,
    bronze_ingested_at,
    dbt_run_id,
    
    -- Data quality flags
    has_complete_customer_info,
    has_delivery_completion_data,
    
    -- Enhanced derived fields
    delivery_delay_minutes,
    order_date,
    order_hour,
    order_day_of_week,
    order_size_category,
    
    -- Additional business enrichments
    CASE 
      WHEN order_hour BETWEEN 6 AND 11 THEN 'BREAKFAST'
      WHEN order_hour BETWEEN 12 AND 15 THEN 'LUNCH'
      WHEN order_hour BETWEEN 18 AND 22 THEN 'DINNER'
      ELSE 'OTHER'
    END AS meal_period,
    
    CASE order_day_of_week
      WHEN 1 THEN 'SUNDAY'
      WHEN 2 THEN 'MONDAY'
      WHEN 3 THEN 'TUESDAY'
      WHEN 4 THEN 'WEDNESDAY'
      WHEN 5 THEN 'THURSDAY'
      WHEN 6 THEN 'FRIDAY'
      WHEN 7 THEN 'SATURDAY'
    END AS day_name,
    
    CASE 
      WHEN order_day_of_week IN (1, 7) THEN 'WEEKEND'
      ELSE 'WEEKDAY'
    END AS day_type,
    
    -- Delivery performance metrics
    CASE
      WHEN actual_delivery_time IS NOT NULL AND estimated_delivery_time IS NOT NULL THEN
        CASE
          WHEN delivery_delay_minutes <= 0 THEN 'ON_TIME'
          WHEN delivery_delay_minutes <= 15 THEN 'SLIGHTLY_DELAYED'
          WHEN delivery_delay_minutes <= 30 THEN 'DELAYED'
          ELSE 'SEVERELY_DELAYED'
        END
      ELSE NULL
    END AS delivery_performance,
    
    -- Order value analysis
    total_amount - delivery_fee - discount_amount AS net_order_value,
    
    CASE
      WHEN discount_amount > 0 THEN TRUE
      ELSE FALSE
    END AS has_discount,
    
    CASE
      WHEN discount_amount > 0 THEN ROUND((discount_amount / total_amount) * 100, 2)
      ELSE 0
    END AS discount_percentage,
    
    -- Add Silver layer metadata
    CURRENT_TIMESTAMP() AS silver_processed_at,
    '{{ invocation_id }}' AS silver_dbt_run_id
    
  FROM bronze_orders
  
  -- Data quality filters for Silver layer
  WHERE order_timestamp IS NOT NULL
    AND total_amount >= 0
    AND delivery_fee >= 0
    AND order_status != 'UNKNOWN'
),

final AS (
  SELECT 
    *,
    
    -- Add row quality score
    (
      CASE WHEN has_complete_customer_info THEN 25 ELSE 0 END +
      CASE WHEN has_delivery_completion_data IS NOT FALSE THEN 25 ELSE 0 END +
      CASE WHEN delivery_address IS NOT NULL THEN 25 ELSE 0 END +
      CASE WHEN items IS NOT NULL THEN 25 ELSE 0 END
    ) AS data_quality_score,
    
    -- Add business flags
    CASE
      WHEN order_status = 'DELIVERED' AND delivery_performance IN ('ON_TIME', 'SLIGHTLY_DELAYED') THEN TRUE
      ELSE FALSE
    END AS is_successful_delivery,
    
    CASE
      WHEN order_status = 'CANCELLED' THEN TRUE
      ELSE FALSE
    END AS is_cancelled_order,
    
    CASE
      WHEN total_amount > 100 AND has_discount THEN TRUE
      ELSE FALSE
    END AS is_high_value_discounted_order
    
  FROM cleaned_orders
)

SELECT * FROM final

-- Add tests and constraints
{{ dbt_utils.group_by(n=60) }}
