"""
Data Contract Validator for iFood Orders
Validates data against defined contracts using Pydantic and custom rules.
"""

import yaml
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
import logging
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field, validator, ValidationError
try:
    from pydantic import EmailStr
except ImportError:
    try:
        from pydantic.types import EmailStr
    except ImportError:
        # Fallback for older versions or if email-validator is not installed
        EmailStr = str
import re

logger = logging.getLogger(__name__)


class OrderStatus(str, Enum):
    """Valid order statuses."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY_FOR_PICKUP = "ready_for_pickup"
    IN_DELIVERY = "in_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class CancellationReason(str, Enum):
    """Valid cancellation reasons."""
    CUSTOMER_REQUEST = "customer_request"
    RESTAURANT_UNAVAILABLE = "restaurant_unavailable"
    PAYMENT_FAILED = "payment_failed"
    DELIVERY_FAILED = "delivery_failed"
    SYSTEM_ERROR = "system_error"


class Channel(str, Enum):
    """Valid order channels."""
    APP = "app"
    WEBSITE = "website"
    PHONE = "phone"
    WHATSAPP = "whatsapp"


class Platform(str, Enum):
    """Valid platforms."""
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"
    MOBILE_WEB = "mobile_web"


class PaymentMethod(str, Enum):
    """Valid payment methods."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PIX = "pix"
    CASH = "cash"
    VOUCHER = "voucher"


class DeliveryAddress(BaseModel):
    """Delivery address model."""
    street: str
    number: str
    complement: Optional[str] = None
    neighborhood: str
    city: str
    state: str = Field(..., pattern=r"^[A-Z]{2}$")
    zipcode: str = Field(..., pattern=r"^[0-9]{5}-[0-9]{3}$")


class OrderItem(BaseModel):
    """Order item model."""
    item_id: str
    name: str
    quantity: int = Field(..., ge=1)
    unit_price: float = Field(..., ge=0)
    observations: Optional[str] = None


class Order(BaseModel):
    """Main order model based on data contract."""
    
    # Identificadores
    order_id: str = Field(..., pattern=r"^ORD[0-9]{10}$")
    customer_id: str = Field(..., pattern=r"^CUST[0-9]{8}$")
    restaurant_id: str = Field(..., pattern=r"^REST[0-9]{6}$")
    
    # Timestamps
    order_timestamp: datetime
    estimated_delivery_time: datetime
    actual_delivery_time: Optional[datetime] = None
    
    # Status
    status: OrderStatus
    cancellation_reason: Optional[CancellationReason] = None
    
    # Valores
    total_amount: float = Field(..., ge=0, le=10000)
    delivery_fee: float = Field(..., ge=0, le=50)
    discount_amount: float = Field(default=0, ge=0)
    
    # PII
    customer_cpf: str = Field(..., pattern=r"^[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}$")
    customer_phone: str = Field(..., pattern=r"^\([0-9]{2}\) [0-9]{4,5}-[0-9]{4}$")
    customer_email: EmailStr
    delivery_address: DeliveryAddress
    
    # Itens
    items: List[OrderItem] = Field(..., min_items=1)
    
    # Metadados
    channel: Channel
    platform: Platform
    payment_method: PaymentMethod
    
    # Rastreabilidade
    created_at: datetime
    updated_at: datetime
    data_source: str
    batch_id: str
    
    @validator('actual_delivery_time')
    def validate_delivery_time(cls, v, values):
        """Validate that delivery time is after order time."""
        if v and 'order_timestamp' in values:
            if v <= values['order_timestamp']:
                raise ValueError('Delivery time must be after order time')
        return v
    
    @validator('estimated_delivery_time')
    def validate_estimated_delivery_time(cls, v, values):
        """Validate that estimated delivery time is reasonable."""
        if 'order_timestamp' in values:
            order_time = values['order_timestamp']
            if v <= order_time:
                raise ValueError('Estimated delivery time must be after order time')
            if v > order_time + timedelta(hours=3):
                raise ValueError('Estimated delivery time too far in the future')
        return v
    
    @validator('cancellation_reason')
    def validate_cancellation_reason(cls, v, values):
        """Validate cancellation reason is provided for cancelled orders."""
        if 'status' in values:
            if values['status'] == OrderStatus.CANCELLED and not v:
                raise ValueError('Cancellation reason required for cancelled orders')
            if values['status'] != OrderStatus.CANCELLED and v:
                raise ValueError('Cancellation reason only valid for cancelled orders')
        return v
    
    @validator('total_amount')
    def validate_total_amount(cls, v, values):
        """Validate total amount calculation."""
        # This would be more complex in real implementation
        if v <= 0:
            raise ValueError('Total amount must be positive')
        return v


