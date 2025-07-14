#!/usr/bin/env python3

"""
SAGE MCP Chat CLI
================

Interactive chat interface for SAGE MCP, based on the working test scripts.
Supports sensor data queries, job scheduling/monitoring, and node information.
"""

import asyncio
import json
import re
import sys
import time  # Add this import for the time module
from typing import Any, Dict, List

from ollama import chat
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def chat_with_mcp():
    """Interactive chat interface for SAGE MCP"""
    
    print("🔌 Connecting to MCP server...")
    
    async with streamablehttp_client("http://localhost:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Fetch tools from MCP server
            tools_response = await session.list_tools()
            formatted_tools = []
            
            if hasattr(tools_response, 'tools'):
                tools = tools_response.tools
                for tool in tools:
                    if not hasattr(tool, 'name') or not hasattr(tool, 'inputSchema'):
                        continue
                    
                    formatted_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": getattr(tool, 'description', ''),
                            "parameters": tool.inputSchema
                        }
                    })
                
                tool_names = [t['function']['name'] for t in formatted_tools]
                print(f"✅ Connected! Available tools: {', '.join(tool_names)}")
                
                # Add special hints for tool categories
                job_tools = [t for t in tool_names if 'job' in t.lower()]
                node_tools = [t for t in tool_names if 'node' in t.lower() or 'list_all_nodes' in t.lower()]
                sensor_tools = [t for t in tool_names if 'sensor' in t.lower() or 'temperature' in t.lower() or 'environmental' in t.lower()]
                
                if job_tools:
                    print(f"🔧 Job management tools: {', '.join(job_tools)}")
                if node_tools:
                    print(f"📍 Node information tools: {', '.join(node_tools)}")
                if sensor_tools:
                    print(f"🌡️ Sensor data tools: {', '.join(sensor_tools)}")
            else:
                print(f"❌ Unexpected tools response format")
                return
            
            # Set up system message and conversation history
            messages = [
                {
                    "role": "system", 
                    "content": (
                        "You are SAGE Assistant, an expert on the SAGE environmental sensing network. "
                        "You help users interact with SAGE nodes, query sensor data, and manage jobs. "
                        "Always use the available tools to retrieve real-time information when asked about nodes, "
                        "sensors, measurements, or jobs. Be helpful, concise, and accurate. "
                        "\n\n"
                        "For temperature extremes by location: Use get_max_temperature_by_location or "
                        "get_min_temperature_by_location for direct answers about temperature extremes in "
                        "specific regions. These tools are more efficient than using get_nodes_by_location "
                        "followed by temperature queries. For sensor-specific queries, include the sensor_type "
                        "parameter (e.g., 'bme680' for BME680 sensors)."
                        "\n\n"
                        "For location-based queries: When users ask about nodes in specific locations (cities, states, or regions "
                        "like 'East Coast', 'Midwest', 'Chicago'), ALWAYS use get_nodes_by_location first to identify nodes in that "
                        "area. Then use get_temperature_range_by_location for temperature ranges across those nodes. Don't try to "
                        "query individual nodes before determining which ones are in the requested location."
                        "\n\n"
                        "For node information: Use get_node_info to get detailed information about a specific node, "
                        "list_all_nodes to list all available nodes, and get_sensor_details to get information "
                        "about specific sensor types. Use these tools when users ask about node capabilities, "
                        "locations, or sensor specifications."
                        "\n\n"
                        "For sensor data queries: Use tools like get_node_temperature, get_environmental_summary, etc. "
                        "For time ranges, use formats like '-1h' or '-30m' instead of words like 'today' or 'now'. "
                        "When asked about specific sensor types (like BME680), make sure to filter data accordingly."
                        "\n\n"
                        "For job management: You can submit jobs with submit_sage_job, check status with check_job_status, "
                        "and query job data with query_job_data. When submitting PTZ-YOLO jobs, use proper parameters like: "
                        "job_name='ptz-yolo-test', nodes='W027', plugin_image='registry.sagecontinuum.org/plebbyd/ptzapp-yolo:0.1.13', "
                        "and plugin_args that include model, iterations, username, password, cameraip, and objects. "
                        "\n\n"
                        "Always parse job IDs from responses when submitting jobs so you can reference them later."
                        "\n\n"
                        "Important: When handling geographic queries about temperature, humidity, or other environmental data, "
                        "always use get_max_temperature_by_location or get_min_temperature_by_location for these specific queries."
                    )
                }
            ]
            
            print("\n💬 SAGE Chat ready! Type 'exit' to quit or 'clear' to reset history.")
            print("📋 Available commands:")
            print("  - Ask about node information (e.g., 'Tell me about node W027', 'List all available nodes')")
            print("  - Query sensor data (e.g., 'What's the temperature at W023?', 'Show environmental data summary')")
            print("  - Ask location questions (e.g., 'What's the highest temperature in Chicago?')")
            print("  - Manage jobs (e.g., 'Submit an image sampling job', 'Check status of job 12345')")
            
            # Main chat loop
            while True:
                # Get user input
                try:
                    user_input = input("\n👤 You: ")
                except EOFError:
                    print("\nGoodbye!")
                    break
                
                # Check for exit command
                if user_input.lower() in ['exit', 'quit']:
                    print("👋 Goodbye!")
                    break
                
                # Check for clear command
                if user_input.lower() == 'clear':
                    messages = messages[:1]  # Keep only system message
                    print("🧹 Chat history cleared.")
                    continue
                
                # Check for help command
                if user_input.lower() in ['help', '?']:
                    print("\n📚 SAGE Assistant Help:")
                    print("  - Node info: 'List all nodes', 'Tell me about node W027', 'What sensors are on W023?'")
                    print("  - Sensor types: 'Tell me about the BME680 sensor', 'What camera models are used?'")
                    print("  - Location queries: 'What's the highest temperature in Chicago?', 'Show temperature range in the Midwest'")
                    print("  - Sensor data: 'Current temperature on W027', 'Show environmental data from last hour'")
                    print("  - Jobs: 'Submit an image sampling job to W027', 'Check job status 12345'")
                    print("  - Commands: 'clear' to reset history, 'exit' to quit")
                    continue
                
                # Add user message to history
                messages.append({"role": "user", "content": user_input})
                
                # Get LLM response
                print("\n🤖 SAGE Assistant:", end="")
                
                try:
                    # Using the same parameters that worked in the test script
                    response = chat(
                        model="qwen3:32b",  # Using the 32b model you mentioned
                        messages=messages,
                        tools=formatted_tools,
                        stream=True,
                        options={
                            "num_ctx": 32000,
                            "temperature": 0.0,  # Very low temperature for consistent tool usage
                            "top_p": 0.1,        # Low top_p for more focused responses
                        },
                    )
                    
                    tool_calls_made = False
                    assistant_response = ""
                    
                    for chunk in response:
                        # Handle tool calls
                        if hasattr(chunk.message, "tool_calls") and chunk.message.tool_calls:
                            tool_calls_made = True
                            print("\n🔧 Querying SAGE data...")
                            
                            # Track tool call results for multi-tool calls
                            tool_results = []
                            
                            for call in chunk.message.tool_calls:
                                fn_name = call.function.name
                                print(f"   → Calling: {fn_name}")
                                
                                # Parse arguments
                                args = {}
                                if hasattr(call.function, 'arguments') and call.function.arguments:
                                    if isinstance(call.function.arguments, str):
                                        try:
                                            args = json.loads(call.function.arguments)
                                            # Convert time ranges
                                            if 'time_range' in args and args['time_range'] in ['today', 'now', 'recent']:
                                                args['time_range'] = '-1h'
                                                print(f"   → Converting time_range to '-1h'")
                                            print(f"   → Args: {args}")
                                        except:
                                            print(f"   → Args: {call.function.arguments}")
                                    else:
                                        args = call.function.arguments
                                        print(f"   → Args: {args}")
                                
                                # Handle Pydantic version compatibility
                                try:
                                    call_dict = call.model_dump() if hasattr(call, 'model_dump') else call.dict()
                                except AttributeError:
                                    call_dict = call.__dict__
                                
                                # Get tool output using the updated function
                                tool_output = await handle_tool_call(call_dict, session)
                                tool_results.append((fn_name, tool_output))
                                
                                # If this was a job submission, extract the job ID
                                if fn_name == "submit_sage_job" and 'Job ID:' in tool_output:
                                    job_id_match = re.search(r'Job ID:\s*(\d+)', tool_output)
                                    if job_id_match:
                                        job_id = job_id_match.group(1)
                                        print(f"   📝 Extracted Job ID: {job_id}")
                                
                                # Add to conversation
                                messages.append({
                                    "role": "assistant",
                                    "content": "",
                                    "tool_calls": [call_dict]
                                })
                                messages.append({
                                    "role": "tool", 
                                    "content": tool_output, 
                                    "tool_call_id": getattr(call, 'id', call.function.name)
                                })
                            
                            # Show summary for multiple tool calls
                            if len(tool_results) > 1:
                                print(f"\n📊 Completed {len(tool_results)} tool calls:")
                                for idx, (fn_name, _) in enumerate(tool_results, 1):
                                    print(f"   {idx}. {fn_name}")
                            
                            # Get final response after tool calls
                            print("\n💬 Processing data...")
                            followup = chat(
                                model="qwen3:32b",  # Using the 32b model you mentioned
                                messages=messages,
                                tools=formatted_tools,
                                stream=True,
                                options={"num_ctx": 32000, "temperature": 0.1},
                            )
                            
                            print()  # New line for response
                            final_response = ""
                            for subchunk in followup:
                                if subchunk.message.content:
                                    content = subchunk.message.content
                                    final_response += content
                                    print(content, end="", flush=True)
                            
                            # Add to history
                            messages.append({"role": "assistant", "content": final_response})
                            break
                        
                        # Handle regular content
                        elif chunk.message.content:
                            content = chunk.message.content
                            assistant_response += content
                            print(f" {content}", end="", flush=True)
                    
                    # If no tool calls were made, add response to history
                    if not tool_calls_made and assistant_response:
                        messages.append({"role": "assistant", "content": assistant_response})
                
                except Exception as e:
                    print(f"\n❌ Error: {e}")


