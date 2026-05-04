#!/usr/bin/env python3
"""Minutely/Air/Astronomy tool tests for MCP Weather server."""

from datetime import datetime, timedelta
from conftest import TestResult


async def test_minutely(client, results):
    coords = "116.41,39.92"
    beijing_id = "101010100"
    lat, lon = 39.92, 116.41
    future_date = (datetime.now() + timedelta(days=10)).strftime("%Y%m%d")

    section = "MINUTELY/AIR/ASTRONOMY TOOL TESTS"
    print(f"\n{'=' * 60}")
    print(section)
    print('=' * 60)

    for lang in [None, "en", "zh"]:
        try:
            kwargs = {"location": coords}
            if lang:
                kwargs["lang"] = lang
            result = await client.call_tool("minutely_precipitation", kwargs)
            if result.data.get("code") == "200":
                results.append(TestResult(f"minutely_precipitation lang={lang}", True))
            else:
                results.append(TestResult(f"minutely_precipitation lang={lang}", False, f"code={result.data.get('code')}"))
        except Exception as e:
            results.append(TestResult(f"minutely_precipitation lang={lang}", False, str(e)[:100]))


async def test_air(client, results):
    lat, lon = 39.92, 116.41

    for lang in ["en", "zh"]:
        try:
            result = await client.call_tool("indices_forecast", {"location": "101010100", "type": "3", "days": "1d", "lang": lang})
            if result.data.get("code") == "200":
                results.append(TestResult(f"indices_forecast lang={lang}", True))
            else:
                results.append(TestResult(f"indices_forecast lang={lang}", False, f"code={result.data.get('code')}"))
        except Exception as e:
            results.append(TestResult(f"indices_forecast lang={lang}", False, str(e)[:100]))

    try:
        result = await client.call_tool("indices_forecast", {"location": "101010100", "type": "1,2,3", "days": "3d"})
        if result.data.get("code") == "200":
            results.append(TestResult("indices_forecast multiple types", True))
        else:
            results.append(TestResult("indices_forecast multiple types", False, f"code={result.data.get('code')}"))
    except Exception as e:
        results.append(TestResult("indices_forecast multiple types", False, str(e)[:100]))

    for lang in [None, "en", "zh"]:
        try:
            kwargs = {"lat": lat, "lon": lon}
            if lang:
                kwargs["lang"] = lang
            result = await client.call_tool("air_now", kwargs)
            data = result.data
            if "indexes" in data or (isinstance(data, dict) and len(data) > 0):
                results.append(TestResult(f"air_now lang={lang}", True))
            else:
                results.append(TestResult(f"air_now lang={lang}", False, f"unexpected data structure"))
        except Exception as e:
            results.append(TestResult(f"air_now lang={lang}", False, str(e)[:100]))

    for local_time in [None, False, True]:
        try:
            kwargs = {"lat": lat, "lon": lon}
            if local_time is not None:
                kwargs["local_time"] = local_time
            result = await client.call_tool("air_hourly", kwargs)
            data = result.data
            if "hours" in data or (isinstance(data, dict) and len(data) > 0):
                results.append(TestResult(f"air_hourly local_time={local_time}", True))
            else:
                results.append(TestResult(f"air_hourly local_time={local_time}", False, f"unexpected data structure"))
        except Exception as e:
            results.append(TestResult(f"air_hourly local_time={local_time}", False, str(e)[:100]))

    try:
        result = await client.call_tool("air_daily", {"lat": lat, "lon": lon, "local_time": True})
        data = result.data
        if "days" in data or (isinstance(data, dict) and len(data) > 0):
            results.append(TestResult("air_daily local_time=True", True))
        else:
            results.append(TestResult("air_daily local_time=True", False, f"unexpected data structure"))
    except Exception as e:
        results.append(TestResult("air_daily local_time=True", False, str(e)[:100]))

    for lang in [None, "en", "zh"]:
        try:
            kwargs = {"location_id": "P53763"}
            if lang:
                kwargs["lang"] = lang
            result = await client.call_tool("air_station", kwargs)
            data = result.data
            if "pollutants" in data or (isinstance(data, dict) and len(data) > 0):
                results.append(TestResult(f"air_station lang={lang}", True))
            else:
                results.append(TestResult(f"air_station lang={lang}", False, f"unexpected data structure"))
        except Exception as e:
            results.append(TestResult(f"air_station lang={lang}", False, str(e)[:100]))


async def test_astronomy(client, results):
    beijing_id = "101010100"
    coords = "116.41,39.92"
    future_date = (datetime.now() + timedelta(days=10)).strftime("%Y%m%d")

    for lang in [None, "en", "zh"]:
        try:
            kwargs = {"location": beijing_id, "date": future_date}
            if lang:
                kwargs["lang"] = lang
            result = await client.call_tool("astronomy_sun", kwargs)
            if result.data.get("code") == "200":
                results.append(TestResult(f"astronomy_sun lang={lang}", True))
            else:
                results.append(TestResult(f"astronomy_sun lang={lang}", False, f"code={result.data.get('code')}"))
        except Exception as e:
            results.append(TestResult(f"astronomy_sun lang={lang}", False, str(e)[:100]))

    try:
        result = await client.call_tool("astronomy_sun", {"location": coords, "date": future_date})
        if result.data.get("code") == "200":
            results.append(TestResult("astronomy_sun by coords", True))
        else:
            results.append(TestResult("astronomy_sun by coords", False, f"code={result.data.get('code')}"))
    except Exception as e:
        results.append(TestResult("astronomy_sun by coords", False, str(e)[:100]))

    for lang in [None, "en", "zh"]:
        try:
            kwargs = {"location": beijing_id, "date": future_date}
            if lang:
                kwargs["lang"] = lang
            result = await client.call_tool("astronomy_moon", kwargs)
            if result.data.get("code") == "200":
                results.append(TestResult(f"astronomy_moon lang={lang}", True))
            else:
                results.append(TestResult(f"astronomy_moon lang={lang}", False, f"code={result.data.get('code')}"))
        except Exception as e:
            results.append(TestResult(f"astronomy_moon lang={lang}", False, str(e)[:100]))

    try:
        result = await client.call_tool("solar_elevation_angle", {
            "location": coords, "date": future_date, "time": "1200",
            "tz": "0800", "alt": 43, "lang": "en"
        })
        data = result.data
        if "solarElevationAngle" in data or (isinstance(data, dict) and len(data) > 0):
            results.append(TestResult("solar_elevation_angle", True))
        else:
            results.append(TestResult("solar_elevation_angle", False, f"unexpected data structure"))
    except Exception as e:
        results.append(TestResult("solar_elevation_angle", False, str(e)[:100]))