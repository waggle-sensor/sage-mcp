#!/usr/bin/env python3

import asyncio
import json
import logging
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, cast
import re
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import yaml
from pydantic import BaseModel, Field, validator
import requests
from plugin_metadata import plugin_registry
from plugin_query_service import plugin_query_service
from pathlib import Path
from plugin_generator import PluginTemplate, PluginRequirements, PluginGenerator
# Add import for models
from models import (
    SageConfig, TimeRange, NodeID, DataType, SelectorRequirements, PluginArguments, PluginSpec, SageJob, CameraSageJob
)
from utils import safe_timestamp_format, parse_time_range
from job_templates import JobTemplates
from data_service import SageDataService
from job_service import SageJobService
from docs_helper import SAGEDocsHelper

SAGE_API_BASE = "https://auth.sagecontinuum.org/api/v-beta"
SAGE_MANIFESTS_URL = "https://auth.sagecontinuum.org/manifests/"
SAGE_SENSORS_URL = "https://auth.sagecontinuum.org/sensors/"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import required modules
try:
    from mcp.server.fastmcp import FastMCP
    from mcp.server.fastmcp.prompts import base
    import sage_data_client
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure you have installed: pip install mcp fastmcp sage-data-client")
    sys.exit(1)



# ----------------------------------------
# Configuration Models
# ----------------------------------------

# (REMOVED: SageConfig)


# ----------------------------------------
# Data Models
# ----------------------------------------

# (REMOVED: TimeRange, NodeID, DataType, SelectorRequirements, PluginArguments, PluginSpec, SageJob, CameraSageJob)


# ----------------------------------------
# Job Models
# ----------------------------------------

# (REMOVED: PluginArguments, PluginSpec, SageJob, CameraSageJob duplicate definitions)


# ----------------------------------------
# Predefined Job Templates
# ----------------------------------------

class JobTemplates:
    """Predefined job templates for common SAGE jobs"""
    
    @staticmethod
    def image_sampler(
        job_name: str,
        nodes: List[str],
        interval_mins: int = 10,
        width: int = 1920,
        height: int = 1080
    ) -> SageJob:
        """Create an image sampler job configuration"""
        plugin_name = "image-sampler"
        plugin = PluginSpec(
            name=plugin_name,
            image=f"waggle/plugin-image-sampler:0.2.0",
            args=PluginArguments(args_dict={
                "width": width,
                "height": height
            }),
            selector=SelectorRequirements(gpu=None, camera=True, usb=None)
        )
        
        # Define science rule for sampling at specified interval
        science_rule = f'schedule("{plugin_name}"): cronjob("{plugin_name}", "*/{interval_mins} * * * *")'
        
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )
    
    @staticmethod
    def ptz_sampler(
        job_name: str,
        nodes: List[str],
        interval_mins: int = 15,
        preset_positions: List[int] = [1, 2, 3]
    ) -> SageJob:
        """Create a PTZ camera sampler job configuration"""
        plugin_name = "ptz-sampler"
        position_args = ",".join(map(str, preset_positions))
        
        plugin = PluginSpec(
            name=plugin_name,
            image=f"waggle/plugin-ptz-sampler:0.3.0",
            args=PluginArguments(args_dict={
                "positions": position_args
            }),
            selector=SelectorRequirements(gpu=None, camera=True, usb=None)
        )
        
        # Define science rule for sampling at specified interval
        science_rule = f'schedule("{plugin_name}"): cronjob("{plugin_name}", "*/{interval_mins} * * * *")'
        
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )
    
    @staticmethod
    def yolo_detector(
        job_name: str,
        nodes: List[str],
        model: str = "yolov5s",
        confidence: float = 0.25,
        interval_mins: int = 10
    ) -> SageJob:
        """Create a YOLO object detection job configuration"""
        plugin_name = "yolo-detector"
        
        plugin = PluginSpec(
            name=plugin_name,
            image=f"waggle/plugin-yolo-detector:0.4.0",
            args=PluginArguments(args_dict={
                "model": model,
                "confidence": confidence
            }),
            selector=SelectorRequirements(gpu=True, camera=True, usb=None)
        )
        
        # Define science rule for running at specified interval
        science_rule = f'schedule("{plugin_name}"): cronjob("{plugin_name}", "*/{interval_mins} * * * *")'
        
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )

    @staticmethod
    def ptz_yolo(
        job_name: str,
        nodes: List[str],
        iterations: int = 10,
        objects: str = "person,car,truck",
        username: str = "",
        password: str = "",
        camera_ip: str = "",
        pan_step: int = 45,
        tilt: int = 0,
        zoom: int = 1,
        model: str = "yolov8n",
        iter_delay: float = 1.0,
        confidence: float = 0.25
    ) -> SageJob:
        """Create a job for the PTZ-YOLO app that combines PTZ camera control with YOLO object detection"""
        plugin = PluginSpec(
            name=job_name,
            image="plebbyd/ptzapp-yolo:0.1.12",
            args=PluginArguments.from_string(
                f"iterations={iterations},"
                f"objects={objects},"
                f"username={username},"
                f"password={password},"
                f"cameraip={camera_ip},"
                f"panstep={pan_step},"
                f"tilt={tilt},"
                f"zoom={zoom},"
                f"model={model},"
                f"iterdelay={iter_delay},"
                f"confidence={confidence}"
            ),
            selector=SelectorRequirements(gpu=True, camera=True, usb=None)
        )
        return SageJob(name=job_name, nodes=nodes, plugins=[plugin])

    @staticmethod
    def air_quality(
        job_name: str,
        nodes: List[str]
    ) -> SageJob:
        """Create an air quality monitoring job"""
        plugin = PluginSpec(
            name="air-quality",
            image="registry.sagecontinuum.org/seanshahkarami/air-quality:0.2.0",
            args=PluginArguments(args_dict={"device": "/host/dev/airquality"}),
            selector=SelectorRequirements(
                gpu=None, camera=None, usb=None,
                custom_selectors={"resource.airquality": "true"}
            ),
            privileged=True
        )
        
        science_rule = 'schedule("air-quality"): True'
        
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule],
            node_value_format="true",
            success_criteria=["WallClock('1day')"]
        )

    @staticmethod
    def mobotix_scan(
        job_name: str,
        nodes: List[str],
        camera_ip: str = "camera-mobotix-thermal",
        mode: str = "direction",
        direction: str = "south",
        angle: str = "15",
        preset_positions: str = "NEH,NEB,NEG,EH,EB,EG,SEH,SEB,SEG,SH,SB,SG,SWH,SWB,SWG",
        username: str = "admin",
        password: str = "meinsm",
        interval_mins: int = 1  # Every minute by default
    ) -> SageJob:
        """Create a Mobotix thermal camera scanning job"""
        plugin = PluginSpec(
            name="mobotix-scan-direction",
            image="registry.sagecontinuum.org/bhupendraraut/mobotix-scan:0.24.8.20",
            args=PluginArguments(args_dict={
                "ip": camera_ip,
                "mode": mode,
                f"-{direction}": angle,  # Fixed direction argument format
                "pt": preset_positions,
                "u": username,
                "p": password
            }),
            selector=SelectorRequirements(gpu=None, camera=None, usb=None)
        )
        
        science_rule = f'schedule("mobotix-scan-direction"): cronjob("mobotix-scan-direction", "* * * * *")'
        
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )

    @staticmethod
    def audio_sampler(
        job_name: str,
        nodes: List[str]
    ) -> SageJob:
        """Create an audio sampling job"""
        plugin = PluginSpec(
            name="audio-sampler",
            image="registry.sagecontinuum.org/seanshahkarami/audio-sampler:0.4.1",
            args=PluginArguments(),
            selector=SelectorRequirements(gpu=None, camera=None, usb=None)
        )
        
        science_rule = 'schedule(audio-sampler): cronjob("audio-sampler", "*/15 * * * *")'
        
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )

    @staticmethod
    def camera_sampler(
        job_name: str,
        nodes: List[str],
        camera_position: str = "bottom"  # "bottom" or "top"
    ) -> SageJob:
        """Create a camera sampling job for top or bottom cameras"""
        plugin_name = f"imagesampler-{camera_position}"
        
        # Use exact format from working YAML - single string after -c
        wget_cmd = f'wget -O ./sample.jpg "http://camera-{camera_position}-rgb-hanwha/stw-cgi/video.cgi?msubmenu=snapshot&action=view"  --user camera --password 0Bscura# && python3 /app/upload.py --name {camera_position}_camera --file-path /sample.jpg'
        
        # Create a custom plugin spec that handles the special -c format
        plugin = PluginSpec(
            name=plugin_name,
            image="registry.sagecontinuum.org/yonghokim/imagesampler:0.3.7",
            args=PluginArguments(args_dict={"__camera_cmd": wget_cmd}),  # Special marker
            selector=SelectorRequirements(
                gpu=None, camera=None, usb=None,
                custom_selectors={"zone": "core"}
            ),
            entrypoint="/bin/bash"
        )
        
        science_rule = f'schedule({plugin_name}): cronjob("{plugin_name}", "10 * * * *")'
        
        # Create a custom job that handles the camera plugin specially
        job = CameraSageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule],
            node_value_format="null",
            success_criteria=[],
            camera_cmd=wget_cmd,
            camera_plugin_name=plugin_name
        )
        
        return job

    @staticmethod
    def cloud_cover(
        job_name: str,
        nodes: List[str],
        camera_stream: str = "top_camera",
        interval_mins: int = 10
    ) -> SageJob:
        """Create a cloud cover detection job"""
        plugin = PluginSpec(
            name="cloud-cover-top",
            image="registry.sagecontinuum.org/seonghapark/cloud-cover:0.1.3",
            args=PluginArguments(args_dict={"stream": camera_stream}),
            selector=SelectorRequirements(gpu=True, camera=None, usb=None)
        )
        
        science_rule = f'schedule("cloud-cover-top"): cronjob("cloud-cover-top", "*/{interval_mins} * * * *")'
        
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )

    @staticmethod
    def solar_irradiance(
        job_name: str,
        nodes: List[str],
        gps_server: str = "wes-gps-server.default.svc.cluster.local"
    ) -> SageJob:
        """Create a solar irradiance monitoring job"""
        plugin = PluginSpec(
            name="solar-irradiance",
            image="registry.sagecontinuum.org/seonghapark/solar-irradiance:0.1.0",
            args=PluginArguments(),
            selector=SelectorRequirements(gpu=None, camera=None, usb=None),
            env={"WAGGLE_GPS_SERVER": gps_server}
        )
        
        science_rule = 'schedule("solar-irradiance"): True'
        
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )

    @staticmethod
    def sound_event_detection(
        job_name: str,
        nodes: List[str],
        duration_s: int = 5,
        publish: bool = True,
        interval_mins: int = 10
    ) -> SageJob:
        """Create a sound event detection job"""
        plugin = PluginSpec(
            name="sound-event-detection",
            image="registry.sagecontinuum.org/dariodematties/sound-event-detection:0.1.1",
            args=PluginArguments(args_dict={
                "DURATION_S": str(duration_s),
                "PUBLISH": str(publish).lower()
            }),
            selector=SelectorRequirements(gpu=None, camera=None, usb=None)
        )
        
        science_rule = f'schedule("sound-event-detection"): cronjob("sound-event-detection", "*/{interval_mins} * * * *")'
        
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )

    @staticmethod
    def avian_diversity_monitoring(
        job_name: str,
        nodes: List[str],
        num_recordings: int = 2,
        sound_interval: int = 30,
        interval_mins: int = 5
    ) -> SageJob:
        """Create an avian diversity monitoring job"""
        plugin = PluginSpec(
            name="avian-diversity-monitoring",
            image="registry.sagecontinuum.org/dariodematties1/avian-diversity-monitoring:0.2.4",
            args=PluginArguments(args_dict={
                "num_rec": str(num_recordings),
                "sound_int": str(sound_interval)
            }),
            selector=SelectorRequirements(gpu=True, camera=None, usb=None)
        )
        
        science_rule = f'schedule("avian-diversity-monitoring"): cronjob("avian-diversity-monitoring", "*/{interval_mins} * * * *")'
        
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )

    @staticmethod
    def weather_classification(
        job_name: str,
        nodes: List[str],
        lidar_ip: str = "10.31.81.196",
        lidar_password: str = "Halo217_1128",
        interval_mins: int = 60  # Hourly by default
    ) -> SageJob:
        """Create a LIDAR weather classification job"""
        plugin = PluginSpec(
            name="weather-classification",
            image="registry.sagecontinuum.org/rjackson/weatherclassification:2025.6.20",
            args=PluginArguments(args_dict={
                "IP": lidar_ip,
                "password": lidar_password
            }),
            selector=SelectorRequirements(gpu=True, camera=None, usb=None)
        )
        
        science_rule = f'schedule("weather-classification"): cronjob("weather-classification", "5 */{interval_mins} * * *")'
        
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )

    @staticmethod
    def waggle_aqt(
        job_name: str,
        nodes: List[str],
        device: str = "/host/dev/waggle-crocus-mux-p4",
        interval_mins: int = 10
    ) -> SageJob:
        """Create a Waggle Air Quality Testing (AQT) job"""
        plugin = PluginSpec(
            name="waggle-aqt",
            image="registry.sagecontinuum.org/jrobrien/waggle-aqt:0.23.5.04",
            args=PluginArguments(args_dict={"device": device}),
            selector=SelectorRequirements(
                gpu=None, camera=None, usb=None,
                custom_selectors={"zone": "core"}
            ),
            privileged=True
        )
        
        science_rule = f'schedule("waggle-aqt"): cronjob("waggle-aqt", "*/{interval_mins} * * * *")'
        
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )

    @staticmethod
    def waggle_wxt536(
        job_name: str,
        nodes: List[str],
        device: str = "/host/dev/waggle-crocus-mux-p3",
        interval_mins: int = 10
    ) -> SageJob:
        """Create a Waggle WXT536 weather station job"""
        plugin = PluginSpec(
            name="waggle-wxt536",
            image="registry.sagecontinuum.org/jrobrien/waggle-wxt536:0.24.11.14",
            args=PluginArguments(args_dict={"device": device}),
            selector=SelectorRequirements(
                gpu=None, camera=None, usb=None,
                custom_selectors={"zone": "core"}
            ),
            privileged=True
        )
        
        science_rule = f'schedule("waggle-wxt536"): cronjob("waggle-wxt536", "*/{interval_mins} * * * *")'
        
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=[plugin],
            science_rules=[science_rule]
        )

    @staticmethod
    def multi_plugin_ml_suite(
        job_name: str,
        nodes: List[str],
        cloud_cover_interval: int = 10,
        sound_event_interval: int = 10,
        avian_monitoring_interval: int = 5,
        cloud_motion_interval: int = 20
    ) -> SageJob:
        """Create a comprehensive ML plugin suite job with multiple plugins"""
        plugins = [
            # Cloud cover detection
            PluginSpec(
                name="cloud-cover-top",
                image="registry.sagecontinuum.org/seonghapark/cloud-cover:0.1.3",
                args=PluginArguments(args_dict={"stream": "top_camera"}),
                selector=SelectorRequirements(gpu=True, camera=None, usb=None)
            ),
            # Solar irradiance
            PluginSpec(
                name="solar-irradiance",
                image="registry.sagecontinuum.org/seonghapark/solar-irradiance:0.1.0",
                args=PluginArguments(),
                selector=SelectorRequirements(gpu=None, camera=None, usb=None)
            ),
            # Sound event detection
            PluginSpec(
                name="sound-event-detection",
                image="registry.sagecontinuum.org/dariodematties/sound-event-detection:0.1.1",
                args=PluginArguments(args_dict={"DURATION_S": "5", "PUBLISH": "true"}),
                selector=SelectorRequirements(gpu=None, camera=None, usb=None)
            ),
            # Avian diversity monitoring
            PluginSpec(
                name="avian-diversity-monitoring",
                image="registry.sagecontinuum.org/dariodematties1/avian-diversity-monitoring:0.2.4",
                args=PluginArguments(args_dict={"num_rec": "2", "sound_int": "30"}),
                selector=SelectorRequirements(gpu=True, camera=None, usb=None)
            )
        ]
        
        science_rules = [
            f'schedule("cloud-cover-top"): cronjob("cloud-cover-top", "*/{cloud_cover_interval} * * * *")',
            'schedule("solar-irradiance"): True',
            f'schedule("sound-event-detection"): cronjob("sound-event-detection", "*/{sound_event_interval} * * * *")',
            f'schedule("avian-diversity-monitoring"): cronjob("avian-diversity-monitoring", "*/{avian_monitoring_interval} * * * *")'
        ]
        
        if cloud_motion_interval > 0:
            science_rules.append(f'schedule("cloud-motion-top"): cronjob("cloud-motion-top", "*/{cloud_motion_interval} * * * *")')
        
        return SageJob(
            name=job_name,
            nodes=nodes,
            plugins=plugins,
            science_rules=science_rules
        )


