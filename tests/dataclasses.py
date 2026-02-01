from collections.abc import Iterable
from dataclasses import dataclass

from app.base import Base


@dataclass
class TestCase:
    name: str


@dataclass
class SeededTestCase(TestCase):
    seed_data: Iterable[Base]
