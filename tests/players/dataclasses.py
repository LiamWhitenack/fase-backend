from collections.abc import Iterable
from dataclasses import dataclass

from tests.dataclasses import SeededTestCase


@dataclass
class GetSalaryYearsTestCase(SeededTestCase):
    name: str
    expected_seasons: Iterable[int]


@dataclass
class GetAggregateSalaryTestCase(SeededTestCase):
    name: str
    expected_aggregate_salary: int


@dataclass
class GetRelativeEarningsTestCase(SeededTestCase):
    name: str
    expected_relative_earnings: float