# ----------------------------------------
# Data Service
# ----------------------------------------

class SageDataService:
    """Service for interacting with SAGE data client"""
    
    @staticmethod
    def query_data(
        start: str,
        end: Optional[str] = None,
        filter_params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """Query data from SAGE with error handling. filter_params['vsn'] defaults to '*' if not set."""
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
        return data_service.query_data(start, end, filter_params)

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
        return data_service.query_data(start, end, filter_params)

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
            df = data_service.query_data(start, end, filter_params)
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
        return data_service.query_data(start, end, filter_params)

    @staticmethod
    def query_environmental_data(
        node_id: Optional[Union[str, NodeID]] = None,
        time_range: Union[str, TimeRange] = "-1h"
    ) -> pd.DataFrame:
        start, end = parse_time_range(time_range)
        filter_params = {"name": "|".join(DataType.environmental_types())}
        if node_id:
            filter_params["vsn"] = str(node_id)
        return data_service.query_data(start, end, filter_params)

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
        return data_service.query_data(start, end, filter_params)


# ----------------------------------------
# Job Service
# ----------------------------------------

class SageJobService:
    """Service for submitting and managing SAGE jobs"""
    
    def __init__(self, config: SageConfig):
        self.config = config
    
    def submit_job(self, job: SageJob) -> Tuple[bool, str]:
        """Submit a job to the SAGE scheduler"""
        try:
            # Create temporary file for job YAML
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                job.write_yaml(f.name)
                temp_yaml_path = f.name
            
            try:
                # Build command with authentication
                cmd = ["sesctl", "submit", "--file-path", temp_yaml_path]
                
                # Add dry-run if enabled
                if self.config.dry_run:
                    cmd.append("--dry-run")
                    logger.info("Using --dry-run mode (no actual submission)")
                
                # Add token and server
                if self.config.token:
                    cmd.extend(["--token", self.config.token])
                
                if self.config.server:
                    cmd.extend(["--server", self.config.server])
                
                logger.info(f"Running command: {' '.join(cmd[:5])} [using configured token]")
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    output = result.stdout.strip()
                    logger.info(f"sesctl output: {output}")
                    
                    # Extract job ID from response
                    job_id = None
                    if "job_id" in output:
                        try:
                            response_json = json.loads(output)
                            job_id = response_json.get("job_id")
                        except json.JSONDecodeError:
                            # Look for job_id in text output
                            import re
                            match = re.search(r'"?job_id"?\s*:\s*"?(\d+)"?', output)
                            if match:
                                job_id = match.group(1)
                    
                    if job_id:
                        status_msg = "Dry-run completed successfully!" if self.config.dry_run else "Submitted"
                        return True, f"✅ Job {'validated' if self.config.dry_run else 'submitted'} successfully!\nJob ID: {job_id}\nJob Name: {job.name}\nNodes: {', '.join(job.nodes)}\nStatus: {status_msg}\n\nUse check_job_status({job_id}) to monitor progress."
                    else:
                        status_msg = "Dry-run completed!" if self.config.dry_run else "Submitted"
                        return True, f"✅ Job {'validated' if self.config.dry_run else 'submitted'} successfully!\nResponse: {output}\nJob Name: {job.name}\nNodes: {', '.join(job.nodes)}\nStatus: {status_msg}"
                else:
                    error_msg = result.stderr.strip() or result.stdout.strip()
                    if "must provide a valid token" in error_msg:
                        return False, f"❌ Authentication required: Please provide a valid SAGE token.\nError: {error_msg}"
                    return False, f"❌ Job submission failed:\n{error_msg}"
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_yaml_path):
                    os.unlink(temp_yaml_path)
            
        except Exception as e:
            logger.error(f"Error submitting job: {e}")
            return False, f"❌ Error submitting job: {e}"
    
    def check_job_status(self, job_id: str) -> str:
        """Check the status of a submitted job"""
        try:
            cmd = ["sesctl", "stat", "--job-id", job_id]
            
            # Add token and server
            if self.config.token:
                cmd.extend(["--token", self.config.token])
            
            if self.config.server:
                cmd.extend(["--server", self.config.server])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                logger.info(f"Job status output: {output}")
                
                # Try to parse as JSON first, then fall back to text parsing
                try:
                    status_json = json.loads(output)
                    return f"📊 Job Status (ID: {job_id}):\n{json.dumps(status_json, indent=2)}"
                except json.JSONDecodeError:
                    # Parse text output
                    return f"📊 Job Status (ID: {job_id}):\n{output}"
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return f"❌ Error checking job status:\n{error_msg}"
            
        except Exception as e:
            logger.error(f"Error checking job status: {e}")
            return f"❌ Error checking job status: {e}"
    
    def force_remove_job(self, job_id: str) -> str:
        """Force remove a job from the scheduler"""
        try:
            # Build command: sesctl rm --force JOB_ID --token TOKEN --server SERVER
            cmd = ["sesctl", "rm", "--force", job_id]
            
            # Add token and server
            if self.config.token:
                cmd.extend(["--token", self.config.token])
            
            if self.config.server:
                cmd.extend(["--server", self.config.server])
            
            logger.info(f"Running force remove command: {' '.join(cmd[:4])} [with token]")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                return f"✅ Job {job_id} removed successfully!\nOutput: {output}"
            else:
                error_output = result.stderr.strip() or result.stdout.strip()
                logger.error(f"sesctl rm failed with return code {result.returncode}: {error_output}")
                return f"❌ Error removing job {job_id}:\nReturn code: {result.returncode}\nError: {error_output}"
            
        except Exception as e:
            logger.error(f"Error removing job: {e}")
            return f"❌ Error removing job: {e}"

    def suspend_job(self, job_id: str) -> str:
        """Suspend a job from the scheduler"""
        try:
            # Build command: sesctl rm --suspend JOB_ID --token TOKEN --server SERVER
            cmd = ["sesctl", "rm", "--suspend", job_id]
            
            # Add token and server
            if self.config.token:
                cmd.extend(["--token", self.config.token])
            
            if self.config.server:
                cmd.extend(["--server", self.config.server])
            
            logger.info(f"Running suspend command: {' '.join(cmd[:4])} [with token]")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                return f"⏸️ Job {job_id} suspended successfully!\nOutput: {output}"
            else:
                error_output = result.stderr.strip() or result.stdout.strip()
                logger.error(f"sesctl rm --suspend failed with return code {result.returncode}: {error_output}")
                return f"❌ Error suspending job {job_id}:\nReturn code: {result.returncode}\nError: {error_output}"
            
        except Exception as e:
            logger.error(f"Error suspending job: {e}")
            return f"❌ Error suspending job: {e}"


# ----------------------------------------
# Initialize Services and MCP
# ----------------------------------------

# Create global configuration
sage_config = SageConfig()

# Initialize services
data_service = SageDataService()
job_service = SageJobService(sage_config)

# Initialize MCP Server
mcp = FastMCP("SageDataMCP")


# ----------------------------------------
# 1. RESOURCES
# ----------------------------------------

@mcp.resource("query://{plugin}")
def query_plugin_data(plugin: str) -> str:
    """Query Sage data for a specific plugin (last 30 min)"""
    try:
        logger.info(f"Querying plugin data for: {plugin}")
        df = data_service.query_plugin_data(plugin)
        
        result = df.to_csv(index=False)
        logger.info(f"Plugin {plugin} query returned {len(result)} characters")
        return result
    except Exception as e:
        error_msg = f"Error querying plugin {plugin}: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.resource("query://plugin-iio")
def query_plugin_iio() -> str:
    """Pre-bound static version of plugin-iio resource"""
    return query_plugin_data("plugin-iio")


@mcp.resource("stats://temperature")
def temperature_stats() -> str:
    """Returns temperature stats grouped by node and sensor"""
    try:
        logger.info("Getting temperature stats...")
        start, end = SageDataService._parse_time_range("-1h")
        df = data_service.query_data(start, end, {"name": "env.temperature"})
        
        if df.empty:
            return "No temperature data found in the last hour"
        
        # Group by node (vsn) and sensor, calculate stats
        stats = df.groupby(["meta.vsn", "meta.sensor"]).value.agg(["size", "min", "max", "mean"])
        result = stats.to_csv()
        logger.info(f"Temperature stats returned {len(result)} characters")
        return result
        
    except Exception as e:
        error_msg = f"Error getting temperature stats: {str(e)}"
        logger.error(error_msg)
        return error_msg


# ----------------------------------------
# 2. SENSOR DATA TOOLS
# ----------------------------------------

@mcp.tool()
def get_node_all_data(node_id: str, time_range: str = "-30m") -> str:
    """Get all available sensor data for a specific node or all nodes if node_id is '*' or empty"""
    try:
        # Only normalize if node_id is not '*' or empty
        if node_id and node_id != '*':
            validated_node = NodeID(value=node_id)
            node_str = str(validated_node)
        else:
            node_str = '*'
        validated_time = TimeRange(value=time_range)
        logger.info(f"Getting all data for node: {node_str}")
        # Query for all data from this node or all nodes
        df = data_service.query_node_data(node_str, validated_time)
        if df.empty:
            return f"No data found for node {node_str} in the last {validated_time}"
        # Group by measurement type and sensor
        summary = df.groupby(["name", "meta.sensor"]).agg({
            "value": ["count", "min", "max", "mean"]
        }).round(2)
        # Get time range
        time_start = data_service._safe_timestamp_format(df.timestamp.min())
        time_end = data_service._safe_timestamp_format(df.timestamp.max())
        result = f"All sensor data for node {node_str} ({validated_time}):\n"
        result += f"Total measurements: {len(df)}\n"
        result += f"Time range: {time_start} to {time_end}\n\n"
        # Add summary by measurement type
        for (name, sensor), group in summary.iterrows():
            result += f"{name} ({sensor}):\n"
            result += f"  Count: {group[('value', 'count')]}\n"
            result += f"  Range: {group[('value', 'min')]} to {group[('value', 'max')]}\n"
            result += f"  Average: {group[('value', 'mean')]}\n\n"
        return result
    except Exception as e:
        return f"Error getting all data for node {node_id}: {str(e)}"


