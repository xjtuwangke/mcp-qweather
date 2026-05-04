#!/usr/bin/env python3
"""
Test configuration and shared fixtures for MCP Weather tests.
"""

from dataclasses import dataclass


@dataclass
class TestResult:
    name: str
    passed: bool
    message: str = ""

    def __str__(self):
        status = "PASS" if self.passed else "FAIL"
        msg = f"[{status}] {self.name}"
        if self.message:
            msg += f" - {self.message}"
        return msg