"""Esquema inicial de observaciones sintéticas, snapshot y decisiones."""
from pathlib import Path

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    ddl = Path(__file__).with_name("0001_esquema.sql").read_text(encoding="utf-8")
    for statement in ddl.split(";"):
        if statement.strip():
            op.execute(statement)


def downgrade() -> None:
    # Orden inverso de dependencias del esquema congelado, sin importar el ORM actual.
    for name in ("creatividad_diaria", "campana_diaria", "busqueda_diaria", "negocio_diario",
                 "medios_diarios", "decision", "creativo", "campana", "grupo_busqueda",
                 "canal", "mercado", "snapshot"):
        op.drop_table(name)
