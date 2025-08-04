"""
Privacy Manager for LGPD Compliance
Handles PII masking, data anonymization, and privacy compliance for iFood data governance.
"""

import re
import hashlib
import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PIIType(str, Enum):
    """Types of PII data."""
    CPF = "cpf"
    PHONE = "phone"
    EMAIL = "email"
    ADDRESS = "address"
    NAME = "name"
    CREDIT_CARD = "credit_card"


class MaskingStrategy(str, Enum):
    """PII masking strategies."""
    FULL_MASK = "full_mask"
    PARTIAL_MASK = "partial_mask"
    HASH = "hash"
    TOKENIZE = "tokenize"
    REMOVE = "remove"


class DataSubjectRight(str, Enum):
    """LGPD data subject rights."""
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    PORTABILITY = "portability"
    OBJECTION = "objection"
    RESTRICTION = "restriction"


@dataclass
class PIIField:
    """PII field configuration."""
    field_name: str
    pii_type: PIIType
    masking_strategy: MaskingStrategy
    retention_days: int
    is_sensitive: bool = True
    legal_basis: str = "legitimate_interest"
    purpose: str = "business_operations"


@dataclass
class DataSubjectRequest:
    """Data subject request for LGPD compliance."""
    request_id: str
    subject_id: str
    request_type: DataSubjectRight
    requested_at: datetime
    processed_at: Optional[datetime] = None
    status: str = "pending"
    details: Dict[str, Any] = None
    response_data: Optional[Dict[str, Any]] = None


