from dataclasses import dataclass

from app.custom_types import MLSafe


@dataclass
class SeasonalMLPayload:
    # ---- identifiers ----
    player_id: int
    team_id: int
    season_id: int

    # ---- basic context ----
    age: float
    games_played: int
    minutes_per_game: float

    # ---- ratings ----
    offensive_rating: float
    defensive_rating: float
    net_rating: float
    estimated_offensive_rating: float
    estimated_defensive_rating: float
    estimated_net_rating: float

    # ---- percentages ----
    assist_percentage: float
    assist_to_turnover: float
    assist_ratio: float
    offensive_rebound_pct: float
    defensive_rebound_pct: float
    rebound_pct: float
    turnover_pct: float
    effective_fg_pct: float
    true_shooting_pct: float
    usage_pct: float

    # ---- pace & impact ----
    pace: float
    pace_per_40: float
    estimated_pace: float
    possessions: int
    pie: float

    # ---- shooting volume ----
    field_goals_made: int
    field_goals_attempted: int
    field_goal_pct: float
    field_goals_made_pg: float
    field_goals_attempted_pg: float

    # ---- scoring ----
    points: int
    points_pg: float

    # ---- rebounds ----
    rebounds: int
    rebounds_pg: float
    offensive_rebounds: int
    defensive_rebounds: int

    # ---- playmaking ----
    assists: int
    assists_pg: float
    turnovers: int
    turnovers_pg: float

    # ---- defense ----
    steals: int
    steals_pg: float
    blocks: int
    blocks_pg: float

    # ---- fouls ----
    personal_fouls: int
    personal_fouls_pg: float

    # ---- 3PT shooting ----
    three_pointers_made: int
    three_pointers_attempted: int
    three_point_pct: float
    three_pointers_made_pg: float
    three_pointers_attempted_pg: float

    # ---- 2PT shooting ----
    two_pointers_made: int
    two_pointers_attempted: int
    two_point_pct: float
    two_pointers_made_pg: float
    two_pointers_attempted_pg: float

    # ---- free throws ----
    free_throws_made: int
    free_throws_attempted: int
    free_throw_pct: float
    free_throws_made_pg: float
    free_throws_attempted_pg: float

    # ---- plus/minus & milestones ----
    plus_minus: int
    plus_minus_pg: float
    double_doubles: int
    triple_doubles: int

    # ---- ML-friendly scoring context ----
    pts_off_tov: int
    pts_2nd_chance: int
    pts_fb: int
    pts_paint: int

    opp_pts_off_tov: int
    opp_pts_2nd_chance: int
    opp_pts_fb: int
    opp_pts_paint: int

    # ---- % of team contributions ----
    pct_fgm: float
    pct_fga: float
    pct_fg3m: float
    pct_fg3a: float
    pct_ftm: float
    pct_fta: float
    pct_oreb: float
    pct_dreb: float
    pct_reb: float
    pct_ast: float
    pct_tov: float
    pct_stl: float
    pct_blk: float
    pct_blka: float
    pct_pf: float
    pct_pfd: float
    pct_pts: float

    def no_colinearity(self) -> dict[str, MLSafe]:
        return {
            "games_played": self.games_played,
            "minutes_per_game": self.minutes_per_game,
            "points_pg": self.points_pg,
            "rebounds_pg": self.rebounds_pg,
            "assists_pg": self.assists_pg,
            "steals_pg": self.steals_pg,
            "blocks_pg": self.blocks_pg,
            "turnovers_pg": self.turnovers_pg,
            "personal_fouls_pg": self.personal_fouls_pg,
            "field_goals_made_pg": self.field_goals_made_pg,
            "field_goals_attempted_pg": self.field_goals_attempted_pg,
            "three_pointers_made_pg": self.three_pointers_made_pg,
            "three_pointers_attempted_pg": self.three_pointers_attempted_pg,
            "two_pointers_made_pg": self.two_pointers_made_pg,
            "two_pointers_attempted_pg": self.two_pointers_attempted_pg,
            "free_throws_made_pg": self.free_throws_made_pg,
            "free_throws_attempted_pg": self.free_throws_attempted_pg,
            "field_goal_pct": self.field_goal_pct,
            "three_point_pct": self.three_point_pct,
            "two_point_pct": self.two_point_pct,
            "free_throw_pct": self.free_throw_pct,
            "assist_percentage": self.assist_percentage,
            "assist_to_turnover": self.assist_to_turnover,
            "assist_ratio": self.assist_ratio,
            "offensive_rebound_pct": self.offensive_rebound_pct,
            "defensive_rebound_pct": self.defensive_rebound_pct,
            "rebound_pct": self.rebound_pct,
            "turnover_pct": self.turnover_pct,
            "usage_pct": self.usage_pct,
            "offensive_rating": self.offensive_rating,
            "defensive_rating": self.defensive_rating,
            "net_rating": self.net_rating,
            "estimated_offensive_rating": self.estimated_offensive_rating,
            "estimated_defensive_rating": self.estimated_defensive_rating,
            "estimated_net_rating": self.estimated_net_rating,
            "estimated_pace": self.estimated_pace,
            "possessions": self.possessions,
            "pts_off_tov": self.pts_off_tov,
            "pts_fb": self.pts_fb,
            "pts_paint": self.pts_paint,
            "opp_pts_off_tov": self.opp_pts_off_tov,
            "opp_pts_fb": self.opp_pts_fb,
            "opp_pts_paint": self.opp_pts_paint,
            "plus_minus_pg": self.plus_minus_pg,
        }
