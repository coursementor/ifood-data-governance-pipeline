"""
Great Expectations Configuration for iFood Data Governance
Configures data quality validation framework with custom expectations and alerting.
"""

import os
from typing import Dict, Any, List
import great_expectations as gx
from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.checkpoint import SimpleCheckpoint
from great_expectations.data_context import BaseDataContext
from great_expectations.data_context.types.base import DataContextConfig
from great_expectations.datasource import BaseDatasource
import logging

logger = logging.getLogger(__name__)


class IFoodDataQualityConfig:
    """Configuration class for iFood data quality framework."""
    
    def __init__(self, config_dir: str = "data_quality/gx_config"):
        self.config_dir = config_dir
        self.context = None
        self._setup_context()
        
    def _setup_context(self) -> None:
        """Setup Great Expectations context."""
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Data context configuration
        data_context_config = DataContextConfig(
            config_version=3.0,
            datasources={
                "postgres_datasource": {
                    "class_name": "Datasource",
                    "execution_engine": {
                        "class_name": "SqlAlchemyExecutionEngine",
                        "connection_string": os.getenv("POSTGRES_CONNECTION_STRING", 
                                                     "postgresql://user:password@localhost:5432/ifood_governance")
                    },
                    "data_connectors": {
                        "default_runtime_data_connector": {
                            "class_name": "RuntimeDataConnector",
                            "batch_identifiers": ["default_identifier_name"]
                        }
                    }
                },
                "bigquery_datasource": {
                    "class_name": "Datasource",
                    "execution_engine": {
                        "class_name": "SqlAlchemyExecutionEngine",
                        "connection_string": f"bigquery://{os.getenv('GCP_PROJECT_ID')}/ifood_data_governance"
                    },
                    "data_connectors": {
                        "default_runtime_data_connector": {
                            "class_name": "RuntimeDataConnector",
                            "batch_identifiers": ["default_identifier_name"]
                        }
                    }
                }
            },
            stores={
                "expectations_store": {
                    "class_name": "ExpectationsStore",
                    "store_backend": {
                        "class_name": "TupleFilesystemStoreBackend",
                        "base_directory": f"{self.config_dir}/expectations/"
                    }
                },
                "validations_store": {
                    "class_name": "ValidationsStore",
                    "store_backend": {
                        "class_name": "TupleFilesystemStoreBackend",
                        "base_directory": f"{self.config_dir}/validations/"
                    }
                },
                "evaluation_parameter_store": {
                    "class_name": "EvaluationParameterStore"
                },
                "checkpoint_store": {
                    "class_name": "CheckpointStore",
                    "store_backend": {
                        "class_name": "TupleFilesystemStoreBackend",
                        "base_directory": f"{self.config_dir}/checkpoints/"
                    }
                }
            },
            expectations_store_name="expectations_store",
            validations_store_name="validations_store",
            evaluation_parameter_store_name="evaluation_parameter_store",
            checkpoint_store_name="checkpoint_store",
            data_docs_sites={
                "local_site": {
                    "class_name": "SiteBuilder",
                    "show_how_to_buttons": True,
                    "store_backend": {
                        "class_name": "TupleFilesystemStoreBackend",
                        "base_directory": f"{self.config_dir}/data_docs/"
                    },
                    "site_index_builder": {
                        "class_name": "DefaultSiteIndexBuilder"
                    }
                }
            },
            anonymous_usage_statistics={
                "enabled": False
            }
        )
        
        # Initialize context
        self.context = BaseDataContext(project_config=data_context_config)
        logger.info("Great Expectations context initialized successfully")
    
    def create_orders_expectation_suite(self) -> str:
        """Create expectation suite for orders data."""
        
        suite_name = "ifood_orders_quality_suite"
        
        # Create or get existing suite
        try:
            suite = self.context.get_expectation_suite(suite_name)
            logger.info(f"Using existing expectation suite: {suite_name}")
        except:
            suite = self.context.create_expectation_suite(suite_name)
            logger.info(f"Created new expectation suite: {suite_name}")
        
        # Clear existing expectations
        suite.expectations = []
        
        # Core data integrity expectations
        expectations = [
            # Primary key constraints
            {
                "expectation_type": "expect_column_values_to_be_unique",
                "kwargs": {"column": "order_id"}
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "order_id"}
            },
            {
                "expectation_type": "expect_column_values_to_match_regex",
                "kwargs": {
                    "column": "order_id",
                    "regex": r"^ORD[0-9]{10}$"
                }
            },
            
            # Foreign key constraints
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "customer_id"}
            },
            {
                "expectation_type": "expect_column_values_to_match_regex",
                "kwargs": {
                    "column": "customer_id",
                    "regex": r"^CUST[0-9]{8}$"
                }
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "restaurant_id"}
            },
            {
                "expectation_type": "expect_column_values_to_match_regex",
                "kwargs": {
                    "column": "restaurant_id",
                    "regex": r"^REST[0-9]{6}$"
                }
            },
            
            # Timestamp validations
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "order_timestamp"}
            },
            {
                "expectation_type": "expect_column_values_to_be_of_type",
                "kwargs": {
                    "column": "order_timestamp",
                    "type_": "datetime64[ns]"
                }
            },
            
            # Status validations
            {
                "expectation_type": "expect_column_values_to_be_in_set",
                "kwargs": {
                    "column": "order_status",
                    "value_set": ["PENDING", "CONFIRMED", "PREPARING", "READY_FOR_PICKUP", 
                                 "IN_DELIVERY", "DELIVERED", "CANCELLED"]
                }
            },
            
            # Financial validations
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {
                    "column": "total_amount",
                    "min_value": 0,
                    "max_value": 1000
                }
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {
                    "column": "delivery_fee",
                    "min_value": 0,
                    "max_value": 50
                }
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {
                    "column": "discount_amount",
                    "min_value": 0,
                    "max_value": 500
                }
            },
            
            # PII format validations (for masked data)
            {
                "expectation_type": "expect_column_values_to_match_regex",
                "kwargs": {
                    "column": "customer_cpf_masked",
                    "regex": r"^[0-9]{3}\.\*\*\*\.[0-9]{3}-\*\*$"
                }
            },
            {
                "expectation_type": "expect_column_values_to_match_regex",
                "kwargs": {
                    "column": "customer_phone_masked",
                    "regex": r"^\([0-9]{2}\) \*\*\*\*-[0-9]{4}$"
                }
            },
            
            # Business logic validations
            {
                "expectation_type": "expect_column_pair_values_A_to_be_greater_than_B",
                "kwargs": {
                    "column_A": "total_amount",
                    "column_B": "delivery_fee"
                }
            },
            {
                "expectation_type": "expect_column_pair_values_A_to_be_greater_than_B",
                "kwargs": {
                    "column_A": "estimated_delivery_time",
                    "column_B": "order_timestamp"
                }
            },
            
            # Data completeness expectations
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "channel"}
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "platform"}
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "payment_method"}
            },
            
            # Data quality score validation
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {
                    "column": "data_quality_score",
                    "min_value": 0,
                    "max_value": 100
                }
            },
            {
                "expectation_type": "expect_column_mean_to_be_between",
                "kwargs": {
                    "column": "data_quality_score",
                    "min_value": 75,
                    "max_value": 100
                }
            },
            
            # Table-level expectations
            {
                "expectation_type": "expect_table_row_count_to_be_between",
                "kwargs": {
                    "min_value": 1,
                    "max_value": 100000
                }
            }
        ]
        
        # Add expectations to suite
        for expectation in expectations:
            suite.add_expectation(
                gx.expectations.registry.get_expectation_class_from_expectation_type(
                    expectation["expectation_type"]
                )(**expectation["kwargs"])
            )
        
        # Save suite
        self.context.save_expectation_suite(suite)
        logger.info(f"Created expectation suite with {len(expectations)} expectations")
        
        return suite_name
    
    def create_checkpoint(self, suite_name: str) -> str:
        """Create checkpoint for automated validation."""
        
        checkpoint_name = "ifood_orders_checkpoint"
        
        checkpoint_config = {
            "name": checkpoint_name,
            "config_version": 1.0,
            "template_name": None,
            "module_name": "great_expectations.checkpoint",
            "class_name": "SimpleCheckpoint",
            "run_name_template": "%Y%m%d-%H%M%S-ifood-orders-validation",
            "expectation_suite_name": suite_name,
            "batch_request": {},
            "action_list": [
                {
                    "name": "store_validation_result",
                    "action": {
                        "class_name": "StoreValidationResultAction"
                    }
                },
                {
                    "name": "update_data_docs",
                    "action": {
                        "class_name": "UpdateDataDocsAction"
                    }
                },
                {
                    "name": "send_slack_notification",
                    "action": {
                        "class_name": "SlackNotificationAction",
                        "slack_webhook": os.getenv("SLACK_WEBHOOK_URL"),
                        "notify_on": "failure"
                    }
                }
            ],
            "evaluation_parameters": {},
            "runtime_configuration": {},
            "validations": []
        }
        
        # Save checkpoint
        self.context.add_checkpoint(**checkpoint_config)
        logger.info(f"Created checkpoint: {checkpoint_name}")
        
        return checkpoint_name
    
    def get_context(self) -> BaseDataContext:
        """Get Great Expectations context."""
        return self.context


def setup_ifood_data_quality() -> IFoodDataQualityConfig:
    """Setup iFood data quality configuration."""
    
    logger.info("Setting up iFood data quality framework...")
    
    # Initialize configuration
    config = IFoodDataQualityConfig()
    
    # Create expectation suite
    suite_name = config.create_orders_expectation_suite()
    
    # Create checkpoint
    checkpoint_name = config.create_checkpoint(suite_name)
    
    logger.info("iFood data quality framework setup completed successfully")
    
    return config


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Setup data quality framework
    config = setup_ifood_data_quality()
    
    print("Great Expectations configuration completed!")
    print(f"Config directory: {config.config_dir}")
    print("You can now run data quality validations using the created checkpoint.")
