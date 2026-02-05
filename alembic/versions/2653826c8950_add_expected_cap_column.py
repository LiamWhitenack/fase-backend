"""add expected cap column

Revision ID: 2653826c8950
Revises: 40e1d2350b71
Create Date: 2026-02-04 21:34:06.873108

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2653826c8950"
down_revision: Union[str, Sequence[str], None] = "40e1d2350b71"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "seasons",
        sa.Column("expected_cap", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("seasons", "expected_cap")
