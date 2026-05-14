"""task_id nullable in Payment

Revision ID: 38e7c099ba73
Revises: e586054e0858
Create Date: 2026-05-14 09:23:40.184348

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "38e7c099ba73"
down_revision = "e586054e0858"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("payment", schema=None) as batch_op:
        batch_op.alter_column("task_id", existing_type=sa.INTEGER(), nullable=True)


def downgrade():
    with op.batch_alter_table("payment", schema=None) as batch_op:
        batch_op.alter_column("task_id", existing_type=sa.INTEGER(), nullable=False)
