# Avances y evidencia ejecutada

## 25/11/2026 · Inicio del Día 1

### Inspección

- Leídos íntegramente los ocho Markdown de raíz: AGENTS, README, ESPECIFICACION_MARGIA, DESIGN, DATOS_SINTETICOS, MODELOS_MATEMATICOS, PLAN_DESARROLLO y PROMPT_CODEX.
- `git status --short --branch`: `main...origin/main`, sin cambios iniciales.
- `git remote -v`: origin `https://github.com/nacho-coding/margia.git`.
- `git log -5 --oneline`: último commit `ccf1a64`.
- `git ls-remote origin refs/heads/main`: HEAD remoto `ccf1a645e152d05ae649d285477ebfb5ee715886`, igual al local (ejecución con acceso de red).
- Node `v26.13.1`, npm `11.20.0`, Docker CLI `29.9.3`, Compose `v5.7.1`. Los alias Windows `python`/`py` no contienen un intérprete utilizable; Python se ejecutará en contenedor.
- Docker Desktop inicialmente detenido; se ha iniciado con `Start-Process ... -WindowStyle Hidden`. Salud todavía pendiente de verificar.
- La red de la consola aislada no resuelve GitHub; se utiliza escalación de red autorizada para dependencias y Git. No se han leído ni mostrado credenciales.

### Tareas y pruebas previstas del incremento

Backlog completo en [backlog.md](backlog.md). Primer incremento: Compose de producción, migraciones y seed; tests de reproducibilidad/FK/reconciliación y economía, API y reinicio; shell/centro y vistas descriptivas; typecheck/build y capturas reales en cuatro resoluciones. No se declara ninguna de estas verificaciones como ejecutada todavía.

### Pendientes y riesgos

- Comprobar motor Docker, descargas y permisos de Git push.
- Medir generación y memoria; ajustar cobertura parcial explícita si hace falta.
- Modelos y recorrido causal completo reservados a D2–D5. No implementados al inicio.

## 25/11/2026 · Cierre técnico del Día 1

### Incremento funcional entregado

- Docker Desktop operativo. PostgreSQL 18, FastAPI/Python 3.13 y Next.js 16/React 19 en producción local, imágenes por digest y paquetes por lockfile. Solo `127.0.0.1:3000` publicado.
- 247.562 registros sintéticos: 730 días de negocio/medios, 24 mercados, ocho canales, 120 campañas, 50 grupos de búsqueda, 80 registros creativos y 12 diseños SVG locales originales. Coberturas parciales visibles.
- API única de KPIs, atribución, búsqueda, biblioteca, integridad y exportación. Filtros de periodo/mercado conservados en URL. No se suman atribuciones como pedidos ni gastos de vistas parciales como inversión nueva.
- Shell visual con navegación por ámbitos, centro económico real, tablas paginadas de Search, biblioteca y detalles, fiabilidad, metodología y reset explícito. Experimentación/escenarios señalados como en desarrollo, sin botones de ejecución ficticios.
- Leídos PRD.md y RFC.md íntegros; se conserva su commit local ajeno `e6b3f97`. Sin cambios a esos documentos.
- Aplicada Modern Web Guidance instalada por el usuario: búsqueda/lectura de guías y revisión de implementación. Fuentes/licencias y correspondencia de guías documentadas. Instalación local de la skill conservada e ignorada en Git; `skills-lock.json` fija su procedencia.

### Comandos y resultados realmente ejecutados

| Comando | Resultado |
|---|---|
| `docker compose up -d --build --wait --wait-timeout 180` | Tres servicios saludables, build de producción correcto |
| `scripts/iniciar.ps1` | Arranque completo probado; muestra URL real, sin exponer la clave local |
| `scripts/detener.ps1` + `scripts/iniciar.ps1 -SinBuild` | Conserva volumen y checksum |
| `scripts/comprobar.ps1` | 18 pytest pasan en 15,26 s; Ruff correcto; health listo |
| `docker compose … python -m pytest -q` | Baterías adicionales de reproducibilidad, economía, integridad y API pasan; una deprecación httpx en TestClient |
| `npm.cmd run test:e2e` | Última regresión: 6 passed (1,3 min); filtros, paginación, detalle, exportación, errores, foco y móvil |
| `npm.cmd run lint` / `typecheck` / `npm ls --depth=0` | Sin errores; árbol directo compatible |
| QA 7 rutas × 4 tamaños | 28 capturas reales; cero infracciones axe detectadas tras corregir contrastes; inspección visual de siete vistas |
| Pila `margia-validacion` desde PostgreSQL vacío | Migración y seed probados, fixture de decisión persiste tras reinicio; reset reconstruye mismos conteos/hash |
| `scripts/reset_demo.ps1 -Confirmar` | Reset principal correcto en 53,75 s; alineado con generador final |
| `git diff --cached --check` y revisión de exclusiones | Se corrige whitespace del DDL; .env, dependencias, dumps, cachés y capturas excluidos |

