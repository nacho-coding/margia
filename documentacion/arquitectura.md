# Arquitectura implementada · Medición, Search, experimentación y creatividad

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

La contribución observada es margen menos medios, antes de costes de plataforma, pruebas y producción. No se presenta como contribución incremental. Search, radar y valor de información utilizan `comparar_captura` y `contribucion` del mismo dominio; las ramas experimentales no modifican ni duplican los hechos del negocio.

## Frontend

Next.js standalone, React y TypeScript. Tokens de DESIGN.md, Inter variable local (OFL), iconos Lucide y carga modular/diferida de ECharts. Filtros compartidos en URL y llamadas a API por contexto, con cancelación de lecturas obsoletas. Diálogos nativos, navegación móvil modal con scroll-snap, tablas semánticas con scroll propio, estados error/reintento y datos ausentes como n/d.

Se aplica la skill Modern Web Guidance instalada por el usuario; la correspondencia entre guías, decisiones y verificaciones se mantiene en [validacion.md](validacion.md). No se ha instalado ninguna dependencia de generación de IA.

## API disponible

`GET /api/v1/health`, `contexto`, `kpis`, `medios`, `busqueda`, `creativos`, `fiabilidad`, `decisiones`, `demo/manifiesto`, `exportar/negocio.csv`; `POST /api/v1/demo/reset` con confirmación literal. Contrato completo: `/api/openapi.json` y documentación `/api/documentacion`. Errores de validación en español; proxy impide mutaciones de origen distinto y exige JSON. No hay autenticación/RBAC: es una POC exclusivamente local.

Medición añade `GET /api/v1/modelos`, `modelos/mmm?dias=…&mercado=…` y `modelos/{id}/curvas?canal=…`, con contratos Pydantic. `app/modelos/mmm.py` es un estimador puro de NumPy/SciPy; no importa el generador ni lee verdad latente. `servicio.py` carga negocio y medios por separado, verifica cobertura, agrega semanas y guarda el artefacto JSON versionado en `modelo` (migración 0002).

El arranque migra, conserva/inicializa el universo y prepara el modelo bajo el mismo advisory lock del reset. Las lecturas no entrenan; reset reconstruye datos y modelo dentro de la misma transacción. Un reinicio conserva ID, parámetros y fecha de creación. Las revisiones del algoritmo usan versión nueva; no se sobrescriben artefactos anteriores. Detalles y límites: [modelo_mmm.md](modelo_mmm.md).

El MMM solo usa siete canales de demanda; SEM marca sigue en los hechos observados y en la atribución, separado de la generación modelada. El backend calcula también la valoración descriptiva de términos de pedidos mediante el margen observado por pedido y la función económica compartida. Esa asignación no se utiliza como incrementalidad causal ni se suma a la contribución observada.

## Pendientes deliberados

Orquestador de escenarios, optimización, decisiones de usuario e incidentes alternativos: backlog D4.3–D5. Escenarios permanece identificado como en desarrollo. El pretest guarda hipótesis y muestra aprendizaje A/B contextual separado; la respuesta económica sigue en 1 mientras no exista efecto identificado sobre pedidos propios.

## One Search y radar

La migración 0003 añade protocolo experimental, asignaciones por par, observaciones por unidad/periodo y evaluaciones Search guardadas. `app/datos/historia_search.py` construye las fixtures explícitas usando `captura.py`, mecanismo compartido con el generador base cuyo checksum permanece intacto. El arranque y reset preparan evidencia y estimador Search después del MMM, bajo el mismo advisory lock.

`app/modelos/search.py` solo recibe observaciones de pre/post, brazo, par, intensidad y ahorro. Estima cambio total de pedidos por euro mediante ratios pre y bootstrap del par completo; no lee el mecanismo del mundo ni identifica recuperación SEO/directo. `search_servicio.py` carga datos, valora mediante el dominio económico y sirve tanto radar como simulador. No hay cálculo económico en JS ni un negocio paralelo de Search.

El radar calcula una vista de la hipótesis persistente del modelo; un GET no crea ejecuciones. El POST de simulación guarda inputs/resultado inmutables por contenido y muestra reutilización al repetir. El enlace incluye ID real y lleva el foco al simulador. Fuente, alcance nacional, pooling, horizonte, extrapolación y costes comparables son explícitos. Modelo/intervalos/evaluaciones: [one_search.md](one_search.md).

## Laboratorio geográfico e información

`app/experimentos/servicio.py` coordina diseño → ejecución → evaluación → aceptación. Solo el orquestador importa el mundo `app/datos/mundo_geo.py`. `app/modelos/geo.py` y `informacion.py` reciben observaciones/utilidades, sin acceso a captura ni verdad. Parejas, MDE, efecto por pares, IC, guardrails y EVPI/EVSI se calculan en Python. El frontend presenta resultados y controles; no calcula beneficio ni actualiza parámetros.

