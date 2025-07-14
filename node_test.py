#!/usr/bin/env python3

import asyncio
import json
from typing import Any

from ollama import chat
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def test_comprehensive_node_queries():
    """Test Ollama with comprehensive node data queries"""
    
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
                    
                print(f"📋 Available tools: {[t['function']['name'] for t in formatted_tools]}")
            else:
                print(f"❌ Unexpected tools response format")
                return
            
            # Simple, natural test queries that should trigger function calls
            test_queries = [
                # Basic temperature queries
                "What is the temperature on node W027?",
                "Get temperature data for W026",
                
                # All sensor data queries  
                "Get all sensor data from node W027",
                "What sensors are on node W026?",
                "Show everything from node W023",
                
                # Environmental data queries
                "What's the humidity and pressure on W027?",
                "Get environmental data for W026",
                "Show temperature, humidity and pressure for W023",
                
                # IIO specific queries
                "Get IIO sensor data from W027",
                "What IIO measurements are on W026?",
                "Show industrial sensor data from W023",
                
                # Search queries
                "Find pressure measurements from W027",
                "Search for humidity data on W026", 
                "Look for temperature sensors on W023",
                
                # General queries
                "Give me an environmental summary",
                "What nodes have temperature data?",
                "Show available nodes",
            ]
            
            print(f"\n🧪 Testing {len(test_queries)} different query types...")
            
            for i, query in enumerate(test_queries, 1):
                print(f"\n{'='*80}")
                print(f"🧪 Test {i}/{len(test_queries)}: {query}")
                print('='*80)
                
                success = await run_query_test(query, formatted_tools, session)
                
                if not success:
                    print("⚠️ This query didn't trigger tool calls - might need better prompting")
                
                # Small delay between tests
                await asyncio.sleep(0.5)
            
            print(f"\n{'='*80}")
            print("🎉 All tests completed!")
            print('='*80)


async def run_query_test(query: str, formatted_tools: list, session: ClientSession) -> bool:
    """Run a single query test and return True if tools were called"""
    
    messages = [{"role": "user", "content": query}]
    
    try:
        # Use the original working system message that had some success
        system_message = {
            "role": "system", 
            "content": "You must use functions to answer questions about sensor data. "
                      "Never provide text responses without calling functions first. "
                      "Always call the appropriate function when users ask about nodes, temperatures, sensors, or measurements."
        }
        messages.insert(0, system_message)
        
        response = chat(
            model="qwen3:1.7b",
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
                print("🔧 Tool calls detected!")
                
                for call in chunk.message.tool_calls:
                    print(f"   → Calling: {call.function.name}")
                    
                    # Show arguments if they exist
                    if hasattr(call.function, 'arguments') and call.function.arguments:
                        if isinstance(call.function.arguments, str):
                            try:
                                args = json.loads(call.function.arguments)
                                print(f"   → Args: {args}")
                            except:
                                print(f"   → Args: {call.function.arguments}")
                        else:
                            print(f"   → Args: {call.function.arguments}")
                    
                    # Handle Pydantic version compatibility
                    try:
                        call_dict = call.model_dump() if hasattr(call, 'model_dump') else call.dict()
                    except AttributeError:
                        call_dict = call.__dict__
                    
                    tool_output = await handle_tool_call(call_dict, session)
                    
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
                
                # Get final response
                print("\n💬 Ollama's response:")
                followup = chat(
                    model="qwen3:1.7b",
                    messages=messages,
                    tools=formatted_tools,
                    stream=True,
                    options={"num_ctx": 32000, "temperature": 0.1},
                )
                
                for subchunk in followup:
                    if subchunk.message.content:
                        print(subchunk.message.content, end="", flush=True)
                print()  # New line
                break
            
            # Handle regular content
            elif chunk.message.content:
                assistant_response += chunk.message.content
                print(chunk.message.content, end="", flush=True)
        
        if not tool_calls_made:
            print(f"\n❌ No tool calls made")
            print(f"💭 Response: {assistant_response[:200]}...")
            return False
        else:
            print(f"\n✅ Successfully used tools!")
            return True
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


async def handle_tool_call(tool_call: dict[str, Any], session: ClientSession) -> str:
    """Handle tool calls"""
    fn = tool_call["function"]["name"]
    args = tool_call["function"]["arguments"]
    
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {}
    
    try:
        result = await session.call_tool(fn, arguments=args)
        
        # Handle different response formats from MCP
        if hasattr(result, 'content') and result.content:
            # Extract text content from MCP response
            if isinstance(result.content, list) and len(result.content) > 0:
                result_str = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
            else:
                result_str = str(result.content)
        else:
            result_str = str(result)
        
        # Show preview
        if len(result_str) > 300:
            preview_lines = result_str.split('\n')[:8]
            preview = '\n'.join(preview_lines) + "\n   ... (truncated)"
            print(f"   ✅ Result preview:\n   {preview.replace(chr(10), chr(10) + '   ')}")
        else:
            print(f"   ✅ Result:\n   {result_str.replace(chr(10), chr(10) + '   ')}")
            
        return result_str
        
    except Exception as e:
        error_msg = f"Tool call failed: {e}"
        print(f"   ❌ {error_msg}")
        return error_msg


if __name__ == "__main__":
    print("🧪 Comprehensive Node Data Testing with Ollama")
    print("=" * 80)
    print("Testing various ways to query node sensor data through MCP tools")
    print("=" * 80)
    
    asyncio.run(test_comprehensive_node_queries())