Hash lógico final: `6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d`. Primer seed medido: 41,364 s; reset aislado bajo carga: 69,408 s. Muestra de RAM en reposo: web 40,25 MiB, API 70,73 MiB, DB 113,4 MiB; no es pico ni memoria total de Docker/VM. Pila aislada detenida; demo principal disponible.

### Defectos encontrados y corregidos

- Query de periodo como Literal[int]: rechazaba el valor textual; convertido a entero validado contra el conjunto permitido.
- Build dentro del sandbox Windows no podía crear el proceso PostCSS; validación de producción realizada en Docker Linux, con éxito.
- Compatibilidad de TS 7 / ESLint 10: se fijan TS 6.0.3 y ESLint 9.39.5 con sus plugins compatibles. Queda aviso de fin de soporte de ESLint 9 en el instalador; revisar cuando Next admita la cadena completa nueva.
- Contraste del antetítulo y rótulo SEO/SEM, moneda en tarjetas móviles, espacio al ocultar un salto de línea y etiqueta sobre el wordmark creativo: corregidos y recapturados.
- Coherencia de categoría de creativo/campaña y checksum independiente del orden de inserción: corregidos, probados y demo reconstruida antes de cerrar versión inicial.
- Cachés de pytest/Ruff intentaban escribir en `/app` dentro del contenedor sin privilegios. Script corregido para desactivar esas cachés, sin elevar usuario.
- La primera prueba operativa se lanzó antes de seed saludable y con script no incorporado; se repitió con readiness, ruta y PYTHONPATH correctos. Solo la repetición satisfactoria cuenta como evidencia.

### Git y bloqueo de publicación

- Commit original de PRD/RFC conservado: `e6b3f97`.
- Primer hito probado: `c7f86dc` — «feat: crear base PostgreSQL y API reproducible con pruebas económicas».
- Interfaz probada: `64502e5` — «feat: conectar interfaz MARGIA con filtros y revisión visual accesible». Cierre documental consultable con `git log -4 --oneline`.
- No había identidad Git configurada; los commits de esta sesión usan identidad de herramienta `Codex <codex@openai.com>` solo en el comando, sin modificar la identidad global del usuario.
- `git push origin main`: GitHub devuelve 403, «Permission to nacho-coding/margia.git denied to ignaciofontal». El conector confirma permiso **read** para esa cuenta. Intento con propietario y credenciales no interactivas: no hay credencial disponible. No se cambia remoto ni se usa force.
- El usuario elige habilitar escritura para `ignaciofontal`; se facilita enlace de colaboradores y se indica aceptar la invitación. El conector disponible no incluye añadir colaboradores. **Reintento de cierre ejecutado: mismo 403**. El último HEAD remoto observado sigue en `ccf1a64`; no se declara que el PRD/RFC o el código estén subidos. Los cambios quedan confirmados localmente, preparados para push normal cuando la cuenta tenga escritura efectiva.

### Próximo incremento

Día 2, D2.1–D2.3: agregación semanal, MMM regularizado con holdout y baseline, diagnóstico, curvas y primer radar económico. La economía aritmética ya está probada; la recuperación de Search y el flujo geo → creatividad → optimización → decisión aún no están implementados. No hay candidata v0.1.0-demo ni etiqueta final.

Evidencia detallada y límites: [validacion.md](validacion.md). Backlog actualizado: [backlog.md](backlog.md). No se han utilizado agentes, LLM locales, GPU ni APIs de pago obligatorias.

## 25/11/2026 · Inicio del incremento de Medición (D2.1–D2.2)

