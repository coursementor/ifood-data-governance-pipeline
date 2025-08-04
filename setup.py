"""
Setup script for iFood Data Governance Pipeline
Initializes the complete data governance system.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

from utils.config_loader import get_config
from catalog.catalog_manager import get_catalog_manager
from security.access_control import get_access_control
from security.privacy_manager import get_privacy_manager
from data_quality.great_expectations_config import setup_ifood_data_quality

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('setup.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def create_directories():
    """Create necessary directories."""
    
    directories = [
        'logs',
        'data',
        'data/bronze',
        'data/silver', 
        'data/gold',
        'data_quality/gx_config',
        'catalog/catalog_data',
        'security/keys',
        'tests/test_data'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")


def initialize_catalog():
    """Initialize the data catalog."""
    
    logger.info("Initializing data catalog...")
    
    catalog_manager = get_catalog_manager()
    dataset_ids = catalog_manager.initialize_ifood_catalog()
    
    logger.info(f"Catalog initialized with datasets: {list(dataset_ids.keys())}")
    
    return dataset_ids


def setup_access_control():
    """Setup access control with default users and roles."""
    
    logger.info("Setting up access control...")
    
    access_control = get_access_control()
    
    # Create default users
    users = [
        {
            'username': 'admin',
            'email': 'admin@ifood.com',
            'full_name': 'System Administrator',
            'roles': ['admin'],
            'department': 'IT',
            'password': 'admin123'
        },
        {
            'username': 'data.engineer',
            'email': 'data.engineer@ifood.com',
            'full_name': 'Data Engineer',
            'roles': ['data_engineer'],
            'department': 'Data Engineering',
            'password': 'engineer123'
        },
        {
            'username': 'data.analyst',
            'email': 'data.analyst@ifood.com',
            'full_name': 'Data Analyst',
            'roles': ['data_analyst'],
            'department': 'Analytics',
            'password': 'analyst123'
        },
        {
            'username': 'business.user',
            'email': 'business.user@ifood.com',
            'full_name': 'Business User',
            'roles': ['business_user'],
            'department': 'Business',
            'password': 'business123'
        }
    ]
    
    for user_data in users:
        try:
            user_id = access_control.create_user(**user_data)
            logger.info(f"Created user: {user_data['username']} ({user_id})")
        except Exception as e:
            logger.warning(f"User {user_data['username']} may already exist: {e}")


def setup_data_quality():
    """Setup data quality framework."""
    
    logger.info("Setting up data quality framework...")
    
    try:
        config = setup_ifood_data_quality()
        logger.info("Data quality framework setup completed")
        return config
    except Exception as e:
        logger.error(f"Error setting up data quality: {e}")
        return None


def create_sample_data():
    """Create sample data for testing."""
    
    logger.info("Creating sample data...")
    
    import json
    import random
    from datetime import datetime, timedelta
    
    # Sample orders data
    sample_orders = []
    
    for i in range(100):
        order = {
            'order_id': f'ORD{random.randint(1000000000, 9999999999)}',
            'customer_id': f'CUST{random.randint(10000000, 99999999)}',
            'restaurant_id': f'REST{random.randint(100000, 999999)}',
            'order_timestamp': (datetime.utcnow() - timedelta(hours=random.randint(1, 24))).isoformat(),
            'order_status': random.choice(['PENDING', 'CONFIRMED', 'PREPARING', 'DELIVERED', 'CANCELLED']),
            'total_amount': round(random.uniform(15.0, 150.0), 2),
            'delivery_fee': round(random.uniform(3.0, 12.0), 2),
            'discount_amount': round(random.uniform(0.0, 20.0), 2),
            'customer_cpf': f'{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}',
            'customer_phone': f'({random.randint(11, 85)}) {random.randint(90000, 99999)}-{random.randint(1000, 9999)}',
            'customer_email': f'customer{i}@email.com',
            'channel': random.choice(['APP', 'WEBSITE', 'PHONE']),
            'platform': random.choice(['IOS', 'ANDROID', 'WEB']),
            'payment_method': random.choice(['CREDIT_CARD', 'PIX', 'CASH']),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'data_source': 'sample_generator',
            'batch_id': 'sample_batch_001'
        }
        sample_orders.append(order)
    
    # Save sample data
    with open('tests/test_data/sample_orders.json', 'w') as f:
        json.dump(sample_orders, f, indent=2)
    
    logger.info(f"Created {len(sample_orders)} sample orders")


def run_initial_tests():
    """Run initial system tests."""
    
    logger.info("Running initial system tests...")
    
    try:
        # Test config loading
        config = get_config()
        config.load()
        logger.info("✅ Config loading test passed")
        
        # Test catalog operations
        catalog_manager = get_catalog_manager()
        catalog_summary = catalog_manager.catalog.get_catalog_summary()
        logger.info(f"✅ Catalog test passed - {catalog_summary['total_datasets']} datasets")
        
        # Test access control
        access_control = get_access_control()
        user_id = access_control.authenticate_user('admin', 'admin123')
        if user_id:
            logger.info("✅ Access control test passed")
        else:
            logger.warning("⚠️ Access control test failed")
        
        # Test privacy manager
        privacy_manager = get_privacy_manager()
        sample_data = {'customer_cpf': '123.456.789-00', 'customer_phone': '(11) 99999-9999'}
        masked_data = privacy_manager.mask_pii_data(sample_data)
        if masked_data['customer_cpf'] != sample_data['customer_cpf']:
            logger.info("✅ Privacy masking test passed")
        else:
            logger.warning("⚠️ Privacy masking test failed")
        
        logger.info("Initial system tests completed")
        
    except Exception as e:
        logger.error(f"System test failed: {e}")


def generate_documentation():
    """Generate system documentation."""
    
    logger.info("Generating system documentation...")
    
    # Create API documentation
    api_docs = """
