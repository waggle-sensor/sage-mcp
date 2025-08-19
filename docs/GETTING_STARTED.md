# Getting Started with SAGE MCP

A comprehensive guide to using the SAGE Model Context Protocol (MCP) server for interacting with the SAGE edge computing ecosystem through LLMs and IDEs like Cursor.

## 🌟 What is SAGE MCP?

The SAGE MCP is a powerful interface that connects Large Language Models (LLMs) and AI-powered IDEs to the SAGE ecosystem. It provides:

- **Real-time sensor data access** from 100+ edge nodes worldwide
- **Intelligent plugin discovery** and recommendation
- **Automated job submission** and monitoring
- **Natural language queries** for complex data analysis
- **Comprehensive documentation** and troubleshooting support

## 📁 Repository Structure

```
sage-mcp/
├── sage_mcp.py              # Main MCP server entry point
├── sage_mcp_server/         # Core server package
│   ├── models.py           # Data models and type definitions
│   ├── data_service.py     # Data access and query service
│   ├── job_service.py      # Job submission and management
│   ├── plugin_*.py         # Plugin system components
│   └── docs_helper.py      # Documentation system
├── bundling/               # Executable building tools
│   ├── build.sh           # Build script for executables
│   ├── build_executable.py # PyInstaller build script
│   └── *.spec, *.py       # PyInstaller configuration
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container deployment
└── docker-compose.yml     # Docker orchestration
```

## 🚀 Quick Setup

### Prerequisites

- Python 3.8+ installed
- Access to an LLM interface (Claude, ChatGPT, etc.) or AI IDE (Cursor)
- Internet connection for SAGE data access

### Installation Options

#### Option 1: Python Development Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd sage-mcp
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Start the MCP server**:
```bash
python sage_mcp.py
```

#### Option 2: Docker Deployment

```bash
# Using docker-compose (recommended)
docker-compose up -d

# Or build and run manually
docker build -t sage-mcp .
docker run -p 8000:8000 sage-mcp
```

#### Option 3: Standalone Executable

```bash
# Build the executable
./bundling/build.sh

# Run the standalone executable
./bundling/dist/sage_mcp
```

The server will start on `http://localhost:8000/mcp` and display available tools and resources.

## 🎯 Core Capabilities

### 1. Sensor Data Exploration

**Discover what's available**:
```
"Show me all available SAGE nodes and their sensors"
"What environmental data is available from the last hour?"
"List nodes in Chicago with temperature sensors"
```

**Query specific data**:
```
"Get temperature readings from node W023 in the last 30 minutes"
"Show me rainfall data from all nodes in Illinois today"
"What's the current air quality in nature preserves?"
```

### 2. Plugin Discovery & Development

**Find existing plugins**:
```
"Find plugins for monitoring bird sounds"
"What computer vision plugins are available for plant detection?"
"Show me plugins that work with PTZ cameras"
```

**Get development guidance**:
```
"How do I create a custom SAGE plugin for detecting flowers?"
"What's the best approach for real-time audio analysis on edge nodes?"
"Help me optimize a YOLO model for edge deployment"
```

### 3. Job Submission & Management

**Submit jobs easily**:
```
"Deploy a cloud cover detection job to nodes W019 and W020"
"Run audio sampling on all nodes in Hawaii for the next week"
"Start a multi-plugin ML suite on prairie research nodes"
```

**Monitor and manage**:
```
"Check the status of job 12345"
"Show me recent data from my flowering plant detection job"
"Remove job 67890 from the scheduler"
```

## 💡 Best Practices for Different Use Cases

### 🔬 Research & Data Analysis

**Exploratory Data Analysis**:
```
"I'm studying pollinator activity. What SAGE data would be most relevant?"
"Show me temperature trends across different ecosystems in the past month"
"Find correlations between flowering patterns and weather data"
```

**Hypothesis Testing**:
```
"Compare bird activity between urban and rural nodes during migration season"
"Analyze the relationship between air quality and plant health indicators"
"Test if rainfall patterns affect flowering timing in prairie ecosystems"
```

**Publication-Ready Analysis**:
```
"Generate a statistical summary of biodiversity metrics from our flower detection data"
"Create a comprehensive environmental report for node W06D over the past year"
"Export data in a format suitable for scientific publication"
```

### 🛠️ Plugin Development

**Planning Phase**:
```
"I want to detect invasive plant species. What's the best technical approach?"
"What hardware requirements do I need for real-time AI inference?"
"Which SAGE nodes would be best for testing a new ecological monitoring plugin?"
```

