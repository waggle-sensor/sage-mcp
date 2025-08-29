from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
import json
import logging
import requests
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

SAGE_PLUGINS_URL = "https://ecr.sagecontinuum.org/api/apps"
ECR_META_FILES_URL = "https://ecr.sagecontinuum.org/api/meta-files"

class PluginInput(BaseModel):
    """Model for plugin input parameters"""
    id: str
    type: str

class PluginSource(BaseModel):
    """Model for plugin source information"""
    architectures: List[str]
    branch: str
    build_args: Dict[str, Any]
    directory: str
    dockerfile: str
    git_commit: Optional[str] = None
    tag: Optional[str] = ""
    url: str

class PluginMetadata(BaseModel):
    """Complete plugin metadata model"""
    id: str
    name: str
    namespace: str
    version: str
    description: str = ""
    keywords: Optional[str] = ""
    authors: Optional[str] = None
    collaborators: Optional[str] = None
    homepage: Optional[str] = None
    license: Optional[str] = None
    inputs: List[PluginInput] = Field(default_factory=list)
    images: Optional[List[str]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: Optional[PluginSource] = None
    science_description: Optional[str] = ""
    science_description_content: str = ""  # The actual content fetched from the science description
    time_created: Optional[datetime] = None
    time_last_updated: Optional[datetime] = None

    def get_full_name(self) -> str:
        """Get the full plugin name including namespace"""
        return f"{self.namespace}/{self.name}:{self.version}"

    def get_search_text(self) -> str:
        """Get concatenated text for semantic search including science description content"""
        return " ".join(filter(None, [
            self.name,
            self.description,
            self.keywords or "",
            self.science_description_content,
            " ".join(str(v) for v in self.metadata.values() if v)
        ]))

    def get_input_schema(self) -> Dict[str, Any]:
        """Get schema of plugin inputs"""
        return {
            input_param.id: {
                "type": input_param.type,
                "description": getattr(input_param, "description", None)
            }
            for input_param in self.inputs
        }

    def matches_query(self, query: str) -> bool:
        """Check if plugin matches a search query"""
        query = query.lower()
        keywords_text = self.keywords.lower() if self.keywords else ""
        searchable_text = " ".join(filter(None, [
            self.name.lower(),
            self.description.lower(),
            keywords_text,
            self.science_description_content.lower(),
            " ".join(str(v).lower() for v in self.metadata.values() if v)
        ]))
        return query in searchable_text

class PluginRegistry:
    """Registry for managing plugin metadata and search"""

    def __init__(self):
        self.plugins: Dict[str, PluginMetadata] = {}
        self.science_description_cache: Dict[str, str] = {}  # Cache for fetched science descriptions
        self.refresh_cache()

    def _fetch_science_description(self, science_description_path: str) -> str:
        """Fetch science description content from ECR"""
        if not science_description_path:
            return ""

        # Check cache first
        if science_description_path in self.science_description_cache:
            return self.science_description_cache[science_description_path]

        try:
            url = f"{ECR_META_FILES_URL}/{science_description_path}"
            logger.info(f"Fetching science description from: {url}")

            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text
                # Cache the content
                self.science_description_cache[science_description_path] = content
                logger.info(f"Successfully fetched science description for {science_description_path}")
                return content
            else:
                logger.warning(f"Failed to fetch science description from {url}: {response.status_code}")
                return ""
        except Exception as e:
            logger.warning(f"Error fetching science description from {science_description_path}: {e}")
            return ""

    def refresh_cache(self) -> None:
        """Refresh the plugin metadata cache from the Sage API"""
        try:
            logger.info(f"Fetching plugins from {SAGE_PLUGINS_URL}")
            response = requests.get(SAGE_PLUGINS_URL, timeout=30)
            if response.status_code == 200:
                plugins_data = response.json().get("data", [])
                logger.info(f"Found {len(plugins_data)} plugins in ECR")

                for plugin_data in plugins_data:
                    try:
                        # Parse basic plugin metadata with proper None handling
                        plugin = PluginMetadata(
                            id=plugin_data.get("id", ""),
                            name=plugin_data.get("name", ""),
                            namespace=plugin_data.get("namespace", ""),
                            version=plugin_data.get("version", "0.0.0"),
                            description=plugin_data.get("description") or "",
                            keywords=plugin_data.get("keywords") or "",
                            authors=plugin_data.get("authors"),
                            collaborators=plugin_data.get("collaborators"),
                            homepage=plugin_data.get("homepage"),
                            license=plugin_data.get("license"),
                            inputs=[PluginInput(**inp) for inp in plugin_data.get("inputs", [])],
                            images=plugin_data.get("images") or [],
                            metadata=plugin_data.get("metadata", {}),
                            science_description=plugin_data.get("science_description") or "",
                            time_created=self._parse_datetime(plugin_data.get("time_created")),
                            time_last_updated=self._parse_datetime(plugin_data.get("time_last_updated"))
                        )

                        # Parse source information if available
                        if "source" in plugin_data and plugin_data["source"]:
                            source_data = plugin_data["source"]
                            plugin.source = PluginSource(
                                architectures=source_data.get("architectures", []),
                                branch=source_data.get("branch") or "",
                                build_args=source_data.get("build_args", {}),
                                directory=source_data.get("directory") or "",
                                dockerfile=source_data.get("dockerfile") or "",
                                git_commit=source_data.get("git_commit"),
                                tag=source_data.get("tag") or "",
                                url=source_data.get("url") or ""
                            )

                        # Fetch science description content if available
                        if plugin.science_description:
                            plugin.science_description_content = self._fetch_science_description(
                                plugin.science_description
                            )

                        if plugin.id:  # Only add if we have a valid ID
                            self.plugins[plugin.id] = plugin
                            logger.debug(f"Cached plugin: {plugin.id}")

                    except Exception as e:
                        logger.warning(f"Error parsing plugin data: {e}")
                        continue

                logger.info(f"Successfully cached {len(self.plugins)} plugins with science descriptions")
            else:
                logger.error(f"Failed to fetch plugins: {response.status_code}")
        except Exception as e:
            logger.error(f"Error refreshing plugin cache: {e}")

    def _parse_datetime(self, dt_string: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from ECR API"""
        if not dt_string:
            return None
        try:
            return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        except Exception:
            return None

    def search_plugins(self, query: str, max_results: int = 10) -> List[PluginMetadata]:
        """Search for plugins matching a query with improved scoring"""
        query_lower = query.lower()
        query_words = query_lower.split()

        scored_plugins = []

        for plugin in self.plugins.values():
            score = 0
            search_text = plugin.get_search_text().lower()

            # Exact name match gets highest score
            if query_lower == plugin.name.lower():
                score += 100

            # Partial name match
            if query_lower in plugin.name.lower():
                score += 50

            # Description match
            if query_lower in plugin.description.lower():
                score += 30

            # Keywords match
            if plugin.keywords and query_lower in plugin.keywords.lower():
                score += 40

            # Science description content match
            if plugin.science_description_content and query_lower in plugin.science_description_content.lower():
                score += 25

            # Word-by-word matching
            for word in query_words:
                if word in search_text:
                    score += 10

            # Category-based scoring
            category_keywords = {
                "camera": ["camera", "image", "video", "ptz", "pan", "tilt", "zoom"],
                "audio": ["audio", "sound", "microphone", "bird", "noise"],
                "detection": ["detect", "yolo", "object", "recognition", "ai", "ml"],
                "environmental": ["temperature", "humidity", "pressure", "weather"],
                "movement": ["motion", "tracking", "movement"]
            }

            for category, keywords in category_keywords.items():
                if any(kw in query_lower for kw in keywords):
                    if any(kw in search_text for kw in keywords):
                        score += 20

            if score > 0:
                scored_plugins.append((plugin, score))

        # Sort by score (descending) and return top results
        scored_plugins.sort(key=lambda x: x[1], reverse=True)
        return [plugin for plugin, score in scored_plugins[:max_results]]

    def get_plugin_by_id(self, plugin_id: str) -> Optional[PluginMetadata]:
        """Get plugin metadata by ID"""
        return self.plugins.get(plugin_id)

    def get_plugins_by_type(self, plugin_type: str) -> List[PluginMetadata]:
        """Get plugins of a specific type/category"""
        return [p for p in self.plugins.values()
                if plugin_type.lower() in p.keywords.lower() if p.keywords]

    def get_data_query_info(self, plugin_id: str) -> Dict[str, Any]:
        """Get information about how to query data from a plugin"""
        plugin = self.get_plugin_by_id(plugin_id)
        if not plugin:
            return {}

        # Extract query parameters from metadata
        query_info = {
            "plugin_name": plugin.name,
            "plugin_id": plugin.id,
            "data_type": plugin.metadata.get("data_type", "upload"),
            "measurement_name": plugin.metadata.get("measurement", f"plugin.{plugin.name}.data"),
            "input_schema": plugin.get_input_schema(),
            "description": plugin.description,
            "science_description": plugin.science_description_content
        }
        return query_info

# Initialize global registry
plugin_registry = PluginRegistry()