"""rename season to season_id across tables"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "40e1d2350b71"
down_revision = "fk_season_all_tables"
branch_labels = None
depends_on = None


TABLES = [
    "awards",
    "games",
    "team_player_salaries",
    "team_player_buyouts",
    "player_games",
    "player_seasons",
    "team_seasons",
]


def _get_fk_constraint_name(table_name: str, column_name: str) -> str | None:
    conn = op.get_bind()

    result = conn.execute(
        sa.text(
            """
            SELECT tc.constraint_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_name = :table_name
              AND kcu.column_name = :column_name
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    ).fetchone()

    if result is None:
        return None

    return result[0]


def upgrade() -> None:
    for table in TABLES:
        fk_name = _get_fk_constraint_name(table, "season")

        if fk_name is not None:
            op.drop_constraint(fk_name, table, type_="foreignkey")

        op.alter_column(table, "season", new_column_name="season_id")

        op.create_foreign_key(
            f"fk_{table}_season_id",
            table,
            "seasons",
            ["season_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    for table in TABLES:
        fk_name = _get_fk_constraint_name(table, "season_id")

        if fk_name is not None:
            op.drop_constraint(fk_name, table, type_="foreignkey")

        op.alter_column(table, "season_id", new_column_name="season")

        op.create_foreign_key(
            f"fk_{table}_season",
            table,
            "seasons",
            ["season"],
            ["id"],
            ondelete="CASCADE",
        )
