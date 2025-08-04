"""
Tests for Data Quality components
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.data_quality_checker import DataQualityChecker, QualityDimension
from contracts.contract_validator import ContractValidator, Order


class TestDataQualityChecker:
    """Test cases for DataQualityChecker."""
    
    @pytest.fixture
    def quality_checker(self):
        """Create DataQualityChecker instance."""
        return DataQualityChecker()
    
    @pytest.fixture
    def sample_orders_data(self):
        """Create sample orders data for testing."""
        return [
            {
                'order_id': 'ORD1234567890',
                'customer_id': 'CUST12345678',
                'restaurant_id': 'REST123456',
                'order_timestamp': '2024-01-15T10:30:00Z',
                'order_status': 'DELIVERED',
                'total_amount': 45.90,
                'delivery_fee': 5.90,
                'discount_amount': 0.00,
                'customer_cpf': '123.456.789-00',
                'customer_phone': '(11) 99999-9999',
                'customer_email': 'test@email.com',
                'channel': 'APP',
                'platform': 'IOS',
                'payment_method': 'CREDIT_CARD',
                'created_at': '2024-01-15T10:30:00Z',
                'updated_at': '2024-01-15T10:30:00Z',
                'data_source': 'test',
                'batch_id': 'test_batch_001',
                'data_quality_score': 95
            },
            {
                'order_id': 'ORD1234567891',
                'customer_id': 'CUST12345679',
                'restaurant_id': 'REST123457',
                'order_timestamp': '2024-01-15T11:30:00Z',
                'order_status': 'CANCELLED',
                'total_amount': 32.50,
                'delivery_fee': 4.50,
                'discount_amount': 5.00,
                'customer_cpf': '987.654.321-00',
                'customer_phone': '(11) 88888-8888',
                'customer_email': 'test2@email.com',
                'channel': 'WEBSITE',
                'platform': 'WEB',
                'payment_method': 'PIX',
                'created_at': '2024-01-15T11:30:00Z',
                'updated_at': '2024-01-15T11:30:00Z',
                'data_source': 'test',
                'batch_id': 'test_batch_001',
                'data_quality_score': 88
            }
        ]
    
    def test_completeness_check(self, quality_checker, sample_orders_data):
        """Test completeness quality checks."""
        
        incomplete_data = sample_orders_data.copy()
        incomplete_data.append({
            'order_id': 'ORD1234567892',
            'customer_id': None,
            'restaurant_id': 'REST123458',
            'order_timestamp': '2024-01-15T12:30:00Z',
            'order_status': 'PENDING',
            'total_amount': 25.00,
            'delivery_fee': 3.00,
            'customer_cpf': None,
            'created_at': '2024-01-15T12:30:00Z',
            'data_source': 'test',
            'batch_id': 'test_batch_001'
        })
        
        result = quality_checker.run_comprehensive_checks(
            data=incomplete_data,
            batch_id='test_batch_completeness'
        )
        
        completeness_checks = [
            check for check in result['quality_checks']
            if check['dimension'] == QualityDimension.COMPLETENESS.value
        ]
        
        assert len(completeness_checks) > 0
        assert any(not check['passed'] for check in completeness_checks)
    
    def test_validity_check(self, quality_checker, sample_orders_data):
        """Test validity quality checks."""
        
        invalid_data = sample_orders_data.copy()
        invalid_data.append({
            'order_id': 'INVALID_ID',  # Invalid format
            'customer_id': 'CUST12345678',
            'restaurant_id': 'REST123456',
            'order_timestamp': '2024-01-15T10:30:00Z',
            'order_status': 'INVALID_STATUS',
            'total_amount': -10.00,
            'delivery_fee': 5.90,
            'customer_cpf': '123.456.789-00',
            'created_at': '2024-01-15T10:30:00Z',
            'data_source': 'test',
            'batch_id': 'test_batch_001'
        })
        
        result = quality_checker.run_comprehensive_checks(
            data=invalid_data,
            batch_id='test_batch_validity'
        )
        
        validity_checks = [
            check for check in result['quality_checks']
            if check['dimension'] == QualityDimension.VALIDITY.value
        ]
        
        assert len(validity_checks) > 0
        assert any(not check['passed'] for check in validity_checks)
    
    def test_uniqueness_check(self, quality_checker, sample_orders_data):
        """Test uniqueness quality checks."""
        
        duplicate_data = sample_orders_data.copy()
        duplicate_data.append({
            'order_id': 'ORD1234567890',
            'customer_id': 'CUST12345680',
            'restaurant_id': 'REST123456',
            'order_timestamp': '2024-01-15T13:30:00Z',
            'order_status': 'PENDING',
            'total_amount': 30.00,
            'delivery_fee': 4.00,
            'created_at': '2024-01-15T13:30:00Z',
            'data_source': 'test',
            'batch_id': 'test_batch_001'
        })
        
        result = quality_checker.run_comprehensive_checks(
            data=duplicate_data,
            batch_id='test_batch_uniqueness'
        )
        
        uniqueness_checks = [
            check for check in result['quality_checks']
            if check['dimension'] == QualityDimension.UNIQUENESS.value
        ]
        
        assert len(uniqueness_checks) > 0
        assert any(not check['passed'] for check in uniqueness_checks)
    
    def test_consistency_check(self, quality_checker, sample_orders_data):
        """Test consistency quality checks."""
        
        inconsistent_data = sample_orders_data.copy()
        inconsistent_data.append({
            'order_id': 'ORD1234567893',
            'customer_id': 'CUST12345681',
            'restaurant_id': 'REST123456',
            'order_timestamp': '2024-01-15T10:30:00Z',
            'order_status': 'PENDING',
            'total_amount': 5.00,
            'delivery_fee': 10.00,
            'created_at': '2024-01-15T10:30:00Z',
            'data_source': 'test',
            'batch_id': 'test_batch_001'
        })
        
        result = quality_checker.run_comprehensive_checks(
            data=inconsistent_data,
            batch_id='test_batch_consistency'
        )
        
        consistency_checks = [
            check for check in result['quality_checks']
            if check['dimension'] == QualityDimension.CONSISTENCY.value
        ]
        
        assert len(consistency_checks) > 0
        assert any(not check['passed'] for check in consistency_checks)
    
    def test_overall_score_calculation(self, quality_checker, sample_orders_data):
        """Test overall quality score calculation."""
        
        result = quality_checker.run_comprehensive_checks(
            data=sample_orders_data,
            batch_id='test_batch_score'
        )
        
        assert 'overall_score' in result
        assert 0 <= result['overall_score'] <= 100
        
        assert 'dimension_scores' in result
        assert len(result['dimension_scores']) > 0
        
        for dimension, score in result['dimension_scores'].items():
            assert 0 <= score <= 100


class TestContractValidator:
    """Test cases for ContractValidator."""
    
    @pytest.fixture
    def contract_validator(self):
        """Create ContractValidator instance."""
        return ContractValidator()
    
    @pytest.fixture
    def valid_order_data(self):
        """Create valid order data."""
        return {
            'order_id': 'ORD1234567890',
            'customer_id': 'CUST12345678',
            'restaurant_id': 'REST123456',
            'order_timestamp': datetime.utcnow(),
            'estimated_delivery_time': datetime.utcnow() + timedelta(minutes=30),
            'order_status': 'PENDING',
            'total_amount': 45.90,
            'delivery_fee': 5.90,
            'discount_amount': 0.00,
            'customer_cpf': '123.456.789-00',
            'customer_phone': '(11) 99999-9999',
            'customer_email': 'test@email.com',
            'delivery_address': {
                'street': 'Rua Teste',
                'number': '123',
                'neighborhood': 'Centro',
                'city': 'São Paulo',
                'state': 'SP',
                'zipcode': '01234-567'
            },
            'items': [
                {
                    'item_id': 'ITEM001',
                    'name': 'Pizza Margherita',
                    'quantity': 1,
                    'unit_price': 40.00
                }
            ],
            'channel': 'APP',
            'platform': 'IOS',
            'payment_method': 'CREDIT_CARD',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'data_source': 'test',
            'batch_id': 'test_batch_001'
        }
    
    def test_valid_order_validation(self, contract_validator, valid_order_data):
        """Test validation of valid order data."""
        
        result = contract_validator.validate_record(valid_order_data)
        
        assert result.is_valid == True
        assert result.record_count == 1
        assert result.valid_count == 1
        assert len(result.errors) == 0
    
    def test_invalid_order_id_format(self, contract_validator, valid_order_data):
        """Test validation with invalid order ID format."""
        
        invalid_data = valid_order_data.copy()
        invalid_data['order_id'] = 'INVALID_ID'
        
        result = contract_validator.validate_record(invalid_data)
        
        assert result.is_valid == False
        assert len(result.errors) > 0
        assert any('order_id' in error for error in result.errors)
    
    def test_invalid_status(self, contract_validator, valid_order_data):
        """Test validation with invalid status."""
        
        invalid_data = valid_order_data.copy()
        invalid_data['order_status'] = 'INVALID_STATUS'
        
        result = contract_validator.validate_record(invalid_data)
        
        assert result.is_valid == False
        assert len(result.errors) > 0
    
    def test_negative_amount(self, contract_validator, valid_order_data):
        """Test validation with negative amount."""
        
        invalid_data = valid_order_data.copy()
        invalid_data['total_amount'] = -10.00
        
        result = contract_validator.validate_record(invalid_data)
        
        assert result.is_valid == False
        assert len(result.errors) > 0
    
    def test_batch_validation(self, contract_validator, valid_order_data):
        """Test batch validation."""
        
        batch_data = [
            valid_order_data,
            {**valid_order_data, 'order_id': 'ORD1234567891'},
            {**valid_order_data, 'order_id': 'INVALID_ID'},
        ]
        
        result = contract_validator.validate_batch(batch_data)
        
        assert result.record_count == 3
        assert result.valid_count == 2
        assert len(result.errors) > 0
        assert result.success_rate == 2/3
    
    def test_contract_info_retrieval(self, contract_validator):
        """Test contract information retrieval."""
        
        contract_info = contract_validator.get_contract_info()
        
        assert 'name' in contract_info
        assert 'version' in contract_info
        assert 'description' in contract_info
        assert 'owner' in contract_info
    
    def test_schema_fields_retrieval(self, contract_validator):
        """Test schema fields retrieval."""
        
        schema_fields = contract_validator.get_schema_fields()
        
        assert len(schema_fields) > 0
        
        for field in schema_fields:
            assert 'name' in field
            assert 'type' in field
            assert 'required' in field
            assert 'description' in field


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
