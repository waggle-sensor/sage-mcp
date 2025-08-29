#!/usr/bin/env python3

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class PluginRequirements(BaseModel):
    """Model for plugin hardware and software requirements"""
    gpu: bool = False
    camera: bool = False
    environmental_sensors: bool = False
    audio: bool = False
    python_packages: List[str] = Field(default_factory=list)
    system_packages: List[str] = Field(default_factory=list)
    custom_hardware: List[str] = Field(default_factory=list)

class PluginTemplate(BaseModel):
    """Model for plugin template configuration"""
    name: str
    description: str
    keywords: List[str] = Field(default_factory=list)
    version: str = "1.0.0"
    authors: List[str] = Field(default_factory=lambda: ["Sage Team"])
    license: str = "MIT"
    requirements: PluginRequirements
    inputs: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    outputs: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    science_description: str = ""

class PluginGenerator:
    """Generator for Sage plugins"""

    def __init__(self):
        self.base_dir = Path.cwd()

    def generate_plugin(self, template: PluginTemplate) -> Path:
        """Generate a complete plugin from template"""
        # Create plugin directory
        plugin_dir = self.base_dir / template.name.lower().replace(" ", "-")
        plugin_dir.mkdir(exist_ok=True)

        # Create required directories
        (plugin_dir / "utils").mkdir(exist_ok=True)
        (plugin_dir / "models").mkdir(exist_ok=True)
        (plugin_dir / "ecr-meta").mkdir(exist_ok=True)

        # Generate all plugin files
        self._write_file(plugin_dir / "requirements.txt", self.generate_requirements(template))
        self._write_file(plugin_dir / "Dockerfile", self.generate_dockerfile(template))
        self._write_file(plugin_dir / "sage.yaml", self.generate_sage_yaml(template))
        self._write_file(plugin_dir / "README.md", self.generate_readme(template))
        self._write_file(plugin_dir / "ecr-meta/ecr-science-description.md", self.generate_science_description(template))
        self._write_file(plugin_dir / "main.py", self.generate_main_code(template))
        self._write_file(plugin_dir / "utils/__init__.py", "")

        # Make main.py executable
        (plugin_dir / "main.py").chmod(0o755)

        return plugin_dir

    def _write_file(self, path: Path, content: str) -> None:
        """Write content to file, creating parent directories if needed"""
        path.parent.mkdir(exist_ok=True)
        path.write_text(content)

    def generate_requirements(self, template: PluginTemplate) -> str:
        """Generate requirements.txt content"""
        reqs = ["pywaggle[all]>=0.55.0"]

        # Add core dependencies based on requirements
        if template.requirements.camera:
            reqs.extend([
                "opencv-python>=4.8.0",
                "numpy>=1.24.0"
            ])

        if template.requirements.gpu:
            reqs.extend([
                "torch>=2.0.0",
                "torchvision>=0.15.0"
            ])

        if template.requirements.audio:
            reqs.extend([
                "librosa>=0.10.0",
                "sounddevice>=0.4.6"
            ])

        # Add custom packages
        reqs.extend(template.requirements.python_packages)

        return "\n".join(sorted(set(reqs)))

    def generate_dockerfile(self, template: PluginTemplate) -> str:
        """Generate Dockerfile content"""
        gpu_base = "waggle/plugin-base:1.1.1-cuda" if template.requirements.gpu else "waggle/plugin-base:1.1.1-ml"

        dockerfile = [
            f"FROM {gpu_base}",
            "",
            "# Install system dependencies",
            "RUN apt-get update && apt-get install -y \\"
        ]

        # Add required system packages
        sys_packages = template.requirements.system_packages
        if template.requirements.camera:
            sys_packages.extend(["libgl1-mesa-glx", "libglib2.0-0"])
        if template.requirements.audio:
            sys_packages.extend(["libsndfile1", "portaudio19-dev"])

        if sys_packages:
            dockerfile.extend([f"    {pkg} \\" for pkg in sys_packages])
            dockerfile.append("    && rm -rf /var/lib/apt/lists/*")

        dockerfile.extend([
            "",
            "# Set working directory",
            "WORKDIR /app",
            "",
            "# Create data directory",
            "RUN mkdir -p /data/images",
            "",
            "# Copy requirements and install Python dependencies",
            "COPY requirements.txt .",
            "RUN pip3 install --no-cache-dir -r requirements.txt",
            "",
            "# Copy application code",
            "COPY main.py .",
            "COPY utils/ ./utils/",
            "",
            "# Create models directory",
            "RUN mkdir -p models",
            "",
            "# Set entrypoint",
            'ENTRYPOINT ["python3", "main.py"]'
        ])

        return "\n".join(dockerfile)

    def generate_sage_yaml(self, template: PluginTemplate) -> str:
        """Generate sage.yaml configuration"""
        config = {
            "name": template.name.lower().replace(" ", "-"),
            "version": template.version,
            "description": template.description,
            "keywords": ",".join(template.keywords),
            "authors": ",".join(template.authors),
            "license": template.license,
            "homepage": "https://github.com/waggle-sensor/sage-apps",
            "inputs": template.inputs,
            "outputs": template.outputs,
            "source": {
                "architectures": ["linux/arm64", "linux/amd64"],
                "url": "https://github.com/waggle-sensor/sage-apps.git"
            },
            "resources": {
                "gpu": template.requirements.gpu,
                "cpu": 1,
                "memory": "2Gi",
                "storage": "5Gi"
            },
            "data": {
                "directory": "/data"
            }
        }
        return yaml.dump(config, sort_keys=False)

    def generate_main_code(self, template: PluginTemplate) -> str:
        """Generate main.py with plugin logic"""
        imports = [
            "#!/usr/bin/env python3",
            "",
            "import argparse",
            "import logging",
            "import time",
            "from pathlib import Path",
            "",
            "# PyWaggle imports",
            "import waggle.plugin as plugin",
        ]

        # Add conditional imports based on requirements
        if template.requirements.camera:
            imports.extend([
                "import cv2",
                "import numpy as np",
                "from waggle.data.vision import Camera"
            ])

        if template.requirements.environmental_sensors:
            imports.append("from waggle.data.sensors import get_sensor_data")

        if template.requirements.audio:
            imports.extend([
                "import sounddevice as sd",
                "import librosa"
            ])

        if template.requirements.gpu:
            imports.extend([
                "import torch",
                "import torchvision"
            ])

        # Add logging configuration
        logging_setup = [
            "",
            "# Configure logging",
            "logging.basicConfig(",
            "    level=logging.INFO,",
            "    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'",
            ")",
            "logger = logging.getLogger(__name__)",
            ""
        ]

        # Generate argument parser
        args_parser = [
            "def main():",
            f"    parser = argparse.ArgumentParser(description='{template.description}')"
        ]

        # Add input arguments
        for name, details in template.inputs.items():
            arg_type = details.get("type", "str")
            default = details.get("default", None)
            description = details.get("description", "")
            args_parser.append(f"    parser.add_argument('--{name}',")
            args_parser.append(f"                      type={arg_type},")
            if default:
                args_parser.append(f"                      default={default},")
            args_parser.append(f"                      help='{description}')")

        # Add main loop
        main_loop = [
            "",
            "    args = parser.parse_args()",
            "",
            "    # Initialize plugin",
            "    plugin.init()",
            ""
        ]

        # Add resource initialization based on requirements
        init_code = []
        if template.requirements.camera:
            init_code.extend([
                "    # Initialize camera",
                "    camera = Camera()",
                ""
            ])

        # Add main processing loop
        processing_loop = [
            "    try:",
            "        while True:",
            "            # Your plugin logic here",
            "",
            "            # Example publishing",
            "            for name, details in outputs.items():",
            "                plugin.publish(name, value)",
            "",
            "            # Sleep for interval",
            "            time.sleep(args.interval if hasattr(args, 'interval') else 30)",
            "",
            "    except KeyboardInterrupt:",
            "        logger.info('Stopping plugin...')",
            "    except Exception as e:",
            "        logger.error(f'Error in main loop: {e}')",
            "        raise",
            "",
            "if __name__ == '__main__':",
            "    main()"
        ]

        # Combine all sections
        return "\n".join(imports + logging_setup + args_parser + main_loop + init_code + processing_loop)

    def generate_readme(self, template: PluginTemplate) -> str:
        """Generate README.md content"""
        hw_reqs = []
        if template.requirements.gpu:
            hw_reqs.append("- GPU (for accelerated processing)")
        if template.requirements.camera:
            hw_reqs.append("- Camera")
        if template.requirements.environmental_sensors:
            hw_reqs.append("- Environmental sensors")
        if template.requirements.audio:
            hw_reqs.append("- Audio input")
        hw_reqs.extend([f"- {hw}" for hw in template.requirements.custom_hardware])

        sw_reqs = [f"- {pkg}" for pkg in template.requirements.python_packages]

        inputs_doc = []
        for name, details in template.inputs.items():
            inputs_doc.extend([
                f"### {name}",
                details.get('description', ''),
                f"Default: `{details.get('default', 'None')}`",
                ""
            ])

        outputs_doc = []
        for name, details in template.outputs.items():
            outputs_doc.extend([
                f"### {name}",
                details.get('description', ''),
                ""
            ])

        readme = f"""# {template.name}

{template.description}

## Overview

{template.science_description}

## Features

{chr(10).join([f"- {name}: {details.get('description', '')}" for name, details in template.outputs.items()])}

## Requirements

### Hardware
{chr(10).join(hw_reqs)}

### Software
{chr(10).join(sw_reqs)}

## Installation

1. Clone the repository:
```bash
git clone https://github.com/waggle-sensor/sage-apps.git
cd {template.name.lower().replace(" ", "-")}
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Build the plugin:
```bash
pluginctl build .
```

2. Run locally:
```bash
pluginctl run .
```

3. Deploy to Sage nodes:
```bash
pluginctl deploy .
```

## Configuration

{chr(10).join(inputs_doc)}

## Output Measurements

{chr(10).join(outputs_doc)}

## Data Storage

Data is stored in `/data/` with appropriate subdirectories based on the data type.

## License

{template.license}"""

        return readme

    def generate_science_description(self, template: PluginTemplate) -> str:
        """Generate science description markdown"""
        hw_reqs = []
        if template.requirements.gpu:
            hw_reqs.append("- GPU required for accelerated processing")
        if template.requirements.camera:
            hw_reqs.append("- Camera access required for image capture")
        if template.requirements.environmental_sensors:
            hw_reqs.append("- Environmental sensors required for context data")
        if template.requirements.audio:
            hw_reqs.append("- Audio input required")
        hw_reqs.extend([f"- {hw}" for hw in template.requirements.custom_hardware])

        measurements = [f"- {name}: {details['description']}"
                       for name, details in template.outputs.items()]

        config = [f"- {name}: {details['description']}"
                 for name, details in template.inputs.items()]

        return f"""# {template.name}

## Overview

{template.description}

## Scientific Applications

{template.science_description}

## Technical Details

### Hardware Requirements
{chr(10).join(hw_reqs)}

### Measurements
{chr(10).join(measurements)}

### Configuration
{chr(10).join(config)}

### Data Storage

The plugin stores data in appropriate subdirectories under `/data/` based on the data type.

### Performance Considerations

- Optimized for edge deployment
- Automatic data publishing to Sage data pipeline
- Resource usage monitored and managed
"""