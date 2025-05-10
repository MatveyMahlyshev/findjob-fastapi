"""update user and vacancy model

Revision ID: d0589d98d0a8
Revises: ddc9b44e5d89
Create Date: 2025-05-10 13:53:37.850728

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d0589d98d0a8"
down_revision: Union[str, None] = "ddc9b44e5d89"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("vacancys", schema=None) as batch_op:
        batch_op.add_column(sa.Column("hr_id", sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            "fk_vacancys_hr_id_users", "users", ["hr_id"], ["id"]
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("vacancys", schema=None) as batch_op:
        batch_op.drop_constraint("fk_vacancys_hr_id_users", type_="foreignkey")
        batch_op.drop_column("hr_id")
