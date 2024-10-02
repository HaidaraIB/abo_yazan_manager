"""add withdrawals col to Account table

Revision ID: 561cb317945c
Revises: 
Create Date: 2024-10-01 14:57:20.820597

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "561cb317945c"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("accounts") as batch_op:
        batch_op.add_column(
            sa.Column(
                name="withdrawals",
                type_=sa.Float,
            )
        )


def downgrade() -> None:
    pass