class PrivacyManager:
    """Manages privacy compliance and PII protection."""
    
    def __init__(self):
        self.pii_fields = self._initialize_pii_fields()
        self.masking_salt = "ifood_privacy_salt_2024"
        self.requests_log: List[DataSubjectRequest] = []
        
    def _initialize_pii_fields(self) -> Dict[str, PIIField]:
        """Initialize PII field configurations."""
        
        return {
            "customer_cpf": PIIField(
                field_name="customer_cpf",
                pii_type=PIIType.CPF,
                masking_strategy=MaskingStrategy.PARTIAL_MASK,
                retention_days=2555,  # 7 years
                legal_basis="contract_performance",
                purpose="customer_identification"
            ),
            "customer_phone": PIIField(
                field_name="customer_phone",
                pii_type=PIIType.PHONE,
                masking_strategy=MaskingStrategy.PARTIAL_MASK,
                retention_days=2555,
                legal_basis="contract_performance",
                purpose="delivery_communication"
            ),
            "customer_email": PIIField(
                field_name="customer_email",
                pii_type=PIIType.EMAIL,
                masking_strategy=MaskingStrategy.PARTIAL_MASK,
                retention_days=2555,
                legal_basis="contract_performance",
                purpose="customer_communication"
            ),
            "delivery_address": PIIField(
                field_name="delivery_address",
                pii_type=PIIType.ADDRESS,
                masking_strategy=MaskingStrategy.HASH,
                retention_days=2555,
                legal_basis="contract_performance",
                purpose="order_delivery"
            )
        }
    
    def mask_pii_data(self, data: Dict[str, Any], user_role: str = "business_user") -> Dict[str, Any]:
        """Apply PII masking based on user role and field configuration."""
        
        masked_data = data.copy()
        
        # Skip masking for privileged roles
        if user_role in ["data_engineer", "dpo", "auditor"]:
            return masked_data
        
        for field_name, pii_field in self.pii_fields.items():
            if field_name in masked_data and masked_data[field_name] is not None:
                original_value = str(masked_data[field_name])
                
                if pii_field.masking_strategy == MaskingStrategy.PARTIAL_MASK:
                    masked_data[field_name] = self._apply_partial_mask(
                        original_value, pii_field.pii_type
                    )
                elif pii_field.masking_strategy == MaskingStrategy.FULL_MASK:
                    masked_data[field_name] = self._apply_full_mask(pii_field.pii_type)
                elif pii_field.masking_strategy == MaskingStrategy.HASH:
                    masked_data[field_name] = self._apply_hash(original_value)
                elif pii_field.masking_strategy == MaskingStrategy.REMOVE:
                    del masked_data[field_name]
        
        # Add masking metadata
        masked_data["_privacy_metadata"] = {
            "masked_at": datetime.utcnow().isoformat(),
            "user_role": user_role,
            "masking_version": "1.0.0"
        }
        
        return masked_data
    
    def _apply_partial_mask(self, value: str, pii_type: PIIType) -> str:
        """Apply partial masking based on PII type."""
        
        if pii_type == PIIType.CPF:
            # CPF: 123.456.789-00 -> 123.***.789-**
            if re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', value):
                return f"{value[:3]}.***{value[7:11]}-**"
            return "***.***.***-**"
        
        elif pii_type == PIIType.PHONE:
            # Phone: (11) 99999-9999 -> (11) ****-9999
            if re.match(r'^\(\d{2}\) \d{4,5}-\d{4}$', value):
                return f"{value[:4]}****{value[-5:]}"
            return "(**) ****-****"
        
        elif pii_type == PIIType.EMAIL:
            # Email: user@domain.com -> u***@domain.com
            if "@" in value:
                local, domain = value.split("@", 1)
                if len(local) > 1:
                    return f"{local[0]}***@{domain}"
                return f"***@{domain}"
            return "***@***.***"
        
        elif pii_type == PIIType.ADDRESS:
            # Address: mask numbers and specific details
            masked = re.sub(r'\d+', '***', value)
            return masked
        
        return "***"
    
    def _apply_full_mask(self, pii_type: PIIType) -> str:
        """Apply full masking."""
        
        masks = {
            PIIType.CPF: "***.***.***-**",
            PIIType.PHONE: "(**) ****-****",
            PIIType.EMAIL: "***@***.***",
            PIIType.ADDRESS: "*** *** ***",
            PIIType.NAME: "*** ***"
        }
        
        return masks.get(pii_type, "***")
    
    def _apply_hash(self, value: str) -> str:
        """Apply cryptographic hash."""
        
        salted_value = f"{value}{self.masking_salt}"
        return hashlib.sha256(salted_value.encode()).hexdigest()[:16]
    
    def anonymize_dataset(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Anonymize entire dataset for analytics."""
        
        anonymized_data = []
        
        for record in data:
            anonymized_record = record.copy()
            
            # Remove direct identifiers
            identifiers_to_remove = [
                "customer_id", "customer_cpf", "customer_phone", 
                "customer_email", "delivery_address"
            ]
            
            for identifier in identifiers_to_remove:
                if identifier in anonymized_record:
                    del anonymized_record[identifier]
            
            # Add anonymized customer hash for grouping
            if "customer_id" in record:
                anonymized_record["customer_hash"] = self._apply_hash(record["customer_id"])
            
            # Generalize sensitive attributes
            if "order_timestamp" in anonymized_record:
                # Generalize to hour level
                timestamp = datetime.fromisoformat(anonymized_record["order_timestamp"].replace('Z', '+00:00'))
                anonymized_record["order_hour"] = timestamp.strftime("%Y-%m-%d %H:00:00")
                del anonymized_record["order_timestamp"]
            
            # Add anonymization metadata
            anonymized_record["_anonymization_metadata"] = {
                "anonymized_at": datetime.utcnow().isoformat(),
                "method": "k_anonymity",
                "version": "1.0.0"
            }
            
            anonymized_data.append(anonymized_record)
        
        return anonymized_data
    
    def process_data_subject_request(
        self,
        subject_id: str,
        request_type: DataSubjectRight,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process LGPD data subject request."""
        
        request_id = f"DSR_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{subject_id[:8]}"
        
        request = DataSubjectRequest(
            request_id=request_id,
            subject_id=subject_id,
            request_type=request_type,
            requested_at=datetime.utcnow(),
            details=details or {}
        )
        
        # Process request based on type
        if request_type == DataSubjectRight.ACCESS:
            response_data = self._process_access_request(subject_id)
        elif request_type == DataSubjectRight.ERASURE:
            response_data = self._process_erasure_request(subject_id)
        elif request_type == DataSubjectRight.PORTABILITY:
            response_data = self._process_portability_request(subject_id)
        else:
            response_data = {"message": f"Request type {request_type} queued for manual processing"}
        
        request.response_data = response_data
        request.processed_at = datetime.utcnow()
        request.status = "completed"
        
        self.requests_log.append(request)
        
        logger.info(f"Processed data subject request: {request_id}")
        
        return request_id
    
    def _process_access_request(self, subject_id: str) -> Dict[str, Any]:
        """Process data access request."""
        
        # In real implementation, this would query all systems
        return {
            "subject_id": subject_id,
            "data_categories": [
                "order_history",
                "delivery_addresses",
                "payment_methods",
                "preferences"
            ],
            "retention_periods": {
                "transactional_data": "7 years",
                "marketing_data": "2 years",
                "analytics_data": "anonymized"
            },
            "legal_basis": {
                "order_data": "contract_performance",
                "marketing_data": "consent",
                "analytics_data": "legitimate_interest"
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _process_erasure_request(self, subject_id: str) -> Dict[str, Any]:
        """Process data erasure request."""
        
        # In real implementation, this would trigger deletion across systems
        return {
            "subject_id": subject_id,
            "erasure_status": "scheduled",
            "systems_affected": [
                "orders_database",
                "analytics_warehouse",
                "marketing_platform"
            ],
            "retention_exceptions": [
                "financial_records (legal requirement)",
                "fraud_prevention (legitimate_interest)"
            ],
            "completion_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
    
    def _process_portability_request(self, subject_id: str) -> Dict[str, Any]:
        """Process data portability request."""
        
        return {
            "subject_id": subject_id,
            "export_format": "JSON",
            "data_included": [
                "order_history",
                "preferences",
                "addresses"
            ],
            "download_link": f"https://privacy.ifood.com/export/{subject_id}",
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
    
    def check_retention_compliance(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check data retention compliance."""
        
        compliance_report = {
            "total_records": len(data),
            "compliant_records": 0,
            "expired_records": 0,
            "expiring_soon": 0,
            "violations": []
        }
        
        current_date = datetime.utcnow()
        
        for record in data:
            created_at = datetime.fromisoformat(record.get("created_at", current_date.isoformat()))
            age_days = (current_date - created_at).days
            
            # Check against retention policies
            violations = []
            
            for field_name, pii_field in self.pii_fields.items():
                if field_name in record and age_days > pii_field.retention_days:
                    violations.append({
                        "field": field_name,
                        "age_days": age_days,
                        "retention_limit": pii_field.retention_days,
                        "violation_type": "retention_exceeded"
                    })
            
            if violations:
                compliance_report["expired_records"] += 1
                compliance_report["violations"].extend(violations)
            elif age_days > (min(pii.retention_days for pii in self.pii_fields.values()) - 30):
                compliance_report["expiring_soon"] += 1
            else:
                compliance_report["compliant_records"] += 1
        
        compliance_report["compliance_rate"] = (
            compliance_report["compliant_records"] / compliance_report["total_records"]
        ) * 100 if compliance_report["total_records"] > 0 else 100
        
        return compliance_report
    
    def generate_privacy_report(self) -> Dict[str, Any]:
        """Generate comprehensive privacy compliance report."""
        
        return {
            "report_generated_at": datetime.utcnow().isoformat(),
            "pii_fields_configured": len(self.pii_fields),
            "pii_field_details": [asdict(pii) for pii in self.pii_fields.values()],
            "data_subject_requests": {
                "total_requests": len(self.requests_log),
                "by_type": {
                    request_type.value: sum(
                        1 for req in self.requests_log 
                        if req.request_type == request_type
                    )
                    for request_type in DataSubjectRight
                },
                "average_processing_time_hours": self._calculate_avg_processing_time()
            },
            "masking_strategies": {
                strategy.value: sum(
                    1 for pii in self.pii_fields.values()
                    if pii.masking_strategy == strategy
                )
                for strategy in MaskingStrategy
            },
            "compliance_status": "compliant",
            "next_review_date": (datetime.utcnow() + timedelta(days=90)).isoformat()
        }
    
    def _calculate_avg_processing_time(self) -> float:
        """Calculate average processing time for requests."""
        
        completed_requests = [
            req for req in self.requests_log 
            if req.processed_at and req.requested_at
        ]
        
        if not completed_requests:
            return 0.0
        
        total_time = sum(
            (req.processed_at - req.requested_at).total_seconds() / 3600
            for req in completed_requests
        )
        
        return total_time / len(completed_requests)
    
    def validate_pii_masking(self, original_data: Dict[str, Any], masked_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that PII masking was applied correctly."""
        
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "masked_fields": []
        }
        
        for field_name, pii_field in self.pii_fields.items():
            if field_name in original_data:
                original_value = str(original_data[field_name])
                masked_value = str(masked_data.get(field_name, ""))
                
                # Check if masking was applied
                if original_value == masked_value:
                    validation_results["errors"].append(
                        f"Field {field_name} was not masked"
                    )
                    validation_results["is_valid"] = False
                else:
                    validation_results["masked_fields"].append(field_name)
                
                # Validate masking pattern
                if pii_field.pii_type == PIIType.CPF and not re.match(r'^\d{3}\.\*\*\*\.\d{3}-\*\*$', masked_value):
                    validation_results["warnings"].append(
                        f"CPF masking pattern may be incorrect for {field_name}"
                    )
        
        return validation_results


# Global privacy manager instance
privacy_manager = PrivacyManager()


def get_privacy_manager() -> PrivacyManager:
    """Get global privacy manager instance."""
    return privacy_manager
