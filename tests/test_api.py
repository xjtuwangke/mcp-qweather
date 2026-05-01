#!/usr/bin/env python3
"""
MCP Weather API Test Script
Run: uv run python tests/test_api.py
"""

import asyncio
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport


async def test_all():
    transport = PythonStdioTransport("server.py", cwd="/Volumes/External/work/mcp-weather")
    async with Client(transport) as client:
        tools = await client.list_tools()
        print(f"Tools ({len(tools)}): {[t.name for t in tools]}\n")

        # ===== Resources (GeoAPI) =====
        print("=" * 50)
        print("GeoAPI Resources")
        print("=" * 50)

        print("\n1. city_search - Search Xi'an")
        result = await client.read_resource("geo://city/%E8%A5%BF%E5%AE%89?number=3")
        print(f"Result: {result[0].text[:200]}...")

        print("\n2. poi_search - Search Beijing scenic")
        result = await client.read_resource("geo://poi/Beijing?type=scenic&number=3")
        print(f"Result: {result[0].text[:200]}...")

        print("\n3. poi_range_search - Tiananmen周边5km scenic")
        result = await client.read_resource("geo://poi/range/116.40528,39.90498?type=scenic&radius=5&number=3")
        print(f"Result: {result[0].text[:200]}...")

        # ===== WeatherAPI Tools =====
        print("\n" + "=" * 50)
        print("WeatherAPI Tests")
        print("=" * 50)

        beijing_id = "101010100"
        coords = "116.41,39.92"

        print("\n4. weather_now - Beijing current weather")
        result = await client.call_tool("weather_now", {"location": beijing_id})
        print(f"Result: {result.data}")

        print("\n5. weather_daily - Beijing 7-day forecast")
        result = await client.call_tool("weather_daily", {"location": beijing_id, "days": "7d"})
        print(f"Result: (7 days of data)")

        print("\n6. weather_hourly - Beijing 24h forecast")
        result = await client.call_tool("weather_hourly", {"location": beijing_id, "hours": "24h"})
        print(f"Result: (24 hours of data)")

        print("\n7. grid_weather_now - Grid current weather")
        result = await client.call_tool("grid_weather_now", {"location": coords})
        print(f"Result: {result.data}")

        print("\n8. grid_weather_daily - Grid 7-day forecast")
        result = await client.call_tool("grid_weather_daily", {"location": coords, "days": "7d"})
        print(f"Result: (7 days of data)")

        print("\n9. grid_weather_hourly - Grid 24h forecast")
        result = await client.call_tool("grid_weather_hourly", {"location": coords, "hours": "24h"})
        print(f"Result: (24 hours of data)")

        # ===== Minutely/Air/Astronomy API Tests =====
        print("\n" + "=" * 50)
        print("Minutely/Air/Astronomy API Tests")
        print("=" * 50)

        print("\n10. minutely_precipitation - Beijing minutely precip")
        result = await client.call_tool("minutely_precipitation", {"location": coords})
        print(f"Result: {result.data}")

        print("\n11. indices_forecast - Beijing clothing index")
        result = await client.call_tool("indices_forecast", {"location": beijing_id, "type": "3", "days": "1d"})
        print(f"Result: {result.data}")

        print("\n12. air_now - Beijing AQI")
        result = await client.call_tool("air_now", {"lat": 39.92, "lon": 116.41})
        print(f"Result: {result.data}")

        print("\n13. air_hourly - Beijing 24h AQI forecast")
        result = await client.call_tool("air_hourly", {"lat": 39.92, "lon": 116.41})
        print(f"Result: (24 hours of data)")

        print("\n14. air_daily - Beijing 3d AQI forecast")
        result = await client.call_tool("air_daily", {"lat": 39.92, "lon": 116.41})
        print(f"Result: (3 days of data)")

        print("\n15. air_station - Air station data")
        result = await client.call_tool("air_station", {"location_id": "P53763"})
        print(f"Result: {result.data}")

        print("\n16. astronomy_sun - Beijing sunrise/sunset")
        result = await client.call_tool("astronomy_sun", {"location": beijing_id, "date": "20260501"})
        print(f"Result: {result.data}")

        print("\n17. astronomy_moon - Beijing moon phase")
        result = await client.call_tool("astronomy_moon", {"location": beijing_id, "date": "20260501"})
        print(f"Result: {result.data}")

        print("\n18. solar_elevation_angle - Beijing solar angles")
        result = await client.call_tool("solar_elevation_angle", {
            "location": coords,
            "date": "20260501",
            "time": "1230",
            "tz": "0800",
            "alt": 43
        })
        print(f"Result: {result.data}")

        print("\n" + "=" * 50)
        print("All tests completed!")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_all())
