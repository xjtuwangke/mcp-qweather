#!/usr/bin/env python3
"""Weather tool tests for MCP Weather server."""

from conftest import TestResult


async def test_weather(client, results):
    beijing_id = "101010100"
    coords = "116.41,39.92"

    section = "WEATHER API TOOL TESTS"
    print(f"\n{'=' * 60}")
    print(section)
    print('=' * 60)

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

    try:
        result = await client.call_tool("weather_now", {"location": coords})
        if result.data.get("code") == "200":
            results.append(TestResult("weather_now by coords", True))
        else:
            results.append(TestResult("weather_now by coords", False, f"code={result.data.get('code')}"))
    except Exception as e:
        results.append(TestResult("weather_now by coords", False, str(e)[:100]))

    for unit in ["m", "i"]:
        try:
            result = await client.call_tool("weather_now", {"location": beijing_id, "unit": unit})
            if result.data.get("code") == "200":
                results.append(TestResult(f"weather_now unit={unit}", True))
            else:
                results.append(TestResult(f"weather_now unit={unit}", False, f"code={result.data.get('code')}"))
        except Exception as e:
            results.append(TestResult(f"weather_now unit={unit}", False, str(e)[:100]))

    for days in ["3d", "7d", "10d", "15d", "30d"]:
        try:
            result = await client.call_tool("weather_daily", {"location": beijing_id, "days": days})
            if result.data.get("code") == "200":
                results.append(TestResult(f"weather_daily days={days}", True))
            else:
                results.append(TestResult(f"weather_daily days={days}", False, f"code={result.data.get('code')}"))
        except Exception as e:
            results.append(TestResult(f"weather_daily days={days}", False, str(e)[:100]))

    for lang in ["en", "zh"]:
        try:
            result = await client.call_tool("weather_daily", {"location": beijing_id, "days": "7d", "lang": lang})
            if result.data.get("code") == "200":
                results.append(TestResult(f"weather_daily lang={lang}", True))
            else:
                results.append(TestResult(f"weather_daily lang={lang}", False, f"code={result.data.get('code')}"))
        except Exception as e:
            results.append(TestResult(f"weather_daily lang={lang}", False, str(e)[:100]))

    for hours in ["24h", "72h", "168h"]:
        try:
            result = await client.call_tool("weather_hourly", {"location": beijing_id, "hours": hours})
            if result.data.get("code") == "200":
                results.append(TestResult(f"weather_hourly hours={hours}", True))
            else:
                results.append(TestResult(f"weather_hourly hours={hours}", False, f"code={result.data.get('code')}"))
        except Exception as e:
            results.append(TestResult(f"weather_hourly hours={hours}", False, str(e)[:100]))

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

    for unit in ["m", "i"]:
        try:
            result = await client.call_tool("grid_weather_now", {"location": coords, "unit": unit})
            if result.data.get("code") == "200":
                results.append(TestResult(f"grid_weather_now unit={unit}", True))
            else:
                results.append(TestResult(f"grid_weather_now unit={unit}", False, f"code={result.data.get('code')}"))
        except Exception as e:
            results.append(TestResult(f"grid_weather_now unit={unit}", False, str(e)[:100]))

    for days in ["3d", "7d"]:
        try:
            result = await client.call_tool("grid_weather_daily", {"location": coords, "days": days})
            if result.data.get("code") == "200":
                results.append(TestResult(f"grid_weather_daily days={days}", True))
            else:
                results.append(TestResult(f"grid_weather_daily days={days}", False, f"code={result.data.get('code')}"))
        except Exception as e:
            results.append(TestResult(f"grid_weather_daily days={days}", False, str(e)[:100]))

    for unit in ["m", "i"]:
        try:
            result = await client.call_tool("grid_weather_daily", {"location": coords, "days": "3d", "unit": unit})
            if result.data.get("code") == "200":
                results.append(TestResult(f"grid_weather_daily unit={unit}", True))
            else:
                results.append(TestResult(f"grid_weather_daily unit={unit}", False, f"code={result.data.get('code')}"))
        except Exception as e:
            results.append(TestResult(f"grid_weather_daily unit={unit}", False, str(e)[:100]))

    for hours in ["24h", "72h"]:
        try:
            result = await client.call_tool("grid_weather_hourly", {"location": coords, "hours": hours})
            if result.data.get("code") == "200":
                results.append(TestResult(f"grid_weather_hourly hours={hours}", True))
            else:
                results.append(TestResult(f"grid_weather_hourly hours={hours}", False, f"code={result.data.get('code')}"))
        except Exception as e:
            results.append(TestResult(f"grid_weather_hourly hours={hours}", False, str(e)[:100]))

    for unit in ["m", "i"]:
        try:
            result = await client.call_tool("grid_weather_hourly", {"location": coords, "hours": "24h", "unit": unit})
            if result.data.get("code") == "200":
                results.append(TestResult(f"grid_weather_hourly unit={unit}", True))
            else:
                results.append(TestResult(f"grid_weather_hourly unit={unit}", False, f"code={result.data.get('code')}"))
        except Exception as e:
            results.append(TestResult(f"grid_weather_hourly unit={unit}", False, str(e)[:100]))