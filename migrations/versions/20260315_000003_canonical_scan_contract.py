"""add canonical scan contract fields and idempotency index

Revision ID: 20260315_000003
Revises: 20260315_000002
Create Date: 2026-03-15 00:00:03
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260315_000003"
down_revision = "20260315_000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("readerscan") as batch_op:
        batch_op.add_column(sa.Column("device_id", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("signal_quality", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("idempotency_key", sa.String(), nullable=True))

    op.create_index("ix_readerscan_idempotency_key", "readerscan", ["idempotency_key"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_readerscan_idempotency_key", table_name="readerscan")

    with op.batch_alter_table("readerscan") as batch_op:
        batch_op.drop_column("idempotency_key")
        batch_op.drop_column("signal_quality")
        batch_op.drop_column("device_id")
