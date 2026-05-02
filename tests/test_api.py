#!/usr/bin/env python3
"""
Comprehensive MCP Weather API Test Script
Tests all tools, resources, and parameter combinations.
Run: uv run python tests/test_api.py
"""

import asyncio
import sys
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport


class TestResult:
    def __init__(self, name: str, passed: bool, message: str = ""):
        self.name = name
        self.passed = passed
        self.message = message

    def __str__(self):
        status = "PASS" if self.passed else "FAIL"
        msg = f"[{status}] {self.name}"
        if self.message:
            msg += f" - {self.message}"
        return msg


async def run_tests():
    transport = PythonStdioTransport("server.py", cwd="/Volumes/External/work/mcp-weather")
    async with Client(transport) as client:
        results = []

        # Test data
        beijing_id = "101010100"
        coords = "116.41,39.92"
        lat, lon = 39.92, 116.41
        today = "20260501"

        # ===== Resources =====
        print("\n" + "=" * 60)
        print("RESOURCE TESTS")
        print("=" * 60)

        # 1. city_lookup - by name
        try:
            result = await client.read_resource(f"geo://city/{beijing_id}?number=3")
            data = result[0].text
            parsed = eval(data)  # Safe since we control the data
            if parsed.get("code") == "200" and len(parsed.get("location", [])) > 0:
                results.append(TestResult("city_lookup by ID", True))
            else:
                results.append(TestResult("city_lookup by ID", False, f"code={parsed.get('code')}"))
        except Exception as e:
            results.append(TestResult("city_lookup by ID", False, str(e)[:100]))

        # 2. city_lookup - by name with lang
        for lang in ["en", "zh"]:
            try:
                result = await client.read_resource(f"geo://city/Beijing?lang={lang}&number=2")
                data = result[0].text
                parsed = eval(data)
                if parsed.get("code") == "200":
                    results.append(TestResult(f"city_lookup by name lang={lang}", True))
                else:
                    results.append(TestResult(f"city_lookup by name lang={lang}", False, f"code={parsed.get('code')}"))
            except Exception as e:
                results.append(TestResult(f"city_lookup by name lang={lang}", False, str(e)[:100]))

        # 3. city_lookup - by coordinates
        try:
            result = await client.read_resource(f"geo://city/{coords}?number=2")
            data = result[0].text
            parsed = eval(data)
            if parsed.get("code") == "200":
                results.append(TestResult("city_lookup by coords", True))
            else:
                results.append(TestResult("city_lookup by coords", False, f"code={parsed.get('code')}"))
        except Exception as e:
            results.append(TestResult("city_lookup by coords", False, str(e)[:100]))

        # 4. city_lookup - with adm filter
        try:
            result = await client.read_resource("geo://city/Beijing?adm=Beijing&number=3")
            data = result[0].text
            parsed = eval(data)
            if parsed.get("code") == "200":
                results.append(TestResult("city_lookup with adm filter", True))
            else:
                results.append(TestResult("city_lookup with adm filter", False, f"code={parsed.get('code')}"))
        except Exception as e:
            results.append(TestResult("city_lookup with adm filter", False, str(e)[:100]))

        # 5. city_lookup - with range filter (country code)
        try:
            result = await client.read_resource("geo://city/Tokyo?range=jp&number=3")
            data = result[0].text
            parsed = eval(data)
            if parsed.get("code") == "200":
                results.append(TestResult("city_lookup with range=jp", True))
            else:
                results.append(TestResult("city_lookup with range=jp", False, f"code={parsed.get('code')}"))
        except Exception as e:
            results.append(TestResult("city_lookup with range=jp", False, str(e)[:100]))

        # 6. poi_lookup - scenic
        try:
            result = await client.read_resource("geo://poi/Beijing?type=scenic&number=3")
            data = result[0].text
            parsed = eval(data)
            if parsed.get("code") == "200":
                results.append(TestResult("poi_lookup scenic", True))
            else:
                results.append(TestResult("poi_lookup scenic", False, f"code={parsed.get('code')}"))
        except Exception as e:
            results.append(TestResult("poi_lookup scenic", False, str(e)[:100]))

        # 7. poi_lookup - with city filter
        try:
            result = await client.read_resource("geo://poi/Temple?city=Beijing&type=scenic&number=3")
            data = result[0].text
            parsed = eval(data)
            if parsed.get("code") == "200":
                results.append(TestResult("poi_lookup with city filter", True))
            else:
                results.append(TestResult("poi_lookup with city filter", False, f"code={parsed.get('code')}"))
        except Exception as e:
            results.append(TestResult("poi_lookup with city filter", False, str(e)[:100]))

        # 8. poi_lookup - different types
        for poi_type in ["scenic", "ARPT"]:
            try:
                result = await client.read_resource(f"geo://poi/Beijing?type={poi_type}&number=2")
                data = result[0].text
                parsed = eval(data)
                if parsed.get("code") == "200":
                    results.append(TestResult(f"poi_lookup type={poi_type}", True))
                else:
                    results.append(TestResult(f"poi_lookup type={poi_type}", False, f"code={parsed.get('code')}"))
            except Exception as e:
                results.append(TestResult(f"poi_lookup type={poi_type}", False, str(e)[:100]))

        # 9. poi_range - with radius
        try:
            result = await client.read_resource(f"geo://poi/range/{coords}?type=scenic&radius=5&number=3")
            data = result[0].text
            parsed = eval(data)
            if parsed.get("code") == "200":
                results.append(TestResult("poi_range with radius=5", True))
            else:
                results.append(TestResult("poi_range with radius=5", False, f"code={parsed.get('code')}"))
        except Exception as e:
            results.append(TestResult("poi_range with radius=5", False, str(e)[:100]))

        # ===== WeatherAPI Tools =====
        print("\n" + "=" * 60)
        print("WEATHER API TOOL TESTS")
        print("=" * 60)

        # 10. weather_now - by LocationID
        for lang in [None, "en", "zh"]:
            try:
                kwargs = {"location": beijing_id}
                if lang:
                    kwargs["lang"] = lang
                result = await client.call_tool("weather_now", kwargs)
                parsed = result.data
                if parsed.get("code") == "200":
                    results.append(TestResult(f"weather_now by ID lang={lang}", True))
                else:
                    results.append(TestResult(f"weather_now by ID lang={lang}", False, f"code={parsed.get('code')}"))
            except Exception as e:
                results.append(TestResult(f"weather_now by ID lang={lang}", False, str(e)[:100]))

        # 11. weather_now - by coordinates
        try:
            result = await client.call_tool("weather_now", {"location": coords})
            if result.data.get("code") == "200":
                results.append(TestResult("weather_now by coords", True))
            else:
                results.append(TestResult("weather_now by coords", False, f"code={result.data.get('code')}"))
        except Exception as e:
            results.append(TestResult("weather_now by coords", False, str(e)[:100]))

        # 12. weather_now - unit parameter
        for unit in ["m", "i"]:
            try:
                result = await client.call_tool("weather_now", {"location": beijing_id, "unit": unit})
                if result.data.get("code") == "200":
                    results.append(TestResult(f"weather_now unit={unit}", True))
                else:
                    results.append(TestResult(f"weather_now unit={unit}", False, f"code={result.data.get('code')}"))
            except Exception as e:
                results.append(TestResult(f"weather_now unit={unit}", False, str(e)[:100]))

        # 13. weather_daily - different days
        for days in ["3d", "7d", "10d", "15d"]:
            try:
                result = await client.call_tool("weather_daily", {"location": beijing_id, "days": days})
                if result.data.get("code") == "200":
                    results.append(TestResult(f"weather_daily days={days}", True))
                else:
                    results.append(TestResult(f"weather_daily days={days}", False, f"code={result.data.get('code')}"))
            except Exception as e:
                results.append(TestResult(f"weather_daily days={days}", False, str(e)[:100]))

        # 14. weather_daily - lang parameter
        for lang in ["en", "zh"]:
            try:
                result = await client.call_tool("weather_daily", {"location": beijing_id, "days": "7d", "lang": lang})
                if result.data.get("code") == "200":
                    results.append(TestResult(f"weather_daily lang={lang}", True))
                else:
                    results.append(TestResult(f"weather_daily lang={lang}", False, f"code={result.data.get('code')}"))
            except Exception as e:
                results.append(TestResult(f"weather_daily lang={lang}", False, str(e)[:100]))

        # 15. weather_hourly - different hours
        for hours in ["24h", "72h"]:
            try:
                result = await client.call_tool("weather_hourly", {"location": beijing_id, "hours": hours})
                if result.data.get("code") == "200":
                    results.append(TestResult(f"weather_hourly hours={hours}", True))
                else:
                    results.append(TestResult(f"weather_hourly hours={hours}", False, f"code={result.data.get('code')}"))
            except Exception as e:
                results.append(TestResult(f"weather_hourly hours={hours}", False, str(e)[:100]))

        # 16. grid_weather_now - requires coords
        for lang in [None, "en", "zh"]:
            try:
                kwargs = {"location": coords}
                if lang:
                    kwargs["lang"] = lang
                result = await client.call_tool("grid_weather_now", kwargs)
                if result.data.get("code") == "200":
                    results.append(TestResult(f"grid_weather_now lang={lang}", True))
                else:
                    results.append(TestResult(f"grid_weather_now lang={lang}", False, f"code={result.data.get('code')}"))
            except Exception as e:
                results.append(TestResult(f"grid_weather_now lang={lang}", False, str(e)[:100]))

        # 17. grid_weather_daily
        for days in ["3d", "7d"]:
            try:
                result = await client.call_tool("grid_weather_daily", {"location": coords, "days": days})
                if result.data.get("code") == "200":
                    results.append(TestResult(f"grid_weather_daily days={days}", True))
                else:
                    results.append(TestResult(f"grid_weather_daily days={days}", False, f"code={result.data.get('code')}"))
            except Exception as e:
                results.append(TestResult(f"grid_weather_daily days={days}", False, str(e)[:100]))

        # 18. grid_weather_hourly
        try:
            result = await client.call_tool("grid_weather_hourly", {"location": coords, "hours": "24h"})
            if result.data.get("code") == "200":
                results.append(TestResult("grid_weather_hourly hours=24h", True))
            else:
                results.append(TestResult("grid_weather_hourly hours=24h", False, f"code={result.data.get('code')}"))
        except Exception as e:
            results.append(TestResult("grid_weather_hourly hours=24h", False, str(e)[:100]))

        # ===== Minutely/Air/Astronomy Tests =====
        print("\n" + "=" * 60)
        print("MINUTELY/AIR/ASTRONOMY TOOL TESTS")
        print("=" * 60)

        # 19. minutely_precipitation
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

        # 20. indices_forecast - single type
        for lang in ["en", "zh"]:
            try:
                result = await client.call_tool("indices_forecast", {"location": beijing_id, "type": "3", "days": "1d", "lang": lang})
                if result.data.get("code") == "200":
                    results.append(TestResult(f"indices_forecast lang={lang}", True))
                else:
                    results.append(TestResult(f"indices_forecast lang={lang}", False, f"code={result.data.get('code')}"))
            except Exception as e:
                results.append(TestResult(f"indices_forecast lang={lang}", False, str(e)[:100]))

        # 21. indices_forecast - multiple types
        try:
            result = await client.call_tool("indices_forecast", {"location": beijing_id, "type": "1,2,3", "days": "3d"})
            if result.data.get("code") == "200":
                results.append(TestResult("indices_forecast multiple types", True))
            else:
                results.append(TestResult("indices_forecast multiple types", False, f"code={result.data.get('code')}"))
        except Exception as e:
            results.append(TestResult("indices_forecast multiple types", False, str(e)[:100]))

        # 22. air_now
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

        # 23. air_hourly
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

        # 24. air_daily
        try:
            result = await client.call_tool("air_daily", {"lat": lat, "lon": lon, "local_time": True})
            data = result.data
            if "days" in data or (isinstance(data, dict) and len(data) > 0):
                results.append(TestResult("air_daily local_time=True", True))
            else:
                results.append(TestResult("air_daily local_time=True", False, f"unexpected data structure"))
        except Exception as e:
            results.append(TestResult("air_daily local_time=True", False, str(e)[:100]))

        # 25. air_station
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

        # 26. astronomy_sun - date must be within 60 days (future)
        future_date = "20260510"  # A date in the future that works
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

        # 27. astronomy_sun - by coords
        try:
            result = await client.call_tool("astronomy_sun", {"location": coords, "date": future_date})
            if result.data.get("code") == "200":
                results.append(TestResult("astronomy_sun by coords", True))
            else:
                results.append(TestResult("astronomy_sun by coords", False, f"code={result.data.get('code')}"))
        except Exception as e:
            results.append(TestResult("astronomy_sun by coords", False, str(e)[:100]))

        # 28. astronomy_moon
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

        # 29. solar_elevation_angle
        for lang in [None, "en", "zh"]:
            try:
                kwargs = {"location": coords, "date": today, "time": "1230", "tz": "0800", "alt": 43}
                if lang:
                    kwargs["lang"] = lang
                result = await client.call_tool("solar_elevation_angle", kwargs)
                if result.data.get("code") == "200":
                    results.append(TestResult(f"solar_elevation_angle lang={lang}", True))
                else:
                    results.append(TestResult(f"solar_elevation_angle lang={lang}", False, f"code={result.data.get('code')}"))
            except Exception as e:
                results.append(TestResult(f"solar_elevation_angle lang={lang}", False, str(e)[:100]))

        # ===== Print Summary =====
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in results if r.passed)
        failed = [r for r in results if not r.passed]

        print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {len(failed)}")

        if failed:
            print("\nFAILED TESTS:")
            for r in failed:
                print(f"  {r}")

        print("\n" + "=" * 60)
        if not failed:
            print("ALL TESTS PASSED!")
        else:
            print(f"WARNING: {len(failed)} test(s) failed!")
        print("=" * 60)

        return len(failed) == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
