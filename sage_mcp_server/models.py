from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import Any, Dict, List, Optional, Union

class SageConfig(BaseModel):
    """Configuration settings for SAGE interactions"""
    token: str = Field(default="4d9473cb2a21cb7716e97e5fdafdbcbf4faea051", 
                       description="SAGE API token for authentication")
    server: str = Field(default="https://es.sagecontinuum.org", 
                       description="SAGE server URL")
    dry_run: bool = Field(default=False, 
                         description="If True, validate but don't submit jobs")

    class Config:
        validate_assignment = True

class TimeRange(BaseModel):
    """Model for time range specifications"""
    value: str
    
    @validator('value')
    def validate_time_range(cls, v: str) -> str:
        if not v or v.strip() == "" or v.lower() in ['latest', 'recent', 'current', 'now']:
            return "-30m"
        return v
    def __str__(self) -> str:
        return self.value

class NodeID(BaseModel):
    """Model for SAGE node identifiers"""
    value: str
    
    @validator('value')
    def normalize_node_id(cls, v: str) -> str:
        if not v:
            return ""
        clean_id = v.upper().strip()
        if clean_id and not clean_id.startswith('W'):
            clean_id = f"W{clean_id}"
        return clean_id
    def __str__(self) -> str:
        return self.value

class DataType(str, Enum):
    """Types of data that can be queried from SAGE"""
    UPLOAD = "upload"
    TEMPERATURE = "env.temperature"
    HUMIDITY = "env.relative_humidity"
    PRESSURE = "env.pressure"
    IIO_TEMP = "iio.in_temp_input"
    IIO_HUMIDITY = "iio.in_humidityrelative_input"
    IIO_PRESSURE = "iio.in_pressure_input"
    IIO_RESISTANCE = "iio.in_resistance_input"
    
    @classmethod
    def environmental_types(cls) -> List[str]:
        return [cls.TEMPERATURE.value, cls.HUMIDITY.value, cls.PRESSURE.value]
    
    @classmethod
    def iio_types(cls) -> List[str]:
        return [
            cls.IIO_TEMP.value, cls.IIO_HUMIDITY.value,
            cls.IIO_PRESSURE.value, cls.IIO_RESISTANCE.value
        ]

class SelectorRequirements(BaseModel):
    """Model for job selector requirements"""
    gpu: Optional[bool] = Field(None, description="Require GPU")
    camera: Optional[bool] = Field(None, description="Require camera")
    usb: Optional[bool] = Field(None, description="Require USB")
    custom_selectors: Dict[str, str] = Field(default_factory=dict, description="Custom selector requirements")
    
    def to_dict(self) -> Dict[str, str]:
        result = {}
        if self.gpu:
            result["resource.gpu"] = "true"
        if self.camera:
            result["resource.camera"] = "true"
        if self.usb:
            result["resource.usb"] = "true"
        result.update(self.custom_selectors)
        return result
    
    @classmethod
    def from_json_str(cls, json_str: str) -> 'SelectorRequirements':
        if not json_str:
            return cls(gpu=None, camera=None, usb=None)
        try:
            import json
            data = json.loads(json_str)
            gpu = str(data.get("resource.gpu", "")).lower() == "true"
            camera = str(data.get("resource.camera", "")).lower() == "true"
            usb = str(data.get("resource.usb", "")).lower() == "true"
            return cls(gpu=gpu, camera=camera, usb=usb)
        except Exception:
            return cls(gpu=None, camera=None, usb=None)

class PluginArguments(BaseModel):
    """Model for plugin arguments"""
    args_dict: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def from_string(cls, args_str: str) -> 'PluginArguments':
        if not args_str:
            return cls()
        args_dict = {}
        try:
            import json
            args_dict = json.loads(args_str)
        except Exception:
            for arg in args_str.split(","):
                if "=" in arg:
                    key, value = arg.split("=", 1)
                    args_dict[key.strip()] = value.strip()
        return cls(args_dict=args_dict)
    
    def to_cli_args(self) -> List[str]:
        args_list = []
        for key, value in self.args_dict.items():
            args_list.extend([f"--{key}", str(value)])
        return args_list

class PluginSpec(BaseModel):
    """Model for plugin specifications"""
    name: str
    image: str
    args: PluginArguments = Field(default_factory=PluginArguments)
    selector: SelectorRequirements = Field(default_factory=lambda: SelectorRequirements(gpu=None, camera=None, usb=None))
    privileged: bool = Field(default=False, description="Run in privileged mode")
    entrypoint: Optional[str] = Field(default=None, description="Custom entrypoint")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    
    def to_dict(self) -> Dict[str, Any]:
        plugin_spec = {
                "image": self.image,
                "volume": {}
            }
        if self.args.args_dict:
            args_list = []
            for key, value in self.args.args_dict.items():
                args_list.extend([f"--{key}", str(value)])
            plugin_spec["args"] = args_list
        selector_dict = self.selector.to_dict()
        if selector_dict:
            plugin_spec["selector"] = selector_dict
        if self.env:
            plugin_spec["env"] = self.env
        if self.privileged:
            plugin_spec["privileged"] = True
        if self.entrypoint:
            plugin_spec["entrypoint"] = self.entrypoint
        return {
            "name": self.name,
            "pluginSpec": plugin_spec
        }

class SageJob(BaseModel):
    """Model for SAGE job definitions"""
    name: str
    nodes: List[str]
    plugins: List[PluginSpec]
    science_rules: List[str] = Field(default_factory=list)
    node_value_format: str = "null"
    success_criteria: List[str] = Field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        if self.node_value_format == "true":
            nodes_dict = {node: True for node in self.nodes}
        else:
            nodes_dict = {node: None for node in self.nodes}
        return {
            "name": self.name,
            "nodes": nodes_dict,
            "plugins": [plugin.to_dict() for plugin in self.plugins],
            "science_rules": self.science_rules,
            "success_criteria": self.success_criteria
        }
    def to_yaml(self) -> str:
        import yaml
        return yaml.dump(self.to_dict(), default_flow_style=False)
    def write_yaml(self, file_path: str) -> None:
        import yaml
        with open(file_path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)

class CameraSageJob(SageJob):
    camera_cmd: str = ""
    camera_plugin_name: str = ""
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        if self.camera_cmd:
            for plugin in base_dict["plugins"]:
                if plugin["name"] == self.camera_plugin_name:
                    plugin["args"].append("-c")
                    plugin["args"].append(self.camera_cmd)
        return base_dict
    def generate_yaml(self) -> str:
        import yaml
        return yaml.dump(self.to_dict(), default_flow_style=False)
    def save_yaml(self, file_path: str) -> None:
        import yaml
        with open(file_path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False) 