"""initial schema

Revision ID: 20260315_000001
Revises:
Create Date: 2026-03-15 00:00:01
"""

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = "20260315_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "animal",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("visual_tag", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("sex", sa.String(), nullable=True),
        sa.Column("estimated_weight", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_animal_tag_id"), "animal", ["tag_id"], unique=False)

    op.create_table(
        "lot",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_lot_name"), "lot", ["name"], unique=False)

    op.create_table(
        "readerscan",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rfid_code", sa.String(), nullable=False),
        sa.Column("reader_name", sa.String(), nullable=True),
        sa.Column("batch_id", sa.String(), nullable=True),
        sa.Column("scanned_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_readerscan_rfid_code"), "readerscan", ["rfid_code"], unique=False)

    op.create_table(
        "event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("animal_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.Enum("check_in", "check_out", "movement", name="eventtype"), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["animal_id"], ["animal.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lotanimal",
        sa.Column("lot_id", sa.Integer(), nullable=False),
        sa.Column("animal_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["animal_id"], ["animal.id"]),
        sa.ForeignKeyConstraint(["lot_id"], ["lot.id"]),
        sa.PrimaryKeyConstraint("lot_id", "animal_id"),
    )


def downgrade() -> None:
    op.drop_table("lotanimal")
    op.drop_table("event")
    op.drop_index(op.f("ix_readerscan_rfid_code"), table_name="readerscan")
    op.drop_table("readerscan")
    op.drop_index(op.f("ix_lot_name"), table_name="lot")
    op.drop_table("lot")
    op.drop_index(op.f("ix_animal_tag_id"), table_name="animal")
    op.drop_table("animal")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS eventtype")
