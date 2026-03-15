"""add constraints, indexes, and audit fields

Revision ID: 20260315_000002
Revises: 20260315_000001
Create Date: 2026-03-15 00:00:02
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260315_000002"
down_revision = "20260315_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("animal") as batch_op:
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
        batch_op.add_column(sa.Column("deleted_at", sa.DateTime(), nullable=True))
        batch_op.create_unique_constraint("uq_animal_tag_id", ["tag_id"])

    with op.batch_alter_table("event") as batch_op:
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
        batch_op.add_column(sa.Column("deleted_at", sa.DateTime(), nullable=True))

    with op.batch_alter_table("lot") as batch_op:
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
        batch_op.add_column(sa.Column("deleted_at", sa.DateTime(), nullable=True))

    with op.batch_alter_table("readerscan") as batch_op:
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
        batch_op.add_column(sa.Column("deleted_at", sa.DateTime(), nullable=True))

    op.create_index(
        "ix_readerscan_rfid_code_batch_id_scanned_at",
        "readerscan",
        ["rfid_code", "batch_id", "scanned_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_readerscan_rfid_code_batch_id_scanned_at", table_name="readerscan")

    with op.batch_alter_table("readerscan") as batch_op:
        batch_op.drop_column("deleted_at")
        batch_op.drop_column("updated_at")
        batch_op.drop_column("created_at")

    with op.batch_alter_table("lot") as batch_op:
        batch_op.drop_column("deleted_at")
        batch_op.drop_column("updated_at")

    with op.batch_alter_table("event") as batch_op:
        batch_op.drop_column("deleted_at")
        batch_op.drop_column("updated_at")
        batch_op.drop_column("created_at")

    with op.batch_alter_table("animal") as batch_op:
        batch_op.drop_constraint("uq_animal_tag_id", type_="unique")
        batch_op.drop_column("deleted_at")
        batch_op.drop_column("updated_at")
