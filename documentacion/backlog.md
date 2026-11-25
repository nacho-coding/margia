# Backlog priorizado de MARGIA

Plan de referencia: seis jornadas, 40–48 horas orientativas. Trabajo secuencial. Fecha de inicio: 25/11/2026. Una tarea solo pasa a verificada con evidencia ejecutada; las estimaciones no son compromisos de funcionalidad terminada.

| ID | Prioridad / jornada / horas | Incremento y aceptación | Validación | Estado |
|---|---|---|---|---|
| D1.1 | P0 · 1 · 1 h | Leer todos los Markdown raíz, conservar historia Git, registrar arquitectura y backlog | Inventario, estado limpio, origin y HEAD remoto | Verificado |
| D1.2 | P0 · 1 · 2 h | Shell premium en español, navegación adaptable, foco, filtros compartidos; módulos pendientes identificados | Typecheck, build, seis recorridos y 28 capturas con axe | Verificado |
| D1.3 | P0 · 1 · 3 h | Compose producción: PostgreSQL, FastAPI, Next.js; migración, seed idempotente y manifiesto reproducible | Arranque limpio, salud, integridad, checksum, reinicio y reset | Verificado |
| D1.4 | P0 · 1 · 2 h | Centro desde API con ventas propias, pedidos, inversión y contribución reconciliados, comparación equivalente y exportación | 18 pytest, API, filtros, exportación y QA visual | Verificado y publicado |
| D2.1 | P0 · 2 · 3 h | MMM semanal de pedidos: train/holdout cronológico, naive, grid reducido y diagnósticos persistidos | Sin fuga, métricas, sensibilidad, comparación baseline | Verificado; reparto inestable bloquea recomendaciones |
| D2.2 | P0 · 2 · 2 h | Medición: atribución separada, curvas con soporte, descomposición reconciliada y bandas empíricas con límites | 26 pytest, API, nueve recorridos, capturas y axe | Verificado; bandas condicionales, no IC causal |
| D2.3 | P0 · 2 · 2 h | Radar económico y primera hipótesis marca; ranking explicable sin sumar oportunidades solapadas | Evidencia histórica, economía común, hipótesis con ID y recorrido al simulador | Verificado; Día 2 cerrado |
| D3.1 | P0 · 3 · 2 h | One Search: evidencia histórica, recorte/costes/equilibrio; efecto directo por euro cuando recuperación no identificable | 39 pytest y recorrido positivo/negativo, soporte, pooling y abstención | Verificado; recuperación no identificada, alternativa contractual implementada |
| D3.2 | P0 · 3 · 3 h | Geo: parejas, aleatorización, MDE, observaciones nuevas, IC por unidades y evaluación versionada | Nulo/adverso, semilla, guardrails, sin fuga; sustitución, obsolescencia, persistencia/reset y UI | Verificado; ramas dependientes no se acumulan |
| D3.3 | P0 · 3 · 2 h | Valor de información discreto con costes y horizonte comparable | 0 ≤ EVSI ≤ EVPI, ruido, prueba no rentable, costes una vez y UI | Verificado; likelihood aproximado y dos acciones, reinversión en D4 |
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

## Siguiente corte verificable

**Días 1–3 cerrados.** Search → diseño geo → información → nueva ejecución → evaluación → sustitución de evidencia, conservando versiones y abstención. No se utiliza atribución ni MMM inestable como recuperación identificada. Siguiente hito: D4.1, modelo creativo ligero y tres variantes con brief por reglas, seguido de A/B, orquestador y optimización. La biblioteca descriptiva ya existe; pretest, efecto creativo en escenarios y A/B siguen pendientes. Los días 5–6 mantienen su alcance; no se declara terminada la POC.
