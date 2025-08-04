"""
iFood Orders Ingestion DAG
Pipeline de ingestão de pedidos com rastreabilidade completa e validação de contratos.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
from airflow.utils.task_group import TaskGroup

# Custom imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.config_loader import get_config
from contracts.contract_validator import ContractValidator
from utils.lineage_tracker import LineageTracker
from utils.data_quality_checker import DataQualityChecker

logger = logging.getLogger(__name__)

# DAG Configuration
DAG_ID = 'ifood_orders_ingestion'
SCHEDULE_INTERVAL = '*/15 * * * *'  # Every 15 minutes
MAX_ACTIVE_RUNS = 1

# Default arguments
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email': ['data-engineering@ifood.com']
}

# Initialize DAG
dag = DAG(
    DAG_ID,
    default_args=default_args,
    description='Pipeline de ingestão de pedidos iFood com governança',
    schedule_interval=SCHEDULE_INTERVAL,
    max_active_runs=MAX_ACTIVE_RUNS,
    catchup=False,
    tags=['ifood', 'orders', 'ingestion', 'governance']
)


def extract_orders_from_api(**context) -> Dict[str, Any]:
    """
    Extract orders from iFood Orders API.
    """
    import requests
    import json
    from datetime import datetime
    
    execution_date = context['execution_date']
    batch_id = f"batch_{execution_date.strftime('%Y%m%d_%H%M%S')}"
    
    logger.info(f"Starting orders extraction for batch: {batch_id}")
    
    # Configuration
    config = get_config()
    api_config = config.get('apis.orders')
    
    # API call parameters
    params = {
        'start_time': (execution_date - timedelta(minutes=15)).isoformat(),
        'end_time': execution_date.isoformat(),
        'limit': 1000
    }
    
    # Simulate API call (in real implementation, this would be actual API)
    orders_data = _simulate_orders_api_response(params, batch_id)
    
    # Store raw data in Bronze layer
    bronze_path = f"bronze/orders/{execution_date.strftime('%Y/%m/%d/%H')}/{batch_id}.json"
    _store_to_gcs(orders_data, bronze_path)
    
    # Track lineage
    lineage_tracker = LineageTracker()
    lineage_tracker.track_extraction(
        source='orders-api',
        destination=bronze_path,
        batch_id=batch_id,
        record_count=len(orders_data),
        execution_date=execution_date
    )
    
    logger.info(f"Extracted {len(orders_data)} orders to {bronze_path}")
    
    return {
        'batch_id': batch_id,
        'bronze_path': bronze_path,
        'record_count': len(orders_data),
        'extraction_timestamp': datetime.utcnow().isoformat()
    }


def validate_contracts(**context) -> Dict[str, Any]:
    """
    Validate extracted data against data contracts.
    """
    ti = context['ti']
    extraction_result = ti.xcom_pull(task_ids='extract_orders')
    
    batch_id = extraction_result['batch_id']
    bronze_path = extraction_result['bronze_path']
    
    logger.info(f"Validating contracts for batch: {batch_id}")
    
    # Load data from Bronze
    orders_data = _load_from_gcs(bronze_path)
    
    # Validate against contract
    validator = ContractValidator()
    validation_result = validator.validate_batch(orders_data)
    
    # Store validation results
    validation_path = f"validation/orders/{context['execution_date'].strftime('%Y/%m/%d/%H')}/{batch_id}_validation.json"
    validation_data = {
        'batch_id': batch_id,
        'validation_timestamp': datetime.utcnow().isoformat(),
        'is_valid': validation_result.is_valid,
        'record_count': validation_result.record_count,
        'valid_count': validation_result.valid_count,
        'success_rate': validation_result.success_rate,
        'errors': validation_result.errors,
        'warnings': validation_result.warnings
    }
    
    _store_to_gcs(validation_data, validation_path)
    
    # Track lineage
    lineage_tracker = LineageTracker()
    lineage_tracker.track_validation(
        source=bronze_path,
        validation_result=validation_path,
        batch_id=batch_id,
        success_rate=validation_result.success_rate
    )
    
    # Fail if validation success rate is below threshold
    min_success_rate = get_config().get('data_quality.thresholds.validity', 0.95)
    if validation_result.success_rate < min_success_rate:
        raise ValueError(f"Validation success rate {validation_result.success_rate:.2%} below threshold {min_success_rate:.2%}")
    
    logger.info(f"Contract validation completed: {validation_result.success_rate:.2%} success rate")
    
    return {
        'batch_id': batch_id,
        'validation_path': validation_path,
        'success_rate': validation_result.success_rate,
        'valid_records': validation_result.valid_count
    }


def transform_to_silver(**context) -> Dict[str, Any]:
    """
    Transform Bronze data to Silver layer with cleansing and standardization.
    """
    ti = context['ti']
    validation_result = ti.xcom_pull(task_ids='validate_contracts')
    extraction_result = ti.xcom_pull(task_ids='extract_orders')
    
    batch_id = validation_result['batch_id']
    bronze_path = extraction_result['bronze_path']
    
    logger.info(f"Transforming to Silver layer for batch: {batch_id}")
    
    # Load validated data
    orders_data = _load_from_gcs(bronze_path)
    
    # Apply transformations
    transformed_data = []
    for order in orders_data:
        transformed_order = _apply_silver_transformations(order)
        transformed_data.append(transformed_order)
    
    # Store in Silver layer
    silver_path = f"silver/orders/{context['execution_date'].strftime('%Y/%m/%d/%H')}/{batch_id}.parquet"
    _store_to_gcs(transformed_data, silver_path, format='parquet')
    
    # Track lineage
    lineage_tracker = LineageTracker()
    lineage_tracker.track_transformation(
        source=bronze_path,
        destination=silver_path,
        batch_id=batch_id,
        transformation_type='bronze_to_silver',
        record_count=len(transformed_data)
    )
    
    logger.info(f"Transformed {len(transformed_data)} orders to Silver layer: {silver_path}")
    
    return {
        'batch_id': batch_id,
        'silver_path': silver_path,
        'record_count': len(transformed_data)
    }


def run_data_quality_checks(**context) -> Dict[str, Any]:
    """
    Run comprehensive data quality checks on Silver data.
    """
    ti = context['ti']
    silver_result = ti.xcom_pull(task_ids='transform_to_silver')
    
    batch_id = silver_result['batch_id']
    silver_path = silver_result['silver_path']
    
    logger.info(f"Running data quality checks for batch: {batch_id}")
    
    # Initialize data quality checker
    dq_checker = DataQualityChecker()
    
    # Load Silver data
    silver_data = _load_from_gcs(silver_path)
    
    # Run quality checks
    quality_results = dq_checker.run_comprehensive_checks(
        data=silver_data,
        batch_id=batch_id,
        data_source='silver_orders'
    )
    
    # Store quality results
    quality_path = f"quality/orders/{context['execution_date'].strftime('%Y/%m/%d/%H')}/{batch_id}_quality.json"
    _store_to_gcs(quality_results, quality_path)
    
    # Track lineage
    lineage_tracker = LineageTracker()
    lineage_tracker.track_quality_check(
        source=silver_path,
        quality_result=quality_path,
        batch_id=batch_id,
        overall_score=quality_results['overall_score']
    )
    
    logger.info(f"Data quality checks completed: {quality_results['overall_score']:.2%} overall score")
    
    return {
        'batch_id': batch_id,
        'quality_path': quality_path,
        'overall_score': quality_results['overall_score']
    }


def load_to_warehouse(**context) -> Dict[str, Any]:
    """
    Load Silver data to Data Warehouse (BigQuery).
    """
    ti = context['ti']
    silver_result = ti.xcom_pull(task_ids='transform_to_silver')
    quality_result = ti.xcom_pull(task_ids='run_data_quality_checks')
    
    batch_id = silver_result['batch_id']
    silver_path = silver_result['silver_path']
    
    logger.info(f"Loading to warehouse for batch: {batch_id}")
    
    # Check quality threshold
    min_quality_score = get_config().get('data_quality.thresholds.overall', 0.90)
    if quality_result['overall_score'] < min_quality_score:
        logger.warning(f"Quality score {quality_result['overall_score']:.2%} below threshold, but proceeding with load")
    
    # Load to BigQuery (this would be actual BigQuery operation)
    warehouse_table = f"ifood_dw.orders_{context['execution_date'].strftime('%Y%m%d')}"
    
    # Track lineage
    lineage_tracker = LineageTracker()
    lineage_tracker.track_load(
        source=silver_path,
        destination=warehouse_table,
        batch_id=batch_id,
        record_count=silver_result['record_count']
    )
    
    logger.info(f"Loaded {silver_result['record_count']} orders to warehouse: {warehouse_table}")
    
    return {
        'batch_id': batch_id,
        'warehouse_table': warehouse_table,
        'load_timestamp': datetime.utcnow().isoformat()
    }


# Helper functions (would be in separate modules in real implementation)
def _simulate_orders_api_response(params: Dict, batch_id: str) -> List[Dict]:
    """Simulate API response for demo purposes."""
    import random
    from datetime import datetime, timedelta
    
    orders = []
    for i in range(random.randint(50, 200)):
        order = {
            'order_id': f'ORD{random.randint(1000000000, 9999999999)}',
            'customer_id': f'CUST{random.randint(10000000, 99999999)}',
            'restaurant_id': f'REST{random.randint(100000, 999999)}',
            'order_timestamp': (datetime.utcnow() - timedelta(minutes=random.randint(1, 15))).isoformat(),
            'status': random.choice(['pending', 'confirmed', 'preparing', 'delivered']),
            'total_amount': round(random.uniform(15.0, 150.0), 2),
            'delivery_fee': round(random.uniform(3.0, 12.0), 2),
            'customer_cpf': f'{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}',
            'customer_phone': f'({random.randint(11, 85)}) {random.randint(90000, 99999)}-{random.randint(1000, 9999)}',
            'customer_email': f'customer{i}@email.com',
            'channel': random.choice(['app', 'website']),
            'platform': random.choice(['ios', 'android', 'web']),
            'payment_method': random.choice(['credit_card', 'pix', 'cash']),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'data_source': 'orders-api',
            'batch_id': batch_id
        }
        orders.append(order)
    
    return orders


def _store_to_gcs(data: Any, path: str, format: str = 'json') -> None:
    """Store data to Google Cloud Storage."""
    # In real implementation, this would use GCS client
    logger.info(f"Storing data to GCS: {path} (format: {format})")


def _load_from_gcs(path: str) -> Any:
    """Load data from Google Cloud Storage."""
    # In real implementation, this would use GCS client
    logger.info(f"Loading data from GCS: {path}")
    return []


def _apply_silver_transformations(order: Dict) -> Dict:
    """Apply Silver layer transformations."""
    # Data cleansing, standardization, enrichment
    transformed = order.copy()
    
    # Add derived fields
    transformed['order_date'] = order['order_timestamp'][:10]
    transformed['order_hour'] = int(order['order_timestamp'][11:13])
    
    # Standardize status
    transformed['status'] = order['status'].lower()
    
    return transformed


# Define tasks
with dag:
    
    # Extraction task
    extract_task = PythonOperator(
        task_id='extract_orders',
        python_callable=extract_orders_from_api,
        doc_md="Extract orders from iFood API with full lineage tracking"
    )
    
    # Contract validation task
    validate_task = PythonOperator(
        task_id='validate_contracts',
        python_callable=validate_contracts,
        doc_md="Validate extracted data against data contracts"
    )
    
    # Silver transformation task
    transform_task = PythonOperator(
        task_id='transform_to_silver',
        python_callable=transform_to_silver,
        doc_md="Transform Bronze data to Silver with cleansing"
    )
    
    # Data quality checks task
    quality_task = PythonOperator(
        task_id='run_data_quality_checks',
        python_callable=run_data_quality_checks,
        doc_md="Run comprehensive data quality validations"
    )
    
    # Warehouse load task
    load_task = PythonOperator(
        task_id='load_to_warehouse',
        python_callable=load_to_warehouse,
        doc_md="Load validated data to BigQuery warehouse"
    )
    
    # Task dependencies
    extract_task >> validate_task >> transform_task >> quality_task >> load_task