- Releídos AGENTS y los seis contratos obligatorios, avances, backlog, arquitectura y decisiones. Inspección: `main...origin/main [ahead 4]`, limpio; remoto correcto, HEAD remoto `ccf1a64`, sin divergencia observada.
- Tres contenedores principales saludables. La consola requiere acceso fuera del sandbox a Docker y localhost; se ejecutan comprobaciones acotadas, sin cambiar la seguridad de Windows.
- Tareas: 104 semanas completas nacionales; MMM restringido con adstock/Hill y controles previos; dos folds rolling anteriores a 20 semanas reservadas; baseline estacional; bootstrap por bloques, sensibilidad y abstención; artefacto PostgreSQL; API tipada y vista con descomposición/curvas/soporte/diagnóstico. El filtro de mercado no inventa estimaciones locales.
- Pruebas previstas: invariantes de curvas y reconciliación, alteración de holdout sin modificar parámetros aprendidos, semilla, persistencia/idempotencia/migración/reset; pytest/Ruff, lint/typecheck/build, Playwright y capturas con axe en cuatro tamaños.
- `git push --dry-run origin main` sigue devolviendo 403 para `ignaciofontal`. No se cambia el remoto ni se reescribe la historia. Se ha comunicado la necesidad de escritura efectiva y aceptación de la invitación; se reintentará al cerrar el hito.
- La primera batería del incremento detecta un error en la prueba de agregación: comparaba DATE con string tipado VARCHAR; corregida para pasar `date`. No se declara satisfactoria esa ejecución (25 passed, 1 failed).

## 25/11/2026 · Cierre verificado de Medición (D2.1–D2.2)

### Entregado

- MMM nacional CPU real de 104 semanas, siete canales de demanda, controles, adstock/Hill y regresión restringida regularizada. SEM marca no se duplica como demanda. Dos validaciones rolling antes de 20 semanas reservadas; escalas exclusivamente de train.
- Modelo persistente con inputs, configuración, semilla, versiones, checksum, diagnóstico y réplicas conjuntas. Migración 0002; preparación batch al arrancar y conservación tras reiniciar. Reset atómico reconstruye el modelo.
- API tipada de modelos/medición/curvas; filtro de periodo solo selecciona semanas completas. Mercado individual devuelve no aplicable, sin prorratear estimaciones nacionales; la atribución mantiene el filtro.
- Medición integra ajuste/naive, banda empírica, descomposición y residual reconciliados, curvas con soporte/extrapolación y marginal, valoración descriptiva de términos, metodología y estado del modelo. Todas las cifras proceden del backend. Fiabilidad incorpora el diagnóstico vigente.
- Resultado adverso conservado: WAPE 1,5583 % frente a 3,1699 % naive, pero sensibilidad del reparto 5,6253 > umbral 1. **Recomendaciones bloqueadas**. No se fuerza un resultado favorable ni se presenta ese reparto como incrementalidad causal.
- La revisión detectó segunda contracción en refits regularizados. Se conserva mmm-1.0.0 y se añade mmm-1.0.1 con errores de refit centrados y medios truncados; bandas de escenarios condicionales, sin garantía de cobertura ni IC causal. Cobertura medida final: 19/20 semanas.

### Comandos y evidencia final

| Comando / comprobación | Resultado |
|---|---|
| `docker compose up -d --build --wait --wait-timeout 180` | Build de producción, TypeScript y tres servicios saludables |
| `scripts/comprobar.ps1` | 26 passed, 1 warning en 22,74 s; Ruff y health correctos |
| `npm.cmd run lint` / `npm.cmd run typecheck` | Sin errores |
| `npm.cmd run test:e2e` | 9 passed (1,5 min), incluida regresión D1 |
| Siete rutas × cuatro resoluciones | 28 capturas con canvas preparados; cero infracciones axe y sin scroll global; inspección visual de Medición, descomposición y metodología |
| Pila nueva `margia-mmm-qa` | Migraciones desde vacío, seed y ajuste saludables |
| `tests/operacion.py preparar/verificar` tras reinicio | Decisión fixture, negocio, hash, resultado y fecha de creación del MMM conservados sin reentrenar |
| `tests/operacion.py reset` en pila aislada | Reconstruye mismo resultado (salvo duración) y hash; nueva fecha de creación, elimina fixture; 43,841 s |
| `docker compose -p margia-mmm-qa down` | Detenida sin borrar volumen; demo principal conservada |
| 15 lecturas de API de modelo guardado | Mín. 22,10 ms; mediana 23,79 ms; máx. 288,78 ms; no es navegación completa |
| RAM de contenedores durante QA | Web 84,96 MiB; API 96,23 MiB; DB 102,8 MiB; no picos ni VM |
| `git diff --cached --check`, revisión de exclusiones | Sin defectos de whitespace; .env, dependencias y capturas fuera de staging |

