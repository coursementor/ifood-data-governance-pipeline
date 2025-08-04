{{
  config(
    materialized='table',
    tags=['bronze', 'orders', 'raw'],
    description='Raw orders data from iFood API with minimal transformations'
  )
}}

/*
Bronze Layer - Raw Orders Data
This model represents the raw orders data as ingested from the iFood Orders API.
Minimal transformations are applied, mainly for data type casting and basic cleansing.
*/

WITH source_data AS (
  SELECT
    -- Identifiers
    order_id,
    customer_id,
    restaurant_id,
    
    -- Timestamps (cast to proper datetime types)
    CAST(order_timestamp AS TIMESTAMP) AS order_timestamp,
    CAST(estimated_delivery_time AS TIMESTAMP) AS estimated_delivery_time,
    CAST(actual_delivery_time AS TIMESTAMP) AS actual_delivery_time,
    
    -- Status fields
    LOWER(TRIM(status)) AS status,
    CASE 
      WHEN LOWER(TRIM(status)) = 'cancelled' THEN LOWER(TRIM(cancellation_reason))
      ELSE NULL 
    END AS cancellation_reason,
    
    -- Financial fields (ensure proper numeric types)
    CAST(total_amount AS DECIMAL(10,2)) AS total_amount,
    CAST(delivery_fee AS DECIMAL(10,2)) AS delivery_fee,
    CAST(COALESCE(discount_amount, 0) AS DECIMAL(10,2)) AS discount_amount,
    
    -- Customer PII (raw, will be masked in Silver)
    customer_cpf,
    customer_phone,
    customer_email,
    
    -- Delivery address (JSON or structured)
    delivery_address,
    
    -- Order items (JSON array)
    items,
    
    -- Metadata
    channel,
    platform,
    payment_method,
    
    -- System fields
    CAST(created_at AS TIMESTAMP) AS created_at,
    CAST(updated_at AS TIMESTAMP) AS updated_at,
    data_source,
    batch_id,
    
    -- Add ingestion metadata
    CURRENT_TIMESTAMP() AS bronze_ingested_at,
    '{{ invocation_id }}' AS dbt_run_id
    
  FROM {{ source('raw', 'orders_api') }}
  
  -- Basic data quality filters
  WHERE order_id IS NOT NULL
    AND customer_id IS NOT NULL
    AND restaurant_id IS NOT NULL
    AND order_timestamp IS NOT NULL
    AND total_amount IS NOT NULL
    AND total_amount >= 0
)

SELECT 
  *,
  
  -- Add data quality flags
  CASE 
    WHEN customer_cpf IS NULL OR customer_cpf = '' THEN FALSE
    WHEN customer_phone IS NULL OR customer_phone = '' THEN FALSE
    WHEN customer_email IS NULL OR customer_email = '' THEN FALSE
    ELSE TRUE
  END AS has_complete_customer_info,
  
  CASE
    WHEN actual_delivery_time IS NOT NULL THEN TRUE
    WHEN status IN ('delivered', 'cancelled') AND actual_delivery_time IS NULL THEN FALSE
    ELSE NULL  -- Order still in progress
  END AS has_delivery_completion_data,
  
  -- Calculate derived fields
  CASE
    WHEN actual_delivery_time IS NOT NULL AND estimated_delivery_time IS NOT NULL
    THEN DATETIME_DIFF(actual_delivery_time, estimated_delivery_time, MINUTE)
    ELSE NULL
  END AS delivery_delay_minutes,
  
  -- Extract date parts for partitioning
  DATE(order_timestamp) AS order_date,
  EXTRACT(HOUR FROM order_timestamp) AS order_hour,
  EXTRACT(DAYOFWEEK FROM order_timestamp) AS order_day_of_week,
  
  -- Business categorization
  CASE
    WHEN total_amount < 20 THEN 'small'
    WHEN total_amount < 50 THEN 'medium'
    WHEN total_amount < 100 THEN 'large'
    ELSE 'extra_large'
  END AS order_size_category

FROM source_data

-- Add basic data quality checks as tests will be defined separately
{{ dbt_utils.group_by(n=50) }}
