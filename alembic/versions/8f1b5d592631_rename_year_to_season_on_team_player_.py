"""rename year to season on team_player_salaries"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "8f1b5d592631"
down_revision = None  # replace with actual previous revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "team_player_salaries",
        "year",
        new_column_name="season",
        existing_type=sa.Integer(),  # change type if it's different
    )


def downgrade() -> None:
    op.alter_column(
        "team_player_salaries",
        "season",
        new_column_name="year",
        existing_type=sa.Integer(),
    )
