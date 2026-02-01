from app.data.connection import Player
from tests.data.player_contract_data import THOMPSON_CONTRACT_DATA
from tests.players.dataclasses import GetSalaryDataTestCase

GET_SALARY_TEST_DATA_TEST_CASES = [
    GetSalaryDataTestCase(
        name="Thompsons",
        seed_data=THOMPSON_CONTRACT_DATA,
    ),
]
