# test_utils.py
import inspect
from collections.abc import Iterable
from dataclasses import dataclass
from functools import wraps

import pytest
from sqlalchemy.orm.session import Session
from starlette.testclient import TestClient

from tests.connection import get_test_session


@pytest.fixture
def client() -> TestClient:
    """TODO: Update when ready to use API"""
    return None  # type: ignore


@pytest.fixture
def session() -> Session:
    with get_test_session() as session:
        return session


@dataclass
class TestCase:
    name: str


def parametrize(cases: Iterable[TestCase] = ()):
    cases = list(cases)

    def decorator(func):
        sig = inspect.signature(func)
        wants_case = "case" in sig.parameters

        # CASE 1: With cases → use pytest.mark.parametrize
        if cases and wants_case:
            return pytest.mark.parametrize("case", cases, ids=[c.name for c in cases])(
                func
            )

        # CASE 2: No cases → return function as-is
        return func

    return decorator
