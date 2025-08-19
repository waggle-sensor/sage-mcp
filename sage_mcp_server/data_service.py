import pandas as pd
from typing import Any, Dict, List, Optional, Tuple, Union
from .models import TimeRange, NodeID, DataType
from .utils import safe_timestamp_format, parse_time_range
import logging
import sage_data_client
import os

logger = logging.getLogger(__name__)

class SageDataService:
    """Service for interacting with SAGE data client"""
    
    @staticmethod
    def query_data(
        start: str,
        end: Optional[str] = None,
        filter_params: Optional[Dict[str, Any]] = None,
        user_token: Optional[str] = None
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
            
            # Note: sage_data_client.query() does not accept authentication parameters
            # Authentication for protected data must be configured at the system level
            # For now, we'll query public data and log authentication status
            if user_token:
                if ':' in user_token:
                    username, _ = user_token.split(':', 1)
                    logger.info(f"User token provided (username: {username}) - attempting query")
                    logger.warning("sage_data_client authentication not yet implemented - may only return public data")
                else:
                    logger.warning(f"Token provided without username. For protected data access, use 'username:token' format")
                    logger.info(f"Attempting query with simple token - may only return public data")
            else:
                logger.info(f"Querying SAGE data without authentication (public data only)")
            
            df = sage_data_client.query(**query_args)
            logger.info(f"Query returned {len(df)} records")
            return df
        except Exception as e:
            logger.error(f"Error querying SAGE data: {e}")
            # If authentication failed, provide helpful error message
            if user_token and ("401" in str(e) or "Unauthorized" in str(e) or "auth" in str(e).lower()):
                logger.error("Authentication failed. Please check your token and permissions.")
                logger.error("For protected data access, you need:")
                logger.error("1. A valid Sage account")
                logger.error("2. Signed Data Use Agreement") 
                logger.error("3. Valid access token from https://portal.sagecontinuum.org/account/access")
                logger.error("4. Token format: 'username:token' or just 'token'")
            return pd.DataFrame()

    @staticmethod
    def query_plugin_data(
        plugin: str,
        time_range: Union[str, TimeRange] = "-30m",
        node_id: Optional[Union[str, NodeID]] = None,
        use_wildcard: bool = False,
        user_token: Optional[str] = None
    ) -> pd.DataFrame:
        start, end = parse_time_range(time_range)
        filter_params = {"plugin": plugin}
        if node_id:
            filter_params["vsn"] = str(node_id)
        return SageDataService.query_data(start, end, filter_params, user_token=user_token)

    @staticmethod
    def query_image_data(
        time_range: Union[str, TimeRange] = "-1h",
        node_id: Optional[Union[str, NodeID]] = None,
        plugin_pattern: str = ".*",
        user_token: Optional[str] = None
    ) -> pd.DataFrame:
        start, end = parse_time_range(time_range)
        filter_params = {"plugin": plugin_pattern}
        if node_id:
            filter_params["vsn"] = str(node_id)
        return SageDataService.query_data(start, end, filter_params, user_token=user_token)

    @staticmethod
    def query_cloud_data(
        time_range: Union[str, TimeRange] = "-1h",
        node_id: Optional[Union[str, NodeID]] = None,
        user_token: Optional[str] = None
    ) -> pd.DataFrame:
        """Query cloud-related data from SAGE"""
        # Define cloud-related plugins
        cloud_plugins = [
            ".*cloud-cover.*",
            ".*cloud-motion.*",
            ".*imagesampler.*"
        ]
        
        start, end = parse_time_range(time_range)
        filter_params = {
            "plugin": '|'.join(cloud_plugins)
        }
        
        if node_id:
            filter_params["vsn"] = str(node_id)
        
        return SageDataService.query_data(start, end, filter_params, user_token=user_token)

    @staticmethod
    def query_node_data(
        node_id: Union[str, NodeID],
        time_range: Union[str, TimeRange] = "-30m",
        measurement_type: Optional[str] = None,
        user_token: Optional[str] = None
    ) -> pd.DataFrame:
        start, end = parse_time_range(time_range)
        filter_params = {"vsn": str(node_id)}
        if measurement_type:
            filter_params["name"] = measurement_type
        return SageDataService.query_data(start, end, filter_params, user_token=user_token)

    @staticmethod
    def query_environmental_data(
        node_id: Optional[Union[str, NodeID]] = None,
        time_range: Union[str, TimeRange] = "-1h",
        user_token: Optional[str] = None
    ) -> pd.DataFrame:
        start, end = parse_time_range(time_range)
        filter_params = {"name": "|".join(DataType.environmental_types())}
        if node_id:
            filter_params["vsn"] = str(node_id)
        return SageDataService.query_data(start, end, filter_params, user_token=user_token)

    @staticmethod
    def query_job_data(
        job_name: str,
        node_id: Optional[Union[str, NodeID]] = None,
        time_range: Union[str, TimeRange] = "-30m",
        data_type: str = "upload",
        user_token: Optional[str] = None
    ) -> pd.DataFrame:
        start, end = parse_time_range(time_range)
        filter_params = {"plugin": f".*{job_name}.*"}
        if node_id:
            filter_params["vsn"] = str(node_id)
        if data_type != "upload":
            filter_params["name"] = data_type
        return SageDataService.query_data(start, end, filter_params, user_token=user_token) 