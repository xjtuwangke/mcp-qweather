#!/usr/bin/env python3
"""Validation error tests for MCP Weather server."""

from datetime import datetime, timedelta
from conftest import TestResult


async def test_validation(client, results):
    beijing_id = "101010100"
    coords = "116.41,39.92"
    future_date = (datetime.now() + timedelta(days=10)).strftime("%Y%m%d")

    section = "VALIDATION ERROR TESTS"
    print(f"\n{'=' * 60}")
    print(section)
    print('=' * 60)

    try:
        await client.call_tool("poi_range", {"location": "invalid,coords", "type": "scenic", "radius": 5})
        results.append(TestResult("validation: invalid coords for poi_range", False, "should have raised error"))
    except Exception as e:
        if "Invalid coordinates" in str(e) or "coordinates" in str(e).lower():
            results.append(TestResult("validation: invalid coords for poi_range", True))
        else:
            results.append(TestResult("validation: invalid coords for poi_range", False, str(e)[:100]))

    try:
        await client.call_tool("poi_range", {"location": coords, "type": "scenic", "radius": 100})
        results.append(TestResult("validation: invalid radius", False, "should have raised error"))
    except Exception as e:
        if "Radius" in str(e) or "radius" in str(e).lower():
            results.append(TestResult("validation: invalid radius", True))
        else:
            results.append(TestResult("validation: invalid radius", False, str(e)[:100]))

    try:
        await client.call_tool("astronomy_sun", {"location": beijing_id, "date": "2026-02-01"})
        results.append(TestResult("validation: invalid date format", False, "should have raised error"))
    except Exception as e:
        if "Invalid date" in str(e) or "date" in str(e).lower():
            results.append(TestResult("validation: invalid date format", True))
        else:
            results.append(TestResult("validation: invalid date format", False, str(e)[:100]))

    try:
        await client.call_tool("weather_daily", {"location": beijing_id, "days": "5d"})
        results.append(TestResult("validation: invalid days", False, "should have raised error"))
    except Exception as e:
        if "Invalid days" in str(e) or "days" in str(e).lower():
            results.append(TestResult("validation: invalid days", True))
        else:
            results.append(TestResult("validation: invalid days", False, str(e)[:100]))

    try:
        await client.call_tool("weather_hourly", {"location": beijing_id, "hours": "48h"})
        results.append(TestResult("validation: invalid hours", False, "should have raised error"))
    except Exception as e:
        if "Invalid hours" in str(e) or "hours" in str(e).lower():
            results.append(TestResult("validation: invalid hours", True))
        else:
            results.append(TestResult("validation: invalid hours", False, str(e)[:100]))

    try:
        await client.call_tool("weather_now", {"location": beijing_id, "unit": "x"})
        results.append(TestResult("validation: invalid unit", False, "should have raised error"))
    except Exception as e:
        if "Invalid unit" in str(e) or "unit" in str(e).lower():
            results.append(TestResult("validation: invalid unit", True))
        else:
            results.append(TestResult("validation: invalid unit", False, str(e)[:100]))

    try:
        await client.call_tool("air_now", {"lat": 100, "lon": 116.41})
        results.append(TestResult("validation: invalid latitude", False, "should have raised error"))
    except Exception as e:
        if "Latitude" in str(e) or "latitude" in str(e).lower():
            results.append(TestResult("validation: invalid latitude", True))
        else:
            results.append(TestResult("validation: invalid latitude", False, str(e)[:100]))

    try:
        await client.call_tool("city_lookup", {"location": "Tokyo", "range": "xxx"})
        results.append(TestResult("validation: invalid country code", False, "should have raised error"))
    except Exception as e:
        if "country code" in str(e).lower() or "country_code" in str(e).lower():
            results.append(TestResult("validation: invalid country code", True))
        else:
            results.append(TestResult("validation: invalid country code", False, str(e)[:100]))

    try:
        await client.call_tool("solar_elevation_angle", {
            "location": coords, "date": future_date, "time": "1200",
            "tz": "9900", "alt": 43.5
        })
        results.append(TestResult("validation: invalid timezone range", False, "should have raised error"))
    except Exception as e:
        if "Invalid timezone" in str(e) or "timezone" in str(e).lower():
            results.append(TestResult("validation: invalid timezone range", True))
        else:
            results.append(TestResult("validation: invalid timezone range", False, str(e)[:100]))

    try:
        await client.call_tool("astronomy_sun", {"location": beijing_id, "date": "20261301"})
        results.append(TestResult("validation: invalid date calendar", False, "should have raised error"))
    except Exception as e:
        if "Invalid date" in str(e) or "date" in str(e).lower():
            results.append(TestResult("validation: invalid date calendar", True))
        else:
            results.append(TestResult("validation: invalid date calendar", False, str(e)[:100]))

    try:
        await client.call_tool("solar_elevation_angle", {
            "location": coords, "date": future_date, "time": "1200",
            "tz": "0800", "alt": 20000
        })
        results.append(TestResult("validation: invalid altitude", False, "should have raised error"))
    except Exception as e:
        if "Altitude" in str(e) or "altitude" in str(e).lower():
            results.append(TestResult("validation: invalid altitude", True))
        else:
            results.append(TestResult("validation: invalid altitude", False, str(e)[:100]))

    try:
        await client.call_tool("city_lookup", {"location": "Beijing", "number": 100})
        results.append(TestResult("validation: invalid number", False, "should have raised error"))
    except Exception as e:
        if "Number" in str(e) or "number" in str(e).lower():
            results.append(TestResult("validation: invalid number", True))
        else:
            results.append(TestResult("validation: invalid number", False, str(e)[:100]))