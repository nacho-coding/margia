# Decisiones de implementación

## 25/11/2026 · Fundaciones

1. Se conserva el checkout y la rama `main`: repositorio inicial de documentación, limpio, con HEAD igual al remoto. No se reescribe historia. Se intentará push normal y se respetará cualquier protección del servidor.
2. Monolito modular con Next.js/TypeScript, FastAPI/SQLAlchemy/Alembic y **PostgreSQL en Docker**. Ninguna base alternativa, LLM, GPU ni API pagada. Un único proxy de API del mismo origen; solo el frontend publica puerto en `127.0.0.1`.
3. El Día 1 entrega datos observados sintéticos e integridad. MMM, recuperación causal, radar económico, experimentos y optimización no se inventan para completar pantallas: sus rutas explican el estado hasta sus incrementos.
4. Se fija el corte de demo en **31/10/2026**, 730 días desde 01/11/2024, independiente del reloj. Dos bloques de 365 días con 4,8 M€ cada uno. Históricos de búsqueda (28 días), campañas (7 días) y creatividad (28 días, cobertura parcial) se declaran con su cobertura; no se rellenan ausencias con ceros.
5. Importes almacenados en céntimos enteros; cocientes sin denominador se devuelven como `null`. Economía compartida en Python. JS solo presenta formatos, gráficos e interacción.
6. El seed queda separado de futuros estimadores. La verdad latente del generador se guarda en fixture de evaluación separado; la API no expone parámetros verdaderos como estimaciones. La reproducción se valida por checksum lógico, excluyendo timestamps.
7. Activos locales originales en SVG, con procedencia explícita; tipografía Inter local bajo OFL. Se usa la skill Sites en su ruta **local-only**: sin registro ni publicación en hosting externo. Prevalece la instrucción explícita de no delegar sobre sugerencias opcionales de la skill.
8. No se interpreta ausencia de historial como historial vacío con resultados inventados. El centro muestra la próxima acción y el estado de evidencia, sin importes de oportunidad hasta tener un estimador.

## Fuentes técnicas consultadas

- [Next.js en Docker, salida standalone](https://docs.docker.com/guides/nextjs/).
- [FastAPI en contenedores](https://fastapi.tiangolo.com/deployment/docker/).
- [Política de versiones PostgreSQL](https://www.postgresql.org/support/versioning/).

Las versiones efectivamente instaladas se fijan en lockfiles e imágenes; consultar el manifiesto técnico y los comandos en avances.

## Incorporación de PRD y RFC durante el desarrollo

Se leen íntegramente PRD.md (376 líneas) y RFC.md (637 líneas), añadidos en el commit ajeno `e6b3f97`. Se conserva ese commit y los documentos sin cambios. Son consistentes con la rebanada vertical del Día 1 y el backlog existente. Su matriz RF/RNF se incorporará a validación. El puerto 8080 del RFC es una propuesta; se mantiene 3000 configurable, seleccionado antes de recibir el RFC. No altera ningún contrato funcional.

La skill Modern Web Guidance instalada por el usuario se aplica a todo el frontend: guías `css-layout`, `dialog`, `navigation-drawer`, `responsive-table`, `accessibility`, `forms` y `performance`. Se conserva sin cambios la instalación del usuario. Se evita cualquier API de IA del navegador; las guías se usan solo para plataforma web.

Compatibilidad comprobada: Next 16.4.6 / React 19.3.1; TypeScript 6.0.3 y ESLint 9.39.5. Se descartan TS 7 y ESLint 10 por límites de los plugins de Next. Imágenes de Node 24, Python 3.13 y PostgreSQL 18 fijadas por digest; dependencias transitivas en lockfiles.
