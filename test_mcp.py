import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    async with streamablehttp_client("http://localhost:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Each item is a (name, resource) tuple
            resources = await session.list_resources()
            print("📚 Available Resources:", [name for name, _ in resources])

            # Attempt to read each known resource
            for resource_name in ["query://plugin-iio", "stats://temperature"]:
                try:
                    content, mime_type = await session.read_resource(resource_name)
                    print(f"\n✅ {resource_name} ({mime_type}):\n{content[:300]}...\n")
                except Exception as e:
                    print(f"\n❌ Failed to read {resource_name}: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
