import asyncio
import json
from typing import Any

from ollama import chat
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


# Connect to MCP and dynamically define callable tools for Ollama
async def fetch_mcp_tools() -> list[dict]:
    async with streamablehttp_client("http://localhost:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()

            formatted_tools = []
            for name, tool in tools:
                if not isinstance(tool, dict):
                    print(f"⚠️ Tool '{name}' is not a dict: {type(tool)} — skipping.")
                    continue
                parameters = tool.get("inputSchema")
                if not parameters:
                    print(f"⚠️ Tool '{name}' has no inputSchema — skipping.")
                    continue
                formatted_tools.append({
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": tool.get("description", ""),
                        "parameters": parameters
                    }
                })
            return formatted_tools



# Map Ollama tool call to actual MCP invocation
async def handle_tool_call(tool_call: dict[str, Any], session: ClientSession):
    fn = tool_call["function"]["name"]
    args = tool_call["function"]["arguments"]
    print(f"\n🔧 Calling tool '{fn}' with args {args}")
    try:
        result = await session.call_tool(fn, arguments=args)
        print(f"\n✅ Tool result: {result}\n")
        return f"[Tool Result]\n{result}"
    except Exception as e:
        return f"❌ Tool call failed: {e}"


# Main routine
async def main():
    mcp_tools = await fetch_mcp_tools()

    async with streamablehttp_client("http://localhost:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            messages = [{"role": "user", "content": "What are the latest temperature stats?"}]

            response = chat(
                model="llama3.2:1b",
                messages=messages,
                tools=mcp_tools,
                stream=True,
                options={"num_ctx": 32000},
            )

            for chunk in response:
                if hasattr(chunk.message, "tool_calls") and chunk.message.tool_calls:
                    for call in chunk.message.tool_calls:
                        tool_output = await handle_tool_call(call.dict(), session)
                        messages.append({"role": "tool", "content": tool_output, "name": call.function.name})

                        print("\n🔁 Resuming chat with tool result...\n")
                        followup = chat(
                            model="llama3.2:1b",
                            messages=messages,
                            tools=mcp_tools,
                            stream=True,
                            options={"num_ctx": 32000},
                        )
                        async for subchunk in followup:
                            print(subchunk.message.content or "", end="", flush=True)
                        return

                if chunk.message.content:
                    print(chunk.message.content, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
