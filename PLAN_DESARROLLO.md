# Plan de seis jornadas · Ejecución secuencial con Codex

## Arquitectura y límites
Monolito modular: Next.js/React/TypeScript + Tailwind + ECharts; FastAPI/Pydantic + SQLAlchemy/Alembic + PostgreSQL; NumPy/Polars o pandas, SciPy, scikit-learn, statsmodels. Docker Compose con frontend, backend, db; sin Redis/Celery salvo necesidad demostrada, sin microservicios, sin 3D, sin IA local, sin agentes. Versiones estables compatibles fijadas tras comprobar documentación; lockfiles. API REST tipada, proxy mismo origen, healthchecks, volúmenes, bind localhost. Perfil CPU: objetivo 8 GB RAM disponibles para Docker o menos, limitar BLAS threads a 2, no cargas pesadas al navegador. Entrenamiento batch al inicializar, cache por snapshot/versión, simulaciones pequeñas síncronas o job persistente simple si supera tiempo razonable. No fingir cancelación. Objetivos medibles, no garantías: navegación <2 s caliente, simulación 200 draws <5 s en máquina objetivo si posible, generación/entrenamiento <5 min; medir y ajustar.

Estructura:
- frontend/src/app, componentes, features, servicios, estilos; public/assets.
- backend/app/api, dominio, datos, modelos, escenarios, persistencia, tests.
- scripts/iniciar.ps1, detener.ps1, comprobar.ps1, reset_demo.ps1.
- documentacion/avances.md, arquitectura.md, decisiones.md, licencias.md, guion_demo.md, validacion.md.
- docker-compose.yml, .env.example, .gitignore, README actualizado.
- API /api/v1: /health, /contexto, /kpis, /medios, /modelos, /busqueda, /creativos, /experimentos (CRUD/diseñar/ejecutar/evaluar), /escenarios (CRUD/ejecutar/comparar/exportar), /oportunidades, /decisiones, /fiabilidad, /demo (incidencia/restaurar/reset). Contratos Pydantic/OpenAPI, ids, unidades, fecha corte, snapshot, evidencia, estados. Validar inputs, SQL parametrizado, no credenciales ni servicios expuestos públicamente.

## Día 1 · Fundaciones (6–8 h)
- D1.1 leer contratos, inspeccionar repo/Git y entorno, crear backlog por horas y criterios, anotar decisiones.
- D1.2 shell visual completo, tokens, navegación y componentes base; rutas no implementadas señaladas como en desarrollo.
- D1.3 Docker prod, migraciones, seed reproducible, entidades y negocio/medios/búsqueda/creatividad, health.
- D1.4 centro de mando real desde API, filtro común, KPIs reconciliados, pruebas integridad, screenshot.
Salida: arranque desde limpio, datos persistentes, UI base profesional, test de seed. Commit y push.

## Día 2 · Medición y primera oportunidad (7–8 h)
- D2.1 agregación semanal, MMM ligero con holdout, baseline naive y diagnóstico; guardar modelo.
- D2.2 visualización descomposición, respuesta/saturación, métricas atribuidas separadas.
- D2.3 motor económico común y primer radar de marca, vínculo a hipótesis.
- D2.4 tests de curvas, métricas, reconciliación y visual.
Salida: modelo computado y consultable con límites, no cifras de frontend. Commit y push.

## Día 3 · One Search, experimentación y valor de información (7–8 h)
- D3.1 vistas búsqueda, estratos, estimación recuperación histórica y supuestos.
- D3.2 recorte interactivo, ahorro, pérdida margen, equilibrio y abstención.
- D3.3 diseño geo pareado, MDE, ejecución sintética, efecto, IC y actualización de evidencia.
- D3.4 EVPI/EVSI discreto o MC ligero con coste; tests de caso positivo/negativo, experimento nulo y seed.
Salida: recorrido centro → búsqueda → experimento → estimación persistida. Commit y push.

