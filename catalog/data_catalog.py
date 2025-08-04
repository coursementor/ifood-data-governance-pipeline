"""
Data Catalog System for iFood Data Governance
Provides comprehensive data cataloging, metadata management, and lineage tracking.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DatasetType(str, Enum):
    """Types of datasets in the catalog."""
    TABLE = "table"
    VIEW = "view"
    FILE = "file"
    API = "api"
    STREAM = "stream"


class DataClassification(str, Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class DataLayer(str, Enum):
    """Data architecture layers."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    MART = "mart"


@dataclass
class ColumnMetadata:
    """Metadata for a dataset column."""
    name: str
    data_type: str
    description: str
    is_nullable: bool = True
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_reference: Optional[str] = None
    is_pii: bool = False
    is_sensitive: bool = False
    classification: DataClassification = DataClassification.INTERNAL
    business_rules: List[str] = field(default_factory=list)
    quality_rules: List[str] = field(default_factory=list)
    sample_values: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DatasetMetadata:
    """Comprehensive metadata for a dataset."""
    id: str
    name: str
    description: str
    dataset_type: DatasetType
    layer: DataLayer
    location: str
    schema_name: str
    table_name: str
    
    # Ownership and governance
    owner: str
    steward: str
    domain: str
    classification: DataClassification
    
    # Schema information
    columns: List[ColumnMetadata]
    primary_keys: List[str]
    foreign_keys: Dict[str, str]
    
    # Data characteristics
    row_count: Optional[int] = None
    size_bytes: Optional[int] = None
    partitioning: Optional[Dict[str, Any]] = None
    
    # Temporal information
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    
    # Quality and lineage
    quality_score: Optional[float] = None
    lineage_upstream: List[str] = field(default_factory=list)
    lineage_downstream: List[str] = field(default_factory=list)
    
    # Business context
    business_purpose: str = ""
    usage_patterns: List[str] = field(default_factory=list)
    access_patterns: Dict[str, Any] = field(default_factory=dict)
    
    # Technical details
    refresh_frequency: Optional[str] = None
    retention_policy: Optional[str] = None
    backup_policy: Optional[str] = None
    
    # Tags and labels
    tags: Set[str] = field(default_factory=set)
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Compliance and privacy
    contains_pii: bool = False
    gdpr_applicable: bool = False
    lgpd_applicable: bool = True
    retention_days: Optional[int] = None


