# test_utils.py
import inspect
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import wraps
from typing import Any

import pytest
from sqlalchemy.orm.session import Session
from starlette.testclient import TestClient

from app.base import Base
from tests.connection import get_test_session
from tests.dataclasses import TestCase


@pytest.fixture
def client() -> TestClient:
    """TODO: Update when ready to use API"""
    return None  # type: ignore


@pytest.fixture
def session() -> Session:
    with get_test_session() as session:
        return session


def parametrize(cases: Iterable[TestCase] = ()) -> Callable[..., Any]:
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
