from __future__ import annotations

# test_utils.py
import inspect
from collections.abc import Callable, Generator, Iterable
from dataclasses import dataclass
from functools import wraps
from typing import Any, NoReturn

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import Session
from starlette.testclient import TestClient

from app.base import Base
from tests.connection import get_test_session
from tests.dataclasses import TestCase


@pytest.fixture
def client() -> TestClient:  # @IgnoreException
    pytest.skip("API client not implemented yet")


@pytest.fixture
def session() -> Generator[Session, None, None]:  # @IgnoreException
    """Provide a clean session for each test."""
    with get_test_session() as session:
        # yield the session for the test
        yield session


def parametrize(cases: Iterable[TestCase] = ()) -> Callable[..., Any]:
    cases = list(cases)

    def decorator(func: Any) -> Any:
        sig = inspect.signature(func)
        wants_case = "case" in sig.parameters

        # CASE 1: With cases → use pytest.mark.parametrize
        if cases and wants_case:
            return pytest.mark.parametrize("case", cases, ids=[c.id for c in cases])(
                func
            )

        # CASE 2: No cases → return function as-is
        return func

    return decorator