@mcp.tool()
def get_node_iio_data(node_id: str, time_range: str = "-30m") -> str:
    """Get IIO (Industrial I/O) sensor data for a specific node"""
    try:
        validated_node = NodeID(value=node_id)
        validated_time = TimeRange(value=time_range)
        logger.info(f"Getting IIO data for node: {validated_node}")
        
        # Query for IIO plugin data
        start, end = SageDataService._parse_time_range(validated_time)
        df = data_service.query_data(
            start, end,
            {
                "plugin": ".*plugin-iio.*",
                "vsn": str(validated_node)
            }
        )
        
        if df.empty:
            return f"No IIO data found for node {validated_node} in the last {validated_time}"
        
        # Process IIO measurements
        iio_measurements = DataType.iio_types() + [DataType.TEMPERATURE.value, 
                                                 DataType.HUMIDITY.value, 
                                                 DataType.PRESSURE.value]
        
        result = f"IIO sensor data for node {validated_node} ({validated_time}):\n"
        result += f"Total IIO measurements: {len(df)}\n\n"
        
        # Process each measurement type
        for measurement in iio_measurements:
            measurement_df = df[df['name'] == measurement]
            if not measurement_df.empty:
                stats = measurement_df.groupby('meta.sensor').value.agg(['count', 'min', 'max', 'mean'])
                result += f"{measurement}:\n"
                for sensor, sensor_stats in stats.iterrows():
                    result += f"  {sensor}: {sensor_stats['count']} readings, "
                    result += f"range: {sensor_stats['min']:.2f}-{sensor_stats['max']:.2f}, "
                    result += f"avg: {sensor_stats['mean']:.2f}\n"
                result += "\n"
        
        # Show any other IIO measurements found
        other_measurements = df[~df['name'].isin(iio_measurements)]['name'].unique()
        if len(other_measurements) > 0:
            result += f"Other IIO measurements found: {', '.join(other_measurements)}\n"
        
        return result
        
    except Exception as e:
        return f"Error getting IIO data for node {node_id}: {str(e)}"


@mcp.tool()
def get_environmental_summary(node_id: str = "", time_range: str = "-1h") -> str:
    """Get environmental data summary (temperature, humidity, pressure) for a node or all nodes"""
    try:
        validated_time = TimeRange(value=time_range)
        validated_node = NodeID(value=node_id) if node_id else None
        
        logger.info(f"Getting environmental summary for node: {validated_node or 'all'}")
        
        # Query environmental data
        df = data_service.query_environmental_data(validated_node, validated_time)
        
        if df.empty:
            node_text = f"node {validated_node}" if validated_node else "any nodes"
            return f"No environmental data found for {node_text} in the last {validated_time}"
        
        result = f"Environmental data summary ({validated_node or 'all nodes'}, {validated_time}):\n\n"
        
        # Group by node, measurement type, and sensor
        grouped = df.groupby(["meta.vsn", "name", "meta.sensor"]).value.agg([
            "count", "min", "max", "mean"
        ]).round(2)
        
        current_node = None
        for (vsn, name, sensor), stats in grouped.iterrows():
            if current_node != vsn:
                current_node = vsn
                result += f"\nNode {vsn}:\n"
            
            result += f"  {name} ({sensor}): "
            result += f"{stats['count']} readings, "
            result += f"{stats['min']}-{stats['max']} (avg: {stats['mean']})\n"
        
        return result
        
    except Exception as e:
        return f"Error getting environmental summary: {str(e)}"


@mcp.tool()
def list_available_nodes(time_range: str = "-1h") -> str:
    """List all available sensor nodes and their last activity"""
    try:
        # Initialize data service
        data_service = SageDataService()
        
        # Query environmental data
        df = data_service.query_environmental_data(time_range=time_range)
        if df.empty:
            return "No active nodes found in the specified time range."

        # Get unique nodes and their latest data
        nodes = df['meta.vsn'].unique().tolist()
        result = []

        deployed_nodes = []
        development_nodes = []
        other_nodes = []
        production_nodes = []
        
        for node in nodes:
            node_df = df[df['meta.vsn'] == node]
            latest = node_df.sort_values('timestamp').iloc[-1]
            phase = latest.get('meta.phase', 'Unknown')
            
            # Format node info
            node_info = f"- {node}"
            if phase == 'Production':
                production_nodes.append(node_info)
            elif phase == 'Development':
                development_nodes.append(node_info)
            else:
                other_nodes.append(node_info)
        
        result = f"Available SAGE Nodes ({len(nodes)} total):\n\n"
        
        if deployed_nodes:
            result += f"🟢 Deployed Nodes ({len(deployed_nodes)}):\n"
            result += "\n".join(deployed_nodes)
            result += "\n"
        
        if development_nodes:
            result += f"🟡 Development Nodes ({len(development_nodes)}):\n"
            result += "\n".join(development_nodes)
            result += "\n"
        
        if production_nodes:
            result += f"🟣 Production Nodes ({len(production_nodes)}):\n"
            result += "\n".join(production_nodes)
            result += "\n"
        
        if other_nodes:
            result += f"⚪ Other Nodes ({len(other_nodes)}):\n"
            result += "\n".join(other_nodes)
        
        result += "\n💡 For detailed node information, use get_node_info(node_id)"
        result += "\n💡 For recent sensor activity, use get_environmental_summary()"
        
        return result.strip()
        
    except Exception as e:
        logger.error(f"Error listing nodes: {e}")
        return f"Error listing nodes: {str(e)}"


@mcp.tool()
def search_measurements(
    measurement_pattern: str,
    node_id: str = "",
    time_range: str = "-30m"
) -> str:
    """Search for specific measurement types using a pattern (regex supported)"""
    try:
        validated_time = TimeRange(value=time_range)
        validated_node = NodeID(value=node_id) if node_id else None
        
        logger.info(f"Searching for measurements matching: {measurement_pattern}")
        
        # Build filter parameters with better pattern matching
        filter_params: Dict[str, Any] = {}
        
        # Handle different pattern types
        if '|' in measurement_pattern:
            # For OR conditions, ensure each part has proper wildcards
            patterns = []
            for part in measurement_pattern.split('|'):
                part = part.strip()
                # Add wildcards if needed
                if not part.startswith('.*'):
                    part = f".*{part}"
                if not part.endswith('.*'):
                    part = f"{part}.*"
                patterns.append(part)
            filter_params["plugin"] = '|'.join(patterns)
        else:
            # Single pattern - ensure it has proper wildcards
            pattern = measurement_pattern
            if not pattern.startswith('.*'):
                pattern = f".*{pattern}"
            if not pattern.endswith('.*'):
                pattern = f"{pattern}.*"
            filter_params["plugin"] = pattern
        
        # Add node filter if specified
        if validated_node:
            filter_params["vsn"] = str(validated_node)
        
        logger.info(f"Using filter parameters: {filter_params}")
        
        # Query for matching measurements
        start, end = SageDataService._parse_time_range(validated_time)
        df = data_service.query_data(start, end, filter_params)
        
        if df.empty:
            # Try name filter if plugin filter returns no results
            name_filter = filter_params.copy()
            name_filter["name"] = name_filter.pop("plugin")
            logger.info(f"Trying name filter: {name_filter}")
            df = data_service.query_data(start, end, name_filter)
            
        if df.empty:
            node_text = f" for node {validated_node}" if validated_node else ""
            return f"No measurements matching '{measurement_pattern}'{node_text} found in the last {validated_time}"
        
        # Show what was found
        result = f"Found {len(df)} records matching '{measurement_pattern}':\n"
        result += f"Time range: {validated_time}\n"
        
        # Group by plugin first
        plugins = sorted(df['plugin'].unique()) if 'plugin' in df.columns else []
        if plugins:
            result += f"\nPlugins found ({len(plugins)}):\n"
            for plugin in plugins:
                plugin_df = df[df['plugin'] == plugin]
                result += f"\n{plugin}:\n"
                
                # Get nodes for this plugin
                nodes = sorted(plugin_df['meta.vsn'].unique())
                result += f"- Nodes: {', '.join(nodes)}\n"
                
                # Get measurements for this plugin
                measurements = sorted(plugin_df['name'].unique())
                result += f"- Measurements: {', '.join(measurements)}\n"
                
                # Show recent data samples
                result += "- Recent data:\n"
                recent = plugin_df.sort_values('timestamp', ascending=False).head(3)
                for _, row in recent.iterrows():
                    timestamp = data_service._safe_timestamp_format(row['timestamp'])
                    node = row.get('meta.vsn', 'N/A')
                    name = row.get('name', 'N/A')
                    value = row.get('value', 'N/A')
                    
                    result += f"  {timestamp} | Node {node} | {name}"
                    if isinstance(value, (int, float)):
                        result += f" | Value: {value:.2f}"
                    elif value != 'N/A':
                        result += f" | Value: {value}"
                    result += "\n"
        else:
            # If no plugins found, group by measurement name
            measurements = sorted(df['name'].unique())
            result += f"\nMeasurements found ({len(measurements)}):\n"
            for measurement in measurements:
                measurement_df = df[df['name'] == measurement]
                result += f"\n{measurement}:\n"
                
                # Get nodes for this measurement
                nodes = sorted(measurement_df['meta.vsn'].unique())
                result += f"- Nodes: {', '.join(nodes)}\n"
                
                # Show recent data samples
                result += "- Recent data:\n"
                recent = measurement_df.sort_values('timestamp', ascending=False).head(3)
                for _, row in recent.iterrows():
                    timestamp = data_service._safe_timestamp_format(row['timestamp'])
                    node = row.get('meta.vsn', 'N/A')
                    value = row.get('value', 'N/A')
                    
                    result += f"  {timestamp} | Node {node}"
                    if isinstance(value, (int, float)):
                        result += f" | Value: {value:.2f}"
                    elif value != 'N/A':
                        result += f" | Value: {value}"
                    result += "\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error searching measurements: {e}")
        return f"Error searching measurements: {str(e)}"


@mcp.tool()
def get_node_temperature(node_id: str, sensor_type: str = "bme680") -> str:
    """Get current temperature data for a specific node/sensor. Defaults to environment (bme680) temperature. Use sensor_type='bme280' for internal/hardware temperature."""
    try:
        validated_node = NodeID(value=node_id)
        logger.info(f"Getting temperature for node: {validated_node} (sensor: {sensor_type})")

        # Query for temperature data, filtered by sensor type
        start, end = SageDataService._parse_time_range("-1h")
        df = data_service.query_data(
            start, end,
            {
                "name": DataType.TEMPERATURE.value,
                "vsn": str(validated_node),
                "sensor": sensor_type
            }
        )

        if df.empty:
            sensor_label = "environment (bme680)" if sensor_type == "bme680" else "internal/hardware (bme280)"
            return f"No {sensor_label} temperature data found for node {validated_node} in the last hour"

        # Get stats for this node
        if not df.empty:
            latest_reading = df.iloc[-1]
            avg_temp = df.value.mean()
            min_temp = df.value.min()
            max_temp = df.value.max()
            reading_count = len(df)

            # Get sensor info
            sensors = df['meta.sensor'].unique()

            # Handle timestamp formatting safely
            last_updated = data_service._safe_timestamp_format(latest_reading.timestamp)

            sensor_label = "environment (bme680)" if sensor_type == "bme680" else "internal/hardware (bme280)"
            result = f"""{sensor_label.capitalize()} temperature data for node {validated_node}:
- Latest reading: {latest_reading.value:.2f}°C (sensor: {latest_reading['meta.sensor']})
- Average over last hour: {avg_temp:.2f}°C
- Min/Max: {min_temp:.2f}°C / {max_temp:.2f}°C
- Total readings: {reading_count}
- Sensors active: {', '.join(sensors)}
- Last updated: {last_updated}"""

            return result

    except Exception as e:
        return f"Error getting temperature for node {node_id}: {str(e)}"


@mcp.tool()
def get_temperature_summary(time_range: str = "-1h", sensor_type: str = "bme680") -> str:
    """Get a summary of current temperature readings across all sensors. Defaults to environment (bme680) temperature. Use sensor_type='bme280' for internal/hardware temperature."""
    try:
        validated_time = TimeRange(value=time_range)

        start, end = SageDataService._parse_time_range(validated_time)
        df = data_service.query_data(start, end, {"name": DataType.TEMPERATURE.value, "sensor": sensor_type})

        if df.empty:
            sensor_label = "environment (bme680)" if sensor_type == "bme680" else "internal/hardware (bme280)"
            return f"No {sensor_label} temperature data available in the last {validated_time}"

        # Calculate overall stats
        total_readings = len(df)
        avg_temp = df.value.mean()
        min_temp = df.value.min()
        max_temp = df.value.max()
        unique_sensors = df['meta.vsn'].nunique()

        sensor_label = "environment (bme680)" if sensor_type == "bme680" else "internal/hardware (bme280)"
        summary = f"""{sensor_label.capitalize()} Temperature Summary (Last {validated_time}):
- Total readings: {total_readings}
- Unique sensors: {unique_sensors}
- Average temperature: {avg_temp:.2f}°C
- Min temperature: {min_temp:.2f}°C
- Max temperature: {max_temp:.2f}°C"""

        return summary

    except Exception as e:
        return f"Error getting temperature summary: {str(e)}"

