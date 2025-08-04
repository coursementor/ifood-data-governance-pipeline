/*
Data Masking Macros for PII Protection
These macros provide consistent PII masking across all models in compliance with LGPD.
*/

-- Macro to mask CPF (Brazilian tax ID)
{% macro mask_cpf(column_name) %}
  CASE 
    WHEN {{ column_name }} IS NOT NULL AND LENGTH({{ column_name }}) = 14 THEN
      CONCAT(
        SUBSTR({{ column_name }}, 1, 3),
        '.***.',
        SUBSTR({{ column_name }}, 8, 3),
        '-**'
      )
    ELSE '***.***.***-**'
  END
{% endmacro %}

-- Macro to mask phone numbers
{% macro mask_phone(column_name) %}
  CASE 
    WHEN {{ column_name }} IS NOT NULL AND LENGTH({{ column_name }}) >= 10 THEN
      CONCAT(
        SUBSTR({{ column_name }}, 1, 4),
        '****-',
        SUBSTR({{ column_name }}, -4)
      )
    ELSE '(**) ****-****'
  END
{% endmacro %}

-- Macro to mask email addresses
{% macro mask_email(column_name) %}
  CASE 
    WHEN {{ column_name }} IS NOT NULL AND STRPOS({{ column_name }}, '@') > 0 THEN
      CONCAT(
        SUBSTR({{ column_name }}, 1, 1),
        '***@',
        SUBSTR({{ column_name }}, STRPOS({{ column_name }}, '@') + 1)
      )
    ELSE '***@***.***'
  END
{% endmacro %}

-- Macro to mask delivery addresses
{% macro mask_address(column_name) %}
  CASE 
    WHEN {{ column_name }} IS NOT NULL THEN
      REGEXP_REPLACE({{ column_name }}, r'\d+', '***')
    ELSE '*** *** ***'
  END
{% endmacro %}

-- Macro to generate hash for pseudonymization
{% macro pseudonymize(column_name, salt='ifood_salt_2024') %}
  TO_HEX(SHA256(CONCAT({{ column_name }}, '{{ salt }}')))
{% endmacro %}

-- Macro to conditionally apply masking based on user role
{% macro conditional_mask(column_name, mask_function, user_role_var='user_role') %}
  {% if var(user_role_var, 'business_user') in ['data_engineer', 'auditor'] %}
    {{ column_name }}
  {% else %}
    {{ mask_function }}
  {% endif %}
{% endmacro %}

-- Macro for data classification tagging
{% macro classify_pii_field(field_name, classification_level='sensitive') %}
  {% set pii_metadata = {
    'field_name': field_name,
    'classification': classification_level,
    'masked_at': modules.datetime.datetime.now().isoformat(),
    'compliance': 'LGPD'
  } %}
  
  -- This would be used in model metadata
  {{ return(pii_metadata) }}
{% endmacro %}

-- Macro to audit PII access
{% macro audit_pii_access(table_name, user_id, access_type='read') %}
  INSERT INTO {{ target.schema }}.pii_access_log (
    table_name,
    user_id,
    access_type,
    access_timestamp,
    session_id
  ) VALUES (
    '{{ table_name }}',
    '{{ user_id }}',
    '{{ access_type }}',
    CURRENT_TIMESTAMP(),
    '{{ invocation_id }}'
  )
{% endmacro %}

-- Macro for data retention compliance
{% macro apply_retention_policy(table_name, retention_days=2555) %}
  DELETE FROM {{ table_name }}
  WHERE created_at < DATE_SUB(CURRENT_DATE(), INTERVAL {{ retention_days }} DAY)
{% endmacro %}

-- Macro to validate PII masking
{% macro validate_pii_masking(column_name, expected_pattern) %}
  {% set validation_query %}
    SELECT 
      COUNT(*) as total_records,
      COUNT(CASE WHEN REGEXP_CONTAINS({{ column_name }}, r'{{ expected_pattern }}') THEN 1 END) as masked_records,
      SAFE_DIVIDE(
        COUNT(CASE WHEN REGEXP_CONTAINS({{ column_name }}, r'{{ expected_pattern }}') THEN 1 END),
        COUNT(*)
      ) * 100 as masking_percentage
    FROM {{ this }}
  {% endset %}
  
  {{ return(validation_query) }}
{% endmacro %}
