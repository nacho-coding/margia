# Procedencia de recursos y dependencias

## Recursos originales

- Monograma MARGIA y favicon: diseño SVG original del proyecto; sin logos de terceros.
- Doce composiciones AUREL en `frontend/public/assets/creatividad`: generadas por `scripts/generar_assets.mjs` mediante primitivas SVG originales. No se han descargado fotografías ni utilizado modelos de IA. Marca ficticia. Reutilización explícita en 80 registros; no se presentan como 80 diseños distintos.
- Activos SVG publicitarios y datos sintéticos: CC BY 4.0; atribución «MARGIA · demostración sintética». [Texto de licencia](https://creativecommons.org/licenses/by/4.0/).

## Recursos de terceros

| Recurso | Licencia | Uso |
|---|---|---|
| Inter / Fontsource | SIL Open Font License 1.1 | Fuente variable local incluida en el bundle; aviso íntegro conservado en `frontend/public/assets/licencias/Inter-OFL.txt`. |
| Lucide | ISC | Iconos de interfaz; paquete npm fijado en lockfile, conserva licencia. |
| Apache ECharts | Apache-2.0 | Series calculadas por backend, representación modular en navegador. |
| React, Next.js, Tailwind, TypeScript | MIT | Framework y compilación; licencias incluidas en dependencias. |
| FastAPI, SQLAlchemy, Alembic, pytest, httpx, Ruff | MIT | Backend y herramientas. |
| Uvicorn, NumPy, SciPy | BSD | Servidor y cálculo CPU. |
| Psycopg | LGPL-3.0 | Adaptador PostgreSQL, sin modificar. |
| PostgreSQL | PostgreSQL License | Base de datos oficial en Docker. |
| Playwright / axe-core | Apache-2.0 / MPL-2.0 | Pruebas y auditoría automática, no dependencias del runtime de producción. |
| Modern Web Guidance | Apache-2.0 | Skill de desarrollo instalada por el usuario desde GoogleChrome, sin modificar. [Repositorio y licencia](https://github.com/GoogleChrome/modern-web-guidance). |

No se publica una licencia global de código en nombre del propietario: la elección de licencia general del repositorio queda pendiente. Las licencias de dependencias y recursos se conservan, sin relicenciarlas. Los nombres de plataformas son etiquetas analíticas; no se incluyen sus logos ni materiales publicitarios.
