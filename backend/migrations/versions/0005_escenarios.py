"""Configuración y ejecuciones inmutables del orquestador común."""
import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("escenario",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("snapshot_id", sa.String(60), sa.ForeignKey("snapshot.id"), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("revision", sa.Integer, nullable=False),
        sa.Column("estado", sa.String(25), nullable=False),
        sa.Column("parametros", sa.JSON, nullable=False),
        sa.Column("creado", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("revision >= 1"))
    op.create_index("ix_escenario_snapshot_id", "escenario", ["snapshot_id"])
    op.create_table("ejecucion",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("escenario_id", sa.String(50), sa.ForeignKey("escenario.id"), nullable=False),
        sa.Column("snapshot_id", sa.String(60), sa.ForeignKey("snapshot.id"), nullable=False),
        sa.Column("revision", sa.Integer, nullable=False),
        sa.Column("version", sa.String(30), nullable=False),
        sa.Column("semilla", sa.Integer, nullable=False),
        sa.Column("entradas", sa.JSON, nullable=False),
        sa.Column("modelos", sa.JSON, nullable=False),
        sa.Column("checksum_fuentes", sa.String(64), nullable=False),
        sa.Column("resultado", sa.JSON, nullable=False),
        sa.Column("creado", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("revision >= 1"))
    op.create_index("ix_ejecucion_escenario_id", "ejecucion", ["escenario_id"])
    op.create_index("ix_ejecucion_snapshot_id", "ejecucion", ["snapshot_id"])


def downgrade():
    op.drop_table("ejecucion")
    op.drop_table("escenario")
