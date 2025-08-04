"""
Data Lineage Tracker
Tracks data lineage and metadata throughout the pipeline.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LineageEventType(str, Enum):
    """Types of lineage events."""
    EXTRACTION = "extraction"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"
    QUALITY_CHECK = "quality_check"
    LOAD = "load"
    AGGREGATION = "aggregation"


class DatasetType(str, Enum):
    """Types of datasets."""
    API = "api"
    FILE = "file"
    TABLE = "table"
    STREAM = "stream"
    CACHE = "cache"


@dataclass
class DatasetInfo:
    """Information about a dataset."""
    name: str
    type: DatasetType
    location: str
    schema_version: Optional[str] = None
    record_count: Optional[int] = None
    size_bytes: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class LineageEvent:
    """A lineage event representing a data operation."""
    event_id: str
    event_type: LineageEventType
    timestamp: datetime
    batch_id: str
    source_datasets: List[DatasetInfo]
    target_datasets: List[DatasetInfo]
    operation_details: Dict[str, Any]
    execution_context: Dict[str, Any]
    quality_metrics: Optional[Dict[str, Any]] = None
    error_info: Optional[Dict[str, Any]] = None


class LineageTracker:
    """Tracks data lineage throughout the pipeline."""
    
    def __init__(self, storage_backend: str = "postgres"):
        self.storage_backend = storage_backend
        self.events: List[LineageEvent] = []
        
    def track_extraction(
        self,
        source: str,
        destination: str,
        batch_id: str,
        record_count: int,
        execution_date: datetime,
        source_type: DatasetType = DatasetType.API,
        destination_type: DatasetType = DatasetType.FILE,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Track data extraction event."""
        
        event_id = str(uuid.uuid4())
        
        source_dataset = DatasetInfo(
            name=source,
            type=source_type,
            location=source,
            record_count=record_count,
            created_at=execution_date
        )
        
        target_dataset = DatasetInfo(
            name=destination,
            type=destination_type,
            location=destination,
            record_count=record_count,
            created_at=datetime.utcnow()
        )
        
        event = LineageEvent(
            event_id=event_id,
            event_type=LineageEventType.EXTRACTION,
            timestamp=datetime.utcnow(),
            batch_id=batch_id,
            source_datasets=[source_dataset],
            target_datasets=[target_dataset],
            operation_details={
                "extraction_method": "api_pull",
                "record_count": record_count,
                "execution_date": execution_date.isoformat()
            },
            execution_context=additional_context or {}
        )
        
        self._store_event(event)
        logger.info(f"Tracked extraction event: {event_id}")
        
        return event_id
    
    def track_transformation(
        self,
        source: str,
        destination: str,
        batch_id: str,
        transformation_type: str,
        record_count: int,
        source_type: DatasetType = DatasetType.FILE,
        destination_type: DatasetType = DatasetType.FILE,
        transformation_rules: Optional[List[str]] = None
    ) -> str:
        """Track data transformation event."""
        
        event_id = str(uuid.uuid4())
        
        source_dataset = DatasetInfo(
            name=source,
            type=source_type,
            location=source
        )
        
        target_dataset = DatasetInfo(
            name=destination,
            type=destination_type,
            location=destination,
            record_count=record_count,
            created_at=datetime.utcnow()
        )
        
        event = LineageEvent(
            event_id=event_id,
            event_type=LineageEventType.TRANSFORMATION,
            timestamp=datetime.utcnow(),
            batch_id=batch_id,
            source_datasets=[source_dataset],
            target_datasets=[target_dataset],
            operation_details={
                "transformation_type": transformation_type,
                "transformation_rules": transformation_rules or [],
                "input_record_count": record_count,
                "output_record_count": record_count
            },
            execution_context={}
        )
        
        self._store_event(event)
        logger.info(f"Tracked transformation event: {event_id}")
        
        return event_id
    
    def track_validation(
        self,
        source: str,
        validation_result: str,
        batch_id: str,
        success_rate: float,
        validation_rules: Optional[List[str]] = None
    ) -> str:
        """Track data validation event."""
        
        event_id = str(uuid.uuid4())
        
        source_dataset = DatasetInfo(
            name=source,
            type=DatasetType.FILE,
            location=source
        )
        
        validation_dataset = DatasetInfo(
            name=validation_result,
            type=DatasetType.FILE,
            location=validation_result,
            created_at=datetime.utcnow()
        )
        
        event = LineageEvent(
            event_id=event_id,
            event_type=LineageEventType.VALIDATION,
            timestamp=datetime.utcnow(),
            batch_id=batch_id,
            source_datasets=[source_dataset],
            target_datasets=[validation_dataset],
            operation_details={
                "validation_type": "contract_validation",
                "validation_rules": validation_rules or [],
                "success_rate": success_rate
            },
            execution_context={},
            quality_metrics={
                "validation_success_rate": success_rate,
                "validation_timestamp": datetime.utcnow().isoformat()
            }
        )
        
        self._store_event(event)
        logger.info(f"Tracked validation event: {event_id}")
        
        return event_id
    
    def track_quality_check(
        self,
        source: str,
        quality_result: str,
        batch_id: str,
        overall_score: float,
        quality_dimensions: Optional[Dict[str, float]] = None
    ) -> str:
        """Track data quality check event."""
        
        event_id = str(uuid.uuid4())
        
        source_dataset = DatasetInfo(
            name=source,
            type=DatasetType.FILE,
            location=source
        )
        
        quality_dataset = DatasetInfo(
            name=quality_result,
            type=DatasetType.FILE,
            location=quality_result,
            created_at=datetime.utcnow()
        )
        
        event = LineageEvent(
            event_id=event_id,
            event_type=LineageEventType.QUALITY_CHECK,
            timestamp=datetime.utcnow(),
            batch_id=batch_id,
            source_datasets=[source_dataset],
            target_datasets=[quality_dataset],
            operation_details={
                "quality_check_type": "comprehensive",
                "overall_score": overall_score,
                "quality_dimensions": quality_dimensions or {}
            },
            execution_context={},
            quality_metrics={
                "overall_quality_score": overall_score,
                "quality_dimensions": quality_dimensions or {},
                "check_timestamp": datetime.utcnow().isoformat()
            }
        )
        
        self._store_event(event)
        logger.info(f"Tracked quality check event: {event_id}")
        
        return event_id
    
    def track_load(
        self,
        source: str,
        destination: str,
        batch_id: str,
        record_count: int,
        destination_type: DatasetType = DatasetType.TABLE
    ) -> str:
        """Track data load event."""
        
        event_id = str(uuid.uuid4())
        
        source_dataset = DatasetInfo(
            name=source,
            type=DatasetType.FILE,
            location=source,
            record_count=record_count
        )
        
        target_dataset = DatasetInfo(
            name=destination,
            type=destination_type,
            location=destination,
            record_count=record_count,
            created_at=datetime.utcnow()
        )
        
        event = LineageEvent(
            event_id=event_id,
            event_type=LineageEventType.LOAD,
            timestamp=datetime.utcnow(),
            batch_id=batch_id,
            source_datasets=[source_dataset],
            target_datasets=[target_dataset],
            operation_details={
                "load_type": "batch_insert",
                "record_count": record_count,
                "destination_table": destination
            },
            execution_context={}
        )
        
        self._store_event(event)
        logger.info(f"Tracked load event: {event_id}")
        
        return event_id
    
    def get_lineage_for_batch(self, batch_id: str) -> List[LineageEvent]:
        """Get all lineage events for a specific batch."""
        return [event for event in self.events if event.batch_id == batch_id]
    
    def get_lineage_for_dataset(self, dataset_name: str) -> List[LineageEvent]:
        """Get lineage events for a specific dataset."""
        events = []
        for event in self.events:
            # Check if dataset is in source or target
            for dataset in event.source_datasets + event.target_datasets:
                if dataset.name == dataset_name:
                    events.append(event)
                    break
        return events
    
    def generate_lineage_graph(self, batch_id: str) -> Dict[str, Any]:
        """Generate a lineage graph for visualization."""
        events = self.get_lineage_for_batch(batch_id)
        
        nodes = {}
        edges = []
        
        for event in events:
            # Add source nodes
            for source in event.source_datasets:
                nodes[source.name] = {
                    "id": source.name,
                    "type": source.type.value,
                    "location": source.location,
                    "record_count": source.record_count
                }
            
            # Add target nodes
            for target in event.target_datasets:
                nodes[target.name] = {
                    "id": target.name,
                    "type": target.type.value,
                    "location": target.location,
                    "record_count": target.record_count
                }
            
            # Add edges
            for source in event.source_datasets:
                for target in event.target_datasets:
                    edges.append({
                        "source": source.name,
                        "target": target.name,
                        "event_type": event.event_type.value,
                        "timestamp": event.timestamp.isoformat(),
                        "operation": event.operation_details
                    })
        
        return {
            "batch_id": batch_id,
            "nodes": list(nodes.values()),
            "edges": edges,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _store_event(self, event: LineageEvent) -> None:
        """Store lineage event to configured backend."""
        self.events.append(event)
        
        # In real implementation, this would store to database
        if self.storage_backend == "postgres":
            self._store_to_postgres(event)
        elif self.storage_backend == "file":
            self._store_to_file(event)
    
    def _store_to_postgres(self, event: LineageEvent) -> None:
        """Store event to PostgreSQL."""
        # Implementation would use actual database connection
        logger.debug(f"Storing lineage event to PostgreSQL: {event.event_id}")
    
    def _store_to_file(self, event: LineageEvent) -> None:
        """Store event to file system."""
        # Implementation would write to file
        logger.debug(f"Storing lineage event to file: {event.event_id}")
    
    def export_lineage_report(self, batch_id: str, format: str = "json") -> str:
        """Export lineage report for a batch."""
        events = self.get_lineage_for_batch(batch_id)
        
        report = {
            "batch_id": batch_id,
            "report_generated_at": datetime.utcnow().isoformat(),
            "total_events": len(events),
            "events": [asdict(event) for event in events],
            "lineage_graph": self.generate_lineage_graph(batch_id)
        }
        
        if format == "json":
            return json.dumps(report, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")


# Global lineage tracker instance
lineage_tracker = LineageTracker()


def get_lineage_tracker() -> LineageTracker:
    """Get global lineage tracker instance."""
    return lineage_tracker