## Día 4 · Creatividad y reinversión (7–8 h)
- D4.1 assets originales locales, biblioteca y filtros, etiquetas y métricas.
- D4.2 ajuste modelo ligero, pretest tres variantes, brief por reglas, prueba A/B simple.
- D4.3 escenarios base/ahorro/reinversión, orquestador común, optimizador con restricciones, MC.
- D4.4 pruebas no doble conteo, factibilidad, visuales.
Salida: selección creativa afecta escenario y cálculo real, comparación económica. Commit y push.

## Día 5 · Producto integrado (7–8 h)
- D5.1 CRUD escenarios, historial y aprobación/rechazo, exportaciones CSV/MD.
- D5.2 radar completo con enlaces y ranking; fiabilidad, incidencia y abstención/restauración.
- D5.3 recorrido E2E principal y alternativo, ajustes de UX, persistencia tras reinicio.
- D5.4 guion demo y documentación; recortar P1 antes de añadir complejidad.
Salida: flujo completo funcional, sin pantallas esenciales inertes. Commit y push.

## Día 6 · Congelación y QA (6–8 h)
- No añadir módulos. Arranque limpio con Docker en modo producción, migración/seed/reset, comprobar persistencia.
- pytest unitarias/integración, lint, typecheck, build, Playwright recorridos y capturas. Revisar escritorio y tablet, errores/estados vacíos, legibilidad, no inglés accidental.
- Medir tiempos/recursos, reducir datos o draws si necesario y documentar. Verificar cálculos con fixture manual, conciliación y que el bloqueo impida aprobar.
- Ensayar guion 7–10 min, preparar fallback snapshot conocido y exportación. README instalación Windows exacta, comandos reales, limitaciones, resultados tests. Commit final, push sin force, etiqueta v0.1.0-demo solo si criterios pasan y permisos lo permiten.
Salida: demo candidata, no producto de producción.

## Prioridad y contingencia
P0 flujo común antes que amplitud. Si retraso: reducir mercados visualizados, número de creatividades originales (mínimo 12 deseado), filtros secundarios, grafo, animaciones, exportaciones accesorias; mantener cálculo, persistencia, calidad/abstención y narrativa. Simplificar MMM a modelo regularizado fijo y señalar limitación; EVPI explícita como cota si EVSI no fiable, no falsificar. Si falta tiempo para funcionalidad P0, registrar pendiente y no marcar finalizada. No sacrificar último día de QA. 40–48 h estimadas, no garantizadas; integración completa puede requerir más.

## Matriz de aceptación
| ID | Prueba | Evidencia |
|---|---|---|
| A01 | Docker arranque limpio, health, reset | comandos/logs |
| A02 | seed y datos reconciliados, FK, sin leakage | pytest |
| A03 | MMM ajustado, holdout y limitaciones | reporte y UI |
| A04 | One Search cambia resultado y equilibrio correcto | fixture + E2E |
| A05 | geo aleatorizado, efecto/IC y actualización versionada | pytest + UI |
| A06 | creatividad pre/post, tres variantes, selección cambia escenario | E2E |
| A07 | base/A/B, optimización factible, coste neto e incertidumbre | invariantes + E2E |
| A08 | EVPI/EVSI correctos o cota explícita | unitarias |
| A09 | incidente bloquea decisión y restauración funciona | E2E |
| A10 | CRUD/decisión/exportación sobreviven reinicio | integración |
| A11 | todos controles esenciales funcionales, errores útiles | recorrido |
| A12 | revisión visual y accesibilidad básica | capturas reales |
| A13 | no IA local, agentes, datos reales, secretos ni API pagada obligatoria | auditoría |
| A14 | docs y commits remotos verificables | Git + README |

## Protocolo Git y entregables
Antes de editar: git status, git remote -v, git log; confirmar que origin es https://github.com/nacho-coding/margia.git. Si carpeta vacía, clonar en ella, no inicializar historia paralela. No hacer force push, no borrar cambios ajenos. Revisar diff y exclusiones (.env, tokens, node_modules, .venv, datos grandes, dumps, capturas pesadas). Commits por hito probado y push; si falla, informar. Al cerrar sesión registrar avances, próximos pasos y comandos reproducibles. Skills permitidas, sin subagentes. No publicar material interno ni datos de clientes. No declarar resultados no probados.
