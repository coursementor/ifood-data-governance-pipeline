"""
Data Quality Checker
Comprehensive data quality validation using Great Expectations and custom rules.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import json
from dataclasses import dataclass, asdict
from enum import Enum

import great_expectations as gx
from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.checkpoint import SimpleCheckpoint

from data_quality.great_expectations_config import IFoodDataQualityConfig

logger = logging.getLogger(__name__)


class QualityDimension(str, Enum):
    """Data quality dimensions."""
    COMPLETENESS = "completeness"
    VALIDITY = "validity"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    ACCURACY = "accuracy"
    UNIQUENESS = "uniqueness"


class QualitySeverity(str, Enum):
    """Quality issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class QualityCheck:
    """Individual quality check result."""
    check_name: str
    dimension: QualityDimension
    passed: bool
    score: float
    severity: QualitySeverity
    message: str
    details: Dict[str, Any]
    execution_time: float


@dataclass
class QualityReport:
    """Comprehensive quality report."""
    batch_id: str
    data_source: str
    check_timestamp: datetime
    total_records: int
    checks_performed: int
    checks_passed: int
    overall_score: float
    dimension_scores: Dict[str, float]
    quality_checks: List[QualityCheck]
    recommendations: List[str]
    metadata: Dict[str, Any]


class DataQualityChecker:
    """Comprehensive data quality checker for iFood orders."""
    
    def __init__(self):
        self.gx_config = IFoodDataQualityConfig()
        self.context = self.gx_config.get_context()
        
    def run_comprehensive_checks(
        self,
        data: List[Dict[str, Any]],
        batch_id: str,
        data_source: str = "unknown"
    ) -> Dict[str, Any]:
        """Run comprehensive data quality checks."""
        
        logger.info(f"Starting comprehensive quality checks for batch: {batch_id}")
        start_time = datetime.utcnow()
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(data)
        
        # Initialize results
        quality_checks = []
        dimension_scores = {}
        
        # Run checks by dimension
        completeness_checks = self._check_completeness(df, batch_id)
        validity_checks = self._check_validity(df, batch_id)
        consistency_checks = self._check_consistency(df, batch_id)
        timeliness_checks = self._check_timeliness(df, batch_id)
        accuracy_checks = self._check_accuracy(df, batch_id)
        uniqueness_checks = self._check_uniqueness(df, batch_id)
        
        # Combine all checks
        all_checks = (
            completeness_checks + validity_checks + consistency_checks +
            timeliness_checks + accuracy_checks + uniqueness_checks
        )
        
        # Calculate dimension scores
        for dimension in QualityDimension:
            dimension_checks = [c for c in all_checks if c.dimension == dimension]
            if dimension_checks:
                dimension_scores[dimension.value] = np.mean([c.score for c in dimension_checks])
            else:
                dimension_scores[dimension.value] = 100.0
        
        # Calculate overall score
        overall_score = np.mean(list(dimension_scores.values()))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(all_checks, dimension_scores)
        
        # Create quality report
        report = QualityReport(
            batch_id=batch_id,
            data_source=data_source,
            check_timestamp=start_time,
            total_records=len(df),
            checks_performed=len(all_checks),
            checks_passed=sum(1 for c in all_checks if c.passed),
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            quality_checks=all_checks,
            recommendations=recommendations,
            metadata={
                "execution_time_seconds": (datetime.utcnow() - start_time).total_seconds(),
                "data_source": data_source,
                "framework_version": "1.0.0"
            }
        )
        
        logger.info(f"Quality checks completed: {overall_score:.2f}% overall score")
        
        return asdict(report)
    
    def _check_completeness(self, df: pd.DataFrame, batch_id: str) -> List[QualityCheck]:
        """Check data completeness."""
        checks = []
        
        # Required fields completeness
        required_fields = [
            'order_id', 'customer_id', 'restaurant_id', 'order_timestamp',
            'order_status', 'total_amount', 'delivery_fee'
        ]
        
        for field in required_fields:
            if field in df.columns:
                null_count = df[field].isnull().sum()
                completeness_rate = ((len(df) - null_count) / len(df)) * 100
                
                checks.append(QualityCheck(
                    check_name=f"{field}_completeness",
                    dimension=QualityDimension.COMPLETENESS,
                    passed=completeness_rate >= 95.0,
                    score=completeness_rate,
                    severity=QualitySeverity.CRITICAL if completeness_rate < 90 else QualitySeverity.MEDIUM,
                    message=f"{field} completeness: {completeness_rate:.2f}%",
                    details={
                        "total_records": len(df),
                        "null_records": int(null_count),
                        "completeness_rate": completeness_rate
                    },
                    execution_time=0.1
                ))
        
        # Overall completeness check
        total_fields = len(df.columns)
        total_nulls = df.isnull().sum().sum()
        total_values = len(df) * total_fields
        overall_completeness = ((total_values - total_nulls) / total_values) * 100
        
        checks.append(QualityCheck(
            check_name="overall_completeness",
            dimension=QualityDimension.COMPLETENESS,
            passed=overall_completeness >= 90.0,
            score=overall_completeness,
            severity=QualitySeverity.HIGH,
            message=f"Overall data completeness: {overall_completeness:.2f}%",
            details={
                "total_fields": total_fields,
                "total_values": total_values,
                "null_values": int(total_nulls)
            },
            execution_time=0.2
        ))
        
        return checks
    
    def _check_validity(self, df: pd.DataFrame, batch_id: str) -> List[QualityCheck]:
        """Check data validity."""
        checks = []
        
        # Order ID format validation
        if 'order_id' in df.columns:
            valid_order_ids = df['order_id'].str.match(r'^ORD[0-9]{10}$').sum()
            validity_rate = (valid_order_ids / len(df)) * 100
            
            checks.append(QualityCheck(
                check_name="order_id_format_validity",
                dimension=QualityDimension.VALIDITY,
                passed=validity_rate >= 98.0,
                score=validity_rate,
                severity=QualitySeverity.CRITICAL,
                message=f"Order ID format validity: {validity_rate:.2f}%",
                details={
                    "valid_ids": int(valid_order_ids),
                    "invalid_ids": int(len(df) - valid_order_ids),
                    "expected_pattern": "ORD[0-9]{10}"
                },
                execution_time=0.1
            ))
        
        # Status validity
        if 'order_status' in df.columns:
            valid_statuses = ['PENDING', 'CONFIRMED', 'PREPARING', 'READY_FOR_PICKUP', 
                            'IN_DELIVERY', 'DELIVERED', 'CANCELLED']
            valid_status_count = df['order_status'].isin(valid_statuses).sum()
            validity_rate = (valid_status_count / len(df)) * 100
            
            checks.append(QualityCheck(
                check_name="order_status_validity",
                dimension=QualityDimension.VALIDITY,
                passed=validity_rate >= 99.0,
                score=validity_rate,
                severity=QualitySeverity.HIGH,
                message=f"Order status validity: {validity_rate:.2f}%",
                details={
                    "valid_statuses": int(valid_status_count),
                    "invalid_statuses": int(len(df) - valid_status_count),
                    "allowed_values": valid_statuses
                },
                execution_time=0.1
            ))
        
        # Amount validity
        if 'total_amount' in df.columns:
            valid_amounts = ((df['total_amount'] >= 0) & (df['total_amount'] <= 1000)).sum()
            validity_rate = (valid_amounts / len(df)) * 100
            
            checks.append(QualityCheck(
                check_name="total_amount_validity",
                dimension=QualityDimension.VALIDITY,
                passed=validity_rate >= 95.0,
                score=validity_rate,
                severity=QualitySeverity.MEDIUM,
                message=f"Total amount validity: {validity_rate:.2f}%",
                details={
                    "valid_amounts": int(valid_amounts),
                    "invalid_amounts": int(len(df) - valid_amounts),
                    "min_value": 0,
                    "max_value": 1000
                },
                execution_time=0.1
            ))
        
        return checks
    
    def _check_consistency(self, df: pd.DataFrame, batch_id: str) -> List[QualityCheck]:
        """Check data consistency."""
        checks = []
        
        # Total amount vs delivery fee consistency
        if 'total_amount' in df.columns and 'delivery_fee' in df.columns:
            consistent_amounts = (df['total_amount'] >= df['delivery_fee']).sum()
            consistency_rate = (consistent_amounts / len(df)) * 100
            
            checks.append(QualityCheck(
                check_name="amount_fee_consistency",
                dimension=QualityDimension.CONSISTENCY,
                passed=consistency_rate >= 98.0,
                score=consistency_rate,
                severity=QualitySeverity.HIGH,
                message=f"Amount-fee consistency: {consistency_rate:.2f}%",
                details={
                    "consistent_records": int(consistent_amounts),
                    "inconsistent_records": int(len(df) - consistent_amounts)
                },
                execution_time=0.1
            ))
        
        # Status-timestamp consistency
        if all(col in df.columns for col in ['order_status', 'order_timestamp', 'actual_delivery_time']):
            delivered_orders = df[df['order_status'] == 'DELIVERED']
            if len(delivered_orders) > 0:
                has_delivery_time = delivered_orders['actual_delivery_time'].notna().sum()
                consistency_rate = (has_delivery_time / len(delivered_orders)) * 100
                
                checks.append(QualityCheck(
                    check_name="delivered_status_timestamp_consistency",
                    dimension=QualityDimension.CONSISTENCY,
                    passed=consistency_rate >= 90.0,
                    score=consistency_rate,
                    severity=QualitySeverity.MEDIUM,
                    message=f"Delivered orders timestamp consistency: {consistency_rate:.2f}%",
                    details={
                        "delivered_orders": len(delivered_orders),
                        "with_delivery_time": int(has_delivery_time)
                    },
                    execution_time=0.1
                ))
        
        return checks
    
    def _check_timeliness(self, df: pd.DataFrame, batch_id: str) -> List[QualityCheck]:
        """Check data timeliness."""
        checks = []
        
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
            now = datetime.utcnow()
            
            # Check data freshness (within last 24 hours)
            fresh_data = df[df['created_at'] >= (now - timedelta(hours=24))]
            freshness_rate = (len(fresh_data) / len(df)) * 100
            
            checks.append(QualityCheck(
                check_name="data_freshness",
                dimension=QualityDimension.TIMELINESS,
                passed=freshness_rate >= 80.0,
                score=freshness_rate,
                severity=QualitySeverity.MEDIUM,
                message=f"Data freshness (24h): {freshness_rate:.2f}%",
                details={
                    "fresh_records": len(fresh_data),
                    "stale_records": len(df) - len(fresh_data),
                    "check_time": now.isoformat()
                },
                execution_time=0.1
            ))
        
        return checks
    
    def _check_accuracy(self, df: pd.DataFrame, batch_id: str) -> List[QualityCheck]:
        """Check data accuracy."""
        checks = []
        
        # Business rule accuracy checks
        if 'data_quality_score' in df.columns:
            high_quality_records = (df['data_quality_score'] >= 75).sum()
            accuracy_rate = (high_quality_records / len(df)) * 100
            
            checks.append(QualityCheck(
                check_name="business_rule_accuracy",
                dimension=QualityDimension.ACCURACY,
                passed=accuracy_rate >= 85.0,
                score=accuracy_rate,
                severity=QualitySeverity.MEDIUM,
                message=f"Business rule accuracy: {accuracy_rate:.2f}%",
                details={
                    "high_quality_records": int(high_quality_records),
                    "low_quality_records": int(len(df) - high_quality_records),
                    "threshold": 75
                },
                execution_time=0.1
            ))
        
        return checks
    
    def _check_uniqueness(self, df: pd.DataFrame, batch_id: str) -> List[QualityCheck]:
        """Check data uniqueness."""
        checks = []
        
        # Order ID uniqueness
        if 'order_id' in df.columns:
            unique_orders = df['order_id'].nunique()
            uniqueness_rate = (unique_orders / len(df)) * 100
            
            checks.append(QualityCheck(
                check_name="order_id_uniqueness",
                dimension=QualityDimension.UNIQUENESS,
                passed=uniqueness_rate >= 99.9,
                score=uniqueness_rate,
                severity=QualitySeverity.CRITICAL,
                message=f"Order ID uniqueness: {uniqueness_rate:.2f}%",
                details={
                    "total_records": len(df),
                    "unique_orders": unique_orders,
                    "duplicate_orders": len(df) - unique_orders
                },
                execution_time=0.1
            ))
        
        return checks
    
    def _generate_recommendations(
        self,
        checks: List[QualityCheck],
        dimension_scores: Dict[str, float]
    ) -> List[str]:
        """Generate quality improvement recommendations."""
        recommendations = []
        
        # Check for critical failures
        critical_failures = [c for c in checks if not c.passed and c.severity == QualitySeverity.CRITICAL]
        if critical_failures:
            recommendations.append("CRITICAL: Address critical data quality failures immediately")
        
        # Dimension-specific recommendations
        if dimension_scores.get('completeness', 100) < 90:
            recommendations.append("Improve data completeness by validating source systems")
        
        if dimension_scores.get('validity', 100) < 95:
            recommendations.append("Implement stronger data validation at ingestion")
        
        if dimension_scores.get('consistency', 100) < 90:
            recommendations.append("Review business rules and data transformation logic")
        
        if dimension_scores.get('timeliness', 100) < 80:
            recommendations.append("Optimize data pipeline for better freshness")
        
        if dimension_scores.get('uniqueness', 100) < 99:
            recommendations.append("Investigate and resolve duplicate data issues")
        
        # General recommendations
        overall_score = np.mean(list(dimension_scores.values()))
        if overall_score < 85:
            recommendations.append("Consider implementing automated data quality monitoring")
        
        return recommendations
    
    def run_great_expectations_validation(
        self,
        data: pd.DataFrame,
        batch_id: str
    ) -> Dict[str, Any]:
        """Run Great Expectations validation."""
        
        try:
            # Create batch request
            batch_request = RuntimeBatchRequest(
                datasource_name="postgres_datasource",
                data_connector_name="default_runtime_data_connector",
                data_asset_name="orders_validation",
                runtime_parameters={"batch_data": data},
                batch_identifiers={"default_identifier_name": batch_id}
            )
            
            # Get checkpoint
            checkpoint = self.context.get_checkpoint("ifood_orders_checkpoint")
            
            # Run validation
            results = checkpoint.run(
                validations=[
                    {
                        "batch_request": batch_request,
                        "expectation_suite_name": "ifood_orders_quality_suite"
                    }
                ]
            )
            
            return {
                "success": results.success,
                "results": results.to_json_dict()
            }
            
        except Exception as e:
            logger.error(f"Great Expectations validation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