@mcp.tool()
def get_node_info(node_id: str) -> str:
    """Get detailed information about a specific SAGE node, including its sensors, location, and hardware"""
    try:
        validated_node = NodeID(value=node_id)
        logger.info(f"Getting detailed node info for: {validated_node}")
        
        url = f"{SAGE_API_BASE}/nodes/{validated_node}/"
        logger.info(f"Fetching from {url}")
        
        response = requests.get(url)
        if response.status_code == 200:
            node_info = response.json()
            
            # Format the response in a readable way
            formatted_info = f"Node {validated_node} Information:\n"
            formatted_info += f"- Name: {node_info.get('name', 'Unknown')}\n"
            formatted_info += f"- Project: {node_info.get('project', 'Unknown')}\n"
            formatted_info += f"- Type: {node_info.get('type', 'Unknown')}\n"
            formatted_info += f"- Focus: {node_info.get('focus', 'Unknown')}\n"
            formatted_info += f"- Phase: {node_info.get('phase', 'Unknown')}\n"
            formatted_info += f"- Location: {node_info.get('location', 'Unknown')}\n"
            formatted_info += f"- Address: {node_info.get('address', 'Unknown')}\n"
            
            if node_info.get('gps_lat') and node_info.get('gps_lon'):
                formatted_info += f"- GPS: {node_info.get('gps_lat')}, {node_info.get('gps_lon')}\n"
            
            # Sensors section
            sensors = node_info.get('sensors', [])
            if sensors:
                formatted_info += f"\nSensors ({len(sensors)}):\n"
                for sensor in sensors:
                    status = "Active" if sensor.get('is_active') else "Inactive"
                    formatted_info += f"- {sensor.get('name', 'Unknown')}: {sensor.get('hw_model', 'Unknown')} ({sensor.get('manufacturer', 'Unknown')}) - {status}\n"
                    if sensor.get('capabilities'):
                        formatted_info += f"  Capabilities: {', '.join(sensor.get('capabilities'))}\n"
            
            # Computes section
            computes = node_info.get('computes', [])
            if computes:
                formatted_info += f"\nCompute Resources ({len(computes)}):\n"
                for compute in computes:
                    status = "Active" if compute.get('is_active') else "Inactive"
                    formatted_info += f"- {compute.get('name', 'Unknown')}: {compute.get('hw_model', 'Unknown')} ({compute.get('manufacturer', 'Unknown')}) - {status}\n"
                    if compute.get('capabilities'):
                        formatted_info += f"  Capabilities: {', '.join(compute.get('capabilities'))}\n"
            
            return formatted_info
        else:
            return f"Error: Could not retrieve node information. Status code: {response.status_code}"
    
    except Exception as e:
        logger.error(f"Error in get_node_info: {e}")
        return f"Error getting detailed information for node {node_id}: {str(e)}"


@mcp.tool()
def list_all_nodes() -> str:
    """List all SAGE nodes and their basic information"""
    try:
        logger.info(f"Fetching all nodes from {SAGE_MANIFESTS_URL}")
        
        response = requests.get(SAGE_MANIFESTS_URL)
        if response.status_code == 200:
            nodes = response.json()
            
            # Format the response in a readable way
            formatted_info = f"Available SAGE Nodes ({len(nodes)}):\n"
            
            # Group nodes by phase
            deployed_nodes = []
            other_nodes = []
            
            for node in nodes:
                node_info = f"- {node.get('vsn', 'Unknown')} ({node.get('name', 'Unknown')})"
                
                if node.get('phase') == 'Deployed':
                    if node.get('address'):
                        node_info += f": {node.get('address')}"
                    deployed_nodes.append(node_info)
                else:
                    phase = node.get('phase', 'Unknown phase')
                    node_info += f": {phase}"
                    other_nodes.append(node_info)
            
            if deployed_nodes:
                formatted_info += "\n\nDeployed Nodes:\n"
                formatted_info += "\n".join(deployed_nodes)
            
            if other_nodes:
                formatted_info += "\n\nOther Nodes:\n"
                formatted_info += "\n".join(other_nodes)
            
            # Add note about getting more details
            formatted_info += "\n\nFor detailed information about a specific node, use get_node_info with the node ID."
            
            return formatted_info
        else:
            return f"Error: Could not retrieve node list. Status code: {response.status_code}"
    
    except Exception as e:
        logger.error(f"Error in list_all_nodes: {e}")
        return f"Error listing all nodes: {str(e)}"


@mcp.tool()
def get_sensor_details(sensor_type: str) -> str:
    """Get detailed information about a specific type of sensor used in SAGE nodes"""
    try:
        if not sensor_type:
            return "Error: No sensor type provided"
        
        logger.info(f"Getting sensor details for type: {sensor_type}")
        logger.info(f"Fetching from {SAGE_SENSORS_URL}")
        
        response = requests.get(SAGE_SENSORS_URL)
        if response.status_code == 200:
            all_sensors = response.json()
            
            # Find matching sensors
            matching_sensors = [s for s in all_sensors if 
                               sensor_type.lower() in s.get('hardware', '').lower() or 
                               sensor_type.lower() in s.get('hw_model', '').lower() or
                               any(sensor_type.lower() in cap.lower() for cap in s.get('capabilities', []))]
            
            if not matching_sensors:
                return f"No sensors found matching '{sensor_type}'. Try a more general search term or check the spelling."
            
            # Format the response in a readable way
            formatted_info = f"Sensor Information for '{sensor_type}' (Found {len(matching_sensors)} matches):\n"
            
            for i, sensor in enumerate(matching_sensors, 1):
                formatted_info += f"\n--- Sensor {i}: {sensor.get('hw_model', 'Unknown')} ---\n"
                formatted_info += f"- Hardware ID: {sensor.get('hardware', 'Unknown')}\n"
                formatted_info += f"- Manufacturer: {sensor.get('manufacturer', 'Unknown')}\n"
                
                if sensor.get('capabilities'):
                    formatted_info += f"- Capabilities: {', '.join(sensor.get('capabilities'))}\n"
                
                if sensor.get('datasheet'):
                    formatted_info += f"- Datasheet: {sensor.get('datasheet')}\n"
                
                if sensor.get('vsns'):
                    formatted_info += f"- Used in nodes: {', '.join(sensor.get('vsns'))}\n"
                
                # Add description in a cleaner format
                if sensor.get('description'):
                    desc = sensor.get('description').replace('# ', '').replace('\r\n\r\n', '\n').replace('\r\n', ' ')
                    # Limit description length for readability
                    if len(desc) > 300:
                        desc = desc[:297] + "..."
                    formatted_info += f"- Description: {desc}\n"
            
            return formatted_info
        else:
            return f"Error: Could not retrieve sensor information. Status code: {response.status_code}"
    
    except Exception as e:
        logger.error(f"Error in get_sensor_details: {e}")
        return f"Error getting sensor details for '{sensor_type}': {str(e)}"

# ----------------------------------------
# 3. JOB SUBMISSION TOOLS
# ----------------------------------------

@mcp.tool()
def submit_sage_job(
    job_name: str,
    nodes: str,  # Comma-separated list like "W027" or "W023,W027" 
    plugin_image: str = "",
    plugin_args: str = "",  # JSON string or comma-separated key=value pairs
    science_rules: str = "",  # Override default science rules
    selector_requirements: str = ""  # JSON string for selector requirements like '{"resource.gpu": "true"}'
) -> str:
    """Submit a job to run on SAGE nodes.
    
    DEPRECATED: Use submit_plugin_job() for pre-configured plugins or this tool for custom images.
    
    If plugin_image is empty, this will provide recommendations based on the job name.
    The job name can be a natural language description of what you want to do.
    
    For pre-configured plugins, use:
    - submit_plugin_job(plugin_type, job_name, nodes, plugin_args)
    - submit_multi_plugin_job(job_name, nodes, plugins_config)
    """
    try:
        # If no plugin specified, treat job_name as a task description and provide recommendations
        if not plugin_image:
            recommendation_msg = find_plugins_for_task(job_name)
            recommendation_msg += "\n\n💡 TIP: For easier job submission, try:\n"
            recommendation_msg += "• submit_plugin_job(plugin_type, job_name, nodes, plugin_args)\n"
            recommendation_msg += "• submit_multi_plugin_job(job_name, nodes, plugins_config)\n"
            recommendation_msg += "\nThese tools handle all the complex configuration automatically!"
            return recommendation_msg
            
        # Normal job submission logic for custom images
        node_list = [n.strip() for n in nodes.split(",") if n.strip()]
        if not node_list:
            raise ValueError("No valid nodes specified")
            
        # Parse plugin arguments
        plugin_args_obj = PluginArguments.from_string(plugin_args)
            
        # Parse selector requirements
        selector_obj = SelectorRequirements.from_json_str(selector_requirements)
            
        # Create plugin spec
        plugin = PluginSpec(
            name=job_name,
            image=plugin_image,
            args=plugin_args_obj,
            selector=selector_obj
        )
            
        # Create and submit job
        job = SageJob(
            name=job_name,
            nodes=node_list,
            plugins=[plugin],
            science_rules=science_rules.split(",") if science_rules else []
        )
            
        job_service = SageJobService(config=SageConfig())
        success, result = job_service.submit_job(job)
            
        if success:
            return f"Successfully submitted job '{job_name}'. Job ID: {result}"
        else:
            return f"Failed to submit job: {result}"
            
    except Exception as e:
        logger.error(f"Error submitting job: {e}")
        return f"Error submitting job: {str(e)}"


@mcp.tool()
def check_job_status(job_id: str) -> str:
    """Check the status of a submitted SAGE job"""
    return job_service.check_job_status(job_id)


@mcp.tool()
def query_job_data(
    job_name: str,
    node_id: str = "",
    time_range: str = "-30m",
    data_type: str = "upload"
) -> str:
    """Query data generated by a running SAGE job"""
    try:
        validated_time = TimeRange(value=time_range)
        validated_node = NodeID(value=node_id) if node_id else None
        
        logger.info(f"Querying data for job: {job_name} on node: {validated_node or 'all'}")
        
        # Smart job name to plugin pattern mapping
        job_to_plugin_patterns = {
            # Map common job name patterns to actual plugin patterns
            "audio": [".*audio.*", ".*sage-audio.*"],
            "air-quality": [".*air-quality.*", ".*airquality.*"],
            "cloud": [".*cloud.*"],
            "image": [".*image.*", ".*sampler.*"],
            "camera": [".*camera.*", ".*imagesampler.*"],
            "sound": [".*sound.*", ".*audio.*"],
            "weather": [".*weather.*", ".*wxt.*"],
            "rain": [".*rain.*", ".*raingauge.*"],
            "temperature": [".*temperature.*", ".*temp.*"],
            "motion": [".*motion.*"],
            "ptz": [".*ptz.*"],
            "yolo": [".*yolo.*"],
            "bird": [".*bird.*", ".*avian.*"],
            "mobotix": [".*mobotix.*"]
        }
        
        # Build filter parameters with intelligent pattern matching
        filter_params = {}
        plugin_patterns = []
        
        # First, try exact job name match
        if not job_name.startswith('.*'):
            plugin_patterns.append(f".*{job_name}.*")
        
        # Then, try to match based on job type keywords
        job_lower = job_name.lower()
        for keyword, patterns in job_to_plugin_patterns.items():
            if keyword in job_lower:
                plugin_patterns.extend(patterns)
                logger.info(f"Detected job type '{keyword}' in job name, adding patterns: {patterns}")
        
        # If we found patterns, use them; otherwise fall back to the original logic
        if plugin_patterns:
            # Remove duplicates while preserving order
            unique_patterns = []
            for pattern in plugin_patterns:
                if pattern not in unique_patterns:
                    unique_patterns.append(pattern)
            filter_params["plugin"] = '|'.join(unique_patterns)
        else:
            # Fallback to original logic
            if '|' in job_name:
                patterns = []
                for part in job_name.split('|'):
                    part = part.strip()
                    if part:
                        patterns.append(part)
                filter_params["plugin"] = '|'.join(patterns)
            else:
                pattern = job_name
                if not pattern.startswith('.*'):
                    pattern = f".*{pattern}"
                if not pattern.endswith('.*'):
                    pattern = f"{pattern}.*"
                filter_params["plugin"] = pattern
        
        if validated_node:
            filter_params["vsn"] = str(validated_node)
        
        if data_type != "upload":
            filter_params["name"] = data_type
        
        logger.info(f"Using filter parameters: {filter_params}")
        
        # Query the data
        start, end = SageDataService._parse_time_range(validated_time)
        df = data_service.query_data(start, end, filter_params)
        
        if df.empty:
            # If no data found with smart matching, try a broader search
            logger.info("No data found with smart matching, trying broader search...")
            broader_patterns = []
            
            # Extract keywords from job name for broader search
            import re
            words = re.findall(r'\w+', job_name.lower())
            for word in words:
                if len(word) > 2:  # Skip very short words
                    broader_patterns.append(f".*{word}.*")
            
            if broader_patterns:
                filter_params["plugin"] = '|'.join(broader_patterns)
                logger.info(f"Trying broader search with patterns: {filter_params['plugin']}")
                df = data_service.query_data(start, end, filter_params)
            
            if df.empty:
                return f"No data found for job '{job_name}' in the last {validated_time}. The job may still be starting up or not producing data yet.\n\n💡 Tip: Try using search_measurements() to see what plugins are actually running on this node."
        
        # Format results
        result = f"📊 Job Data Summary for '{job_name}' (last {validated_time}):\n\n"
        
        # Basic stats
        total_records = len(df)
        unique_nodes = df['meta.vsn'].nunique() if 'meta.vsn' in df.columns else 0
        unique_plugins = df['plugin'].nunique() if 'plugin' in df.columns else 0
        unique_measurements = df['name'].nunique() if 'name' in df.columns else 0
        
        result += f"Total records: {total_records}\n"
        result += f"Nodes reporting: {unique_nodes}\n"
        result += f"Plugins active: {unique_plugins}\n"
        result += f"Measurement types: {unique_measurements}\n"
        
        # Show plugins and measurements found
        if 'plugin' in df.columns:
            plugins = sorted(df['plugin'].unique())
            result += f"\nPlugins: {', '.join(plugins)}\n"
        
        if 'name' in df.columns:
            measurements = sorted(df['name'].unique())
            result += f"Measurements: {', '.join(measurements)}\n"
        
        # Show time range
        if 'timestamp' in df.columns:
            latest = data_service._safe_timestamp_format(df['timestamp'].max())
            earliest = data_service._safe_timestamp_format(df['timestamp'].min())
            result += f"\nTime range: {earliest} to {latest}\n"
        
        # Show sample of recent data
        result += "\nRecent data sample:\n"
        recent = df.sort_values('timestamp', ascending=False).head(5)
        for _, row in recent.iterrows():
            timestamp = data_service._safe_timestamp_format(row.get('timestamp', 'N/A'))
            node = row.get('meta.vsn', 'N/A')
            name = row.get('name', 'N/A')
            plugin = row.get('plugin', 'N/A')
            value = row.get('value', 'N/A')
            result += f"  {timestamp} | Node {node} | {name}"
            if isinstance(value, (int, float)):
                result += f" | Value: {value:.2f}"
            elif value != 'N/A':
                result += f" | Value: {value}"
            result += f" | Plugin: {plugin}\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error querying job data: {e}")
        return f"Error querying job data: {str(e)}"


