from dataclasses import dataclass


@dataclass
class CareerAverages:
    games_played: int = 0

    points_pg: float = 0
    rebounds_pg: float = 0
    assists_pg: float = 0
    steals_pg: float = 0
    blocks_pg: float = 0
    turnovers_pg: float = 0
    minutes_per_game: float = 0

    field_goal_pct: float = 0
    three_point_pct: float = 0
    free_throw_pct: float = 0
