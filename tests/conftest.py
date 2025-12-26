import pytest

from dotenv import load_dotenv

load_dotenv()

def pytest_addoption(parser):
    parser.addoption(
        "--query", action="store", help="Query parameter."
    )