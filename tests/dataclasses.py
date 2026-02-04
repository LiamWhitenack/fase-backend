from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from app.base import Base


@dataclass
class TestCase:
    id: str


@dataclass
class SeededTestCase(TestCase):
    seed_data: Iterable[dict[str, Any]]
