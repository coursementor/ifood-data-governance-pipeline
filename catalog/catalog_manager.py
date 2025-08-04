"""
Data Catalog Manager
Provides high-level operations for managing the data catalog.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from catalog.data_catalog import (
    DataCatalog, DatasetMetadata, ColumnMetadata,
    DatasetType, DataClassification, DataLayer
)
from contracts.contract_validator import ContractValidator
from utils.config_loader import get_config

logger = logging.getLogger(__name__)


class CatalogManager:
    """High-level manager for data catalog operations."""
    
    def __init__(self):
        self.catalog = DataCatalog()
        self.config = get_config()
        
    def register_orders_dataset(
        self,
        layer: DataLayer,
        location: str,
        schema_name: str = "ifood_governance",
        table_name: str = "orders"
    ) -> str:
        """Register orders dataset in the catalog."""
        
        # Load contract for schema information
        contract_validator = ContractValidator()
        contract_info = contract_validator.get_contract_info()
        schema_fields = contract_validator.get_schema_fields()
        
        # Create column metadata from contract
        columns = []
        for field in schema_fields:
            column = ColumnMetadata(
                name=field['name'],
                data_type=field['type'],
                description=field['description'],
                is_nullable=not field['required'],
                is_pii=field.get('pii', False),
                is_sensitive=field.get('sensitive', False),
                classification=DataClassification.CONFIDENTIAL if field.get('sensitive') else DataClassification.INTERNAL
            )
            columns.append(column)
        
        # Determine dataset name based on layer
        dataset_name = f"{layer.value}_orders"
        
        # Create dataset metadata
        dataset = DatasetMetadata(
            id="",  # Will be generated
            name=dataset_name,
            description=f"iFood orders data in {layer.value} layer - {contract_info['description']}",
            dataset_type=DatasetType.TABLE,
            layer=layer,
            location=location,
            schema_name=schema_name,
            table_name=table_name,
            owner=contract_info['owner'],
            steward="data-engineering@ifood.com",
            domain=contract_info['domain'],
            classification=DataClassification.CONFIDENTIAL,
            columns=columns,
            primary_keys=["order_id"],
            foreign_keys={
                "customer_id": "customers.customer_id",
                "restaurant_id": "restaurants.restaurant_id"
            },
            business_purpose="Track and analyze iFood delivery orders throughout their lifecycle",
            usage_patterns=[
                "Real-time order monitoring",
                "Business intelligence and reporting",
                "Customer behavior analysis",
                "Operational metrics"
            ],
            refresh_frequency="15 minutes" if layer == DataLayer.BRONZE else "hourly",
            retention_policy="7 years (LGPD compliance)",
            contains_pii=True,
            lgpd_applicable=True,
            retention_days=2555,  # 7 years
            tags={
                "orders", "delivery", "ifood", "transactional",
                layer.value, "pii", "lgpd"
            },
            labels={
                "version": contract_info['version'],
                "sla_availability": str(contract_info['sla']['availability']),
                "sla_freshness": contract_info['sla']['freshness']
            }
        )
        
        # Register dataset
        dataset_id = self.catalog.register_dataset(dataset)
        
        logger.info(f"Registered {layer.value} orders dataset: {dataset_id}")
        
        return dataset_id
    
    def setup_orders_lineage(self) -> None:
        """Setup lineage relationships for orders datasets."""
        
        # Find datasets by layer
        bronze_datasets = self.catalog.search_datasets(layer=DataLayer.BRONZE, query="orders")
        silver_datasets = self.catalog.search_datasets(layer=DataLayer.SILVER, query="orders")
        gold_datasets = self.catalog.search_datasets(layer=DataLayer.GOLD, query="orders")
        
        # Create lineage relationships
        if bronze_datasets and silver_datasets:
            self.catalog.add_lineage_relationship(
                source_dataset_id=bronze_datasets[0].id,
                target_dataset_id=silver_datasets[0].id,
                relationship_type="transformation",
                transformation_logic="Data cleansing, PII masking, standardization",
                metadata={
                    "transformation_tool": "dbt",
                    "model_name": "silver_orders",
                    "quality_checks": True
                }
            )
        
        if silver_datasets and gold_datasets:
            self.catalog.add_lineage_relationship(
                source_dataset_id=silver_datasets[0].id,
                target_dataset_id=gold_datasets[0].id,
                relationship_type="aggregation",
                transformation_logic="Daily aggregation with business metrics",
                metadata={
                    "transformation_tool": "dbt",
                    "model_name": "gold_orders_daily_summary",
                    "aggregation_level": "daily"
                }
            )
        
        logger.info("Setup orders lineage relationships")
    
    def register_api_source(self) -> str:
        """Register the orders API as a data source."""
        
        # Create minimal column metadata for API
        api_columns = [
            ColumnMetadata(
                name="raw_json",
                data_type="json",
                description="Raw JSON response from orders API",
                is_nullable=False
            )
        ]
        
        dataset = DatasetMetadata(
            id="",
            name="orders_api_source",
            description="iFood Orders API - source of truth for order data",
            dataset_type=DatasetType.API,
            layer=DataLayer.BRONZE,  # Source layer
            location="https://api.ifood.com/orders",
            schema_name="external",
            table_name="orders_api",
            owner="platform-team@ifood.com",
            steward="data-engineering@ifood.com",
            domain="delivery",
            classification=DataClassification.INTERNAL,
            columns=api_columns,
            primary_keys=[],
            foreign_keys={},
            business_purpose="Real-time order data ingestion from operational systems",
            usage_patterns=["Data ingestion", "Real-time monitoring"],
            refresh_frequency="real-time",
            tags={"api", "source", "orders", "real-time"},
            labels={
                "api_version": "v2",
                "rate_limit": "1000/minute",
                "authentication": "oauth2"
            }
        )
        
        dataset_id = self.catalog.register_dataset(dataset)
        
        logger.info(f"Registered API source dataset: {dataset_id}")
        
        return dataset_id
    
    def update_dataset_quality_metrics(
        self,
        dataset_name: str,
        quality_results: Dict[str, Any]
    ) -> None:
        """Update quality metrics for a dataset."""
        
        datasets = self.catalog.search_datasets(query=dataset_name)
        
        if not datasets:
            logger.warning(f"Dataset not found: {dataset_name}")
            return
        
        dataset = datasets[0]  # Take first match
        
        # Extract quality metrics
        overall_score = quality_results.get('overall_score', 0)
        dimension_scores = quality_results.get('dimension_scores', {})
        
        # Update dataset
        self.catalog.update_dataset_statistics(
            dataset_id=dataset.id,
            quality_score=overall_score,
            row_count=quality_results.get('total_records')
        )
        
        # Update column statistics if available
        column_stats = {}
        for check in quality_results.get('quality_checks', []):
            if 'column' in check.get('details', {}):
                column_name = check['details']['column']
                if column_name not in column_stats:
                    column_stats[column_name] = {}
                
                column_stats[column_name][check['check_name']] = {
                    'score': check['score'],
                    'passed': check['passed'],
                    'message': check['message']
                }
        
        if column_stats:
            self.catalog.update_dataset_statistics(
                dataset_id=dataset.id,
                column_statistics=column_stats
            )
        
        logger.info(f"Updated quality metrics for dataset: {dataset_name}")
    
    def get_data_lineage_report(self, dataset_name: str) -> Dict[str, Any]:
        """Generate comprehensive lineage report for a dataset."""
        
        datasets = self.catalog.search_datasets(query=dataset_name)
        
        if not datasets:
            return {"error": f"Dataset not found: {dataset_name}"}
        
        dataset = datasets[0]
        
        # Get lineage information
        upstream_lineage = self.catalog.get_upstream_lineage(dataset.id)
        downstream_lineage = self.catalog.get_downstream_lineage(dataset.id)
        lineage_graph = self.catalog.generate_lineage_graph(dataset.id)
        
        return {
            "dataset": {
                "id": dataset.id,
                "name": dataset.name,
                "description": dataset.description,
                "layer": dataset.layer.value,
                "owner": dataset.owner,
                "quality_score": dataset.quality_score
            },
            "upstream_lineage": upstream_lineage,
            "downstream_lineage": downstream_lineage,
            "lineage_graph": lineage_graph,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def get_governance_dashboard_data(self) -> Dict[str, Any]:
        """Get data for governance dashboard."""
        
        catalog_summary = self.catalog.get_catalog_summary()
        
        # Get datasets by layer
        datasets_by_layer = {}
        for layer in DataLayer:
            datasets = self.catalog.search_datasets(layer=layer)
            datasets_by_layer[layer.value] = [
                {
                    "id": d.id,
                    "name": d.name,
                    "description": d.description,
                    "owner": d.owner,
                    "quality_score": d.quality_score,
                    "contains_pii": d.contains_pii,
                    "updated_at": d.updated_at.isoformat()
                }
                for d in datasets
            ]
        
        # Get PII datasets
        pii_datasets = self.catalog.search_datasets()
        pii_datasets = [d for d in pii_datasets if d.contains_pii]
        
        # Quality metrics
        quality_scores = [d.quality_score for d in self.catalog.datasets.values() if d.quality_score]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            "catalog_summary": catalog_summary,
            "datasets_by_layer": datasets_by_layer,
            "pii_datasets": [
                {
                    "name": d.name,
                    "classification": d.classification.value,
                    "retention_days": d.retention_days,
                    "owner": d.owner
                }
                for d in pii_datasets
            ],
            "quality_metrics": {
                "average_quality_score": avg_quality,
                "datasets_with_quality_data": len(quality_scores),
                "total_datasets": len(self.catalog.datasets)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def initialize_ifood_catalog(self) -> Dict[str, str]:
        """Initialize the complete iFood catalog structure."""
        
        logger.info("Initializing iFood data catalog...")
        
        dataset_ids = {}
        
        # Register API source
        dataset_ids['api_source'] = self.register_api_source()
        
        # Register orders datasets for each layer
        dataset_ids['bronze_orders'] = self.register_orders_dataset(
            layer=DataLayer.BRONZE,
            location="gcs://ifood-data-lake/bronze/orders/",
            table_name="bronze_orders"
        )
        
        dataset_ids['silver_orders'] = self.register_orders_dataset(
            layer=DataLayer.SILVER,
            location="gcs://ifood-data-lake/silver/orders/",
            table_name="silver_orders"
        )
        
        dataset_ids['gold_orders'] = self.register_orders_dataset(
            layer=DataLayer.GOLD,
            location="bigquery://ifood-project/ifood_dw.gold_orders_daily_summary",
            table_name="gold_orders_daily_summary"
        )
        
        # Setup lineage relationships
        self.setup_orders_lineage()
        
        logger.info("iFood data catalog initialization completed")
        
        return dataset_ids


# Global catalog manager instance
catalog_manager = CatalogManager()


def get_catalog_manager() -> CatalogManager:
    """Get global catalog manager instance."""
    return catalog_manager
