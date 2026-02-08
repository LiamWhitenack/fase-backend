from typing import Any

from sqlalchemy import Float, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base
from app.custom_types import MLSafe
from app.data.league.player.core import Player
from app.data.league.season import Season
from app.data.league.team.core import Team
from app.modeling.payload_types.seasonal import SeasonalMLPayload


class PlayerSeason(Base):
    __tablename__ = "player_seasons"

    # ---- identifiers ----
    id: Mapped[int] = mapped_column(primary_key=True)

    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)

    season_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("seasons.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # ---- basic context ----
    age: Mapped[float | None] = mapped_column(Float)
    games_played: Mapped[int] = mapped_column(Integer)
    wins: Mapped[int] = mapped_column(Integer)
    losses: Mapped[int] = mapped_column(Integer)
    win_pct: Mapped[float] = mapped_column(Float)
    minutes_per_game: Mapped[float] = mapped_column(Float)

    # ---- ratings ----
    offensive_rating: Mapped[float] = mapped_column(Float)
    defensive_rating: Mapped[float] = mapped_column(Float)
    net_rating: Mapped[float] = mapped_column(Float)

    estimated_offensive_rating: Mapped[float | None] = mapped_column(Float)
    estimated_defensive_rating: Mapped[float | None] = mapped_column(Float)
    estimated_net_rating: Mapped[float | None] = mapped_column(Float)

    # ---- percentages ----
    assist_percentage: Mapped[float] = mapped_column(Float)
    assist_to_turnover: Mapped[float] = mapped_column(Float)
    assist_ratio: Mapped[float] = mapped_column(Float)

    offensive_rebound_pct: Mapped[float] = mapped_column(Float)
    defensive_rebound_pct: Mapped[float] = mapped_column(Float)
    rebound_pct: Mapped[float] = mapped_column(Float)

    turnover_pct: Mapped[float] = mapped_column(Float)
    effective_fg_pct: Mapped[float] = mapped_column(Float)
    true_shooting_pct: Mapped[float] = mapped_column(Float)
    usage_pct: Mapped[float] = mapped_column(Float)

    # ---- pace & impact ----
    pace: Mapped[float] = mapped_column(Float)
    pace_per_40: Mapped[float] = mapped_column(Float)
    estimated_pace: Mapped[float | None] = mapped_column(Float)

    possessions: Mapped[int] = mapped_column(Integer)
    pie: Mapped[float] = mapped_column(Float)

    # ---- shooting volume ----
    field_goals_made: Mapped[int] = mapped_column(Integer)
    field_goals_attempted: Mapped[int] = mapped_column(Integer)
    field_goal_pct: Mapped[float] = mapped_column(Float)

    field_goals_made_pg: Mapped[float] = mapped_column(Float)
    field_goals_attempted_pg: Mapped[float] = mapped_column(Float)

    # ---- scoring ----
    points: Mapped[int] = mapped_column(Integer)
    points_pg: Mapped[float] = mapped_column(Float)

    # ---- rebounds ----
    rebounds: Mapped[int] = mapped_column(Integer)
    rebounds_pg: Mapped[float] = mapped_column(Float)

    offensive_rebounds: Mapped[int] = mapped_column(Integer)
    defensive_rebounds: Mapped[int] = mapped_column(Integer)

    # ---- playmaking ----
    assists: Mapped[int] = mapped_column(Integer)
    assists_pg: Mapped[float] = mapped_column(Float)

    turnovers: Mapped[int] = mapped_column(Integer)
    turnovers_pg: Mapped[float] = mapped_column(Float)

    # ---- defense ----
    steals: Mapped[int] = mapped_column(Integer)
    steals_pg: Mapped[float] = mapped_column(Float)

    blocks: Mapped[int] = mapped_column(Integer)
    blocks_pg: Mapped[float] = mapped_column(Float)

    # ---- fouls ----
    personal_fouls: Mapped[int] = mapped_column(Integer)
    personal_fouls_pg: Mapped[float] = mapped_column(Float)

    # ---- 3PT shooting ----
    three_pointers_made: Mapped[int] = mapped_column(Integer)
    three_pointers_attempted: Mapped[int] = mapped_column(Integer)
    three_point_pct: Mapped[float] = mapped_column(Float)

    three_pointers_made_pg: Mapped[float] = mapped_column(Float)
    three_pointers_attempted_pg: Mapped[float] = mapped_column(Float)

    # ---- 2PT shooting ----
    two_pointers_made: Mapped[int] = mapped_column(Integer)
    two_pointers_attempted: Mapped[int] = mapped_column(Integer)
    two_point_pct: Mapped[float] = mapped_column(Float)

    two_pointers_made_pg: Mapped[float] = mapped_column(Float)
    two_pointers_attempted_pg: Mapped[float] = mapped_column(Float)

    # ---- free throws ----
    free_throws_made: Mapped[int] = mapped_column(Integer)
    free_throws_attempted: Mapped[int] = mapped_column(Integer)
    free_throw_pct: Mapped[float] = mapped_column(Float)

    free_throws_made_pg: Mapped[float] = mapped_column(Float)
    free_throws_attempted_pg: Mapped[float] = mapped_column(Float)

    # ---- plus/minus & milestones ----
    plus_minus: Mapped[int] = mapped_column(Integer)
    plus_minus_pg: Mapped[float] = mapped_column(Float)

    double_doubles: Mapped[int] = mapped_column(Integer)
    triple_doubles: Mapped[int] = mapped_column(Integer)

    # ---- ML-friendly scoring context ----
    pts_off_tov: Mapped[int] = mapped_column(Integer)
    pts_2nd_chance: Mapped[int] = mapped_column(Integer)
    pts_fb: Mapped[int] = mapped_column(Integer)
    pts_paint: Mapped[int] = mapped_column(Integer)

    opp_pts_off_tov: Mapped[int] = mapped_column(Integer)
    opp_pts_2nd_chance: Mapped[int] = mapped_column(Integer)
    opp_pts_fb: Mapped[int] = mapped_column(Integer)
    opp_pts_paint: Mapped[int] = mapped_column(Integer)

    # ---- % of team contributions ----
    pct_fgm: Mapped[float] = mapped_column(Float)
    pct_fga: Mapped[float] = mapped_column(Float)
    pct_fg3m: Mapped[float] = mapped_column(Float)
    pct_fg3a: Mapped[float] = mapped_column(Float)
    pct_ftm: Mapped[float] = mapped_column(Float)
    pct_fta: Mapped[float] = mapped_column(Float)

    pct_oreb: Mapped[float] = mapped_column(Float)
    pct_dreb: Mapped[float] = mapped_column(Float)
    pct_reb: Mapped[float] = mapped_column(Float)
    pct_ast: Mapped[float] = mapped_column(Float)
    pct_tov: Mapped[float] = mapped_column(Float)
    pct_stl: Mapped[float] = mapped_column(Float)
    pct_blk: Mapped[float] = mapped_column(Float)
    pct_blka: Mapped[float] = mapped_column(Float)
    pct_pf: Mapped[float] = mapped_column(Float)
    pct_pfd: Mapped[float] = mapped_column(Float)
    pct_pts: Mapped[float] = mapped_column(Float)

    # ---- relationships ----
    season: Mapped[Season] = relationship("Season")
    player: Mapped[Player] = relationship(back_populates="seasons")
    team: Mapped[Team] = relationship(back_populates="player_seasons")

    __table_args__ = (
        Index(
            "ix_player_season_unique",
            "player_id",
            "team_id",
            "season_id",
            unique=True,
        ),
    )

    @classmethod
    def from_nba_api_json(
        cls, player: int, team: int, season: int, data: dict[str, Any]
    ) -> PlayerSeason:
        two_point_makes = data["FGM"] - data["FG3M"]
        two_point_attempts = data["FGA"] - data["FG3A"]
        return cls(
            # ---- identifiers ----
            player_id=player,
            team_id=team,
            season_id=season,
            # ---- basic context ----
            age=data["AGE"],
            games_played=data["GP"],
            wins=data["W"],
            losses=data["L"],
            win_pct=data["W_PCT"],
            minutes_per_game=data["MIN"],
            # ---- shooting volume ----
            field_goals_made=data["FGM"],
            field_goals_attempted=data["FGA"],
            field_goal_pct=data["FG_PCT"],
            field_goals_made_pg=data["FGM_PG"],
            field_goals_attempted_pg=data["FGA_PG"],
            # ---- 3PT ----
            three_pointers_made=data["FG3M"],
            three_pointers_attempted=data["FG3A"],
            three_point_pct=data["FG3_PCT"],
            three_pointers_made_pg=data["FG3M"] / data["GP"],
            three_pointers_attempted_pg=data["FG3A"] / data["GP"],
            # ---- 2PT ----
            two_pointers_made=two_point_makes,
            two_pointers_attempted=two_point_attempts,
            two_point_pct=(two_point_makes / two_point_attempts)
            if two_point_attempts
            else 0,
            two_pointers_made_pg=two_point_makes / data["GP"],
            two_pointers_attempted_pg=two_point_attempts / data["GP"],
            # ---- free throws ----
            free_throws_made=data["FTM"],
            free_throws_attempted=data["FTA"],
            free_throw_pct=data["FT_PCT"],
            free_throws_made_pg=data["FTM"] / data["GP"],
            free_throws_attempted_pg=data["FTA"] / data["GP"],
            # ---- scoring ----
            points=data["PTS"],
            points_pg=data["PTS"] / data["GP"],
            # ---- rebounds ----
            rebounds=data["REB"],
            rebounds_pg=data["REB"] / data["GP"],
            offensive_rebounds=data["OREB"],
            defensive_rebounds=data["DREB"],
            # ---- playmaking ----
            assists=data["AST"],
            assists_pg=data["AST"] / data["GP"],
            turnovers=data["TOV"],
            turnovers_pg=data["TOV"] / data["GP"],
            # ---- defense ----
            steals=data["STL"],
            steals_pg=data["STL"] / data["GP"],
            blocks=data["BLK"],
            blocks_pg=data["BLK"] / data["GP"],
            # ---- fouls ----
            personal_fouls=data["PF"],
            personal_fouls_pg=data["PF"] / data["GP"],
            # ---- plus/minus & milestones ----
            plus_minus=data["PLUS_MINUS"],
            plus_minus_pg=data["PLUS_MINUS"] / data["GP"],
            double_doubles=data["DD2"],
            triple_doubles=data["TD3"],
            # ---- ratings ----
            offensive_rating=data["OFF_RATING"],
            defensive_rating=data["DEF_RATING"],
            net_rating=data["NET_RATING"],
            estimated_offensive_rating=data["E_OFF_RATING"],
            estimated_defensive_rating=data["E_DEF_RATING"],
            estimated_net_rating=data["E_NET_RATING"],
            # ---- percentages ----
            assist_percentage=data["AST_PCT"],
            assist_to_turnover=data["AST_TO"],
            assist_ratio=data["AST_RATIO"],
            offensive_rebound_pct=data["OREB_PCT"],
            defensive_rebound_pct=data["DREB_PCT"],
            rebound_pct=data["REB_PCT"],
            turnover_pct=data["TM_TOV_PCT"],
            effective_fg_pct=data["EFG_PCT"],
            true_shooting_pct=data["TS_PCT"],
            usage_pct=data["USG_PCT"],
            # ---- pace & impact ----
            pace=data["PACE"],
            pace_per_40=data["PACE_PER40"],
            estimated_pace=data["E_PACE"],
            possessions=data["POSS"],
            pie=data["PIE"],
            # ---- ML-friendly scoring context ----
            pts_off_tov=data["PTS_OFF_TOV"],
            pts_2nd_chance=data["PTS_2ND_CHANCE"],
            pts_fb=data["PTS_FB"],
            pts_paint=data["PTS_PAINT"],
            opp_pts_off_tov=data["OPP_PTS_OFF_TOV"],
            opp_pts_2nd_chance=data["OPP_PTS_2ND_CHANCE"],
            opp_pts_fb=data["OPP_PTS_FB"],
            opp_pts_paint=data["OPP_PTS_PAINT"],
            # ---- % of team contributions ----
            pct_fgm=data["PCT_FGM"],
            pct_fga=data["PCT_FGA"],
            pct_fg3m=data["PCT_FG3M"],
            pct_fg3a=data["PCT_FG3A"],
            pct_ftm=data["PCT_FTM"],
            pct_fta=data["PCT_FTA"],
            pct_oreb=data["PCT_OREB"],
            pct_dreb=data["PCT_DREB"],
            pct_reb=data["PCT_REB"],
            pct_ast=data["PCT_AST"],
            pct_tov=data["PCT_TOV"],
            pct_stl=data["PCT_STL"],
            pct_blk=data["PCT_BLK"],
            pct_blka=data["PCT_BLKA"],
            pct_pf=data["PCT_PF"],
            pct_pfd=data["PCT_PFD"],
            pct_pts=data["PCT_PTS"],
        )

    # ---- helper method to return ML payload ----
    def ml_data(self, player_season: PlayerSeason) -> SeasonalMLPayload:
        res: dict[str, MLSafe | None] = {
            # identifiers
            "player_id": player_season.player_id,
            "team_id": player_season.team_id,
            "season_id": player_season.season_id,
            # basic context
            "age": player_season.age,
            "games_played": player_season.games_played,
            "minutes_per_game": player_season.minutes_per_game,
            # ratings
            "offensive_rating": player_season.offensive_rating,
            "defensive_rating": player_season.defensive_rating,
            "net_rating": player_season.net_rating,
            "estimated_offensive_rating": player_season.estimated_offensive_rating,
            "estimated_defensive_rating": player_season.estimated_defensive_rating,
            "estimated_net_rating": player_season.estimated_net_rating,
            # percentages
            "assist_percentage": player_season.assist_percentage,
            "assist_to_turnover": player_season.assist_to_turnover,
            "assist_ratio": player_season.assist_ratio,
            "offensive_rebound_pct": player_season.offensive_rebound_pct,
            "defensive_rebound_pct": player_season.defensive_rebound_pct,
            "rebound_pct": player_season.rebound_pct,
            "turnover_pct": player_season.turnover_pct,
            "effective_fg_pct": player_season.effective_fg_pct,
            "true_shooting_pct": player_season.true_shooting_pct,
            "usage_pct": player_season.usage_pct,
            # pace & impact
            "pace": player_season.pace,
            "pace_per_40": player_season.pace_per_40,
            "estimated_pace": player_season.estimated_pace,
            "possessions": player_season.possessions,
            "pie": player_season.pie,
            # shooting volume
            "field_goals_made": player_season.field_goals_made,
            "field_goals_attempted": player_season.field_goals_attempted,
            "field_goal_pct": player_season.field_goal_pct,
            "field_goals_made_pg": player_season.field_goals_made_pg,
            "field_goals_attempted_pg": player_season.field_goals_attempted_pg,
            # scoring
            "points": player_season.points,
            "points_pg": player_season.points_pg,
            # rebounds
            "rebounds": player_season.rebounds,
            "rebounds_pg": player_season.rebounds_pg,
            "offensive_rebounds": player_season.offensive_rebounds,
            "defensive_rebounds": player_season.defensive_rebounds,
            # playmaking
            "assists": player_season.assists,
            "assists_pg": player_season.assists_pg,
            "turnovers": player_season.turnovers,
            "turnovers_pg": player_season.turnovers_pg,
            # defense
            "steals": player_season.steals,
            "steals_pg": player_season.steals_pg,
            "blocks": player_season.blocks,
            "blocks_pg": player_season.blocks_pg,
            # fouls
            "personal_fouls": player_season.personal_fouls,
            "personal_fouls_pg": player_season.personal_fouls_pg,
            # 3PT shooting
            "three_pointers_made": player_season.three_pointers_made,
            "three_pointers_attempted": player_season.three_pointers_attempted,
            "three_point_pct": player_season.three_point_pct,
            "three_pointers_made_pg": player_season.three_pointers_made_pg,
            "three_pointers_attempted_pg": player_season.three_pointers_attempted_pg,
            # 2PT shooting
            "two_pointers_made": player_season.two_pointers_made,
            "two_pointers_attempted": player_season.two_pointers_attempted,
            "two_point_pct": player_season.two_point_pct,
            "two_pointers_made_pg": player_season.two_pointers_made_pg,
            "two_pointers_attempted_pg": player_season.two_pointers_attempted_pg,
            # free throws
            "free_throws_made": player_season.free_throws_made,
            "free_throws_attempted": player_season.free_throws_attempted,
            "free_throw_pct": player_season.free_throw_pct,
            "free_throws_made_pg": player_season.free_throws_made_pg,
            "free_throws_attempted_pg": player_season.free_throws_attempted_pg,
            # plus/minus & milestones
            "plus_minus": player_season.plus_minus,
            "plus_minus_pg": player_season.plus_minus_pg,
            "double_doubles": player_season.double_doubles,
            "triple_doubles": player_season.triple_doubles,
            # ML-friendly scoring context
            "pts_off_tov": player_season.pts_off_tov,
            "pts_2nd_chance": player_season.pts_2nd_chance,
            "pts_fb": player_season.pts_fb,
            "pts_paint": player_season.pts_paint,
            "opp_pts_off_tov": player_season.opp_pts_off_tov,
            "opp_pts_2nd_chance": player_season.opp_pts_2nd_chance,
            "opp_pts_fb": player_season.opp_pts_fb,
            "opp_pts_paint": player_season.opp_pts_paint,
            # % of team contributions
            "pct_fgm": player_season.pct_fgm,
            "pct_fga": player_season.pct_fga,
            "pct_fg3m": player_season.pct_fg3m,
            "pct_fg3a": player_season.pct_fg3a,
            "pct_ftm": player_season.pct_ftm,
            "pct_fta": player_season.pct_fta,
            "pct_oreb": player_season.pct_oreb,
            "pct_dreb": player_season.pct_dreb,
            "pct_reb": player_season.pct_reb,
            "pct_ast": player_season.pct_ast,
            "pct_tov": player_season.pct_tov,
            "pct_stl": player_season.pct_stl,
            "pct_blk": player_season.pct_blk,
            "pct_blka": player_season.pct_blka,
            "pct_pf": player_season.pct_pf,
            "pct_pfd": player_season.pct_pfd,
            "pct_pts": player_season.pct_pts,
        }
        for key, value in res.items():
            if value is None:
                raise Exception(f"{key} is missing")
        return SeasonalMLPayload(**res)  # type: ignore[invalid-argument-type]
