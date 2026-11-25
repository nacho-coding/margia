"""Artefactos MMM persistentes e independientes del generador."""
import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("modelo",
                    sa.Column("id", sa.String(60), primary_key=True),
                    sa.Column("snapshot_id", sa.String(60), sa.ForeignKey("snapshot.id"), nullable=False),
                    sa.Column("version", sa.String(30), nullable=False),
                    sa.Column("checksum_datos", sa.String(64), nullable=False),
                    sa.Column("resultado", sa.JSON(), nullable=False),
                    sa.Column("creado", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                    sa.UniqueConstraint("snapshot_id", "version", "checksum_datos"))
    op.create_index("ix_modelo_snapshot_id", "modelo", ["snapshot_id"])


def downgrade():
    op.drop_table("modelo")