@mcp.tool()
def force_remove_job(job_id: str) -> str:
    """Force remove a job from the scheduler"""
    return job_service.force_remove_job(job_id)


@mcp.tool()
def suspend_job(job_id: str) -> str:
    """Suspend a job from the scheduler"""
    return job_service.suspend_job(job_id)


# ----------------------------------------
# 4. TEMPLATE JOB SUBMISSION TOOLS
# ----------------------------------------

@mcp.tool()
def submit_plugin_job(
    plugin_type: str,
    job_name: str,
    nodes: str
) -> str:
    """Submit a SAGE plugin job using hardcoded working templates.
    
    Supported plugin types:
    - air_quality: Air quality monitoring
    - audio_sampler: Audio sampling (15 min intervals)
    - camera_sampler: Camera sampling (bottom camera, hourly)
    - camera_sampler_top: Camera sampling (top camera, hourly)
    
    Args:
        plugin_type: Type of plugin to deploy
        job_name: Name for the job
        nodes: Comma-separated list of node IDs
    """
    try:
        # Parse nodes
        node_list = [NodeID(value=node.strip()).value for node in nodes.split(",")]
        
        # Map plugin types to template methods (hardcoded, no custom args)
        if plugin_type == "air_quality":
            job = JobTemplates.air_quality(job_name=job_name, nodes=node_list)
        elif plugin_type == "audio_sampler":
            job = JobTemplates.audio_sampler(job_name=job_name, nodes=node_list)
        elif plugin_type == "camera_sampler":
            job = JobTemplates.camera_sampler(job_name=job_name, nodes=node_list, camera_position="bottom")
        elif plugin_type == "camera_sampler_top":
            job = JobTemplates.camera_sampler(job_name=job_name, nodes=node_list, camera_position="top")
        else:
            available_types = "air_quality, audio_sampler, camera_sampler, camera_sampler_top"
            return f"❌ Unknown plugin type '{plugin_type}'. Available types: {available_types}"
        
        # Submit job
        success, message = job_service.submit_job(job)
        return message
        
    except Exception as e:
        logger.error(f"Error submitting {plugin_type} job: {e}")
        return f"❌ Error submitting {plugin_type} job: {str(e)}"


# ----------------------------------------
# GEOGRAPHICAL QUERY TOOLS
# ----------------------------------------

@mcp.tool()
def get_nodes_by_location(location: str) -> str:
    """Find nodes in a specific geographic location or region (city, state, region, etc.)"""
    try:
        logger.info(f"Getting nodes in location: {location}")
        response = requests.get(SAGE_MANIFESTS_URL)
        if response.status_code != 200:
            return f"Error: Could not retrieve node list. Status code: {response.status_code}"
        nodes = response.json()
        if not nodes:
            return "No nodes found in the database."

        location_lower = location.lower().strip()

        # Define region mappings
        regions = {
            "east coast": ["new york", "massachusetts", "rhode island", "connecticut", "new jersey", 
                          "delaware", "maryland", "virginia", "north carolina", "south carolina", 
                          "georgia", "florida", "pennsylvania", "washington dc", "washington d.c.",
                          "maine", "new hampshire", "vermont", "ny", "ma", "ri", "ct", "nj", "de", 
                          "md", "va", "nc", "sc", "ga", "fl", "pa", "dc", "me", "nh", "vt", "eastern"],
            "west coast": ["california", "oregon", "washington", "ca", "or", "wa", "western"],
            "midwest": ["illinois", "indiana", "michigan", "ohio", "wisconsin", "minnesota", 
                       "iowa", "missouri", "kansas", "nebraska", "south dakota", "north dakota",
                       "il", "in", "mi", "oh", "wi", "mn", "ia", "mo", "ks", "ne", "sd", "nd", "chicago"],
            "southwest": ["arizona", "new mexico", "texas", "oklahoma", "nevada", "az", "nm", "tx", "ok", "nv"],
            "southeast": ["alabama", "mississippi", "louisiana", "tennessee", "kentucky", "al", "ms", "la", "tn", "ky"]
        }

        # Check if the location is a region
        is_region = False
        target_states = []
        for region, states in regions.items():
            if location_lower == region:
                is_region = True
                target_states.extend(states)
                break

        matching_nodes = []
        debug_info = []
        for node in nodes:
            node_vsn = node.get('vsn', 'Unknown')
            node_address = node.get('address', '').lower()
            node_location = node.get('location', '').lower()
            node_name = node.get('name', '').lower()

            # Use substring match for city
            city_match = (location_lower in node_address) or (location_lower in node_location)
            region_match = False
            if is_region:
                for state in target_states:
                    if state in node_address or state in node_location or state in node_name:
                        region_match = True
                        break

            include = (is_region and region_match) or (not is_region and city_match)
            debug_info.append({
                'vsn': node_vsn,
                'address': node_address,
                'location': node_location,
                'city_match': bool(city_match),
                'region_match': bool(region_match),
                'included': include
            })
            if include:
                matching_nodes.append(node)

        # Log debug info for all nodes considered
        logger.info("Node filtering debug info:")
        for info in debug_info:
            logger.info(f"Node {info['vsn']}: address='{info['address']}', location='{info['location']}', city_match={info['city_match']}, region_match={info['region_match']}, included={info['included']}")

        if not matching_nodes:
            logger.info(f"No nodes matched for location '{location}'.")
            return f"No SAGE nodes found in {location}."

        matching_nodes.sort(key=lambda x: x.get('vsn', ''))
        result = f"Found {len(matching_nodes)} nodes in or near {location}:\n\n"
        for node in matching_nodes:
            vsn = node.get('vsn', 'Unknown')
            name = node.get('name', 'Unknown')
            address = node.get('address', 'Unknown location')
            phase = node.get('phase', 'Unknown phase')
            result += f"- Node {vsn}: {name}\n"
            result += f"  Location: {address}\n"
            result += f"  Status: {phase}\n"
            sensors = node.get('sensors', [])
            if sensors:
                sensor_names = [s.get('name', 'Unknown') for s in sensors]
                result += f"  Sensors: {', '.join(sensor_names[:5])}"
                if len(sensor_names) > 5:
                    result += f" and {len(sensor_names) - 5} more"
                result += "\n"
            result += "\n"
        logger.info(f"Included nodes for location '{location}': {[n.get('vsn', 'Unknown') for n in matching_nodes]}")
        return result
    except Exception as e:
        logger.error(f"Error in get_nodes_by_location: {e}")
        return f"Error finding nodes in {location}: {str(e)}"

@mcp.tool()
def get_measurement_stat_by_location(
    location: str,
    measurement_type: str = "env.temperature",
    stat: str = "max",  # 'min', 'max', or 'avg'
    time_range: str = "-1h",
    sensor_type: str = "bme680",
    filter_expr: str = ""
) -> str:
    """Get a statistic (min, max, avg) for any measurement type (e.g., temperature, pressure) across all nodes in a specific location. Supports optional filtering with a pandas query expression (e.g., 'value > 5').
    Args:
        location: City, region, or state to search for nodes.
        measurement_type: Measurement type (e.g., 'env.temperature', 'env.pressure').
        stat: Statistic to compute ('min', 'max', or 'avg').
        time_range: Time range for the query (e.g., '-1h', 'today').
        sensor_type: Sensor type to filter (e.g., 'bme680', 'bme280').
        filter_expr: Optional pandas query expression to filter the data (e.g., 'value > 5').
    Returns:
        A string summary of the requested statistic for the measurement in the location.
    """
    import pandas as pd
    import re
    try:
        # Rain measurement metadata
        rain_meta = {
            "env.raingauge.rint": {
                "unit": "mm/hr",
                "desc": "Hydreon RG-15 rain gauge rain intensity (past minute, extrapolated to hour)"
            },
            "env.raingauge.event_acc": {
                "unit": "mm",
                "desc": "Hydreon RG-15 rain gauge rain event precipitation accumulation (resets 60 min after last drop)"
            },
            "env.raingauge.total_acc": {
                "unit": "mm",
                "desc": "Hydreon RG-15 rain gauge total precipitation accumulation (since last reset)"
            }
        }
        logger.info(f"Getting {stat} of {measurement_type} for location: {location}")
        validated_time = TimeRange(value=time_range)
        # Get all nodes in the specified location
        location_result = get_nodes_by_location(location)
        if "No SAGE nodes found" in location_result or "Error" in location_result:
            return location_result
        # Parse the location result to extract node IDs
        vsn_pattern = r"Node (W\d+):"
        node_ids = re.findall(vsn_pattern, location_result)
        if not node_ids:
            return f"Found nodes in {location}, but couldn't extract node IDs."
        # Limit to max 20 nodes for performance
        if len(node_ids) > 20:
            logger.info(f"Limiting query from {len(node_ids)} to 20 nodes for performance")
            node_ids = node_ids[:20]
        logger.info(f"Querying {measurement_type} data for {len(node_ids)} nodes in {location}")
        all_data = []
        is_raingauge = measurement_type.startswith("env.raingauge")
        for node_id in node_ids:
            if is_raingauge:
                # Use a regex plugin filter for rain gauge queries
                filter_params = {
                    "plugin": ".*plugin-raingauge.*",
                    "vsn": node_id
                }
                logger.info(f"Querying SAGE data with plugin regex filter: {filter_params}")
                start, end = SageDataService._parse_time_range(validated_time)
                df = data_service.query_data(start, end, filter_params)
                logger.info(f"[Rain plugin] Raw df shape: {df.shape}, columns: {list(df.columns) if not df.empty else 'EMPTY'}")
                # Now filter for the measurement_type in the DataFrame
                if not df.empty:
                    df2 = df[df['name'] == measurement_type]
                    logger.info(f"[Rain plugin] After measurement filter: {df2.shape}, columns: {list(df2.columns) if not df2.empty else 'EMPTY'}")
                    if not df2.empty:
                        df2['node_id'] = node_id
                        all_data.append(df2)
                # Fallback: if no data found, try querying by measurement name only
                if df.empty:
                    fallback_params = {
                        "name": measurement_type,
                        "vsn": node_id
                    }
                    logger.info(f"[Rain fallback] Querying SAGE data with fallback filter: {fallback_params}")
                    start, end = SageDataService._parse_time_range(validated_time)
                    df_fallback = data_service.query_data(start, end, fallback_params)
                    logger.info(f"[Rain fallback] Fallback df shape: {df_fallback.shape}, columns: {list(df_fallback.columns) if not df_fallback.empty else 'EMPTY'}")
                    if not df_fallback.empty:
                        df_fallback['node_id'] = node_id
                        all_data.append(df_fallback)
            else:
                # Default logic for other measurement types
                filter_params = {
                    "name": measurement_type,
                    "vsn": node_id
                }
                if sensor_type:
                    filter_params["sensor"] = sensor_type
                logger.info(f"Querying SAGE data with filter: {filter_params}")
                start, end = SageDataService._parse_time_range(validated_time)
                df = data_service.query_data(start, end, filter_params)
                if not df.empty:
                    df['node_id'] = node_id
                    all_data.append(df)
        if not all_data:
            return f"No {measurement_type} data found for nodes in {location} during the last {validated_time}"
        combined_data = pd.concat(all_data, ignore_index=True)
        # Apply filter expression if provided
        if filter_expr:
            try:
                filtered_data = combined_data.query(filter_expr)
                logger.info(f"Applied filter expression '{filter_expr}': {len(filtered_data)} records remain")
            except Exception as e:
                logger.error(f"Invalid filter expression '{filter_expr}': {e}")
                return f"Error: Invalid filter expression '{filter_expr}': {e}"
        else:
            filtered_data = combined_data
        if filtered_data.empty:
            return f"No {measurement_type} data matched the filter '{filter_expr}' for nodes in {location} during the last {validated_time}"
        # Add units and description for rain measurements
        unit = ""
        desc = ""
        if is_raingauge and measurement_type in rain_meta:
            unit = rain_meta[measurement_type]["unit"]
            desc = rain_meta[measurement_type]["desc"]
        # Compute the requested statistic
        if stat == "min":
            idx = filtered_data['value'].idxmin()
            reading = filtered_data.loc[idx]
            stat_val = reading['value']
            stat_node = reading['node_id']
            stat_time = data_service._safe_timestamp_format(reading['timestamp'])
            stat_str = f"Minimum {measurement_type} in {location} (last {validated_time}, filter: '{filter_expr}'):\n\n"
            stat_str += f"❄️ {stat_val:.2f}{' ' + unit if unit else ''} measured at node {stat_node}\n  Time: {stat_time}\n  Data from {len(filtered_data)} filtered readings\n"
            if desc:
                stat_str += f"Description: {desc}\n"
        elif stat == "max":
            idx = filtered_data['value'].idxmax()
            reading = filtered_data.loc[idx]
            stat_val = reading['value']
            stat_node = reading['node_id']
            stat_time = data_service._safe_timestamp_format(reading['timestamp'])
            stat_str = f"Maximum {measurement_type} in {location} (last {validated_time}, filter: '{filter_expr}'):\n\n"
            stat_str += f"🔥 {stat_val:.2f}{' ' + unit if unit else ''} measured at node {stat_node}\n  Time: {stat_time}\n  Data from {len(filtered_data)} filtered readings\n"
            if desc:
                stat_str += f"Description: {desc}\n"
        elif stat == "avg":
            stat_val = filtered_data['value'].mean()
            stat_str = f"Average {measurement_type} in {location} (last {validated_time}, filter: '{filter_expr}'):\n\n"
            stat_str += f"📊 {stat_val:.2f}{' ' + unit if unit else ''} (from {len(filtered_data)} filtered readings)\n"
            if desc:
                stat_str += f"Description: {desc}\n"
        else:
            return f"Error: Unknown stat '{stat}'. Use 'min', 'max', or 'avg'."
        return stat_str
    except Exception as e:
        logger.error(f"Error in get_measurement_stat_by_location: {e}")
        return f"Error getting {stat} of {measurement_type} for {location}: {str(e)}"