# iFood Data Governance API Documentation

## Overview
This document describes the APIs available in the iFood Data Governance system.

## Authentication
All API endpoints require authentication using session tokens.

## Endpoints

### Data Catalog
- `GET /api/catalog/datasets` - List all datasets
- `GET /api/catalog/datasets/{id}` - Get dataset details
- `POST /api/catalog/datasets` - Register new dataset
- `GET /api/catalog/lineage/{id}` - Get dataset lineage

### Data Quality
- `GET /api/quality/reports` - Get quality reports
- `POST /api/quality/validate` - Run quality validation
- `GET /api/quality/metrics` - Get quality metrics

### Access Control
- `POST /api/auth/login` - User authentication
- `GET /api/auth/permissions` - Get user permissions
- `POST /api/auth/authorize` - Check authorization

### Privacy
- `POST /api/privacy/mask` - Mask PII data
- `POST /api/privacy/request` - Submit LGPD request
- `GET /api/privacy/compliance` - Get compliance report
"""
    
    with open('docs/API.md', 'w') as f:
        f.write(api_docs)
    
    deployment_guide = """
# Deployment Guide

## Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Apache Airflow 2.7+

## Installation Steps

1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables
4. Run setup: `python setup.py`
5. Start services: `streamlit run dashboards/main.py`

## Configuration
Edit `config/config.yaml` with your environment settings.

## Monitoring
Access dashboard at http://localhost:8501
"""
    
    with open('docs/DEPLOYMENT.md', 'w') as f:
        f.write(deployment_guide)
    
    logger.info("Documentation generated")


def main():
    """Main setup function."""
    
    print("🍔 iFood Data Governance Pipeline Setup")
    print("=" * 50)
    
    try:
        create_directories()
        
        initialize_catalog()
        setup_access_control()
        setup_data_quality()
        
        create_sample_data()
        
        run_initial_tests()
        
        # Generate documentation
        generate_documentation()
        
        print("\n✅ Setup completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Start the dashboard: streamlit run dashboards/main.py")
        print("2. Access at: http://localhost:8501")
        print("3. Login with: admin / admin123")
        print("4. Check logs in: setup.log")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        print(f"\n❌ Setup failed: {e}")
        print("Check setup.log for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