**Development Support**:
```
"Help me create a YOLO training dataset for plant species classification"
"What's the proper way to integrate environmental sensors with computer vision?"
"Debug this PyWaggle code for publishing sensor measurements"
```

**Deployment Guidance**:
```
"How do I submit my plugin to the Edge Code Repository?"
"Create a job configuration for deploying my plugin to nature preserve nodes"
"What are the best practices for error handling in edge applications?"
```

### 📊 Operational Monitoring

**System Health**:
```
"Check the status of all active jobs across the SAGE network"
"Show me nodes that haven't reported data in the last hour"
"What plugins are currently running on node W083?"
```

**Performance Optimization**:
```
"Which nodes have the best GPU performance for computer vision tasks?"
"Recommend optimal sampling intervals for battery-powered sensors"
"How can I reduce bandwidth usage for my image processing plugin?"
```

## 🔧 Deployment Options

### Development Mode
For development and testing, run the server directly with Python:
```bash
python sage_mcp.py
```
This allows for easy debugging and code modifications.

### Docker Deployment
For production deployments, use Docker:
```bash
# Start with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f sage-mcp

# Stop the service
docker-compose down
```

### Standalone Executable
For environments without Python or Docker, create a standalone executable:
```bash
# Build the executable (from project root)
./bundling/build.sh

# The executable will be created at bundling/dist/sage_mcp
# Copy and run on target machines without Python installed
./bundling/dist/sage_mcp
```

**Executable Benefits:**
- No Python installation required on target machines
- Self-contained with all dependencies included
- Smaller deployment footprint than Docker
- Easy distribution and deployment

**Configuration:**
All deployment methods support environment variables:
- `MCP_HOST` - Server bind address (default: 0.0.0.0)
- `MCP_PORT` - Server port (default: 8000)

Example:
```bash
MCP_HOST=127.0.0.1 MCP_PORT=8080 python sage_mcp.py
```

## 🔧 Advanced Usage Patterns

### Multi-Modal Data Integration

Combine different data types for comprehensive analysis:

```
"Correlate audio recordings of bird calls with flowering plant counts"
"Analyze how weather patterns affect both air quality and biodiversity"
"Create a timeline showing relationships between camera data and environmental sensors"
```

### Automated Workflows

Set up intelligent monitoring and alerting:

```
"Create a job that automatically detects unusual flowering patterns and alerts researchers"
"Set up monitoring for rare bird species vocalizations across multiple nodes"
"Build a system that correlates extreme weather events with ecosystem responses"
```

### Cross-Ecosystem Comparisons

Compare data across different environments:

```
"Compare biodiversity metrics between prairie, forest, and wetland nodes"
"Analyze how the same plant species behaves in different climate zones"
"Study pollinator activity patterns across urban vs. rural environments"
```

## 🎨 Using with Different Tools

### Cursor IDE Integration

1. **Install MCP extension** in Cursor
2. **Configure MCP server** endpoint: `http://localhost:8000/mcp`
3. **Use in chat interface**:
   - Ask questions about SAGE data directly in your IDE
   - Get code suggestions for plugin development
   - Debug issues with real-time assistance

**Example Cursor workflow**:
```
User: "I'm writing a plugin to detect flowering plants. Help me optimize the YOLO model."

MCP: [Provides specific code suggestions, training parameters, and deployment recommendations]

User: "Now help me create the job configuration to deploy this to prairie nodes."

MCP: [Generates complete YAML configuration and submission commands]
```

### Claude/ChatGPT Integration

**Through API or web interface**:
1. Mention you're working with SAGE ecosystem
2. Ask specific questions about data, plugins, or deployment
3. Request code examples, configurations, or analysis

**Example conversation flow**:
```
User: "I'm a researcher studying climate change impacts on flowering plants. How can SAGE help?"

MCP: "SAGE offers excellent opportunities for your research! Here's what's available:

🌸 Relevant Data Sources:
- High-resolution camera data from nature preserves (W06D, W020, W083)
- Environmental sensors (temperature, humidity, precipitation)
- Existing flowering plant detection plugins

🔧 Recommended Approach:
1. Deploy computer vision plugins to monitor flowering patterns
2. Correlate with weather data for climate impact analysis
3. Set up long-term monitoring across different ecosystems

📍 Best Nodes for Your Research:
- W06D (Paintbrush Prairie, IL): Prairie flowering species
- W020 (Emiquon Nature Preserve, IL): Wetland plants
- W083 (Konza Prairie, KS): Grassland ecosystem

Would you like me to help you set up a flowering plant detection job?"
```

