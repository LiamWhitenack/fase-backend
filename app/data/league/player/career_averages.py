from dataclasses import dataclass


@dataclass
class CareerStats:
    games_played: int = 0

    points_pg: float = 0
    rebounds_pg: float = 0
    assists_pg: float = 0
    steals_pg: float = 0
    blocks_pg: float = 0
    turnovers_pg: float = 0
    minutes_per_game: float = 0

    three_point_made: int = 0
    three_point_attempted: int = 0

    free_throw_made: int = 0
    free_throw_attempted: int = 0

    field_goal_pct: float = 0
    three_point_pct: float = 0
    free_throw_pct: float = 0

    percentile: float = 0.5

    def to_scalar(self) -> dict[str, int | float]:
        return {
            "games_played": self.games_played,
            "points_pg": self.points_pg,
            "rebounds_pg": self.rebounds_pg,
            "assists_pg": self.assists_pg,
            "steals_pg": self.steals_pg,
            "blocks_pg": self.blocks_pg,
            "turnovers_pg": self.turnovers_pg,
            "minutes_per_game": self.minutes_per_game,
            "field_goal_pct": self.field_goal_pct,
            "three_point_pct": self.three_point_pct,
            "free_throw_pct": self.free_throw_pct,
        }
