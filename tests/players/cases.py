from app.data.connection import Player
from tests.data.thompson_contract_data import THOMPSON_CONTRACT_DATA
from tests.data.williams_contract_data import WILLIAMS_CONTRACT_DATA
from tests.players.dataclasses import GetAggregateSalaryTestCase, GetSalaryYearsTestCase

GET_SALARY_YEARS_TEST_CASES = [
    GetSalaryYearsTestCase(
        id="Active Veteran",
        name="Klay Thompson",
        expected_seasons=range(2012, 2028),
        seed_data=THOMPSON_CONTRACT_DATA,
    ),
    GetSalaryYearsTestCase(
        id="Potential Superstar",
        name="Patrick Williams",
        expected_seasons=range(2021, 2031),
        seed_data=WILLIAMS_CONTRACT_DATA,
    ),
]
GET_AGGREGATE_SALARY_TEST_CASES = [
    GetAggregateSalaryTestCase(
        id="Active Veteran",
        name="Klay Thompson",
        expected_aggregate_salary=318_625_530,
        seed_data=THOMPSON_CONTRACT_DATA,
    ),
    GetAggregateSalaryTestCase(
        id="Potential Superstar",
        name="Patrick Williams",
        expected_aggregate_salary=149_101_641,
        seed_data=WILLIAMS_CONTRACT_DATA,
    ),
]