async def handle_tool_call(tool_call: Dict[str, Any], session: ClientSession) -> str:
    """Handle tool calls with improved debugging and response handling"""
    fn = tool_call["function"]["name"]
    args = tool_call["function"]["arguments"]
    
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {}
    
    try:
        # Special handling for job-related tools
        if fn == "submit_sage_job":
            print(f"   📝 Submitting job: {args.get('job_name', 'unnamed')}")
            
            # Ensure plugin_args is properly formatted
            if 'plugin_args' in args and isinstance(args['plugin_args'], dict):
                # Convert dict to comma-separated string
                plugin_args = ','.join([f"{k}={v}" for k, v in args['plugin_args'].items()])
                args['plugin_args'] = plugin_args
                print(f"   ℹ️ Converted plugin_args dict to string format")
        
        # Special handling for location-based temperature queries
        if fn == "get_nodes_by_location":
            print(f"   📍 Finding nodes in location: {args.get('location', 'unknown')}")
            # Check if this is for a temperature query
            if any(temp_word in str(args).lower() for temp_word in ["temperature", "temp", "hot", "cold"]):
                print(f"   ⚠️ Note: For temperature queries, use get_max_temperature_by_location or get_min_temperature_by_location instead")
        
        # Add debug timestamp for long-running operations
        start_time = time.time()
        print(f"   ⏱️ Starting tool call at {time.strftime('%H:%M:%S')}")
        
        # Call the tool with the provided arguments
        result = await session.call_tool(fn, arguments=args)
        
        # Add debug timestamp for completion
        elapsed = time.time() - start_time
        print(f"   ⏱️ Tool call completed in {elapsed:.2f} seconds")
        
        # Handle different response formats from MCP
        if hasattr(result, 'content') and result.content:
            # Extract text content from MCP response
            if isinstance(result.content, list) and len(result.content) > 0:
                result_str = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
            else:
                result_str = str(result.content)
        else:
            result_str = str(result)
        
        # Show preview - shorter for very large results
        result_len = len(result_str)
        print(f"   📊 Result size: {result_len} characters")
        
        if result_len > 1000:
            preview_lines = result_str.split('\n')[:3]  # Show fewer lines for large results
            preview = '\n'.join(preview_lines) + f"\n   ... (truncated {result_len-300}+ characters)"
            print(f"   ✅ Result preview (large):\n   {preview.replace(chr(10), chr(10) + '   ')}")
        elif result_len > 300:
            preview_lines = result_str.split('\n')[:4]
            preview = '\n'.join(preview_lines) + "\n   ... (truncated)"
            print(f"   ✅ Result preview:\n   {preview.replace(chr(10), chr(10) + '   ')}")
        else:
            print(f"   ✅ Result:\n   {result_str.replace(chr(10), chr(10) + '   ')}")
        
        # For node location results, check size and warn if very large
        if fn == "get_nodes_by_location" and result_len > 2000:
            print(f"   ⚠️ Warning: Large location result ({result_len} chars). Consider using more specific tools.")
            
        return result_str
        
    except Exception as e:
        error_msg = f"Tool call failed: {e}"
        print(f"   ❌ {error_msg}")
        return error_msg


if __name__ == "__main__":
    print("🌟 SAGE MCP Chat CLI")
    print("=" * 50)
    print("Enhanced with location temperature tools and improved debugging")
    print("=" * 50)
    
    try:
        asyncio.run(chat_with_mcp())
    except KeyboardInterrupt:
        print("\n👋 Session terminated by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")