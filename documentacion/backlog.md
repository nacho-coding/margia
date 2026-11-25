# Backlog priorizado de MARGIA

Plan de referencia: seis jornadas, 40–48 horas orientativas. Trabajo secuencial. Fecha de inicio: 25/11/2026. Una tarea solo pasa a verificada con evidencia ejecutada; las estimaciones no son compromisos de funcionalidad terminada.

| ID | Prioridad / jornada / horas | Incremento y aceptación | Validación | Estado |
|---|---|---|---|---|
| D1.1 | P0 · 1 · 1 h | Leer todos los Markdown raíz, conservar historia Git, registrar arquitectura y backlog | Inventario, estado limpio, origin y HEAD remoto | Verificado |
| D1.2 | P0 · 1 · 2 h | Shell premium en español, navegación adaptable, foco, filtros compartidos; módulos pendientes identificados | Typecheck, build, seis recorridos y 28 capturas con axe | Verificado |
| D1.3 | P0 · 1 · 3 h | Compose producción: PostgreSQL, FastAPI, Next.js; migración, seed idempotente y manifiesto reproducible | Arranque limpio, salud, integridad, checksum, reinicio y reset | Verificado |
| D1.4 | P0 · 1 · 2 h | Centro desde API con ventas propias, pedidos, inversión y contribución reconciliados, comparación equivalente y exportación | 18 pytest, API, filtros, exportación y QA visual | Verificado; push pendiente de permisos |
| D2.1 | P0 · 2 · 3 h | MMM semanal de pedidos: train/holdout cronológico, naive, grid reducido y diagnósticos persistidos | Sin fuga, métricas, sensibilidad, comparación baseline | Pendiente |
| D2.2 | P0 · 2 · 2 h | Medición: atribución separada, curvas con soporte, descomposición reconciliada e intervalos honestos | API, reconciliación, recorrido visual | Pendiente |
| D2.3 | P0 · 2 · 2 h | Radar económico y primera hipótesis marca; ranking explicable sin sumar oportunidades solapadas | Fixture + evidencia y enlaces con ID | Pendiente |
| D3.1 | P0 · 3 · 2 h | One Search: estimación por evidencia histórica, recorte/recuperación/costes y equilibrio | Caso 12.000 € / −21.000 €, límites y abstención | Pendiente |
| D3.2 | P0 · 3 · 3 h | Geo: parejas, aleatorización, MDE, observaciones nuevas, IC por unidades y evaluación versionada | Nulo/negativo, semilla, guardrails, sin fuga de verdad | Pendiente |
| D3.3 | P0 · 3 · 2 h | Valor de información discreto con costes y horizonte comparable | 0 ≤ EVSI ≤ EVPI, prueba no rentable, UI | Pendiente |
| D4.1 | P0 · 4 · 2 h | Biblioteca: 12 diseños locales/80 registros; modelo ligero, tres variantes y brief por reglas | Licencias, holdout por activo y tiempo, CTR/CVR separados | Pendiente |
| D4.2 | P0 · 4 · 2 h | A/B aleatorio con denominadores, IC, coste y actualización | Resultado negativo, multiplicidad, versión persistida | Pendiente |
| D4.3 | P0 · 4 · 3 h | Orquestador común base/ahorro/reinversión, 200 draws compartidos; optimización factible y opción mantener | No doble SEM, waterfall, seed, restricciones/inviabilidad | Pendiente |
| D5.1 | P0 · 5 · 2 h | CRUD escenarios, ejecución inmutable, decisiones con motivo y CSV/Markdown | API, transiciones, exportación, reinicio | Pendiente |
| D5.2 | P0 · 5 · 2 h | Snapshots alternativos de tracking/faltantes, dependencia y bloqueo al aprobar, restauración | E2E incidencia → abstención → restauración sin borrar historia | Pendiente |
| D5.3 | P0 · 5 · 3 h | Recorrido integrado Search → geo → creatividad → optimización → decisión, alternativa no actuar | Playwright de ambos recorridos y guion 7–10 min | Pendiente |
| D6.1 | P0 · 6 · 3 h | Congelación: arranque limpio/reset, persistencia, regresión matemática y API, lint/build | A01–A14 con resultados reales | Pendiente |
| D6.2 | P0 · 6 · 3 h | Corregir QA visual/accesibilidad, medir CPU/latencias, revisar secretos/licencias, preparar presentación | Capturas, comandos Windows y limitaciones documentadas; commit/push | Pendiente |
| P1 | P1 · solo tras P0 | Tema oscuro, editor de brief, cartera de experimentos, grafo, filtros secundarios | No consume la jornada de congelación | Aplazado |
| P2 | P2 · futuro | Conectores, seguridad multicliente y activación real | Fuera de esta POC | Fuera de alcance |

## Puertas de salida

- **Día 1:** contenedores de producción saludables, datos persistentes reproducibles, cifras servidas por API, filtros y revisión visual real. Si Docker no puede arrancar, registrar bloqueo; no sustituir PostgreSQL por SQLite.
- **Días 2–5:** cada cálculo nuevo debe conservar inputs, snapshot, versión y semilla; ningún resultado precalculado se presenta como ejecución nueva.
- **Día 6:** no añadir módulos. Solo se etiqueta candidata si A01–A14 pasan; toda cobertura parcial se declara.
