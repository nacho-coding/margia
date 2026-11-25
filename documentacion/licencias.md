# Procedencia de recursos y dependencias

## Recursos originales

- Monograma MARGIA y favicon: diseño SVG original del proyecto; sin logos de terceros.
- Doce composiciones AUREL en `frontend/public/assets/creatividad`: generadas por `scripts/generar_assets.mjs` mediante primitivas SVG originales. No se han descargado fotografías ni utilizado modelos de IA. Marca ficticia. Reutilización explícita en 80 registros; no se presentan como 80 diseños distintos.
- Nueve composiciones adicionales de pretest (`pretest-{hogar,moda,belleza}-{espacio,marco,detalle}.svg`): creadas con `scripts/generar_variantes.mjs`, reutilizando los productos SVG originales y nuevas jerarquías visuales. Recursos locales precreados, versión `variantes-1.0.0`; no son nueve observaciones adicionales ni imágenes generadas durante la evaluación. Misma licencia CC BY 4.0 y atribución del proyecto. Las rutas publicadas se conservan para mantener evaluaciones antiguas.
- Nueve fotografías sintéticas en `frontend/public/assets/creatividad/fotografia-v2`: generadas con Imagegen integrada durante el desarrollo, a petición del usuario, sin fotografías de terceros ni personas reales. Escenas de producto, textura y uso para hogar/moda/belleza; AUREL es ficticia. Se distribuyen como recursos de demostración bajo CC BY 4.0, atribución «MARGIA · imagen sintética generada con IA». Prompts exactos en [creatividad_prompts.json](creatividad_prompts.json), pesos/dimensiones/hashes en el manifiesto del backend. No se presentan como evidencias observadas de rendimiento ni como fotografías reales.
- Activos SVG publicitarios y datos sintéticos: CC BY 4.0; atribución «MARGIA · demostración sintética». [Texto de licencia](https://creativecommons.org/licenses/by/4.0/).

## Recursos de terceros

| Recurso | Licencia | Uso |
|---|---|---|
| Inter / Fontsource | SIL Open Font License 1.1 | Fuente variable local incluida en el bundle; aviso íntegro conservado en `frontend/public/assets/licencias/Inter-OFL.txt`. |
| Lucide | ISC | Iconos de interfaz; paquete npm fijado en lockfile, conserva licencia. |
| Apache ECharts | Apache-2.0 | Series calculadas por backend, representación modular en navegador. |
| React, Next.js, Tailwind, TypeScript | MIT | Framework y compilación; licencias incluidas en dependencias. |
| Sharp | Apache-2.0 | Transcodificación local a WebP; dependencia de Next ya fijada en el lockfile, sin nueva instalación. Se conservan los avisos de sus dependencias nativas. |
| FastAPI, SQLAlchemy, Alembic, pytest, httpx, Ruff | MIT | Backend y herramientas. |
| Uvicorn, NumPy, SciPy | BSD | Servidor y cálculo CPU. |
| Psycopg | LGPL-3.0 | Adaptador PostgreSQL, sin modificar. |
| PostgreSQL | PostgreSQL License | Base de datos oficial en Docker. |
| Playwright / axe-core | Apache-2.0 / MPL-2.0 | Pruebas y auditoría automática, no dependencias del runtime de producción. |
| Modern Web Guidance | Apache-2.0 | Skill de desarrollo instalada por el usuario desde GoogleChrome, sin modificar. [Repositorio y licencia](https://github.com/GoogleChrome/modern-web-guidance). |

No se publica una licencia global de código en nombre del propietario: la elección de licencia general del repositorio queda pendiente. Las licencias de dependencias y recursos se conservan, sin relicenciarlas. Los nombres de plataformas son etiquetas analíticas; no se incluyen sus logos ni materiales publicitarios.