@dataclass
class LineageRelationship:
    """Represents a lineage relationship between datasets."""
    id: str
    source_dataset_id: str
    target_dataset_id: str
    relationship_type: str  # transformation, copy, aggregation, etc.
    transformation_logic: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataCatalog:
    """Main data catalog system."""
    
    def __init__(self, storage_path: str = "catalog/catalog_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.datasets: Dict[str, DatasetMetadata] = {}
        self.lineage_relationships: Dict[str, LineageRelationship] = {}
        
        self._load_catalog()
    
    def register_dataset(self, dataset: DatasetMetadata) -> str:
        """Register a new dataset in the catalog."""
        
        if not dataset.id:
            dataset.id = str(uuid.uuid4())
        
        dataset.updated_at = datetime.utcnow()
        
        # Validate dataset
        self._validate_dataset(dataset)
        
        # Store dataset
        self.datasets[dataset.id] = dataset
        
        # Save to storage
        self._save_dataset(dataset)
        
        logger.info(f"Registered dataset: {dataset.name} ({dataset.id})")
        
        return dataset.id
    
    def get_dataset(self, dataset_id: str) -> Optional[DatasetMetadata]:
        """Get dataset by ID."""
        return self.datasets.get(dataset_id)
    
    def search_datasets(
        self,
        query: str = "",
        layer: Optional[DataLayer] = None,
        domain: Optional[str] = None,
        owner: Optional[str] = None,
        tags: Optional[List[str]] = None,
        classification: Optional[DataClassification] = None
    ) -> List[DatasetMetadata]:
        """Search datasets based on criteria."""
        
        results = []
        
        for dataset in self.datasets.values():
            # Text search in name and description
            if query and query.lower() not in (dataset.name + " " + dataset.description).lower():
                continue
            
            # Layer filter
            if layer and dataset.layer != layer:
                continue
            
            # Domain filter
            if domain and dataset.domain != domain:
                continue
            
            # Owner filter
            if owner and dataset.owner != owner:
                continue
            
            # Tags filter
            if tags and not any(tag in dataset.tags for tag in tags):
                continue
            
            # Classification filter
            if classification and dataset.classification != classification:
                continue
            
            results.append(dataset)
        
        # Sort by relevance (name match first, then updated_at)
        results.sort(key=lambda d: (
            query.lower() not in d.name.lower(),
            -d.updated_at.timestamp()
        ))
        
        return results
    
    def add_lineage_relationship(
        self,
        source_dataset_id: str,
        target_dataset_id: str,
        relationship_type: str,
        transformation_logic: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a lineage relationship between datasets."""
        
        relationship_id = str(uuid.uuid4())
        
        relationship = LineageRelationship(
            id=relationship_id,
            source_dataset_id=source_dataset_id,
            target_dataset_id=target_dataset_id,
            relationship_type=relationship_type,
            transformation_logic=transformation_logic,
            metadata=metadata or {}
        )
        
        self.lineage_relationships[relationship_id] = relationship
        
        # Update dataset lineage references
        if source_dataset_id in self.datasets:
            self.datasets[source_dataset_id].lineage_downstream.append(target_dataset_id)
        
        if target_dataset_id in self.datasets:
            self.datasets[target_dataset_id].lineage_upstream.append(source_dataset_id)
        
        self._save_lineage_relationship(relationship)
        
        logger.info(f"Added lineage relationship: {source_dataset_id} -> {target_dataset_id}")
        
        return relationship_id
    
    def get_upstream_lineage(self, dataset_id: str, depth: int = 5) -> Dict[str, Any]:
        """Get upstream lineage for a dataset."""
        
        def _get_upstream_recursive(current_id: str, current_depth: int) -> Dict[str, Any]:
            if current_depth <= 0 or current_id not in self.datasets:
                return {}
            
            dataset = self.datasets[current_id]
            upstream_data = {
                "dataset": asdict(dataset),
                "upstream": {}
            }
            
            for upstream_id in dataset.lineage_upstream:
                upstream_data["upstream"][upstream_id] = _get_upstream_recursive(
                    upstream_id, current_depth - 1
                )
            
            return upstream_data
        
        return _get_upstream_recursive(dataset_id, depth)
    
    def get_downstream_lineage(self, dataset_id: str, depth: int = 5) -> Dict[str, Any]:
        """Get downstream lineage for a dataset."""
        
        def _get_downstream_recursive(current_id: str, current_depth: int) -> Dict[str, Any]:
            if current_depth <= 0 or current_id not in self.datasets:
                return {}
            
            dataset = self.datasets[current_id]
            downstream_data = {
                "dataset": asdict(dataset),
                "downstream": {}
            }
            
            for downstream_id in dataset.lineage_downstream:
                downstream_data["downstream"][downstream_id] = _get_downstream_recursive(
                    downstream_id, current_depth - 1
                )
            
            return downstream_data
        
        return _get_downstream_recursive(dataset_id, depth)
    
    def generate_lineage_graph(self, dataset_id: str) -> Dict[str, Any]:
        """Generate a complete lineage graph for visualization."""
        
        nodes = {}
        edges = []
        visited = set()
        
        def _add_dataset_to_graph(current_id: str):
            if current_id in visited or current_id not in self.datasets:
                return
            
            visited.add(current_id)
            dataset = self.datasets[current_id]
            
            # Add node
            nodes[current_id] = {
                "id": current_id,
                "name": dataset.name,
                "type": dataset.dataset_type.value,
                "layer": dataset.layer.value,
                "domain": dataset.domain,
                "classification": dataset.classification.value
            }
            
            # Add upstream relationships
            for upstream_id in dataset.lineage_upstream:
                edges.append({
                    "source": upstream_id,
                    "target": current_id,
                    "type": "upstream"
                })
                _add_dataset_to_graph(upstream_id)
            
            # Add downstream relationships
            for downstream_id in dataset.lineage_downstream:
                edges.append({
                    "source": current_id,
                    "target": downstream_id,
                    "type": "downstream"
                })
                _add_dataset_to_graph(downstream_id)
        
        _add_dataset_to_graph(dataset_id)
        
        return {
            "nodes": list(nodes.values()),
            "edges": edges,
            "center_node": dataset_id,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def update_dataset_statistics(
        self,
        dataset_id: str,
        row_count: Optional[int] = None,
        size_bytes: Optional[int] = None,
        quality_score: Optional[float] = None,
        column_statistics: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> None:
        """Update dataset statistics."""
        
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset {dataset_id} not found")
        
        dataset = self.datasets[dataset_id]
        
        if row_count is not None:
            dataset.row_count = row_count
        
        if size_bytes is not None:
            dataset.size_bytes = size_bytes
        
        if quality_score is not None:
            dataset.quality_score = quality_score
        
        if column_statistics:
            for column in dataset.columns:
                if column.name in column_statistics:
                    column.statistics.update(column_statistics[column.name])
        
        dataset.updated_at = datetime.utcnow()
        self._save_dataset(dataset)
        
        logger.info(f"Updated statistics for dataset: {dataset.name}")
    
    def get_catalog_summary(self) -> Dict[str, Any]:
        """Get catalog summary statistics."""
        
        total_datasets = len(self.datasets)
        
        # Count by layer
        layer_counts = {}
        for layer in DataLayer:
            layer_counts[layer.value] = sum(
                1 for d in self.datasets.values() if d.layer == layer
            )
        
        # Count by classification
        classification_counts = {}
        for classification in DataClassification:
            classification_counts[classification.value] = sum(
                1 for d in self.datasets.values() if d.classification == classification
            )
        
        # Count datasets with PII
        pii_datasets = sum(1 for d in self.datasets.values() if d.contains_pii)
        
        # Average quality score
        quality_scores = [d.quality_score for d in self.datasets.values() if d.quality_score]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else None
        
        return {
            "total_datasets": total_datasets,
            "layer_distribution": layer_counts,
            "classification_distribution": classification_counts,
            "datasets_with_pii": pii_datasets,
            "average_quality_score": avg_quality,
            "total_lineage_relationships": len(self.lineage_relationships),
            "last_updated": max(
                (d.updated_at for d in self.datasets.values()),
                default=datetime.utcnow()
            ).isoformat()
        }
    
    def _validate_dataset(self, dataset: DatasetMetadata) -> None:
        """Validate dataset metadata."""
        
        if not dataset.name:
            raise ValueError("Dataset name is required")
        
        if not dataset.owner:
            raise ValueError("Dataset owner is required")
        
        if not dataset.domain:
            raise ValueError("Dataset domain is required")
        
        # Validate column metadata
        for column in dataset.columns:
            if not column.name:
                raise ValueError("Column name is required")
            
            if not column.data_type:
                raise ValueError(f"Data type is required for column {column.name}")
    
    def _save_dataset(self, dataset: DatasetMetadata) -> None:
        """Save dataset to storage."""
        
        dataset_file = self.storage_path / f"dataset_{dataset.id}.json"
        
        with open(dataset_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(dataset), f, indent=2, default=str)
    
    def _save_lineage_relationship(self, relationship: LineageRelationship) -> None:
        """Save lineage relationship to storage."""
        
        lineage_file = self.storage_path / f"lineage_{relationship.id}.json"
        
        with open(lineage_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(relationship), f, indent=2, default=str)
    
    def _load_catalog(self) -> None:
        """Load catalog from storage."""
        
        # Load datasets
        for dataset_file in self.storage_path.glob("dataset_*.json"):
            try:
                with open(dataset_file, 'r', encoding='utf-8') as f:
                    dataset_data = json.load(f)
                
                # Convert back to dataclass (simplified)
                dataset = DatasetMetadata(**dataset_data)
                self.datasets[dataset.id] = dataset
                
            except Exception as e:
                logger.error(f"Error loading dataset from {dataset_file}: {e}")
        
        # Load lineage relationships
        for lineage_file in self.storage_path.glob("lineage_*.json"):
            try:
                with open(lineage_file, 'r', encoding='utf-8') as f:
                    lineage_data = json.load(f)
                
                relationship = LineageRelationship(**lineage_data)
                self.lineage_relationships[relationship.id] = relationship
                
            except Exception as e:
                logger.error(f"Error loading lineage from {lineage_file}: {e}")
        
        logger.info(f"Loaded {len(self.datasets)} datasets and {len(self.lineage_relationships)} lineage relationships")


# Global catalog instance
catalog = DataCatalog()


def get_catalog() -> DataCatalog:
    """Get global catalog instance."""
    return catalog
