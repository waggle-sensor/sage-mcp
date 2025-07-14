from typing import Dict, List, Optional, Union, Any
import logging
from datetime import datetime, timedelta
import pandas as pd
import sage_data_client

from plugin_registry import (
    PluginRegistry,
    QueryBuilder,
    DataCategory,
    MeasurementType,
    Plugin
)

logger = logging.getLogger(__name__)

class DataQueryResult:
    """Container for query results with metadata"""
    def __init__(
        self,
        data: pd.DataFrame,
        measurement: Optional[MeasurementType] = None,
        query_params: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        self.data = data
        self.measurement = measurement
        self.query_params = query_params or {}
        self.error = error
        self.timestamp = datetime.now()

    @property
    def is_empty(self) -> bool:
        return self.data.empty

    @property
    def row_count(self) -> int:
        return len(self.data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format"""
        return {
            "data": self.data.to_dict() if not self.data.empty else {},
            "measurement": {
                "name": self.measurement.name,
                "category": self.measurement.category,
                "unit": self.measurement.unit,
                "description": self.measurement.description
            } if self.measurement else None,
            "query_params": self.query_params,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
            "row_count": self.row_count
        }

class PluginDataService:
    """Service for querying plugin data using the registry"""
    
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self.query_builder = QueryBuilder(registry)

    def query_measurement(
        self,
        measurement_name: str,
        node_id: Optional[str] = None,
        time_range: str = "-30m",
        start: str = None,
        end: str = None,
        filter_expr: Optional[str] = None
    ) -> DataQueryResult:
        """Query data for a specific measurement type"""
        try:
            # Get measurement info
            measurement = self.registry.get_measurement_info(measurement_name)
            if not measurement:
                return DataQueryResult(
                    pd.DataFrame(),
                    error=f"Unknown measurement type: {measurement_name}"
                )
            # Use provided start/end or parse from time_range
            if not start:
                from datetime import datetime, timedelta
                import re
                if 'T' in time_range and 'Z' in time_range:
                    try:
                        start_time = datetime.strptime(time_range, '%Y-%m-%dT%H:%M:%SZ')
                        end_time = start_time + timedelta(hours=1)
                        start = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
                        end = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
                    except Exception:
                        start = time_range
                        end = None
                else:
                    match = re.match(r'-(\d+)([hm])', time_range)
                    now = datetime.utcnow()
                    if match:
                        amount = int(match.group(1))
                        unit = match.group(2)
                        if unit == 'h':
                            delta = timedelta(hours=amount)
                        else:
                            delta = timedelta(minutes=amount)
                        start = (now - delta).strftime('%Y-%m-%dT%H:%M:%SZ')
                        end = now.strftime('%Y-%m-%dT%H:%M:%SZ')
                    else:
                        start = time_range
                        end = None
            params = {"name": measurement_name}
            if node_id:
                params["vsn"] = node_id
            else:
                params["vsn"] = "*"
            df = sage_data_client.query(start=start, end=end, filter=params)
            # Apply additional filtering if provided
            if filter_expr and not df.empty:
                try:
                    df = df.query(filter_expr)
                except Exception as e:
                    return DataQueryResult(
                        df,
                        measurement=measurement,
                        query_params=params,
                        error=f"Filter expression error: {str(e)}"
                    )
            return DataQueryResult(
                df,
                measurement=measurement,
                query_params=params
            )
        except Exception as e:
            logger.error(f"Error querying measurement {measurement_name}: {e}")
            return DataQueryResult(
                pd.DataFrame(),
                measurement=measurement if 'measurement' in locals() else None,
                query_params=params if 'params' in locals() else None,
                error=str(e)
            )

    def query_category(
        self,
        category: DataCategory,
        node_id: Optional[str] = None,
        time_range: str = "-30m",
        filter_expr: Optional[str] = None
    ) -> List[DataQueryResult]:
        """Query all measurements in a category"""
        results = []
        measurements = self.registry.get_measurements_by_category(category)

        for measurement in measurements:
            result = self.query_measurement(
                measurement_name=measurement.name,
                node_id=node_id,
                time_range=time_range,
                filter_expr=filter_expr
            )
            results.append(result)

        return results

    def get_latest_values(
        self,
        measurement_name: str,
        node_id: Optional[str] = None,
        time_range: str = "-5m"
    ) -> DataQueryResult:
        """Get latest values for a measurement"""
        result = self.query_measurement(
            measurement_name=measurement_name,
            node_id=node_id,
            time_range=time_range
        )

        if not result.is_empty:
            # Keep only the latest value per node
            result.data = result.data.sort_values('timestamp').groupby('meta.vsn').last()

        return result

    def get_measurement_stats(
        self,
        measurement_name: str,
        node_id: Optional[str] = None,
        time_range: str = "-1h",
        filter_expr: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get statistics for a measurement"""
        result = self.query_measurement(
            measurement_name=measurement_name,
            node_id=node_id,
            time_range=time_range,
            filter_expr=filter_expr
        )

        if result.is_empty:
            return {
                "error": result.error or "No data found",
                "measurement": measurement_name,
                "stats": None
            }

        # Calculate statistics
        stats = {
            "count": len(result.data),
            "mean": result.data['value'].mean(),
            "min": result.data['value'].min(),
            "max": result.data['value'].max(),
            "std": result.data['value'].std(),
            "nodes": len(result.data['meta.vsn'].unique()),
            "time_range": {
                "start": result.data['timestamp'].min(),
                "end": result.data['timestamp'].max()
            }
        }

        return {
            "measurement": measurement_name,
            "unit": result.measurement.unit if result.measurement else None,
            "stats": stats,
            "query_params": result.query_params
        } 