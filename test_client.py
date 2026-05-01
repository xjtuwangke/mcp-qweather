import asyncio
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

async def main():
    transport = PythonStdioTransport("server.py", cwd="/Volumes/External/work/mcp-weather")
    client = Client(transport)

    async with client:
        tools = await client.list_tools()
        print(f"Tools: {[t.name for t in tools]}")

        result = await client.call_tool("city_search", {"location": "西安"})
        print(f"Result: {result.data}")


asyncio.run(main())