Se reutilizan `experimento` (protocolo/eventos JSON), `asignacion_experimento`, `observacion_experimento` y `modelo`; sin nuevos servicios, dependencias ni DDL. Los eventos separan hora real y fecha simulada. Advisory lock compartido con reset serializa mutaciones y evita doble ejecución. IDs de diseño por contenido, observaciones inmutables tras ejecución y transiciones validadas por API.

Una evaluación compatible sustituye Search mediante nueva versión con relación al modelo anterior. La cadena determina el vigente; no depende de timestamps. Copias idénticas reutilizan la versión, diseños obsoletos no la sobrescriben y evaluaciones anteriores siguen consultables. Fiabilidad valida también cobertura de la evidencia vigente. La optimización MMM permanece bloqueada por su propio diagnóstico.

`GET /api/v1/experimentos`, `POST /experimentos/disenar`, `GET /experimentos/{id}` y POST `/ejecutar`, `/evaluar`, `/aceptar`, con contratos Pydantic/OpenAPI. Persistencia/reset y fórmulas detalladas en [experimentos_geo.md](experimentos_geo.md).

## Biblioteca y pretest creativo

`app/modelos/creatividad.py` ajusta una regresión binomial regularizada de clics/impresiones. Estimador puro, train/holdout separados por fechas y componentes de composición/campaña, referencia por canal y 200 refits por grupos. `app/creatividad/servicio.py` carga observaciones, conserva el modelo versionado y calcula las referencias/brief en Python. Las lecturas no ajustan ni generan recursos.

Migración 0004 añade `pretest_creativo` y `seleccion_creativa`. Evaluaciones por contenido y selecciones inmutables guardan snapshot, versión, semilla, inputs y referencia del recurso local. Advisory lock común serializa mutaciones con reset. El arranque prepara el modelo creativo tras MMM/Search y el reset lo reconstruye dentro de la transacción.

`app/creatividad/recursos.py` sirve el catálogo fotográfico versionado, con manifiesto de nueve WebP y 36 combinaciones de perfil/escena/placement. La biblioteca añade una recreación visual sin modificar el recurso ni los hechos históricos. El frontend compone formatos Meta/TikTok/Display/YouTube con metadatos del backend; el flujo de preparación espera la carga/decodificación real y el POST, identifica la simulación y conserva errores/reintentos. No hay IA de runtime ni vídeo generado.

El pretest presenta tres escenas con referencia histórica contextual compartida y guarda una hipótesis. Conserva sin cambios los resultados y SVG de la versión anterior. El predictor histórico no identifica un ganador ni transforma CTR/CVR en pedidos. Multiplicador económico 1; sin integración de escenarios todavía. API, diagnóstico, denominadores y límites en [creatividad.md](creatividad.md).

## A/B creativo y aprendizaje de CTR

`app/creatividad/experimentos.py` coordina protocolo → observaciones → contraste → aprendizaje. Reutiliza `experimento`, tipo `ab_creativo`, y `modelo`, sin DDL nuevo. El mundo separado `app/datos/mundo_ab.py` comparte únicamente el mecanismo base de tasas con el generador original; `app/modelos/ab.py` es un estimador puro sin importarlo. Se conserva el checksum original.

La aleatorización opera sobre oportunidades independientes, equilibradas por fecha. Protocolo, recursos, semilla, asignaciones completas comprimidas y observaciones diarias quedan persistidos. La API oculta datos de compresión/draws, permite exportar oportunidades en CSV y valida sus huellas antes de evaluar/aceptar. Las ramas no modifican hechos de negocio; GET no ejecuta.

Wilson para tasas y Newcombe-Wilson para diferencias de CTR, con Bonferroni en los contrastes previstos contra control. MDE aproximado y costes calculados en Python. Los draws Beta de respuesta describen incertidumbre del parámetro; CVR es secundario condicionado al clic. Ninguna de esas cifras demuestra demanda propia.

Una evaluación compatible puede crear `creatividad-ab-1.0.0` en el contexto exacto. La cadena conserva versiones, sustituye sin acumular ramas dependientes, reutiliza evidencia idéntica y rechaza diseños obsoletos. El pretest consulta este aprendizaje aparte del modelo histórico y su JSON inmutable. Las rutas geo/A/B filtran su tipo; reset/reinicio usan el mismo advisory lock. Contratos, fórmula, endpoints y límites en [experimentos_ab.md](experimentos_ab.md).