# ----------------------------------------
# 5. PROMPTS
# ----------------------------------------

@mcp.prompt()
def summarize_temperature_anomalies() -> list[base.Message]:
    """Prompt to analyze temperature anomalies"""
    return [
        base.UserMessage("Can you summarize any temperature anomalies from the past hour?")
    ]


@mcp.prompt()
def suggest_image_sampler_cron() -> list[base.Message]:
    """Prompt for cron expression help"""
    return [
        base.UserMessage(
            "Help me write a scienceRule cron expression for the image-sampler plugin "
            "that samples every 10 minutes between 6am and 6pm."
        )
    ]


@mcp.prompt()
def suggest_environmental_job() -> list[base.Message]:
    """Prompt for environmental monitoring job setup"""
    return [
        base.UserMessage(
            "I want to monitor environmental conditions (temperature, humidity, pressure) "
            "across all nodes. What kind of job should I set up?"
        )
    ]


# ----------------------------------------
# 6. STARTUP AND SERVER ENTRY
# ----------------------------------------

async def print_registered() -> None:
    """Print registered components for debugging"""
    try:
        # Get server capabilities
        tools = await mcp.list_tools()
        resources = await mcp.list_resources()
        prompts = await mcp.list_prompts()

        print("\n" + "="*50)
        print("🚀 SageDataMCP Server Starting...")
        print("="*50)
        print(f"✅ Registered tools ({len(tools)}):")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
            
        print(f"\n✅ Registered resources ({len(resources)}):")
        for resource in resources:
            print(f"   - {resource.name}: {resource.description}")
            
        print(f"\n✅ Registered prompts ({len(prompts)}):")
        for prompt in prompts:
            print(f"   - {prompt.name}: {prompt.description}")
            
        print(f"\n🌐 Server will be available at: http://localhost:8000/mcp")
        print("="*50 + "\n")
        
    except Exception as e:
        logger.error(f"Error during startup registration check: {e}")
        # Don't exit here, let the server try to start anyway


def test_sage_connection() -> bool:
    """Test connection to SAGE data client"""
    try:
        logger.info("Testing sage_data_client connection...")
        test_df = sage_data_client.query(start="-5m", filter={"name": "env.temperature"})
        logger.info(f"✅ sage_data_client working - found {len(test_df)} recent temperature records")
        return True
    except Exception as e:
        logger.warning(f"⚠️ sage_data_client test failed: {e}")
        logger.warning("Server will start but temperature queries may fail")
        return False


def main() -> None:
    """Main entry point"""
    # Test sage_data_client availability
    test_sage_connection()

    # Print registration info
    try:
        asyncio.run(print_registered())
    except Exception as e:
        logger.error(f"Error printing registration info: {e}")
    
    # Start the server
    try:
        logger.info("Starting MCP server...")
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

@mcp.tool()
def find_plugins_for_task(task_description: str) -> str:
    """Find and recommend plugins/apps suitable for a given task description.
    
    This tool analyzes the task description and matches it against available plugins
    in the ECR registry, considering their descriptions, keywords, and capabilities.
    
    Args:
        task_description: Natural language description of the desired task
    """
    try:
        # Normalize task description
        task = task_description.lower() if task_description else ""
        if not task:
            return "Please provide a task description to find relevant plugins."
        
        logger.info(f"Searching for plugins matching task: {task_description}")
        
        # Use the improved plugin registry search
        matching_plugins = plugin_registry.search_plugins(task, max_results=10)
        
        if not matching_plugins:
            suggestion = "Try using different keywords or check these categories:\n"
            suggestion += "- Camera/Vision: camera, image, video, ptz, detection\n"
            suggestion += "- Audio: sound, audio, microphone, bird, noise\n"
            suggestion += "- Environmental: temperature, humidity, pressure, weather\n"
            suggestion += "- AI/Detection: yolo, object detection, recognition\n"
            suggestion += "- Movement: motion, tracking, pan, tilt, zoom"
            return f"No plugins found matching '{task_description}'.\n\n{suggestion}"
            
        response_parts = [f"Found {len(matching_plugins)} plugins matching your task '{task_description}':"]
        
        for i, plugin in enumerate(matching_plugins, 1):
            response_parts.append(f"\n{i}. {plugin.name} (v{plugin.version}):")
            response_parts.append(f"   Image: {plugin.id}")
            
            if plugin.description:
                response_parts.append(f"   Description: {plugin.description}")
            
            if plugin.keywords:
                response_parts.append(f"   Keywords: {plugin.keywords}")
            
            if plugin.authors:
                response_parts.append(f"   Authors: {plugin.authors}")
            
            if plugin.inputs:
                input_params = ", ".join(f"{inp.id} ({inp.type})" for inp in plugin.inputs)
                response_parts.append(f"   Parameters: {input_params}")
            
            if plugin.homepage:
                response_parts.append(f"   Homepage: {plugin.homepage}")
            
            # Show a snippet of the science description if available
            if plugin.science_description_content:
                # Take first 200 characters of science description
                science_snippet = plugin.science_description_content[:200].strip()
                if len(plugin.science_description_content) > 200:
                    science_snippet += "..."
                response_parts.append(f"   Science Description: {science_snippet}")
            
            response_parts.append("")
            
        return "\n".join(response_parts)
        
    except Exception as e:
        logger.error(f"Error finding plugins: {e}")
        return f"An unexpected error occurred while searching for plugins. Please try again later. Error: {str(e)}"

@mcp.tool()
def get_plugin_data(plugin_id: str, nodes: str = "", time_range: str = "-1h") -> str:
    """Query and format data from a specific plugin"""
    try:
        # Parse nodes if provided
        node_list = [n.strip() for n in nodes.split(",")] if nodes else None
        
        # Get plugin metadata
        plugin = plugin_registry.get_plugin_by_id(plugin_id)
        if not plugin:
            return f"Plugin not found: {plugin_id}"
        
        # Query data
        df = plugin_query_service.query_plugin_data(
            plugin_id=plugin_id,
            nodes=node_list,
            time_range=time_range
        )
        
        # Format results
        return plugin_query_service.format_plugin_data(df, plugin)
        
    except Exception as e:
        logger.error(f"Error getting plugin data: {e}")
        return f"Error getting plugin data: {str(e)}"

@mcp.tool()
def get_cloud_images(time_range: str = "-1h", node_id: str = "") -> str:
    """Get recent cloud images from SAGE nodes. If no node_id is specified, searches across all nodes."""
    try:
        validated_time = TimeRange(value=time_range)
        validated_node = NodeID(value=node_id) if node_id else None
        logger.info(f"Querying cloud images for time range: {validated_time}")
        
        # Define cloud-related plugins with proper wildcards
        cloud_plugins = [
            ".*cloud-cover.*",
            ".*cloud-motion.*",
            ".*imagesampler.*"
        ]
        
        # Build filter parameters
        filter_params = {
            "plugin": '|'.join(cloud_plugins)
        }
        
        if validated_node:
            filter_params["vsn"] = str(validated_node)
        
        logger.info(f"Using filter parameters: {filter_params}")
        
        # Query the data
        start, end = SageDataService._parse_time_range(validated_time)
        df = data_service.query_data(start, end, filter_params)
        
        if df.empty:
            node_text = f" for node {validated_node}" if validated_node else ""
            return f"No cloud images found{node_text} in the last {validated_time}"
        
        # Format results
        result = f"Cloud images found (last {validated_time}):\n\n"
        
        # Basic stats
        total_records = len(df)
        unique_nodes = df['meta.vsn'].nunique() if 'meta.vsn' in df.columns else 0
        unique_plugins = df['plugin'].nunique() if 'plugin' in df.columns else 0
        unique_measurements = df['name'].nunique() if 'name' in df.columns else 0
        
        result += f"Total records: {total_records}\n"
        result += f"Nodes reporting: {unique_nodes}\n"
        result += f"Plugins active: {unique_plugins}\n"
        result += f"Measurement types: {unique_measurements}\n\n"
        
        # Group by plugin
        plugins = sorted(df['plugin'].unique()) if 'plugin' in df.columns else []
        for plugin in plugins:
            plugin_df = df[df['plugin'] == plugin]
            result += f"Plugin: {plugin}\n"
            
            # Get nodes for this plugin
            nodes = sorted(plugin_df['meta.vsn'].unique())
            result += f"- Nodes: {', '.join(nodes)}\n"
            
            # Get measurements
            measurements = sorted(plugin_df['name'].unique())
            result += f"- Measurements: {', '.join(measurements)}\n"
            
            # Show recent data samples
            result += "- Recent data:\n"
            recent = plugin_df.sort_values('timestamp', ascending=False).head(3)
            for _, row in recent.iterrows():
                timestamp = data_service._safe_timestamp_format(row['timestamp'])
                node = row.get('meta.vsn', 'N/A')
                name = row.get('name', 'N/A')
                value = row.get('value', 'N/A')
                
                result += f"  {timestamp} | Node {node} | {name}"
                if isinstance(value, (int, float)):
                    result += f" | Value: {value:.2f}"
                elif value != 'N/A':
                    result += f" | Value: {value}"
                result += "\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting cloud images: {e}")
        return f"Error getting cloud images: {str(e)}"

@mcp.tool()
def mcp_sage_get_cloud_images(time_range: str = "-1h", node_id: str = "") -> str:
    """Get recent cloud images and cloud-related data from SAGE nodes"""
    return get_cloud_images(time_range, node_id)

@mcp.tool()
def get_image_data(time_range: str = "-1h", node_id: str = "", plugin_pattern: str = ".*") -> str:
    """Get recent image data from SAGE nodes. Supports filtering by node and plugin pattern."""
    try:
        validated_time = TimeRange(value=time_range)
        validated_node = NodeID(value=node_id) if node_id else None
        
        logger.info(f"Querying image data for time range: {validated_time}")
        if validated_node:
            logger.info(f"Filtering for node: {validated_node}")
        
        # Build filter parameters with better pattern matching
        filter_params = {}
        
        # Handle different pattern types for plugin pattern
        if '|' in plugin_pattern:
            # For OR conditions, ensure each part has proper wildcards
            patterns = []
            for part in plugin_pattern.split('|'):
                part = part.strip()
                if not part.startswith('.*'):
                    part = f".*{part}"
                if not part.endswith('.*'):
                    part = f"{part}.*"
                patterns.append(part)
            filter_params["plugin"] = '|'.join(patterns)
        else:
            # Single pattern - ensure it has proper wildcards
            pattern = plugin_pattern
            if not pattern.startswith('.*'):
                pattern = f".*{pattern}"
            if not pattern.endswith('.*'):
                pattern = f"{pattern}.*"
            filter_params["plugin"] = pattern
        
        if validated_node:
            filter_params["vsn"] = str(validated_node)
        
        logger.info(f"Using filter parameters: {filter_params}")
        
        # Query image data
        start, end = SageDataService._parse_time_range(validated_time)
        df = data_service.query_data(start, end, filter_params)
        
        if df.empty:
            node_text = f" for node {validated_node}" if validated_node else ""
            pattern_text = f" matching pattern '{plugin_pattern}'" if plugin_pattern != ".*" else ""
            return f"No image data found{node_text}{pattern_text} in the last {validated_time}"
        
        # Format results
        result = f"Image data found (last {validated_time}):\n\n"
        
        # Get basic stats
        total_records = len(df)
        unique_nodes = df['meta.vsn'].nunique() if 'meta.vsn' in df.columns else 0
        unique_plugins = df['plugin'].nunique() if 'plugin' in df.columns else 0
        
        result += f"Total records: {total_records}\n"
        result += f"Nodes reporting: {unique_nodes}\n"
        result += f"Plugins active: {unique_plugins}\n"
        
        # Show plugins found
        if 'plugin' in df.columns:
            plugins = sorted(df['plugin'].unique())
            result += f"\nPlugins: {', '.join(plugins)}\n"
        
        # Show time range
        if 'timestamp' in df.columns:
            latest = data_service._safe_timestamp_format(df['timestamp'].max())
            earliest = data_service._safe_timestamp_format(df['timestamp'].min())
            result += f"Data range: {earliest} to {latest}\n"
        
        # Show sample of recent data by plugin
        if 'plugin' in df.columns:
            result += f"\nRecent data by plugin:\n"
            for plugin in plugins:
                plugin_df = df[df['plugin'] == plugin]
                result += f"\nPlugin: {plugin}\n"
                result += f"  Records: {len(plugin_df)}\n"
                
                # Get nodes for this plugin
                nodes = sorted(plugin_df['meta.vsn'].unique())
                result += f"  Nodes: {', '.join(nodes)}\n"
                
                # Show sample of recent data for this plugin
                recent_data = plugin_df.sort_values('timestamp', ascending=False).head(3)
                result += "  Recent data:\n"
                for _, row in recent_data.iterrows():
                    timestamp = data_service._safe_timestamp_format(row.get('timestamp', 'N/A'))
                    node = row.get('meta.vsn', 'N/A')
                    name = row.get('name', 'N/A')
                    value = row.get('value', 'N/A')
                    result += f"    {timestamp} | Node: {node} | {name}"
                    if isinstance(value, (int, float)):
                        result += f" | Value: {value:.2f}"
                    elif value != 'N/A':
                        result += f" | Value: {value}"
                    result += "\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting image data: {e}")
        return f"Error getting image data: {str(e)}"

