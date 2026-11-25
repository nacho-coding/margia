"""Herramienta de desarrollo: captura el DDL inicial. No se ejecuta al arrancar."""
from pathlib import Path

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

from app.persistencia import tablas  # noqa: F401
from app.persistencia.db import Base

dialect = postgresql.dialect()
root = Path("migrations/versions")
statements = []
for table in Base.metadata.sorted_tables:
    statements.append(str(CreateTable(table).compile(dialect=dialect)).strip() + ";")
    for index in sorted(table.indexes, key=lambda i: i.name):
        statements.append(str(CreateIndex(index).compile(dialect=dialect)).strip() + ";")
ddl = "\n".join(line.rstrip() for line in "\n\n".join(statements).splitlines()) + "\n"
(root / "0001_esquema.sql").write_text(ddl, encoding="utf-8")
print("DDL inicial congelado; revisar antes de versionarlo.")
