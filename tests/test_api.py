#!/usr/bin/env python3
"""
Comprehensive MCP Weather API Test Script
Tests all tools, resources, and parameter combinations.
Run: uv run python tests/test_api.py
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
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
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    transport = PythonStdioTransport(os.path.join(script_dir, "server.py"), cwd=script_dir)
    async with Client(transport) as client:
        results = []

        # Test data
        beijing_id = "101010100"
        coords = "116.41,39.92"
        lat, lon = 39.92, 116.41
        today = datetime.now().strftime("%Y%m%d")
        future_date = (datetime.now() + timedelta(days=10)).strftime("%Y%m%d")

        # ===== Geo Tool Tests =====
        print("\n" + "=" * 60)
        print("GEO TOOL TESTS")
        print("=" * 60)

        # 1. city_lookup - by name
        try:
            result = await client.call_tool("city_lookup", {"location": beijing_id, "number": 3})
            parsed = result.data
            if parsed.get("code") == "200" and len(parsed.get("location", [])) > 0:
                results.append(TestResult("city_lookup by ID", True))
            else:
                results.append(TestResult("city_lookup by ID", False, f"code={parsed.get('code')}"))
        except Exception as e:
            results.append(TestResult("city_lookup by ID", False, str(e)[:100]))

        # 2. city_lookup - by name with lang
        for lang in ["en", "zh"]:
            try:
                result = await client.call_tool("city_lookup", {"location": "Beijing", "number": 2, "lang": lang})
                parsed = result.data
                if parsed.get("code") == "200":
                    results.append(TestResult(f"city_lookup by name lang={lang}", True))
                else:
                    results.append(TestResult(f"city_lookup by name lang={lang}", False, f"code={parsed.get('code')}"))
            except Exception as e:
                results.append(TestResult(f"city_lookup by name lang={lang}", False, str(e)[:100]))

        # 3. city_lookup - by coordinates
        try:
            result = await client.call_tool("city_lookup", {"location": coords, "number": 2})
            parsed = result.data
            if parsed.get("code") == "200":
                results.append(TestResult("city_lookup by coords", True))
            else:
                results.append(TestResult("city_lookup by coords", False, f"code={parsed.get('code')}"))
        except Exception as e:
            results.append(TestResult("city_lookup by coords", False, str(e)[:100]))

        # 4. city_lookup - with adm filter
        try:
            result = await client.call_tool("city_lookup", {"location": "Beijing", "adm": "Beijing", "number": 3})
            parsed = result.data
            if parsed.get("code") == "200":
                results.append(TestResult("city_lookup with adm filter", True))
            else:
                results.append(TestResult("city_lookup with adm filter", False, f"code={parsed.get('code')}"))
        except Exception as e:
            results.append(TestResult("city_lookup with adm filter", False, str(e)[:100]))

        # 5. city_lookup - with range filter (country code)
        try:
            result = await client.call_tool("city_lookup", {"location": "Tokyo", "range": "jp", "number": 3})
            parsed = result.data
            if parsed.get("code") == "200":
                results.append(TestResult("city_lookup with range=jp", True))
            else:
                results.append(TestResult("city_lookup with range=jp", False, f"code={parsed.get('code')}"))
        except Exception as e:
            results.append(TestResult("city_lookup with range=jp", False, str(e)[:100]))

        # 6. poi_lookup - scenic
        try:
            result = await client.call_tool("poi_lookup", {"location": "Beijing", "type": "scenic", "number": 3})
            parsed = result.data
            if parsed.get("code") == "200":
                results.append(TestResult("poi_lookup scenic", True))
            else:
                results.append(TestResult("poi_lookup scenic", False, f"code={parsed.get('code')}"))
        except Exception as e:
            results.append(TestResult("poi_lookup scenic", False, str(e)[:100]))

        # 7. poi_lookup - with city filter
        try:
            result = await client.call_tool("poi_lookup", {"location": "Temple", "city": "Beijing", "type": "scenic", "number": 3})
            parsed = result.data
            if parsed.get("code") == "200":
                results.append(TestResult("poi_lookup with city filter", True))
            else:
                results.append(TestResult("poi_lookup with city filter", False, f"code={parsed.get('code')}"))
        except Exception as e:
            results.append(TestResult("poi_lookup with city filter", False, str(e)[:100]))

        # 8. poi_lookup - different types
        for poi_type in ["scenic"]:
            try:
                result = await client.call_tool("poi_lookup", {"location": "Beijing", "type": poi_type, "number": 2})
                parsed = result.data
                if parsed.get("code") == "200":
                    results.append(TestResult(f"poi_lookup type={poi_type}", True))
                else:
                    results.append(TestResult(f"poi_lookup type={poi_type}", False, f"code={parsed.get('code')}"))
            except Exception as e:
                results.append(TestResult(f"poi_lookup type={poi_type}", False, str(e)[:100]))

        # 9. poi_range - with radius
        try:
            result = await client.call_tool("poi_range", {"location": coords, "type": "scenic", "radius": 5, "number": 3})
            parsed = result.data
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

        # ===== Validation Error Tests =====
        print("\n" + "=" * 60)
        print("VALIDATION ERROR TESTS")
        print("=" * 60)

        # 30. Invalid coordinates should raise ValueError
        try:
            await client.call_tool("poi_range", {"location": "invalid,coords", "type": "scenic", "radius": 5})
            results.append(TestResult("validation: invalid coords for poi_range", False, "should have raised error"))
        except Exception as e:
            if "Invalid coordinates" in str(e) or "coordinates" in str(e).lower():
                results.append(TestResult("validation: invalid coords for poi_range", True))
            else:
                results.append(TestResult("validation: invalid coords for poi_range", False, str(e)[:100]))

        # 31. Invalid radius should raise ValueError
        try:
            await client.call_tool("poi_range", {"location": coords, "type": "scenic", "radius": 100})
            results.append(TestResult("validation: invalid radius", False, "should have raised error"))
        except Exception as e:
            if "Radius" in str(e) or "radius" in str(e).lower():
                results.append(TestResult("validation: invalid radius", True))
            else:
                results.append(TestResult("validation: invalid radius", False, str(e)[:100]))

        # 32. Invalid date format should raise ValueError
        try:
            await client.call_tool("astronomy_sun", {"location": beijing_id, "date": "2026-02-01"})
            results.append(TestResult("validation: invalid date format", False, "should have raised error"))
        except Exception as e:
            if "Invalid date" in str(e) or "date" in str(e).lower():
                results.append(TestResult("validation: invalid date format", True))
            else:
                results.append(TestResult("validation: invalid date format", False, str(e)[:100]))

        # 33. Invalid days value should raise ValueError
        try:
            await client.call_tool("weather_daily", {"location": beijing_id, "days": "5d"})
            results.append(TestResult("validation: invalid days", False, "should have raised error"))
        except Exception as e:
            if "Invalid days" in str(e) or "days" in str(e).lower():
                results.append(TestResult("validation: invalid days", True))
            else:
                results.append(TestResult("validation: invalid days", False, str(e)[:100]))

        # 34. Invalid hours value should raise ValueError
        try:
            await client.call_tool("weather_hourly", {"location": beijing_id, "hours": "48h"})
            results.append(TestResult("validation: invalid hours", False, "should have raised error"))
        except Exception as e:
            if "Invalid hours" in str(e) or "hours" in str(e).lower():
                results.append(TestResult("validation: invalid hours", True))
            else:
                results.append(TestResult("validation: invalid hours", False, str(e)[:100]))

        # 35. Invalid unit should raise ValueError
        try:
            await client.call_tool("weather_now", {"location": beijing_id, "unit": "x"})
            results.append(TestResult("validation: invalid unit", False, "should have raised error"))
        except Exception as e:
            if "Invalid unit" in str(e) or "unit" in str(e).lower():
                results.append(TestResult("validation: invalid unit", True))
            else:
                results.append(TestResult("validation: invalid unit", False, str(e)[:100]))

        # 36. Invalid latitude should raise ValueError
        try:
            await client.call_tool("air_now", {"lat": 100, "lon": 116.41})
            results.append(TestResult("validation: invalid latitude", False, "should have raised error"))
        except Exception as e:
            if "Latitude" in str(e) or "latitude" in str(e).lower():
                results.append(TestResult("validation: invalid latitude", True))
            else:
                results.append(TestResult("validation: invalid latitude", False, str(e)[:100]))

        # 37. Invalid country code should raise ValueError
        try:
            await client.call_tool("city_lookup", {"location": "Tokyo", "range": "xxx"})
            results.append(TestResult("validation: invalid country code", False, "should have raised error"))
        except Exception as e:
            if "country code" in str(e).lower() or "country_code" in str(e).lower():
                results.append(TestResult("validation: invalid country code", True))
            else:
                results.append(TestResult("validation: invalid country code", False, str(e)[:100]))

        # 38. Invalid timezone should raise ValueError
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

        # 39. Invalid date (month 13) should raise ValueError
        try:
            await client.call_tool("astronomy_sun", {"location": beijing_id, "date": "20261301"})
            results.append(TestResult("validation: invalid date calendar", False, "should have raised error"))
        except Exception as e:
            if "Invalid date" in str(e) or "date" in str(e).lower():
                results.append(TestResult("validation: invalid date calendar", True))
            else:
                results.append(TestResult("validation: invalid date calendar", False, str(e)[:100]))

        # 40. Invalid altitude should raise ValueError
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

        # 41. Invalid number should raise ValueError
        try:
            await client.call_tool("city_lookup", {"location": "Beijing", "number": 100})
            results.append(TestResult("validation: invalid number", False, "should have raised error"))
        except Exception as e:
            if "Number" in str(e) or "number" in str(e).lower():
                results.append(TestResult("validation: invalid number", True))
            else:
                results.append(TestResult("validation: invalid number", False, str(e)[:100]))

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
