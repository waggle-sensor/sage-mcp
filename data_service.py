import pandas as pd
from typing import Any, Dict, List, Optional, Tuple, Union
from models import TimeRange, NodeID, DataType
from utils import safe_timestamp_format, parse_time_range
import logging
import sage_data_client

logger = logging.getLogger(__name__)

class SageDataService:
    """Service for interacting with SAGE data client"""
    
    @staticmethod
    def query_data(
        start: str,
        end: Optional[str] = None,
        filter_params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        try:
            if filter_params is None:
                filter_params = {}
            if "vsn" not in filter_params:
                filter_params["vsn"] = "*"
            if isinstance(start, TimeRange):
                start, end = parse_time_range(start)
            elif isinstance(start, str) and not ('T' in start and 'Z' in start):
                start, end = parse_time_range(start)
            query_args = {"start": start, "filter": filter_params}
            if end:
                query_args["end"] = end
            logger.info(f"Querying SAGE data with: {query_args}")
            df = sage_data_client.query(**query_args)
            logger.info(f"Query returned {len(df)} records")
            return df
        except Exception as e:
            logger.error(f"Error querying SAGE data: {e}")
            return pd.DataFrame()

    @staticmethod
    def query_plugin_data(
        plugin: str,
        time_range: Union[str, TimeRange] = "-30m",
        node_id: Optional[Union[str, NodeID]] = None,
        use_wildcard: bool = False
    ) -> pd.DataFrame:
        start, end = parse_time_range(time_range)
        filter_params = {"plugin": plugin}
        if node_id:
            filter_params["vsn"] = str(node_id)
        return SageDataService.query_data(start, end, filter_params)

    @staticmethod
    def query_image_data(
        time_range: Union[str, TimeRange] = "-1h",
        node_id: Optional[Union[str, NodeID]] = None,
        plugin_pattern: str = ".*"
    ) -> pd.DataFrame:
        start, end = parse_time_range(time_range)
        filter_params = {"plugin": plugin_pattern}
        if node_id:
            filter_params["vsn"] = str(node_id)
        return SageDataService.query_data(start, end, filter_params)

    @staticmethod
    def query_cloud_data(
        time_range: Union[str, TimeRange] = "-1h",
        node_id: Optional[Union[str, NodeID]] = None
    ) -> pd.DataFrame:
        start, end = parse_time_range(time_range)
        cloud_plugins = [
            ".*cloud-cover.*",
            ".*cloud-motion.*",
            ".*imagesampler.*"
        ]
        all_data = []
        for plugin in cloud_plugins:
            filter_params = {"plugin": plugin}
            if node_id:
                filter_params["vsn"] = str(node_id)
            df = SageDataService.query_data(start, end, filter_params)
            if not df.empty:
                all_data.append(df)
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()

    @staticmethod
    def query_node_data(
        node_id: Union[str, NodeID],
        time_range: Union[str, TimeRange] = "-30m",
        measurement_type: Optional[str] = None
    ) -> pd.DataFrame:
        start, end = parse_time_range(time_range)
        filter_params = {"vsn": str(node_id)}
        if measurement_type:
            filter_params["name"] = measurement_type
        return SageDataService.query_data(start, end, filter_params)

    @staticmethod
    def query_environmental_data(
        node_id: Optional[Union[str, NodeID]] = None,
        time_range: Union[str, TimeRange] = "-1h"
    ) -> pd.DataFrame:
        start, end = parse_time_range(time_range)
        filter_params = {"name": "|".join(DataType.environmental_types())}
        if node_id:
            filter_params["vsn"] = str(node_id)
        return SageDataService.query_data(start, end, filter_params)

    @staticmethod
    def query_job_data(
        job_name: str,
        node_id: Optional[Union[str, NodeID]] = None,
        time_range: Union[str, TimeRange] = "-30m",
        data_type: str = "upload"
    ) -> pd.DataFrame:
        start, end = parse_time_range(time_range)
        filter_params = {"task": job_name, "name": data_type}
        if node_id:
            filter_params["vsn"] = str(node_id)
        return SageDataService.query_data(start, end, filter_params) 