@dataclass
class ValidationResult:
    """Result of contract validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    record_count: int
    valid_count: int
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.record_count == 0:
            return 0.0
        return self.valid_count / self.record_count


class ContractValidator:
    """Validates data against contract specifications."""
    
    def __init__(self, contract_path: str = "contracts/orders_contract.yaml"):
        self.contract_path = Path(contract_path)
        self.contract = self._load_contract()
        
    def _load_contract(self) -> Dict[str, Any]:
        """Load contract from YAML file."""
        if not self.contract_path.exists():
            raise FileNotFoundError(f"Contract file not found: {self.contract_path}")
            
        with open(self.contract_path, 'r', encoding='utf-8') as file:
            contract = yaml.safe_load(file)
            
        logger.info(f"Contract loaded: {contract['contract']['name']} v{contract['contract']['version']}")
        return contract
    
    def validate_record(self, record: Dict[str, Any]) -> ValidationResult:
        """Validate a single record against the contract."""
        errors = []
        warnings = []
        
        try:
            # Validate using Pydantic model
            order = Order(**record)
            
            # Additional custom validations
            custom_errors = self._run_custom_validations(record)
            errors.extend(custom_errors)
            
            is_valid = len(errors) == 0
            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                record_count=1,
                valid_count=1 if is_valid else 0
            )
            
        except ValidationError as e:
            for error in e.errors():
                field = '.'.join(str(loc) for loc in error['loc'])
                message = f"Field '{field}': {error['msg']}"
                errors.append(message)
                
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                record_count=1,
                valid_count=0
            )
    
    def validate_batch(self, records: List[Dict[str, Any]]) -> ValidationResult:
        """Validate a batch of records."""
        all_errors = []
        all_warnings = []
        valid_count = 0
        
        for i, record in enumerate(records):
            result = self.validate_record(record)
            
            if result.is_valid:
                valid_count += 1
            else:
                # Add record index to errors
                for error in result.errors:
                    all_errors.append(f"Record {i}: {error}")
                    
            all_warnings.extend([f"Record {i}: {w}" for w in result.warnings])
        
        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            record_count=len(records),
            valid_count=valid_count
        )
    
    def _run_custom_validations(self, record: Dict[str, Any]) -> List[str]:
        """Run custom validation rules defined in contract."""
        errors = []
        
        # Status transition validation
        if not self._validate_status_transition(record):
            errors.append("Invalid status transition")
            
        # Business rule validations
        if record.get('total_amount', 0) < record.get('delivery_fee', 0):
            errors.append("Total amount cannot be less than delivery fee")
            
        return errors
    
    def _validate_status_transition(self, record: Dict[str, Any]) -> bool:
        """Validate status transitions are logical."""
        # This would check against previous status in real implementation
        # For now, just basic validation
        status = record.get('status')
        cancellation_reason = record.get('cancellation_reason')
        
        if status == 'cancelled' and not cancellation_reason:
            return False
            
        return True
    
    def get_contract_info(self) -> Dict[str, Any]:
        """Get contract information."""
        contract_info = self.contract['contract']
        return {
            'name': contract_info['name'],
            'version': contract_info['version'],
            'description': contract_info['description'],
            'owner': contract_info['owner'],
            'domain': contract_info['domain'],
            'sla': contract_info['sla']
        }
    
    def get_schema_fields(self) -> List[Dict[str, Any]]:
        """Get schema field information."""
        schema = self.contract['contract']['schema']
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        fields = []
        for field_name, field_info in properties.items():
            fields.append({
                'name': field_name,
                'type': field_info.get('type'),
                'required': field_name in required,
                'description': field_info.get('description'),
                'pii': field_info.get('pii', False),
                'sensitive': field_info.get('sensitive', False)
            })
            
        return fields
