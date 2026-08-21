"""Track the source of ingredient nutrition values.

Revision ID: 002_nutrition_source
Revises: 001_initial
Create Date: 2026-08-20

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_nutrition_source"
down_revision: Union[str, Sequence[str], None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "ingredients",
        sa.Column(
            "nutrition_source",
            sa.String(length=20),
            nullable=False,
            server_default="manual",
        ),
    )


def downgrade() -> None:
    op.drop_column("ingredients", "nutrition_source")
