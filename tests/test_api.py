#!/usr/bin/env python3
"""
Test runner for MCP Weather server.
Orchestrates all test modules and prints summary.

Run: uv run python tests/test_api.py
"""

import asyncio
import sys
import os
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

from conftest import TestResult
import test_geo
import test_weather
import test_minutely
import test_validation
import test_coords


async def run_tests():
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    transport = PythonStdioTransport(os.path.join(script_dir, "server.py"), args=["--stdio"], cwd=script_dir)
    async with Client(transport) as client:
        results = []

        await test_geo.test_geo(client, results)
        await test_weather.test_weather(client, results)
        await test_minutely.test_minutely(client, results)
        await test_minutely.test_air(client, results)
        await test_minutely.test_astronomy(client, results)
        await test_validation.test_validation(client, results)
        await test_coords.test_coordinate_rounding(client, results)

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