@mcp.tool()
def query_plugin_data_nl(query: str) -> str:
    """Query plugin data using natural language. Examples:
    - "Show me cloud cover data from the last hour"
    - "Get temperature readings from nodes W019, W020 in the last 30 minutes"
    - "What's the latest rain data from Chicago nodes?"
    """
    try:
        return plugin_query_service.query_by_natural_language(query)
    except Exception as e:
        logger.error(f"Error processing natural language query: {e}")
        return f"Error processing your query: {str(e)}"

@mcp.tool()
def mcp_sage_query_plugin_data_nl(query: str) -> str:
    """Query plugin data using natural language. Examples:
    - "Show me cloud cover data from the last hour"
    - "Get temperature readings from nodes W019, W020 in the last 30 minutes"
    - "What's the latest rain data from Chicago nodes?"
    """
    try:
        return plugin_query_service.query_by_natural_language(query)
    except Exception as e:
        logger.error(f"Error processing natural language query: {e}")
        return f"Error processing your query: {str(e)}"

@mcp.tool()
def mcp_sage_search_measurements(
    measurement_pattern: str,
    node_id: str = "",
    time_range: str = "-30m"
) -> str:
    """Search for specific measurement types using a pattern (regex supported)"""
    try:
        validated_time = TimeRange(value=time_range)
        validated_node = NodeID(value=node_id) if node_id else None
        
        logger.info(f"Searching for measurements matching: {measurement_pattern}")
        
        # Build filter parameters with better pattern matching
        filter_params: Dict[str, Any] = {}
        
        # Handle different pattern types
        if '|' in measurement_pattern:
            # For OR conditions, ensure each part has proper wildcards
            patterns = []
            for part in measurement_pattern.split('|'):
                part = part.strip()
                # Add wildcards if needed
                if not part.startswith('.*'):
                    part = f".*{part}"
                if not part.endswith('.*'):
                    part = f"{part}.*"
                patterns.append(part)
            filter_params["plugin"] = '|'.join(patterns)
        else:
            # Single pattern - ensure it has proper wildcards
            pattern = measurement_pattern
            if not pattern.startswith('.*'):
                pattern = f".*{pattern}"
            if not pattern.endswith('.*'):
                pattern = f"{pattern}.*"
            filter_params["plugin"] = pattern
        
        # Add node filter if specified
        if validated_node:
            filter_params["vsn"] = str(validated_node)
        
        logger.info(f"Using filter parameters: {filter_params}")
        
        # Query for matching measurements
        start, end = SageDataService._parse_time_range(validated_time)
        df = data_service.query_data(start, end, filter_params)
        
        if df.empty:
            # Try name filter if plugin filter returns no results
            name_filter = filter_params.copy()
            name_filter["name"] = name_filter.pop("plugin")
            logger.info(f"Trying name filter: {name_filter}")
            df = data_service.query_data(start, end, name_filter)
            
        if df.empty:
            node_text = f" for node {validated_node}" if validated_node else ""
            return f"No measurements matching '{measurement_pattern}'{node_text} found in the last {validated_time}"
        
        # Show what was found
        result = f"Found {len(df)} records matching '{measurement_pattern}':\n"
        result += f"Time range: {validated_time}\n"
        
        # Group by plugin first
        plugins = sorted(df['plugin'].unique()) if 'plugin' in df.columns else []
        if plugins:
            result += f"\nPlugins found ({len(plugins)}):\n"
            for plugin in plugins:
                plugin_df = df[df['plugin'] == plugin]
                result += f"\n{plugin}:\n"
                
                # Get nodes for this plugin
                nodes = sorted(plugin_df['meta.vsn'].unique())
                result += f"- Nodes: {', '.join(nodes)}\n"
                
                # Get measurements for this plugin
                measurements = sorted(plugin_df['name'].unique())
                result += f"- Measurements: {', '.join(measurements)}\n"
                
                # Show recent data samples
                result += "- Recent data:\n"
                recent = plugin_df.sort_values('timestamp', ascending=False).head(3)
                for _, row in recent.iterrows():
                    timestamp = data_service._safe_timestamp_format(row['timestamp'])
                    node = row.get('meta.vsn', 'N/A')
                    name = row.get('name', 'N/A')
                    value = row.get('value', 'N/A')
                    
                    result += f"  {timestamp} | Node {node} | {name}"
                    if isinstance(value, (int, float)):
                        result += f" | Value: {value:.2f}"
                    elif value != 'N/A':
                        result += f" | Value: {value}"
                    result += "\n"
        else:
            # If no plugins found, group by measurement name
            measurements = sorted(df['name'].unique())
            result += f"\nMeasurements found ({len(measurements)}):\n"
            for measurement in measurements:
                measurement_df = df[df['name'] == measurement]
                result += f"\n{measurement}:\n"
                
                # Get nodes for this measurement
                nodes = sorted(measurement_df['meta.vsn'].unique())
                result += f"- Nodes: {', '.join(nodes)}\n"
                
                # Show recent data samples
                result += "- Recent data:\n"
                recent = measurement_df.sort_values('timestamp', ascending=False).head(3)
                for _, row in recent.iterrows():
                    timestamp = data_service._safe_timestamp_format(row['timestamp'])
                    node = row.get('meta.vsn', 'N/A')
                    value = row.get('value', 'N/A')
                    
                    result += f"  {timestamp} | Node {node}"
                    if isinstance(value, (int, float)):
                        result += f" | Value: {value:.2f}"
                    elif value != 'N/A':
                        result += f" | Value: {value}"
                    result += "\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error searching measurements: {e}")
        return f"Error searching measurements: {str(e)}"

@mcp.tool()
def mcp_sage_query_job_data(
    job_name: str,
    node_id: str = "",
    time_range: str = "-30m",
    data_type: str = "upload"
) -> str:
    """Query data generated by a running SAGE job"""
    # Use the improved query_job_data function
    return query_job_data(job_name, node_id, time_range, data_type)

@mcp.tool()
def submit_multi_plugin_job(
    job_name: str,
    nodes: str,
    plugins_config: str
) -> str:
    """Submit a job with multiple plugins running together.
    
    Args:
        job_name: Name for the job
        nodes: Comma-separated list of node IDs
        plugins_config: JSON string defining multiple plugins and their configurations
        
    Example plugins_config:
    '[
        {
            "plugin_type": "cloud_cover",
            "args": {"camera_stream": "top_camera", "interval_mins": 10}
        },
        {
            "plugin_type": "solar_irradiance", 
            "args": {"gps_server": "wes-gps-server.default.svc.cluster.local"}
        },
        {
            "plugin_type": "sound_event_detection",
            "args": {"duration_s": 5, "publish": true, "interval_mins": 10}
        }
    ]'
    
    Or use the pre-configured ML suite:
    '{"preset": "ml_suite", "cloud_cover_interval": 10, "sound_event_interval": 10, "avian_monitoring_interval": 5}'
    """
    try:
        # Initialize job service
        config = SageConfig()
        job_service = SageJobService(config)
        
        # Parse node list
        node_list = [node.strip() for node in nodes.split(',') if node.strip()]
        if not node_list:
            return "❌ No valid nodes specified"
        
        # Initialize plugin list and science rules
        plugins = []
        science_rules = []
        
        # Configure each plugin
        for plugin_type in plugin_types:
            try:
                template_method = plugin_map.get(plugin_type)
                if not template_method:
                    return f"❌ Plugin type '{plugin_type}' not supported"
                
                # Create individual plugin job to extract specs
                if plugin_type == "image_sampler":
                    temp_job = template_method(
                        job_name=f"temp_{plugin_type}",
                        nodes=["W000"],  # Dummy node
                        interval_mins=10  # Default interval
                    )
                    plugins.extend(temp_job.plugins)
                elif plugin_type == "cloud_cover":
                    temp_job = template_method(
                        job_name=f"temp_{plugin_type}",
                        nodes=["W000"],
                        camera_stream="top_camera",
                        interval_mins=cloud_cover_interval
                    )
                    plugins.extend(temp_job.plugins)
                # Add other plugin types as needed
                else:
                    return f"❌ Plugin type '{plugin_type}' not yet supported in multi-plugin jobs"
                
                # Extract plugin spec and science rules
                plugins.extend(temp_job.plugins)
                science_rules.extend(temp_job.science_rules)
                
            except Exception as e:
                return f"❌ Error configuring plugin {plugin_type}: {str(e)}"
        
        # Create the multi-plugin job
        job = SageJob(
            name=job_name,
            nodes=node_list,
            plugins=plugins,
            science_rules=science_rules
        )

        # Submit job
        success, message = job_service.submit_job(job)
        return message

    except Exception as e:
        logger.error(f"Error submitting multi-plugin job: {e}")
        return f"❌ Error submitting multi-plugin job: {str(e)}"

@mcp.tool()
def mcp_sage_recommend_plugins(task_description: str) -> str:
    """Recommend SAGE plugins/apps based on a natural language task description.
    
    Args:
        task_description: Natural language description of what you want to do
    """
    return find_plugins_for_task(task_description)


# Add these new MCP tools after the existing tools

@mcp.tool()
def ask_sage_docs(question: str) -> str:
    """Ask questions about SAGE documentation and get comprehensive answers with examples and links"""
    try:
        if not question.strip():
            return "Please provide a specific question about SAGE. " + docs_helper.list_faq_topics()
        
        return docs_helper.search_and_answer(question)
        
    except Exception as e:
        logger.error(f"Error querying documentation: {e}")
        return f"Error searching documentation: {str(e)}"


@mcp.tool()
def sage_faq(topic: str = "") -> str:
    """Get answers to frequently asked questions about SAGE. Available topics: getting_started, plugin_development, data_access, job_submission, sensors, troubleshooting, node_access"""
    try:
        if not topic:
            return docs_helper.list_faq_topics()
        
        answer = docs_helper.get_faq_answer(topic)
        if answer:
            return answer
        else:
            available_topics = ", ".join(docs_helper.faqs.keys())
            return f"Topic '{topic}' not found. Available topics: {available_topics}"
        
    except Exception as e:
        logger.error(f"Error getting FAQ: {e}")
        return f"Error getting FAQ: {str(e)}"


@mcp.tool()
def search_sage_docs(query: str, max_results: int = 5) -> str:
    """Search SAGE documentation for specific topics, commands, or concepts"""
    try:
        if not query.strip():
            return "Please provide a search query. Examples: 'pluginctl commands', 'data API', 'job submission'"
        
        results = docs_helper.search_docs(query, max_results)
        
        if not results:
            return f"No documentation found for '{query}'. Try different keywords or check the FAQ topics."
        
        response_parts = [f"Documentation search results for '{query}':\n"]
        
        for i, (section, content, score) in enumerate(results, 1):
            response_parts.append(f"**{i}. {section}** (relevance: {score})")
            response_parts.append(content)
            response_parts.append("")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        logger.error(f"Error searching documentation: {e}")
        return f"Error searching documentation: {str(e)}"


# Add new prompts for guided tutorials

@mcp.prompt()
def getting_started_guide() -> list[base.Message]:
    """Interactive guide for new SAGE users - walks through account creation, data access, and first steps"""
    return [
        base.UserMessage(
            "I'm new to SAGE and want to get started. Can you walk me through:\n"
            "1. How to create an account and get access\n"
            "2. How to explore available data and sensors\n"
            "3. How to access data using the Python client\n"
            "4. How to submit my first job\n"
            "5. How to monitor job status and results\n\n"
            "Please provide step-by-step instructions with examples."
        )
    ]


@mcp.prompt()
def plugin_development_guide() -> list[base.Message]:
    """Comprehensive guide for creating custom SAGE plugins/edge apps"""
    return [
        base.UserMessage(
            "I want to create a custom SAGE plugin (edge app). Please guide me through:\n"
            "1. Plugin architecture and requirements\n"
            "2. Setting up the development environment\n"
            "3. Using the cookiecutter template\n"
            "4. PyWaggle integration for sensors and data publishing\n"
            "5. Docker container setup and Dockerfile best practices\n"
            "6. Testing with pluginctl on development nodes\n"
            "7. Publishing to the Edge Code Repository (ECR)\n"
            "8. Job submission and scheduling\n\n"
            "Include code examples and common troubleshooting tips."
        )
    ]


