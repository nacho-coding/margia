"""Históricos explícitos, asignaciones/observaciones y evaluaciones One Search."""
import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("experimento",
        sa.Column("id", sa.String(80), primary_key=True),
        sa.Column("snapshot_id", sa.String(60), sa.ForeignKey("snapshot.id"), nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("estado", sa.String(30), nullable=False),
        sa.Column("origen", sa.String(120), nullable=False),
        sa.Column("inicio_pre", sa.Date, nullable=False),
        sa.Column("inicio_post", sa.Date, nullable=False),
        sa.Column("fin", sa.Date, nullable=False),
        sa.Column("recorte", sa.Float, nullable=False),
        sa.Column("semilla", sa.Integer, nullable=False),
        sa.Column("protocolo", sa.JSON, nullable=False),
        sa.CheckConstraint("recorte >= 0 AND recorte <= 1"))
    op.create_index("ix_experimento_snapshot_id", "experimento", ["snapshot_id"])
    op.create_table("asignacion_experimento",
        sa.Column("experimento_id", sa.String(80), sa.ForeignKey("experimento.id"), primary_key=True),
        sa.Column("mercado_id", sa.String(20), sa.ForeignKey("mercado.id"), primary_key=True),
        sa.Column("par_id", sa.String(20), nullable=False),
        sa.Column("brazo", sa.String(20), nullable=False),
        sa.Column("probabilidad", sa.Float, nullable=False),
        sa.CheckConstraint("brazo IN ('control', 'tratamiento')"))
    op.create_table("observacion_experimento",
        sa.Column("experimento_id", sa.String(80), primary_key=True),
        sa.Column("mercado_id", sa.String(20), primary_key=True),
        sa.Column("periodo", sa.String(10), primary_key=True),
        sa.Column("pedidos", sa.Integer, nullable=False),
        sa.Column("gasto_cent", sa.BigInteger, nullable=False),
        sa.Column("presupuesto_cent", sa.BigInteger, nullable=False),
        sa.ForeignKeyConstraint(["experimento_id", "mercado_id"], ["asignacion_experimento.experimento_id", "asignacion_experimento.mercado_id"]),
        sa.CheckConstraint("periodo IN ('pre', 'post')"),
        sa.CheckConstraint("pedidos >= 0 AND gasto_cent >= 0 AND presupuesto_cent >= 0"))
    op.create_table("simulacion_search",
        sa.Column("id", sa.String(60), primary_key=True),
        sa.Column("snapshot_id", sa.String(60), sa.ForeignKey("snapshot.id"), nullable=False),
        sa.Column("modelo_id", sa.String(60), sa.ForeignKey("modelo.id"), nullable=False),
        sa.Column("entradas", sa.JSON, nullable=False),
        sa.Column("resultado", sa.JSON, nullable=False),
        sa.Column("creado", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_simulacion_search_snapshot_id", "simulacion_search", ["snapshot_id"])


def downgrade():
    for nombre in ("simulacion_search", "observacion_experimento", "asignacion_experimento", "experimento"):
        op.drop_table(nombre)
