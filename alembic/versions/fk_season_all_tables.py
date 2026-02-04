"""make season columns foreign keys to seasons.id"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "fk_season_all_tables"
down_revision = "e0260afe60ef"  # <-- the previous migration
branch_labels = None
depends_on = None


# List of tables with season columns
tables = [
    "awards",
    "games",
    "team_player_salaries",
    "team_player_buyouts",
    "player_games",
    "player_seasons",
    "team_seasons",
]


def upgrade() -> None:
    # Step 1: populate seasons table with any existing season values
    for table in tables:
        op.execute(
            f"""
            INSERT INTO seasons (id)
            SELECT DISTINCT season FROM {table}
            WHERE season IS NOT NULL
            ON CONFLICT (id) DO NOTHING;
            """
        )

    # Step 2: add foreign key constraints
    for table in tables:
        op.create_foreign_key(
            f"fk_{table}_season",
            table,
            "seasons",
            ["season"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    # Drop the foreign keys in reverse
    for table in tables:
        op.drop_constraint(f"fk_{table}_season", table, type_="foreignkey")