### Jupyter Notebook Integration

**For data analysis workflows**:
```python
# Connect to SAGE MCP from Jupyter
import requests
import pandas as pd

# Query through MCP
response = requests.post('http://localhost:8000/mcp', 
                        json={"query": "Get temperature data from W023 last 24 hours"})
data = response.json()

# Continue with your analysis
df = pd.DataFrame(data)
df.plot()
```

## 📚 Common Workflows & Examples

### Workflow 1: Ecological Research Setup

**Goal**: Study bird migration patterns and habitat preferences

**Step 1 - Explore Available Data**:
```
"What audio monitoring capabilities does SAGE have?"
"Show me nodes along known bird migration routes"
"List plugins for bird sound detection and classification"
```

**Step 2 - Deploy Monitoring**:
```
"Deploy avian diversity monitoring to nodes W019, W020, and W023"
"Set up audio sampling every 15 minutes during migration season"
"Configure bird call detection with high sensitivity settings"
```

**Step 3 - Analyze Results**:
```
"Show me bird activity patterns from the last week"
"Correlate bird detections with weather conditions"
"Compare species diversity between different habitat types"
```

### Workflow 2: Climate Change Research

**Goal**: Monitor ecosystem responses to temperature changes

**Step 1 - Baseline Data Collection**:
```
"Get historical temperature data from all prairie nodes for the past year"
"Show me flowering timing data from nature preserve nodes"
"What vegetation monitoring plugins are available?"
```

**Step 2 - Set Up Monitoring**:
```
"Deploy flowering plant detection to all prairie and forest nodes"
"Configure environmental sensors for high-frequency sampling"
"Set up automated alerts for temperature anomalies"
```

**Step 3 - Analysis & Correlation**:
```
"Analyze correlation between temperature trends and flowering timing"
"Compare ecosystem responses across different climate zones"
"Generate publication-ready statistical summaries"
```

### Workflow 3: Plugin Development

**Goal**: Create a custom plugin for invasive species detection

**Step 1 - Planning & Research**:
```
"What's the best approach for real-time plant species classification?"
"Show me examples of successful computer vision plugins"
"Which nodes have the best hardware for AI inference?"
```

**Step 2 - Development Support**:
```
"Help me create a YOLO training dataset for invasive plants"
"Generate a plugin template for plant species detection"
"What are the PyWaggle best practices for sensor integration?"
```

**Step 3 - Testing & Deployment**:
```
"Create a test job configuration for my invasive species plugin"
"Help me debug this plugin deployment issue"
"Generate documentation for submitting to the Edge Code Repository"
```

## ⚡ Pro Tips for Maximum Efficiency

### 1. Be Specific with Queries
```
❌ "Show me data"
✅ "Show me temperature readings from prairie nodes in Illinois over the last 48 hours"

❌ "Deploy a plugin"
✅ "Deploy the cloud cover detection plugin to nodes W019 and W020 with 10-minute intervals"
```

### 2. Use Natural Language for Complex Requests
```
"I need to compare flowering patterns between wet and dry years. Help me identify relevant nodes, time periods, and set up the analysis workflow."
```

### 3. Leverage Context Awareness
```
"Based on my previous query about bird migration, now help me correlate that data with flowering plant availability during the same time periods."
```

### 4. Ask for Complete Solutions
```
"I want to study pollinator-plant interactions. Give me a complete research plan including data sources, plugin deployments, analysis methods, and expected outputs."
```

### 5. Request Code and Configurations
```
"Generate the complete YAML job configuration and Python analysis code for studying urban heat island effects using SAGE data."
```

## 🛠️ Troubleshooting & Common Issues

### Connection Issues

**Problem**: MCP server not responding
**Solutions**:
```
"Help me troubleshoot MCP server connection issues"
"Check if the SAGE API endpoints are accessible"
"Verify my authentication tokens and permissions"
```

### Data Access Issues

**Problem**: No data returned from queries
**Solutions**:
```
"Why am I not getting data from node W023?"
"Check if there are any active jobs on the nodes I'm querying"
"Verify the time range and measurement names in my query"
```

### Plugin Development Issues