Modelo vigente `mmm-4246cd7b830a0a9f7cfc`, versión `mmm-1.0.1`; ajuste observado 0,153 s, sin seed. Checksum del universo permanece `6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d`. Detalles, fallos iniciales y limitaciones en [validacion.md](validacion.md); método completo en [modelo_mmm.md](modelo_mmm.md). Se mantiene el warning heredado httpx/TestClient.

### Git, pendientes y riesgos

- Backend probado: `4477940` — «feat: ajustar MMM nacional con validación temporal y persistencia».
- Interfaz probada: `d0ad46e` — «feat: mostrar diagnóstico MMM y curvas con soporte y límites». Identidad temporal Codex, sin modificar configuración global.
- Reintento real `git push origin main`: **403**, «Permission to nacho-coding/margia.git denied to ignaciofontal». No se publica, no se cambia origin ni se usa force. Escritura efectiva/aceptación de invitación todavía pendiente. Los cuatro commits previos se conservan junto a los nuevos; el cierre documental se añade como commit separado. El remoto observado sigue en `ccf1a64`.
- **D2.3 no cerrado.** Próximo corte: evidencia histórica y estimador Search (D3.1) para alimentar un radar económico defendible. Mientras tanto se mantiene la hipótesis observada del centro sin impacto esperado inventado. La decisión de orden queda registrada en decisiones.md.
- Continúan pendientes geo/EVSI, creatividad predictiva/A-B, escenarios/orquestador/optimización, decisiones e incidencias. El Día 2 completo y la POC no se declaran terminados.
- Sin agentes/subagentes, LLM locales, GPU, dependencias nuevas ni servicios externos de runtime. No se han modificado los contratos de producto para acomodar el resultado.

## 25/11/2026 · Cierre pendiente D2.3 y dependencia Search

- El usuario solicita resolver la dependencia, sin arrastrar D2.3. Se mantiene el contrato matemático: implementar evidencia histórica y estimador directo de cambio de pedidos por euro ahorrado, sin inferir recuperación de SEO/SEM. Se cerrarán radar y simulador juntos, tras pruebas.
- Inspección inicial: árbol limpio, `main` siete commits por delante; contratos ya revisados y conservados. Plan: históricos explícitos de arranque sin alterar hechos ni checksum, asignaciones/observaciones persistentes, estimador por pares con pooling e incertidumbre, economía compartida, hipótesis con ID, simulaciones guardadas y radar funcional.
- Pruebas previstas: preservación del mundo y su hash; reproducibilidad de históricos, aleatorización/unidades, estimador sin verdad/futuro; recorte 0/100, costes comunes/incrementales, pérdidas y equilibrio, soporte, abstención y no doble gasto. API, persistencia/reset aislados, pytest/Ruff, lint/TypeScript/build y recorrido visual/Playwright.
- Skill Modern Web Guidance: consultada guía `forms` para validación nativa, labels, rangos y envío accesible; no se añaden dependencias.
- Acceso GitHub resuelto por el usuario durante el incremento: `git fetch origin main` sin divergencias y `git push origin main` correcto (`ccf1a64..ea9a8ab`). Los siete commits previos ya están publicados. El código nuevo permanece sin confirmar hasta superar sus pruebas.

## 25/11/2026 · Día 2 cerrado: radar y One Search verificados

### Entregado y dependencia resuelta

