"""Command for running all Testcontainers tests from the project checkout."""

from pathlib import Path
from sys import argv

from pytest import main as pytest_main


def main() -> int:
    """Run the Testcontainers suite, forward pytest arguments, and return its exit code."""
    test_directory = Path(__file__).resolve().parents[2] / "tests" / "testcontainers"
    return int(pytest_main([str(test_directory), *argv[1:]]))
