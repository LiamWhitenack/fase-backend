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

    op.alter_column(
        "seasons",
        "max_salary_cap",
        existing_type=sa.Float(),
        type_=sa.Integer(),
        postgresql_using="max_salary_cap::integer",
    )

    op.alter_column(
        "seasons",
        "inflation_adjusted_cap",
        existing_type=sa.Float(),
        type_=sa.Integer(),
        postgresql_using="inflation_adjusted_cap::integer",
    )

    op.alter_column(
        "seasons",
        "luxury_tax_threshold",
        existing_type=sa.Float(),
        type_=sa.Integer(),
        postgresql_using="luxury_tax_threshold::integer",
    )

    op.alter_column(
        "seasons",
        "first_apron",
        existing_type=sa.Float(),
        type_=sa.Integer(),
        postgresql_using="first_apron::integer",
    )

    op.alter_column(
        "seasons",
        "second_apron",
        existing_type=sa.Float(),
        type_=sa.Integer(),
        postgresql_using="second_apron::integer",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "seasons",
        "second_apron",
        existing_type=sa.Integer(),
        type_=sa.Float(),
        postgresql_using="second_apron::float",
    )

    op.alter_column(
        "seasons",
        "first_apron",
        existing_type=sa.Integer(),
        type_=sa.Float(),
        postgresql_using="first_apron::float",
    )

    op.alter_column(
        "seasons",
        "luxury_tax_threshold",
        existing_type=sa.Integer(),
        type_=sa.Float(),
        postgresql_using="luxury_tax_threshold::float",
    )

    op.alter_column(
        "seasons",
        "inflation_adjusted_cap",
        existing_type=sa.Integer(),
        type_=sa.Float(),
        postgresql_using="inflation_adjusted_cap::float",
    )

    op.alter_column(
        "seasons",
        "max_salary_cap",
        existing_type=sa.Integer(),
        type_=sa.Float(),
        postgresql_using="max_salary_cap::float",
    )

    op.drop_column("seasons", "expected_cap")
