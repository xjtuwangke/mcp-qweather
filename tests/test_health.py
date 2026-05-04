#!/usr/bin/env python3
"""
Health check test - runs independently since it requires HTTP server.
Run: uv run python tests/test_health.py
"""

import asyncio
import sys
import os
import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conftest import TestResult


async def run_health_test():
    results = []

    print("=" * 60)
    print("HEALTH CHECK TEST")
    print("=" * 60)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/.well-known/health", timeout=10.0)
            if response.status_code == 200 and response.json().get("status") == "ok":
                results.append(TestResult("health check GET /.well-known/health", True))
                print("\n[PASS] health check GET /.well-known/health")
            else:
                results.append(TestResult("health check GET /.well-known/health", False, f"status={response.status_code}"))
                print(f"\n[FAIL] health check GET /.well-known/health - status={response.status_code}")
    except Exception as e:
        results.append(TestResult("health check GET /.well-known/health", False, str(e)[:100]))
        print(f"\n[FAIL] health check GET /.well-known/health - {str(e)[:100]}")

    print("\n" + "=" * 60)
    if results[0].passed:
        print("HEALTH CHECK PASSED!")
    else:
        print("HEALTH CHECK FAILED!")
    print("=" * 60)

    return results[0].passed


if __name__ == "__main__":
    success = asyncio.run(run_health_test())
    sys.exit(0 if success else 1)