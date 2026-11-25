# Arquitectura implementada · Fundaciones y Medición

El [RFC](../RFC.md) recoge el diseño objetivo; este archivo describe únicamente el incremento existente.

```text
Navegador → localhost:3000 → Next.js de producción → proxy /api
                                                  ↓ red de contenedores
                                            FastAPI /api/v1
                                                  ↓ red interna
                                          PostgreSQL 18 + volumen
```

Solo se publica el puerto web con bind 127.0.0.1. PostgreSQL y FastAPI no publican puertos del host. Los procesos de aplicación usan usuarios sin privilegios. El límite configurado es 1 GiB DB + 2 GiB API + 1 GiB web; esto no es una medición de consumo real. BLAS limitado a dos hilos. Sin Redis, workers externos, IA ni servicios pagados.

## Persistencia y generación

- SQLAlchemy síncrono y Alembic; migración inicial con DDL congelado para que no dependa de futuros cambios del ORM.
- 24 mercados ficticios, ocho canales, 120 campañas, 50 grupos y 80 registros creativos con 12 composiciones originales. Granos separados y FK en PostgreSQL.
- 730 días de negocio y medios; búsqueda 28 días, campañas siete y creatividad 28 con mercados parciales. La cobertura se devuelve en cada vista.
- Inversión normalizada en dos bloques de 365 días, 4,8 M€ cada uno, asignación de céntimos por mayor resto. El gasto Search/campañas/creatividad no se suma a medios.
- Pedidos propios generados una vez, con estacionalidad, promoción, demanda por adstock/saturación y captura mutuamente excluyente. Atribución de plataforma solapada y descriptiva.
- Semilla raíz 260725 y cinco substreams SeedSequence. Manifiesto y checksum SHA-256 canónico por tabla/grano, sin reloj de sistema. Verdad latente separada en `/app/evaluacion`, inaccesible por API y no montada como código del estimador.
- `seed` idempotente bajo advisory lock: un reinicio conserva los datos. Reset genera primero y sustituye exclusivamente el esquema demo dentro de una transacción.

## Una fuente de cifras

`app/api/consultas.py` agrega hechos de negocio y medios por separado; nunca une hechos de distinto grano para calcular ventas. El dominio Python calcula contribución y aritmética económica. El frontend recibe valores, aplica formato español, orden visual y selección de series. No hay modelos económicos en JavaScript.

La contribución observada es margen menos medios, antes de costes futuros de plataforma, pruebas y producción. No se presenta como contribución incremental. La función de recorte está probada con la fixture contractual pero todavía no se expone como estimación de la empresa ficticia.

## Frontend

Next.js standalone, React y TypeScript. Tokens de DESIGN.md, Inter variable local (OFL), iconos Lucide y carga modular/diferida de ECharts. Filtros compartidos en URL y llamadas a API por contexto, con cancelación de lecturas obsoletas. Diálogos nativos, navegación móvil modal con scroll-snap, tablas semánticas con scroll propio, estados error/reintento y datos ausentes como n/d.

Se aplica la skill Modern Web Guidance instalada por el usuario; la correspondencia entre guías, decisiones y verificaciones se mantiene en [validacion.md](validacion.md). No se ha instalado ninguna dependencia de generación de IA.

## API disponible

`GET /api/v1/health`, `contexto`, `kpis`, `medios`, `busqueda`, `creativos`, `fiabilidad`, `decisiones`, `demo/manifiesto`, `exportar/negocio.csv`; `POST /api/v1/demo/reset` con confirmación literal. Contrato completo: `/api/openapi.json` y documentación `/api/documentacion`. Errores de validación en español; proxy impide mutaciones de origen distinto y exige JSON. No hay autenticación/RBAC: es una POC exclusivamente local.

Medición añade `GET /api/v1/modelos`, `modelos/mmm?dias=…&mercado=…` y `modelos/{id}/curvas?canal=…`, con contratos Pydantic. `app/modelos/mmm.py` es un estimador puro de NumPy/SciPy; no importa el generador ni lee verdad latente. `servicio.py` carga negocio y medios por separado, verifica cobertura, agrega semanas y guarda el artefacto JSON versionado en `modelo` (migración 0002).

El arranque migra, conserva/inicializa el universo y prepara el modelo bajo el mismo advisory lock del reset. Las lecturas no entrenan; reset reconstruye datos y modelo dentro de la misma transacción. Un reinicio conserva ID, parámetros y fecha de creación. Las revisiones del algoritmo usan versión nueva; no se sobrescriben artefactos anteriores. Detalles y límites: [modelo_mmm.md](modelo_mmm.md).

El MMM solo usa siete canales de demanda; SEM marca sigue en los hechos observados y en la atribución, separado de la generación modelada. El backend calcula también la valoración descriptiva de términos de pedidos mediante el margen observado por pedido y la función económica compartida. Esa asignación no se utiliza como incrementalidad causal ni se suma a la contribución observada.

## Pendientes deliberados

Radar económico estimado, recuperación experimental, geo/A-B, valor de información, orquestador de escenarios, optimización, decisiones de usuario e incidentes alternativos: backlog D2.3–D5. Los módulos correspondientes se identifican como en desarrollo. El generador inicial no sustituye esos estimadores ni un gemelo causal completo. La respuesta creativa del negocio y el mundo experimental se ampliarán junto con sus pruebas antes de utilizarse en escenarios.
