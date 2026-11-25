"""Evaluaciones creativas inmutables y selecciones por referencia."""
import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("pretest_creativo",
        sa.Column("id", sa.String(60), primary_key=True),
        sa.Column("snapshot_id", sa.String(60), sa.ForeignKey("snapshot.id"), nullable=False),
        sa.Column("modelo_id", sa.String(60), sa.ForeignKey("modelo.id"), nullable=False),
        sa.Column("entradas", sa.JSON, nullable=False),
        sa.Column("resultado", sa.JSON, nullable=False),
        sa.Column("creado", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_pretest_creativo_snapshot_id", "pretest_creativo", ["snapshot_id"])
    op.create_table("seleccion_creativa",
        sa.Column("id", sa.String(60), primary_key=True),
        sa.Column("pretest_id", sa.String(60), sa.ForeignKey("pretest_creativo.id"), nullable=False),
        sa.Column("variante_id", sa.String(40), nullable=False),
        sa.Column("creado", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("pretest_id", "variante_id"))
    op.create_index("ix_seleccion_creativa_pretest_id", "seleccion_creativa", ["pretest_id"])


def downgrade():
    op.drop_table("seleccion_creativa")
    op.drop_table("pretest_creativo")