**Problem**: Plugin build or deployment failures
**Solutions**:
```
"Debug this Docker build error in my SAGE plugin"
"Help me fix this PyWaggle sensor integration issue"
"Why is my plugin not publishing data to SAGE?"
```

### Performance Issues

**Problem**: Slow queries or timeouts
**Solutions**:
```
"Optimize my data query for better performance"
"Recommend efficient sampling strategies for large datasets"
"Help me reduce bandwidth usage in my plugin"
```

## 📖 Learning Resources

### Getting Started Tutorials
```
"Give me a beginner's tutorial for SAGE data analysis"
"Walk me through creating my first SAGE plugin step by step"
"Show me examples of successful ecological research using SAGE"
```

### Advanced Topics
```
"Explain advanced PyWaggle features for sensor integration"
"How do I implement custom machine learning models on edge nodes?"
"Best practices for multi-node collaborative sensing applications"
```

### Documentation & References
```
"Where can I find the complete SAGE API documentation?"
"Show me examples of published research using SAGE data"
"Get me links to SAGE community forums and support channels"
```

## 🚀 What's Next?

### Upcoming Features
- **Enhanced natural language processing** for even more intuitive queries
- **Automated research workflow generation** based on scientific objectives
- **Real-time collaborative analysis** tools for research teams
- **Integration with popular scientific computing platforms**

### Community Contributions
- **Share your successful workflows** to help other researchers
- **Contribute new plugin templates** for common research needs
- **Participate in SAGE community challenges** and hackathons
- **Provide feedback** to improve the MCP interface

### Getting Involved
```
"How can I contribute to the SAGE community?"
"Show me current research opportunities using SAGE"
"Connect me with other researchers using similar methodologies"
```

---

## 📞 Support & Community

- **Documentation**: [SAGE Docs](https://docs.sagecontinuum.org)
- **Portal**: [SAGE Portal](https://portal.sagecontinuum.org)
- **Community**: [SAGE Forums](https://github.com/waggle-sensor/waggle/discussions)
- **Support**: sage-support@anl.gov

**Ready to revolutionize your research with AI-powered edge sensing? Start exploring SAGE MCP today!** 🌟

## Creating Custom Plugins

The SAGE MCP includes a powerful plugin generation feature that allows you to create new plugins using natural language descriptions. This is accessible through the MCP interface:

### Using the MCP Interface

Ask the MCP server to create plugins for you:

```
"Create a plugin that uses computer vision to detect and count flowering plants in camera images"

"Generate a bird species detection plugin that analyzes audio recordings"

"Help me create a plugin for monitoring air quality using environmental sensors"
```

### Plugin Creation Tool

The MCP server provides a `create_plugin` tool that you can use through natural language:

**Basic Plugin Creation:**
```
"Create a plugin called 'Flower Detector' that uses computer vision to detect flowering plants"
```

**With Specific Requirements:**
```
"Create a plugin for bird sound analysis that requires GPU, audio sensors, and uses torch and librosa libraries"
```

### Generated Plugin Structure

The plugin generator creates a complete plugin structure with:

- `main.py`: Core plugin logic with PyWaggle integration
- `utils/`: Directory for helper functions
- `models/`: Directory for ML models
- `requirements.txt`: Python dependencies
- `Dockerfile`: Container configuration
- `sage.yaml`: Plugin metadata
- `../README.md`: Usage documentation
- `ecr-meta/`: Science description

### Customizing the Plugin

After generation:

1. Review the generated files
2. Add your core logic to `main.py`
3. Add helper functions in `utils/`
4. Update dependencies in `requirements.txt`
5. Modify metadata in `sage.yaml` if needed

### Building and Deploying

The MCP server will provide you with complete deployment instructions when it creates your plugin, including:

```bash
# Build the plugin
cd your-plugin-directory
sudo pluginctl build .

# Test locally  
sudo pluginctl run .

# Deploy to SAGE nodes (through job submission)
# Use the MCP server's job submission tools for deployment
```

### Integration with SAGE Ecosystem

The generated plugins integrate seamlessly with:
- **PyWaggle**: For sensor data access and publishing
- **SAGE Infrastructure**: Automatic deployment and scheduling
- **Edge Code Repository (ECR)**: Plugin sharing and distribution
- **Job Management**: Through the MCP server's job submission tools

**Next Steps After Plugin Creation:**
1. Review and customize the generated code
2. Test locally using pluginctl
3. Submit deployment jobs through the MCP server
4. Monitor plugin performance and data output
5. Share successful plugins with the SAGE community