- **D2.3 cerrado**, con D3.1 implementado como dependencia: primer radar económico de marca enlazado a una hipótesis real y al simulador. El centro muestra evidencia histórica disponible; no sigue anunciando este trabajo como próximo incremento.
- 12 históricos sintéticos explícitos de arranque, 288 asignaciones y 576 observaciones pre/post. Mismo mecanismo de captura del universo, pares aleatorizados, placebo y subsemillas registradas. No se añaden a los KPIs ni se hacen pasar por nuevas ejecuciones del usuario.
- Modelo `search-1.0.0` (`search-90c0cd70be0bef7b8d7a`), bootstrap de 12 pares completos y pooling nacional. Estima cambio total de pedidos por euro ahorrado; recuperación SEO/directo no identificada, como permite el contrato matemático. No depende del reparto MMM bloqueado.
- Simulador 0–100 %, soporte 25/50/75 %, costes experimentales, cuota común/incremental, contribución, bandas, riesgo, equilibrio en pedidos, comparación y waterfall reconciliados desde Python. Mercado individual, otro horizonte o extrapolación se señalan como hipótesis; escenarios negativos recomiendan mantener.
- Evaluaciones inmutables por contenido, input/snapshot/modelo/semilla guardados y reutilización declarada. Históricos consultables con asignaciones y observaciones. Enlace desde radar lleva ID y foco al formulario; errores conservan valores y permiten reintentar.

### Evidencia ejecutada

| Comando / comprobación | Resultado |
|---|---|
| `docker compose up -d --build --wait --wait-timeout 180` | Build de producción, TypeScript y tres servicios saludables |
| `docker compose run --rm --no-deps --volume "${PWD}/backend:/app" backend python -m pytest -q -p no:cacheprovider` | 39 passed, 1 warning en 29,10 s; preservación exacta del mundo, dominio, modelos y API |
| `docker compose exec -T backend ruff check --no-cache .` | Correcto; imports iniciales ordenados con Ruff |
| `npm.cmd run lint` / `npm.cmd run typecheck` | Sin errores |
| `npm.cmd run test:e2e` | 13 passed (1,8 min); incluye regresión de fundaciones y MMM |
| `npm.cmd run test:e2e -- tests/search.spec.ts` | Repetición final tras ajuste móvil: 4 passed (20,2 s) |
| Capturas / axe | 28 vistas generales, cuatro paneles de evaluación y un negativo, más dos de MMM; cero infracciones detectadas y sin desbordamiento global |
| QA visual manual | Centro actualizado, simulador 1440/1280/móvil y waterfall negativo; etiquetas móviles acortadas y leyenda SEO/SEM separada de fechas |
| Pila nueva `margia-search-qa` | Migraciones 0001–0003 desde PostgreSQL vacío; seed y modelos preparados |
| `tests/operacion.py preparar/verificar` tras reinicio | Conserva decisión fixture, hechos, MMM, evidencia Search y evaluación guardada exacta |
| `tests/operacion.py reset` aislado | Reconstruye mismos hechos y modelos, elimina evaluaciones/fixture; 52,718 s |
| `docker compose -p margia-search-qa down` | Pila aislada detenida sin borrar volumen; principal conservada |

El checksum original sigue exactamente en `6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d`. Ejemplo calculado, no fijado en UI: recorte 50 %, 28 días nacionales, costes nuevos cero → ahorro 34.898,03 €, cambio de margen −18.401,94 €, neto 16.496,09 €, p05–p95 −7.104,57 a 39.307,73 €, 9,5 % de draws negativos. Con cuota incremental de 100.000 € el resultado es negativo y recomienda mantener. No se eliminan pérdidas ni se estrechan bandas para favorecer el relato.

### Git y siguiente hito

- Backend probado: `2d4c194` — «feat: estimar efecto de marca con evidencia experimental y economía común».
- Interfaz probada: `c9fd02d` — «feat: conectar radar de marca con simulación y evidencia consultable». Cierre documental separado; identidad temporal Codex, sin alterar configuración global.
- Acceso `ignaciofontal` efectivo y 403 resuelto. Siete commits previos y los dos nuevos de código publicados con push normal a `origin/main` (`ea9a8ab..c9fd02d`), sin cambiar remoto ni forzar historia. `git ls-remote origin refs/heads/main` verifica `c9fd02d5761d10eb2d2f93d6123fc0b3e911d503`. El cierre documental se confirma y publica como commit separado.
- **No queda D2.3 pendiente. Días 1 y 2 cerrados; D3.1 disponible.** Siguiente hito del plan: D3.2, nuevos experimentos geográficos con diseño, ejecución y actualización de evidencia, seguido de D3.3/valor de información. No se confunden las fixtures de arranque con esas funciones futuras ni se declara terminada la POC completa.
- Método y límites: [one_search.md](one_search.md). Pruebas y advertencias: [validacion.md](validacion.md). Permanece la deprecación conocida de httpx/TestClient. Sin agentes, LLM, GPU, dependencias nuevas ni datos reales.
