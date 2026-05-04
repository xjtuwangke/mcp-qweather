#!/usr/bin/env python3
"""Coordinate rounding tests for MCP Weather server."""

from conftest import TestResult


async def test_coordinate_rounding(client, results):
    section = "COORDINATE ROUNDING TESTS"
    print(f"\n{'=' * 60}")
    print(section)
    print('=' * 60)

    try:
        result = await client.call_tool("weather_now", {"location": "116.41556,39.92687"})
        if result.data.get("code") == "200":
            results.append(TestResult("coords rounding: many decimals", True))
        else:
            results.append(TestResult("coords rounding: many decimals", False, f"code={result.data.get('code')}"))
    except Exception as e:
        results.append(TestResult("coords rounding: many decimals", False, str(e)[:100]))

    try:
        result = await client.call_tool("weather_now", {"location": "116.416,39.927"})
        if result.data.get("code") == "200":
            results.append(TestResult("coords rounding: 3 decimals", True))
        else:
            results.append(TestResult("coords rounding: 3 decimals", False, f"code={result.data.get('code')}"))
    except Exception as e:
        results.append(TestResult("coords rounding: 3 decimals", False, str(e)[:100]))

    try:
        result = await client.call_tool("air_now", {"lat": 39.92687, "lon": 116.41})
        data = result.data
        if "indexes" in data or (isinstance(data, dict) and len(data) > 0):
            results.append(TestResult("lat rounding: many decimals", True))
        else:
            results.append(TestResult("lat rounding: many decimals", False, f"unexpected data structure"))
    except Exception as e:
        results.append(TestResult("lat rounding: many decimals", False, str(e)[:100]))

    try:
        result = await client.call_tool("air_now", {"lat": 39.92, "lon": 116.41556})
        data = result.data
        if "indexes" in data or (isinstance(data, dict) and len(data) > 0):
            results.append(TestResult("lon rounding: many decimals", True))
        else:
            results.append(TestResult("lon rounding: many decimals", False, f"unexpected data structure"))
    except Exception as e:
        results.append(TestResult("lon rounding: many decimals", False, str(e)[:100]))

    try:
        result = await client.call_tool("weather_now", {"location": "-73.98572,40.74843"})
        if result.data.get("code") == "200":
            results.append(TestResult("coords rounding: negative lon", True))
        else:
            results.append(TestResult("coords rounding: negative lon", False, f"code={result.data.get('code')}"))
    except Exception as e:
        results.append(TestResult("coords rounding: negative lon", False, str(e)[:100]))

    try:
        result = await client.call_tool("weather_now", {"location": "0,0"})
        if result.data.get("code") == "200":
            results.append(TestResult("coords rounding: zero coordinates", True))
        else:
            results.append(TestResult("coords rounding: zero coordinates", False, f"code={result.data.get('code')}"))
    except Exception as e:
        results.append(TestResult("coords rounding: zero coordinates", False, str(e)[:100]))

    try:
        result = await client.call_tool("air_now", {"lat": -90.0, "lon": 0.0})
        data = result.data
        if "indexes" in data or (isinstance(data, dict) and len(data) > 0):
            results.append(TestResult("lat boundary: -90", True))
        else:
            results.append(TestResult("lat boundary: -90", False, f"unexpected data structure"))
    except Exception as e:
        results.append(TestResult("lat boundary: -90", False, str(e)[:100]))

    try:
        result = await client.call_tool("air_now", {"lat": 90.0, "lon": 0.0})
        data = result.data
        if "indexes" in data or (isinstance(data, dict) and len(data) > 0):
            results.append(TestResult("lat boundary: 90", True))
        else:
            results.append(TestResult("lat boundary: 90", False, f"unexpected data structure"))
    except Exception as e:
        results.append(TestResult("lat boundary: 90", False, str(e)[:100]))

    try:
        result = await client.call_tool("air_now", {"lat": 0.0, "lon": -180.0})
        data = result.data
        if "indexes" in data or (isinstance(data, dict) and len(data) > 0):
            results.append(TestResult("lon boundary: -180", True))
        else:
            results.append(TestResult("lon boundary: -180", False, f"unexpected data structure"))
    except Exception as e:
        results.append(TestResult("lon boundary: -180", False, str(e)[:100]))

    try:
        result = await client.call_tool("air_now", {"lat": 0.0, "lon": 180.0})
        data = result.data
        if "indexes" in data or (isinstance(data, dict) and len(data) > 0):
            results.append(TestResult("lon boundary: 180", True))
        else:
            results.append(TestResult("lon boundary: 180", False, f"unexpected data structure"))
    except Exception as e:
        results.append(TestResult("lon boundary: 180", False, str(e)[:100]))