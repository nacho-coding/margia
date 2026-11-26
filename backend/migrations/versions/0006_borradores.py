"""Borradores revisables e historial; las ejecuciones existentes se conservan."""
import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("escenario", sa.Column("editable", sa.Boolean, nullable=False, server_default=sa.false()))
    op.create_table("revision_escenario",
        sa.Column("escenario_id", sa.String(50), sa.ForeignKey("escenario.id"), primary_key=True),
        sa.Column("revision", sa.Integer, primary_key=True),
        sa.Column("parametros", sa.JSON, nullable=False),
        sa.Column("creado", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("revision >= 1"))
    op.execute("INSERT INTO revision_escenario (escenario_id, revision, parametros, creado) "
               "SELECT id, revision, parametros, creado FROM escenario")
    op.create_table("evento_escenario",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("escenario_id", sa.String(50), sa.ForeignKey("escenario.id"), nullable=False),
        sa.Column("revision", sa.Integer, nullable=False),
        sa.Column("tipo", sa.String(25), nullable=False),
        sa.Column("motivo", sa.String(1000), nullable=False),
        sa.Column("creado", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_evento_escenario_escenario_id", "evento_escenario", ["escenario_id"])


def downgrade():
    op.drop_table("evento_escenario")
    op.drop_table("revision_escenario")
    op.drop_column("escenario", "editable")