@mcp.prompt()
def data_analysis_guide() -> list[base.Message]:
    """Guide for accessing, querying, and analyzing SAGE data"""
    return [
        base.UserMessage(
            "I want to work with SAGE data for analysis. Please help me understand:\n"
            "1. What types of data are available (sensors, measurements, etc.)\n"
            "2. How to use the Python sage-data-client for queries\n"
            "3. How to filter data by time, location, and sensor type\n"
            "4. How to access uploaded files (images, audio)\n"
            "5. How to work with protected data and authentication\n"
            "6. Best practices for data analysis and visualization\n"
            "7. How to set up triggers and real-time monitoring\n\n"
            "Provide practical examples with code snippets."
        )
    ]


@mcp.prompt()
def troubleshooting_guide() -> list[base.Message]:
    """Comprehensive troubleshooting guide for common SAGE issues"""
    return [
        base.UserMessage(
            "I'm having issues with SAGE and need troubleshooting help. Please provide guidance for:\n"
            "1. Plugin/edge app development issues (build failures, runtime errors)\n"
            "2. Job submission and scheduling problems\n"
            "3. Data access and query issues\n"
            "4. Node access and SSH connection problems\n"
            "5. ECR submission and publication issues\n"
            "6. Common error messages and their solutions\n"
            "7. How to get help and contact support\n\n"
            "Include diagnostic commands and debugging techniques."
        )
    ]


# Add this new class after the existing imports and before the configuration models
class SAGEDocsHelper:
    """Helper class for searching and answering questions from SAGE documentation"""
    
    def __init__(self, docs_file_path: str = "llms.md"):
        self.docs_file_path = docs_file_path
        self.docs_content = ""
        self.sections = {}
        self.faqs = {}
        self._load_documentation()
        self._setup_faqs()
    
    def _load_documentation(self):
        """Load and parse the documentation file"""
        try:
            docs_path = Path(self.docs_file_path)
            if docs_path.exists():
                with open(docs_path, 'r', encoding='utf-8') as f:
                    self.docs_content = f.read()
                self._parse_sections()
                logger.info(f"Loaded documentation from {self.docs_file_path}")
            else:
                logger.warning(f"Documentation file {self.docs_file_path} not found")
        except Exception as e:
            logger.error(f"Error loading documentation: {e}")
    
    def _parse_sections(self):
        """Parse the markdown into sections for better organization"""
        if not self.docs_content:
            return
        
        # Split by main headers (# or ##)
        sections = re.split(r'\n(#{1,2})\s+(.+)', self.docs_content)
        
        current_section = ""
        current_content = ""
        
        for i in range(0, len(sections), 3):
            if i + 2 < len(sections):
                header_level = sections[i + 1] if i + 1 < len(sections) else ""
                header_text = sections[i + 2] if i + 2 < len(sections) else ""
                content = sections[i] if i < len(sections) else ""
                
                if header_text:
                    if current_section:
                        self.sections[current_section] = current_content
                    current_section = header_text.strip()
                    current_content = content
                else:
                    current_content += content
        
        # Add the last section
        if current_section:
            self.sections[current_section] = current_content
    
    def _setup_faqs(self):
        """Setup frequently asked questions and answers"""
        self.faqs = {
            "getting_started": {
                "question": "How do I get started with SAGE?",
                "answer": """To get started with SAGE:

1. **Create an account**: Visit https://portal.sagecontinuum.org and sign in
2. **Explore existing data**: Use the Data Query Browser to see available sensor data
3. **Access sensors**: Learn about available sensors at different nodes
4. **Create edge apps**: Develop applications that run on edge nodes
5. **Submit jobs**: Schedule your applications to run on SAGE nodes

Key resources:
- Portal: https://portal.sagecontinuum.org
- Documentation: https://docs.sagecontinuum.org
- Data API: https://data.sagecontinuum.org/api/v1/query"""
            },
            
            "plugin_development": {
                "question": "How do I create a SAGE plugin/edge app?",
                "answer": """To create a SAGE plugin (edge app):

1. **Use the template**: Start with the cookiecutter template:
   ```bash
   pip3 install --upgrade cookiecutter
   cookiecutter gh:waggle-sensor/cookiecutter-sage-app
   ```

2. **Key components needed**:
   - `main.py`: Your main application code
   - `requirements.txt`: Python dependencies
   - `Dockerfile`: Container build instructions
   - `sage.yaml`: Plugin metadata

3. **Use PyWaggle**: Install and use the PyWaggle library:
   ```bash
   pip3 install pywaggle[all]
   ```

4. **Test on nodes**: Use `pluginctl` to build and test:
   ```bash
   sudo pluginctl build .
   sudo pluginctl run --name myapp <image>
   ```

5. **Publish to ECR**: Submit to Edge Code Repository at https://portal.sagecontinuum.org"""
            },
            
            "data_access": {
                "question": "How do I access SAGE data?",
                "answer": """To access SAGE data, you have several options:

1. **Python Sage Data Client** (recommended):
   ```python
   import sage_data_client
   df = sage_data_client.query(
       start="-1h",
       filter={"name": "env.temperature"}
   )
   ```

2. **HTTP API**:
   ```bash
   curl -H 'Content-Type: application/json' \\
   https://data.sagecontinuum.org/api/v1/query -d '{
       "start": "-1h",
       "filter": {"sensor": "bme680"}
   }'
   ```

3. **Portal**: Use the Data Query Browser at https://portal.sagecontinuum.org

4. **Protected data**: Some data requires authentication - contact us for access."""
            },
            
            "job_submission": {
                "question": "How do I submit jobs to SAGE nodes?",
                "answer": """To submit jobs to SAGE nodes:

1. **Get sesctl tool**: Download from https://github.com/waggle-sensor/edge-scheduler/releases

2. **Create job YAML**:
   ```yaml
   name: myjob
   plugins:
   - name: my-plugin
     pluginSpec:
       image: registry.sagecontinuum.org/user/plugin:version
   nodes:
     W023: true
   scienceRules:
   - 'schedule("my-plugin"): cronjob("my-plugin", "*/5 * * * *")'
   ```

3. **Submit with sesctl**:
   ```bash
   export SES_HOST=https://es.sagecontinuum.org
   export SES_USER_TOKEN=<your-token>
   sesctl create --file-path myjob.yaml
   sesctl submit --job-id <job-id>
   ```

4. **Monitor**: Check status with `sesctl stat --job-id <job-id>`"""
            },
            
            "sensors": {
                "question": "What sensors are available in SAGE?",
                "answer": """SAGE nodes include various sensors:

**Environmental Sensors**:
- BME680: temperature, humidity, pressure, gas
- RG-15: rainfall measurements
- GPS: location data

**Cameras**:
- XNV-8080R: 5MP camera (92.1° horizontal view)
- XNV-8082R: 6MP camera (114° horizontal view)  
- XNF-8010RV: 6MP fisheye (192° view)
- XNV-8081Z: 5MP PTZ camera

**Audio**:
- ETS ML1-WS: 20-16 kHz microphone

**Custom Sensors**:
- Software-defined Radio
- LIDAR systems
- Radiation detectors
- Mobotix infrared cameras

View all sensors: https://portal.sagecontinuum.org/sensors"""
            },
            
            "troubleshooting": {
                "question": "How do I troubleshoot issues?",
                "answer": """Common troubleshooting steps:

**Plugin Issues**:
1. Check logs: `pluginctl logs <plugin-name>`
2. Inspect pod: `sudo kubectl describe pod <pod-name>`
3. Check entrypoint in Dockerfile
4. Verify image builds: `sudo pluginctl build .`

**Job Issues**:
1. Check job status: `sesctl stat --job-id <id>`
2. Verify plugin is public in ECR
3. Check node permissions
4. Review science rules syntax

**Data Issues**:
1. Query recent data to verify publishing
2. Check measurement names and metadata
3. Verify timestamps and filters

**Access Issues**:
1. Ensure account is approved
2. Check SSH keys are uploaded
3. Verify tokens are current

Contact us at: https://docs.sagecontinuum.org/docs/contact-us"""
            },
            
            "node_access": {
                "question": "How do I access SAGE nodes?",
                "answer": """To access SAGE nodes:

1. **Get approved account**: Sign in at https://portal.sagecontinuum.org
2. **Setup SSH access**: 
   - Go to Portal → Your Account → Access Creds
   - Follow "Update SSH Public Keys" instructions
   - Complete "Finish Setup for Node Access"

3. **Connect to development nodes**:
   ```bash
   ssh waggle-dev-node-W023  # example node
   ```

4. **Test connection**:
   ```bash
   ssh waggle-dev-sshd  # should return "no command provided"
   ```

**Note**: Node access is currently limited. Contact us for development node access.

**Available tools on nodes**:
- `pluginctl`: Build and test plugins
- `kubectl`: Manage containers
- Standard development tools"""
            }
        }
    
    def search_docs(self, query: str, max_results: int = 3) -> List[Tuple[str, str, float]]:
        """Search documentation for relevant content"""
        if not self.docs_content:
            return []
        
        query_lower = query.lower()
        query_words = re.findall(r'\w+', query_lower)
        
        results = []
        
        # Search in sections
        for section_name, content in self.sections.items():
            content_lower = content.lower()
            
            # Calculate relevance score
            score = 0
            
            # Exact phrase match gets highest score
            if query_lower in content_lower:
                score += 100
            
            # Word matches
            for word in query_words:
                if word in content_lower:
                    score += 10
                if word in section_name.lower():
                    score += 20
            
            # Section name relevance
            if any(word in section_name.lower() for word in query_words):
                score += 50
            
            if score > 0:
                # Limit content length for readability
                preview = content[:500] + "..." if len(content) > 500 else content
                results.append((section_name, preview, score))
        
        # Sort by score and return top results
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:max_results]
    
    def get_faq_answer(self, topic: str) -> str:
        """Get FAQ answer for a specific topic"""
        if topic.lower() in self.faqs:
            faq = self.faqs[topic.lower()]
            return f"**{faq['question']}**\n\n{faq['answer']}"
        return ""
    
    def list_faq_topics(self) -> str:
        """List available FAQ topics"""
        topics = list(self.faqs.keys())
        return "Available FAQ topics:\n" + "\n".join(f"- {topic}" for topic in topics)
    
    def search_and_answer(self, question: str) -> str:
        """Search docs and provide a comprehensive answer"""
        # First check if it matches any FAQ topics
        question_lower = question.lower()
        
        # Check for FAQ topic keywords
        faq_matches = []
        for topic, faq in self.faqs.items():
            if any(word in question_lower for word in topic.split('_')):
                faq_matches.append(topic)
        
        response_parts = []
        
        # If we have FAQ matches, include them
        if faq_matches:
            response_parts.append("## Quick Answer (FAQ):")
            for topic in faq_matches[:2]:  # Limit to 2 FAQ matches
                response_parts.append(self.get_faq_answer(topic))
                response_parts.append("")
        
        # Search documentation for additional context
        search_results = self.search_docs(question)
        
        if search_results:
            response_parts.append("## Additional Documentation:")
            for i, (section, content, score) in enumerate(search_results, 1):
                response_parts.append(f"**{i}. {section}**")
                response_parts.append(content)
                response_parts.append("")
        
        if not response_parts:
            return f"I couldn't find specific information about '{question}' in the documentation. " + \
                   f"Try asking about: {', '.join(self.faqs.keys())} or contact us for help."
        
        return "\n".join(response_parts)

# Initialize the documentation helper
docs_helper = SAGEDocsHelper()

@mcp.tool()
def create_plugin(
    description: str,
    name: str,
    use_gpu: bool = False,
    use_camera: bool = False,
    use_env_sensors: bool = False,
    use_audio: bool = False,
    packages: str = "",  # Comma-separated list of Python packages
    system_deps: str = ""  # Comma-separated list of system dependencies
) -> str:
    """Create a new SAGE plugin from description"""
    try:
        # Create plugin template
        template = PluginTemplate(
            name=name,
            description=description,
            requirements=PluginRequirements(
                gpu=use_gpu,
                camera=use_camera,
                environmental_sensors=use_env_sensors,
                audio=use_audio,
                python_packages=packages.split(",") if packages else [],
                system_packages=system_deps.split(",") if system_deps else []
            )
        )

        # Generate plugin
        generator = PluginGenerator()
        plugin_path = generator.generate_plugin(template)

        # Return success message with deployment instructions
        return f"""✅ Plugin '{name}' created successfully at {plugin_path}

IMPORTANT DEPLOYMENT INFORMATION:
-------------------------------
1. Base Image: For ML plugins requiring GPU, use:
   FROM waggle/plugin-base:1.1.1-ml-cuda10.2-l4t

2. Deployment Steps:
   a) Package the plugin:
      tar -czf {name}.tar.gz {name}/

   b) Transfer to node:
      scp {name}.tar.gz waggle-dev-node-WXXX:~

   c) SSH into node:
      ssh waggle-dev-node-WXXX

   d) Extract and deploy:
      mkdir -p {name}
      cd {name}
      tar -xzf ../{name}.tar.gz --strip-components=1
      sudo pluginctl build .
      sudo pluginctl run .

Note: Replace WXXX with your target node ID (e.g., W0B6).
The sudo commands will work without a password on SAGE nodes."""

    except Exception as e:
        logger.error(f"Error creating plugin: {e}")
        return f"❌ Error creating plugin: {str(e)}"


if __name__ == "__main__":
    main()