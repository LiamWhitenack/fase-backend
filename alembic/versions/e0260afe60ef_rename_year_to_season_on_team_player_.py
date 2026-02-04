"""rename year to season on team_player_buyouts"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "e0260afe60ef"
down_revision = "8f1b5d592631"  # replace with actual previous revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "team_player_buyouts",
        "year",
        new_column_name="season",
        existing_type=sa.Integer(),  # change type if it's different
    )


def downgrade() -> None:
    op.alter_column(
        "team_player_buyouts",
        "season",
        new_column_name="year",
        existing_type=sa.Integer(),
    )
