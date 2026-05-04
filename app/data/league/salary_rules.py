from dataclasses import dataclass


@dataclass
class MinSalaries:
    two_way = 0.0041
    year_0 = 0.0082
    year_1 = 0.0132
    year_2 = 0.0148
    year_3 = 0.0154
    year_4 = 0.0159
    year_5 = 0.0173
    year_6 = 0.0186
    year_7 = 0.0199
    year_8 = 0.0213
    year_9 = 0.0214

    otherwise = 0.0235

    def __post_init__(self) -> None:
        self.years = [
            self.year_0,
            self.year_1,
            self.year_2,
            self.year_3,
            self.year_4,
            self.year_5,
            self.year_6,
            self.year_7,
            self.year_8,
            self.year_9,
        ]

    def eligibility(self, num_seasons: int) -> float:
        if num_seasons > 9:
            return self.otherwise
        return self.years[num_seasons]


@dataclass
class MaxSalaries:
    year_lt_7 = 0.25
    year_lt_10 = 0.3
    otherwise = 0.35
    supermax = 0.35  # only in seasons after 2016-17 for players who have not changed teams and just made an all-nba team or made 2 of the last 3

    def eligibility(
        self, season_id: int, num_seasons: int, teams: int, award_years: set[int]
    ) -> float:
        if num_seasons < 10:
            if self.supermax_eligible(season_id, teams, award_years):
                return self.supermax
            elif num_seasons >= 7:
                return self.year_lt_10
            else:
                return self.year_lt_7
        else:
            return self.otherwise

    def supermax_eligible(
        self, season_id: int, teams: int, award_years: set[int]
    ) -> bool:
        return (
            season_id >= 2017
            and teams == 1
            and (
                season_id in award_years
                or {season_id - 1, season_id - 2}.issubset(award_years)
            )
        )


MAX_SALARIES = MaxSalaries()
MIN_SALARIES = MinSalaries()
