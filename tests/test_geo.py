#!/usr/bin/env python3
"""Geo tool tests for MCP Weather server."""

from conftest import TestResult


async def test_geo(client, results):
    beijing_id = "101010100"
    coords = "116.41,39.92"

    section = "GEO TOOL TESTS"
    print(f"\n{'=' * 60}")
    print(section)
    print('=' * 60)

    try:
        result = await client.call_tool("city_lookup", {"location": beijing_id, "number": 3})
        parsed = result.data
        if parsed.get("code") == "200" and len(parsed.get("location", [])) > 0:
            results.append(TestResult("city_lookup by ID", True))
        else:
            results.append(TestResult("city_lookup by ID", False, f"code={parsed.get('code')}"))
    except Exception as e:
        results.append(TestResult("city_lookup by ID", False, str(e)[:100]))

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

    try:
        result = await client.call_tool("city_lookup", {"location": coords, "number": 2})
        parsed = result.data
        if parsed.get("code") == "200":
            results.append(TestResult("city_lookup by coords", True))
        else:
            results.append(TestResult("city_lookup by coords", False, f"code={parsed.get('code')}"))
    except Exception as e:
        results.append(TestResult("city_lookup by coords", False, str(e)[:100]))

    try:
        result = await client.call_tool("city_lookup", {"location": "Beijing", "adm": "Beijing", "number": 3})
        parsed = result.data
        if parsed.get("code") == "200":
            results.append(TestResult("city_lookup with adm filter", True))
        else:
            results.append(TestResult("city_lookup with adm filter", False, f"code={parsed.get('code')}"))
    except Exception as e:
        results.append(TestResult("city_lookup with adm filter", False, str(e)[:100]))

    try:
        result = await client.call_tool("city_lookup", {"location": "Tokyo", "range": "jp", "number": 3})
        parsed = result.data
        if parsed.get("code") == "200":
            results.append(TestResult("city_lookup with range=jp", True))
        else:
            results.append(TestResult("city_lookup with range=jp", False, f"code={parsed.get('code')}"))
    except Exception as e:
        results.append(TestResult("city_lookup with range=jp", False, str(e)[:100]))

    try:
        result = await client.call_tool("poi_lookup", {"location": "Beijing", "type": "scenic", "number": 3})
        parsed = result.data
        if parsed.get("code") == "200":
            results.append(TestResult("poi_lookup scenic", True))
        else:
            results.append(TestResult("poi_lookup scenic", False, f"code={parsed.get('code')}"))
    except Exception as e:
        results.append(TestResult("poi_lookup scenic", False, str(e)[:100]))

    try:
        result = await client.call_tool("poi_lookup", {"location": "Temple", "city": "Beijing", "type": "scenic", "number": 3})
        parsed = result.data
        if parsed.get("code") == "200":
            results.append(TestResult("poi_lookup with city filter", True))
        else:
            results.append(TestResult("poi_lookup with city filter", False, f"code={parsed.get('code')}"))
    except Exception as e:
        results.append(TestResult("poi_lookup with city filter", False, str(e)[:100]))

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

    try:
        result = await client.call_tool("poi_range", {"location": coords, "type": "scenic", "radius": 5, "number": 3})
        parsed = result.data
        if parsed.get("code") == "200":
            results.append(TestResult("poi_range with radius=5", True))
        else:
            results.append(TestResult("poi_range with radius=5", False, f"code={parsed.get('code')}"))
    except Exception as e:
        results.append(TestResult("poi_range with radius=5", False, str(e)[:100]))