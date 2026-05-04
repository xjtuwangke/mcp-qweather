import asyncio
import os
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport


async def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    transport = PythonStdioTransport(os.path.join(script_dir, "server.py"), args=["--stdio"], cwd=script_dir)

    async with Client(transport) as client:
        tools = await client.list_tools()
        print(f"Tools: {[t.name for t in tools]}")

        result = await client.call_tool("city_lookup", {"location": "西安"})
        print(f"Result: {result.data}")


if __name__ == "__main__":
    asyncio.run(main())
