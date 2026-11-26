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

## 25/11/2026 · Inicio de experimentación y valor de información (D3.2–D3.3)

- Inspección: `main...origin/main`, limpio, HEAD `575826c`, origin correcto y `git fetch origin main` sin divergencias; tres servicios Docker saludables. Releídos los seis contratos, AGENTS, avances, backlog, arquitectura y decisiones. Trabajo secuencial sin agentes.
- Tareas: diseño geo con preperiodo, parejas y asignación reproducible; MDE y equilibrio; nuevas observaciones sintéticas posteriores al corte; evaluación por pares, guardrails y actualización versionada Search por sustitución; valor de información con costes y horizonte explícitos; interfaz y navegación desde Search.
- Pruebas previstas: nulo/negativo, semilla, unidades aleatorizadas, ausencia de verdad/futuro en estimador, estados/idempotencia, abstención, sustitución sin acumular ramas dependientes, EVSI/EVPI y prueba cara; regresión pytest/Ruff, lint/TypeScript/build, Playwright/axe/capturas, arranque vacío/reinicio/reset aislados. No se declaran ejecutadas todavía.
- Modern Web Guidance: consultada guía `forms`; sin dependencias nuevas. Fuentes matemáticas primarias: NIST (comparaciones pareadas) y SciPy (cuadratura normal).

## 25/11/2026 · Día 3 cerrado: geo y valor de información verificados

### Implementado

- Laboratorio funcional desde One Search: objetivo/hipótesis, pedidos como KPI, selección de mercados, preperiodo, duración, recorte, coste, cuota, riesgo y semilla. Emparejamiento por volumen/tendencia/variabilidad, asignación 0,5 dentro de par, equilibrio, placebo, calendario y MDE. Aviso cuando el efecto de referencia queda por debajo del MDE y supuestos de spillover explícitos.
- Ejecución real del mundo sintético en rama posterior al corte, separada del negocio. Guarda asignaciones y observaciones nuevas pre/post. El estimador no lee verdad ni futuro: compara pares, normaliza tamaños y calcula efecto/IC con el par como unidad.
- Evaluación y abstención con guardrails; aceptación explícita crea versión Search o reutiliza evidencia idéntica, sin pooling de ramas dependientes. Cadena de versiones persistente; diseños obsoletos no sobrescriben el vigente. Evaluaciones antiguas y modelos anteriores conservados. Fiabilidad bloquea si falta evidencia vigente.
- EVPI/EVSI para mantener/recortar, likelihood normal ligado al MDE, coste de prueba y oportunidad de esperar en un horizonte comparable. `geo-1.0.1` conserva las 400 réplicas, incluidas colas raras, tras detectar que 40 cuantiles podían ocultarlas. No se obliga a que experimentar compense. Reinversión sigue en D4.
- Interfaz adaptable, validación/error/reintento/foco, historial con origen, tablas de observaciones, gráfico de efecto e IC y pre/post/contrafactual. Backend calcula todas las cifras; frontend presenta. Sin nuevos servicios, migraciones innecesarias, IA ni dependencias.

### Comandos y resultados ejecutados

| Comando / comprobación | Resultado |
|---|---|
| `docker compose up -d --build --wait --wait-timeout 180` | Build de producción y tres servicios saludables, solo localhost |
| `./scripts/comprobar.ps1` | 61 passed, 1 warning en 25,39 s; salud y Ruff correctos |
| pytest completo con código final y prior completo | 61 passed, 1 warning en 22,07 s; Ruff correcto |
| pytest completo con evidencia geo aceptada | 61 passed, 1 warning en 19,54 s, antes del ajuste de prior; regresión de estado posterior a uso |
| `npm.cmd run lint` / `typecheck` | Sin errores ni advertencias finales |
| `MARGIA_QA_URL=…:3002 npm.cmd run test:e2e` (variable de PowerShell) | 16 passed (2,0 min) en la pila aislada |
| `npm.cmd run test:e2e -- tests/geo.spec.ts` tras geo-1.0.1 | 3 passed (27,2 s), capturas y axe repetidos |
| pytest geo de la imagen final, secuencial | 22 passed, 1 warning en 5,90 s |
| Capturas / revisión | 28 vistas generales y resultados en cuatro tamaños; cero infracciones axe detectadas, sin desbordamiento global; inspección manual |
| Pila nueva `margia-geo-qa` | Arranque desde PostgreSQL vacío, migraciones 0001–0003 y seed/modelos preparados |
| `tests/operacion.py preparar/verificar` tras reinicio | Conserva hechos, decisión fixture, MMM, modelos/evaluaciones Search y protocolo/observaciones/evaluación geo; sin reejecutar |
| `tests/operacion.py reset` aislado | 41,342 s; mismo checksum, elimina ramas de usuario y restaura Search original |
| `docker compose -p margia-geo-qa down` | Pila temporal detenida, volumen conservado; demo principal saludable en localhost:3000 |
| Diseño + guardado con 400 estados, muestra CPU | 0,651 s; EVPI 38,3356 €, EVSI 0,5434 €, corrección de límites 0 €; no benchmark general |

Checksum del negocio intacto: `6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d`. Pruebas nulas, adversas, evidencia escasa, costes altos, copias idénticas y versiones obsoletas cubiertas. Se mantienen resultados negativos y bandas amplias. Fallos iniciales y correcciones, incluida interferencia entre dos comprobaciones de QA repetida secuencialmente, documentados en [validacion.md](validacion.md); no se cuentan como pruebas satisfactorias.

### Git, límites y siguiente fase

- Backend probado: `6727ac5` — «feat: ejecutar experimentos geo y valorar información con evidencia versionada»; corrección de colas y riesgo: `55ffc1c` — «fix: conservar colas de incertidumbre en el valor de información»; interfaz: `8d21059` — «feat: conectar laboratorio geo con Search y revisión visual accesible». Se conserva identidad temporal Codex, sin cambiar configuración global.
- `git fetch origin main` sin divergencias. Push normal de los tres hitos correcto: `575826c..8d21059`. `git ls-remote origin refs/heads/main` confirma `8d21059c94eeeb274da388e1c98f6dd04097358a`. Origin se mantiene en `https://github.com/nacho-coding/margia.git`, sin force ni cambios ajenos. El cierre documental se confirma y publica como commit separado.
- **Días 1–3 cerrados.** Siguiente: D4.1, modelo creativo ligero, tres variantes y brief por reglas; después A/B y orquestador/optimización. Día 5: CRUD de escenarios, decisiones/exportación e incidencias/restauración; Día 6: congelación, regresión final, rendimiento, auditoría y presentación. P1/P2 continúan aplazados.
- El reparto MMM permanece bloqueado por sensibilidad: el futuro orquestador debe respetarlo o aportar calibración compatible, sin relajar umbrales. EVSI es aproximado y depende del likelihood; no se promete potencia real ni independencia entre ramas sintéticas. La aprobación de medios y la POC completa siguen pendientes.
- Método y límites en [experimentos_geo.md](experimentos_geo.md). Sin agentes/subagentes, datos reales, LLM, GPU ni servicios externos de runtime.

## 25/11/2026 · Inicio de creatividad predictiva (D4.1 del backlog)

- Inspección: árbol limpio en `main`, HEAD `a957663`, origin correcto y fetch sin divergencias. Tres contenedores principales saludables. Releídos AGENTS, seis contratos, avances y pendientes; trabajo secuencial sin agentes.
- Alcance: modelo binomial regularizado de CTR con denominadores reales, validación temporal y por composición/campaña, referencia por canal, incertidumbre por grupos y artefacto persistente. Biblioteca con filtros y pretest de tres composiciones locales, brief por reglas y selección guardada para pasos posteriores.
- Restricción identificada: 28 días; categoría/tono/CTA ligados y composición no identificada por el modelo. Se estimarán paquetes observados; las composiciones nuevas compartirán referencia contextual sin inventar diferencias ni un ganador. El multiplicador económico seguirá en 1 hasta evidencia compatible. D4.2 A/B y D4.3 escenarios permanecen fuera de este corte.
- Pruebas previstas: separación de campañas/composiciones y fechas, alteración de holdout sin cambiar parámetros, CTR ponderado, reproducibilidad, bandas y abstención, integridad/identidad de hechos, API/selección, arranque vacío/reinicio/reset; pytest/Ruff, lint/TypeScript/build y Playwright/axe/capturas. Sin verificaciones nuevas declaradas aún.
- Modern Web Guidance: guía `forms` consultada; se reutilizan componentes accesibles y activos originales, sin dependencias nuevas.

## 25/11/2026 · D4.1 cerrado: biblioteca y pretest creativo contextual

### Implementado y límites respetados

- Biblioteca con filtros de canal, categoría, audiencia y objetivo, ordenación por ID/inversión/CTR/CVR, paginación, detalle y vacío real. Se conservan las 12 composiciones observadas, 80 registros y todos los hechos originales.
- Modelo `creatividad-1.0.0`: binomial de clics/impresiones, ridge fija 10, train/holdout separados por composición/campaña y fecha, naive por canal y 200 refits de grupos completos. Parámetros, semilla, checksum, soporte y métricas persistidos. No importa el mundo ni usa verdad/futuro; las lecturas y filtros no reentrenan. CVR sigue siendo conversión/clic observado en train por canal.
- Tres composiciones precreadas por perfil (nueve SVG originales locales), formulario de contexto, referencia CTR y esperanza de clics, brief por reglas, selección persistente e historial. Migración aditiva 0004. El frontend presenta; Python calcula. Sin IA generativa fingida ni servicios nuevos.
- El histórico no identifica efectos diferenciales de estas composiciones: las tres comparten referencia y bandas, sin ganador. Categoría/tono/CTA forman un paquete. Multiplicador económico 1 hasta evidencia compatible. La selección guarda una hipótesis; A/B y aplicación en escenarios continúan pendientes.
- Holdout calculado: pérdida logarítmica 0,069705 frente a naive 0,070046; CTR observado 1,3089 %, modelo agregado 1,2489 %. Estado **limitado**. Solo 19,05 % de tasas de filas reservadas dentro de las bandas de parámetros; se explica que no son intervalos predictivos ni IC causales. No se oculta este diagnóstico ni se regenera el seed para mejorarlo.

### Comandos y resultados ejecutados

| Comando / comprobación | Resultado |
|---|---|
| `node scripts/generar_variantes.mjs` | Nueve SVG originales, productos propios reutilizados, licencia/procedencia registradas |
| Alembic 0004 sobre principal y arranque vacío de QA | Dos tablas nuevas, sin borrar hechos; migraciones 0001–0004 correctas en la pila nueva |
| pytest creativo | 12 passed, 1 warning en 2,41 s |
| pytest completo con código montado | 73 passed, 1 warning en 22,92 s; Ruff correcto |
| `docker compose -p margia-creatividad-qa up -d --build --wait --wait-timeout 180` | Build final correcto y tres servicios saludables en 127.0.0.1:3002 |
| `npm.cmd run lint` / `typecheck` | Sin errores ni advertencias finales |
| Playwright específico inicial | 4 passed (21,5 s), antes de los últimos ajustes visuales |
| `MARGIA_QA_URL=…:3002 npm.cmd run test:e2e` (variable PowerShell) | Regresión completa final: 20 passed (2,2 min) |
| Capturas/axe | Cuatro tamaños del pretest y comparadores de tres perfiles; regresión general de las siete rutas, sin infracciones axe detectadas ni desbordamiento global; revisión manual escritorio/móvil |
| `tests/operacion.py preparar` → reinicio → `verificar` | Conserva hechos, MMM, Search/geo, modelo creativo con fecha original, pretest y selección exactos; sin reentrenar |
| `tests/operacion.py reset` en QA | 42,154 s; mismo checksum, modelo reproducible, hipótesis de usuario eliminadas, evidencia inicial restaurada |
| `docker compose up -d --build --wait --wait-timeout 180` | Principal actualizada conservando volumen; tres servicios saludables, solo localhost:3000 |
| `./scripts/comprobar.ps1` contra imagen final principal | 73 passed, 1 warning en 25,94 s; Ruff y salud correctos |
| `docker compose -p margia-creatividad-qa down` | Pila aislada detenida, volumen conservado; principal saludable |

Comprobación final API principal: modelo `creatividad-bfce2ee924571d327baa`, nueve variantes disponibles, estado limitado. El checksum original sigue en `6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d`. Ajuste creativo observado 1,043 s en la principal / 1,017 s en QA; muestras CPU, no benchmark general. Se mantienen avisos conocidos de httpx/TestClient y del entorno de color Playwright.

Un rebuild intermedio falló con E/S de caché Turbopack y Docker se detuvo. Se recuperó reiniciando Desktop, con recuperación automática de PostgreSQL, y se retiraron por ID 37 entradas de caché regenerable de MARGIA del día (1,63 GB), sin eliminar volúmenes ni datos. Build, regresión y operación finales se repitieron correctamente. C: sigue con alrededor de 1,3 GiB libres: riesgo de entorno para futuras compilaciones; no se atribuye definitivamente la caída a esa condición. Detalle en [validacion.md](validacion.md).

### Git y continuación

- Backend probado: `e979811` — «feat: estimar CTR contextual y guardar hipótesis creativas trazables».
- Interfaz/recursos probados: `fc5ce9b` — «feat: conectar biblioteca con pretest visual y selección persistente».
- Fetch sin divergencias; push normal a `origin/main` correcto (`a957663..fc5ce9b`). `git ls-remote origin refs/heads/main` confirma `fc5ce9bb7987908ba71af9c84ed9505ffdac7dd7`. Sin force, cambio de remoto ni configuración global de identidad; cierre documental como commit separado.
- **Días 1–3 y D4.1 verificados.** Siguiente: D4.2 A/B creativo aleatorio con denominadores, incertidumbre, coste, multiplicidad y actualización versionada; después D4.3 orquestador base/ahorro/reinversión y optimización factible. El reparto MMM continúa bloqueado por sensibilidad, sin relajar umbrales.
- Día 5: CRUD de escenarios, ejecuciones/decisiones/exportaciones, incidencias/restauración y recorrido integrado. Día 6: congelación, regresión A01–A14, rendimiento, revisión visual, secretos/licencias y presentación. P1/P2 aplazados; no se declara completo el Día 4 ni la POC.
- Método completo: [creatividad.md](creatividad.md). Modern Web Guidance `forms` aplicada con validación nativa/API, foco, textarea redimensionable y submit bloqueado solo durante POST real. Sin agentes/subagentes, datos reales, LLM, GPU ni dependencias de runtime nuevas.

## 25/11/2026 · Inicio de revisión fotográfica y adaptación por plataforma

- Solicitud del usuario: sustituir el aspecto de boceto por ejemplos realistas y adaptados a TikTok, Meta, Display y YouTube; preparación simulada permitida. Árbol limpio en `main`, HEAD `589d0df`, origin correcto y fetch sin divergencias. Releídos los contratos y el estado verificado; trabajo secuencial sin agentes.
- Tareas: nueve imágenes fotográficas sintéticas mediante Imagegen durante el desarrollo, empaquetado WebP ligero y local, composiciones específicas por placement, integración en biblioteca/pretest, preparación visual con carga/decodificación reales y aviso discreto de catálogo precreado. Conservar rutas antiguas, modelos, resultados guardados y checksum del negocio.
- Pruebas previstas: versiones/placements y metadatos por canal en API, conservación de evaluaciones anteriores, carga de todas las imágenes y proporciones, cambio de plataforma, preparación/error/reintento, móvil y reduced-motion, pytest/Ruff, lint/TypeScript/build y Playwright/axe/capturas. No se declaran todavía ejecutadas las comprobaciones de este incremento.
- Skills: Imagegen integrada y Modern Web Guidance `optimize-image-priority` / `responsive-design`. Sin dependencias nuevas de IA ni llamadas generativas de runtime. La simulación se identifica como tal, sin alterar estimaciones ni fingir evidencia de rendimiento de las fotografías nuevas.

## 25/11/2026 · Revisión fotográfica por plataforma verificada

- Nueve fotografías sintéticas generadas con Imagegen durante el desarrollo: producto, material y uso en hogar/moda/belleza. Empaquetadas localmente como WebP (1.047.498 bytes total, máximo 169.146 por imagen), con dimensiones/hash/procedencia y prompts exactos conservados. La segunda pasada del empaquetador mantiene los bytes; rechaza sobrescribir una ruta versionada con contenido distinto. Los PNG pesados y rutas locales no se publican.
- Catálogo de 36 composiciones posibles, tres por perfil y plataforma. Meta 4:5, TikTok 9:16, Display 1200:628 y YouTube 16:9 con tratamientos propios; los dos canales de vídeo muestran fotogramas estáticos. La biblioteca muestra recreaciones señaladas y permite consultar la composición histórica. No se modifican los hechos ni las métricas para aparentar que las fotografías ya tuvieron rendimiento.
- «Generar propuestas de ejemplo»: preparación simulada con carga/decodificación real, estados, error/reintento, foco y bloqueo de controles solo durante trabajo. Después presenta imágenes, referencia calculada, brief y selección. Cambiar de plataforma retira las propuestas anteriores hasta preparar el nuevo contexto. Imágenes sintéticas/precreadas identificadas, sin llamadas IA fingidas en runtime ni progreso inventado.
- Rutas y versiones nuevas `fotografia-2.0.0` / `composicion-2.0.0`. Evaluaciones/selecciones anteriores y sus SVG conservados exactamente. Modelo creativo, semilla, particiones y parámetros sin cambios; multiplicador 1 y sin ganador visual identificado. A/B y escenarios mantienen su alcance pendiente.

| Comando / comprobación | Resultado |
|---|---|
| Imagegen integrada | Nueve imágenes generadas e inspeccionadas; prompts en `documentacion/creatividad_prompts.json` |
| `node scripts/preparar_imagenes.mjs`, dos pasadas | Nueve WebP locales, hashes/tamaños verificados, sin dependencia nueva |
| pytest con código montado / Ruff | 78 passed, 1 warning en 22,63 s; Ruff correcto |
| `npm.cmd run lint` / `typecheck` | Correctos |
| Builds Docker de QA y principal | Correctos, servicios saludables, persistencia conservada |
| Playwright creativo inicial | 6 passed (40,4 s), antes del ajuste final de encuadre Meta |
| Regresión completa final `npm.cmd run test:e2e -- --trace off` en QA | 22 passed (2,1 min), capturas y accesibilidad activas |
| Capturas / revisión visual | Biblioteca, cuatro tamaños del pretest, cuatro placements escritorio/móvil y tres perfiles; axe sin infracciones detectadas ni desbordamiento global |
| `./scripts/comprobar.ps1` contra imagen final | 78 passed, 1 warning en 22,69 s; Ruff y salud correctos |
| Operación QA preparar → reinicio → verificar | Modelo, texto, recursos, placement, pretest y selección exactos; sin reentrenar |
| `docker compose -p margia-creatividad-qa down` | Pila aislada detenida sin borrar volumen; principal saludable en localhost:3000 |

Checksum original intacto: `6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d`; modelo `creatividad-bfce2ee924571d327baa`, versión `creatividad-1.0.0`, limitado. No hay migraciones nuevas ni reset de la demo principal. El reset de D4.1 no se repite en esta revisión visual.

Una regresión previa dio 21 passed/1 failed por `ENOSPC` al guardar capturas y trazas, no se cuenta como satisfactoria. Se retiró solo caché `.next` del proyecto tras verificar su ruta (36,96 MiB); la repetición completa sin grabación de trazas pasa manteniendo screenshots y axe. C: sigue con unos 130 MiB libres: riesgo de entorno abierto. Sin borrar volúmenes, datos ni fotografías. Avisos heredados httpx y color de Playwright permanecen. Detalles, fuentes de formato y límites en [validacion.md](validacion.md) y [creatividad.md](creatividad.md).

- Recursos/catálogo probados: `dcf7738` — «feat: incorporar fotografía sintética y catálogo por plataforma».
- Interfaz probada: `5106181` — «feat: preparar propuestas visuales adaptadas a cada plataforma».
- Fetch sin divergencias; push normal correcto (`589d0df..5106181`), HEAD remoto confirmado `5106181a744d9b60cac02cdefa443bc7424a507c`. Se conserva `origin/main`; cierre documental separado, sin force ni cambios ajenos.
- Siguiente hito sigue siendo D4.2 A/B; después D4.3 orquestador/optimización, Día 5 integración/decisiones/incidencias y Día 6 congelación/QA/presentación. El reparto MMM continúa bloqueado por sensibilidad. Esta revisión mejora D4.1; no declara cerrados el Día 4 ni la POC.
- Imagegen y guías web aplicadas por el propio Codex, secuencialmente, sin agentes ni modelos locales. Recursos de runtime enteramente locales.

## 25/11/2026 · Inicio de A/B creativo (D4.2)

- Inspección: `main` limpio, HEAD `3a7f211`, origin correcto y fetch sin divergencias. Releídos los seis contratos, instrucciones permanentes, avances y backlog; sin agentes.
- Tareas: protocolo congelado desde un pretest, dos o tres brazos, asignación aleatoria por oportunidad sintética y equilibrada por fecha, observaciones nuevas posteriores al corte, denominadores/costes comparables, IC de diferencias de CTR con multiplicidad, CVR secundario separado, aprendizaje versionado por contexto y sin pooling de ramas dependientes. Conservar hechos y evaluaciones anteriores; no inferir beneficio desde clics.
- Pruebas previstas: checksum original, semilla/asignación reproducible, futuro inaccesible antes de ejecutar, nulo/adverso, ceros y denominadores, multiplicidad, costes una vez, validez/abstención, duplicados/obsolescencia, conservación de versiones, API, persistencia/reset aislado, pytest/Ruff, lint/TypeScript/build y Playwright/axe/capturas. Todavía no ejecutadas para D4.2.
- Entorno: C: tenía 106,5 MiB libres. Lectura de VHD denegada por permisos de Hyper-V; no se compacta ni se modifica el disco. TRIM sobre el montaje Docker solo informa 6,9 MiB y no resuelve espacio. Se verifica la ruta absoluta de `_cacache` de npm y se elimina únicamente esa caché de descargas regenerable (2.525,3 MiB), conservando paquetes instalados, configuración, proyectos y volúmenes. C: pasa a 2,57 GiB libres.
- Modern Web Guidance: guía `forms` consultada para el nuevo protocolo y transiciones. Se mantienen imágenes y formatos fotográficos locales; no hacen falta recursos generativos nuevos.

## 25/11/2026 · D4.2 cerrado: A/B creativo y aprendizaje por contexto

### Implementado y límites

- Flujo selección/pretest → protocolo → ejecución → evaluación → aprendizaje guardado. Dos o tres brazos del mismo pretest, contexto y recursos congelados, hipótesis, calendario, exposición, costes, semilla y MDE aproximado. Historial consultable, estados reales y filtros que conservan la prueba en URL sin reejecutarla.
- Mundo A/B separado `mundo-ab-1.0.0`: oportunidades independientes con asignación aleatoria completa y equilibrada por fecha. Observaciones nuevas solo al ejecutar, sin futuro en GET ni suma a ventas/medios propios. Asignaciones completas comprimidas, SHA-256, reconciliación con conteos y exportación CSV por oportunidad. El mecanismo base compartido conserva exactamente el universo original.
- Estimador puro `creatividad-ab-1.0.0`: CTR primario con denominador impresiones, CVR secundario condicionado a clic, Wilson para tasas y Newcombe-Wilson para diferencias; Bonferroni en dos contrastes predefinidos frente al control. Costes comparables y producción una vez. Muestra insuficiente impide guardar; nulo/adverso compatible puede actualizar.
- Aprendizaje de respuesta con prior Jeffreys y 200 draws por brazo, separado de los IC frecuentistas y de nuevos clics. Versiones por contexto exacto, sustitución sin acumular ramas dependientes, copias reutilizadas, diseños obsoletos rechazados y modelos anteriores conservados. Huellas verificadas también entre evaluación y aceptación.
- El pretest muestra el CTR experimental en una sección distinta de su referencia histórica. Predictor `creatividad-1.0.0`, JSON de pretests/selecciones, fotografías, placements y SVG publicados conservados. **CTR/CVR no identifican pedidos ni beneficio: multiplicador económico 1, también después de aceptar.** No hay integración de escenarios aún.
- Reutilizadas tablas `experimento`/`modelo`, sin nuevas migraciones, dependencias, servicios ni IA de runtime. Catálogos geo/A/B separados. Método, fórmulas, fuentes y API en [experimentos_ab.md](experimentos_ab.md).

### Comandos y evidencia ejecutada

| Comando / comprobación | Resultado |
|---|---|
| `docker compose -p margia-ab-qa exec -T backend python -m pytest -q -p no:cacheprovider tests/test_ab.py` | 11 passed, 1 warning en 2,30 s |
| Ruff sobre backend QA | Correcto |
| `npm.cmd run lint` / `typecheck` | Correctos; lint repetido tras el último cambio y TypeScript incluido en build final |
| Builds de producción QA y principal | Correctos; principal actualizada conservando volumen |
| Playwright A/B inicial | 3 passed (36,4 s); captura prematura de diseño corregida antes de la regresión completa |
| Regresión completa `npm.cmd run test:e2e -- --trace off` en QA | 25 passed (3,0 min), screenshots y axe activos |
| A/B tras ajustar espaciado | 3 passed (29,7 s) |
| Recorridos finales afectados: `tests/ab.spec.ts tests/creatividad.spec.ts --trace off` | 9 passed (1,3 min), tras aclarar las tarjetas históricas y el aprendizaje separado |
| Capturas/axe | Diseño y resultado A/B en cuatro tamaños, cuatro plataformas conservadas, regresión general sin infracciones detectadas ni desbordamiento global; revisión manual escritorio/móvil |
| `tests/operacion.py preparar` → reinicio → `verificar`, con `PYTHONPATH=/app`, en QA nueva | Protocolo, observaciones, aprendizaje completo y fecha exacta conservados, junto con hechos/modelos/selecciones anteriores |
| `tests/operacion.py reset`, solo en QA | 44,807 s; mismo checksum, A/B/modelos de usuario eliminados y evidencia inicial restaurada |
| `./scripts/comprobar.ps1` sobre imagen principal final de backend | 89 passed, 1 warning en 27,98 s; Ruff y salud correctos |
| `docker compose -p margia-ab-qa down` | QA detenida sin borrar volumen; principal con tres servicios saludables, solo localhost:3000 publicado |

Las repeticiones específicas no se cuentan como pruebas únicas adicionales. La última aclaración de texto solo modifica el frontend; los nueve recorridos afectados y su build final pasan después. La API principal confirma el modelo histórico `creatividad-bfce2ee924571d327baa`, versión `creatividad-1.0.0`, y el checksum original `6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d`. Cero pruebas A/B de QA en la principal; no se resetea la demo de usuario.

Incidencias corregidas: primer build con props incorrectas de `ModuleLink`; primer comando operativo sin `PYTHONPATH=/app` falló al importar antes de preparar fixtures; primera captura de diseño esperaba una lista de imágenes todavía vacía. Se corrigen y se repiten las comprobaciones afectadas. Detalle en [validacion.md](validacion.md). Avisos heredados httpx y color Playwright; no se ocultan como fallos resueltos. Espacio final C: **2,58 GiB** libres; sin ENOSPC ni caída Docker en este corte, aunque el margen de entorno sigue limitado.

### Git y fases restantes

- Backend probado: `df28955` — «feat: ejecutar A/B creativo y versionar aprendizaje CTR por contexto».
- Interfaz probada: `0febdcb` — «feat: conectar selección creativa con pruebas A/B y aprendizaje visible».
- Fetch sin divergencias; push normal a `origin/main` correcto (`3a7f211..0febdcb`). `git ls-remote origin refs/heads/main` confirma `0febdcbbd13866220f64be701332028d8baf31d7`. Cierre documental en commit separado. Sin force, cambio de remoto, configuración global de identidad ni cambios ajenos.
- **Días 1–3 y D4.1–D4.2 verificados.** Siguiente D4.3: orquestador común base/ahorro/reinversión, draws compartidos, restricciones, costes y optimización factible con opción mantener. El MMM sigue bloqueando recomendaciones de reparto por sensibilidad; no se relaja ese diagnóstico ni se aplica un multiplicador económico desde CTR.
- Día 5: CRUD de escenarios, ejecuciones inmutables, decisiones con motivo y exportaciones; incidencias/restauración y recorrido integrado. Día 6: congelación, regresión A01–A14, rendimiento, revisión visual, secretos/licencias y presentación. P1/P2 aplazados. No se declara cerrado el Día 4 ni la POC.
- Modern Web Guidance `forms` aplicada; trabajo secuencial del propio Codex, sin agentes, subagentes ni delegación.

## 25/11/2026 · Inicio de orquestación y reinversión (D4.3)

- Inspección: `main` limpio en `caf532d`, origin correcto y fetch sin divergencias. Servicios principales saludables y C: con 2,64 GiB libres. Releídos los seis contratos, instrucciones permanentes, avances y backlog. Trabajo propio secuencial, sin agentes.
- Tareas: proyección nacional de 28 días con estacionalidad observada, comparador común base/ahorro/reinversión, costes una sola vez, 200 draws compartidos, presupuestos dentro del soporte, búsqueda determinista con riesgo y opción mantener. Selección creativa trazable y coste de producción; multiplicador económico 1. Ejecuciones inmutables guardadas, interfaz real y navegación desde Search/creatividad/medición.
- Decisión contractual: usar la alternativa de deltas agregados no solapados: respuesta de demanda de siete canales y cambio de captura SEM marca separado. No leer parámetros del mundo ni sumar SEM al MMM. Interacciones no identificadas declaradas. El MMM actual sigue bloqueado/no optimizable; su reinversión será hipótesis y la búsqueda automática excluirá esa dependencia, conservando las opciones Search respaldadas. La asignación con curvas habilitadas se verificará con fixtures explícitas, sin alterar el artefacto de la demo.
- Base: referencia estacional a 52 semanas, ajustada por nivel reciente; ticket/margen por pedido y perfil de inversión fijos desde los últimos 28 días. Ruido por bloques de errores históricos del predictor base calculados solo antes del holdout, separado de parámetros MMM/Search y supuestos de transporte. Bandas condicionales, sin garantía de cobertura.
- Pruebas previstas: nulo/costes/contratación, reconciliación por draw, semilla/ruido común, adstock inicial/soporte, sin doble SEM, selección y versiones, riesgo/negativo/inviabilidad de rejilla, bloqueo real del MMM/datos, API/persistencia/reset aislado, pytest/Ruff, lint/TypeScript/build, E2E/axe/capturas en cuatro tamaños. Todavía no se declaran ejecutadas para D4.3. D5 CRUD/decisiones/incidencias y D6 permanecen pendientes.
- Modern Web Guidance `forms` y `responsive-table` consultadas para los controles y el comparador; sin nuevas dependencias de runtime ni recursos gráficos.

## 25/11/2026 · D4.3 cerrado: comparación y búsqueda con restricciones

### Implementado

- Laboratorio de escenarios real: proyección nacional de 28 días, base/A ahorro/B reinversión, costes comparables, selección creativa congelada, presupuestos por canal, bandas/riesgo y waterfall reconciliado. Enlaces por ID desde evaluación Search y selección creativa; medición conserva el canal. Historial y filtros recuperan la ejecución guardada sin recalcular.
- Orquestador único de deltas agregados: siete canales de demanda con stock reconstruido y cuatro pasos semanales; SEM marca solo en captura Search. Interacción no identificada declarada. El comparador económico común sirve también el contrato histórico Search, sin doble ahorro ni costes. Ticket/margen fijos desde la referencia observada.
- Base estacional con nivel reciente, errores de train y cinco bloques reservados. Diagnóstico calculado: WAPE 1,2100 % frente a 2,5781 % naive, cuatro de cinco totales en banda; estado limitado, sin garantía de cobertura. No se fuerza calibración ni se lee verdad/futuro del generador.
- Las mismas 200 réplicas para base/A/B y rejilla: vectores conjuntos MMM/Search y error base común. Media, p05/p50/p95 y fracción de pérdida condicionados a supuestos. La rejilla verifica límites, soporte semanal y riesgo, compara mantener/ahorro y no promete óptimo global. Sin candidato implica abstención, con base solo de referencia si incumple restricciones.
- El MMM sigue **bloqueado/no optimizable**. B es hipótesis; la búsqueda automática excluye reinversión y considera opciones Search con evidencia suficiente. Un canal intacto no exige transportar una curva fuera de soporte; cualquier cambio sí conserva esa comprobación. La asignación completa se prueba con fixture explícita, sin habilitar el modelo real.
- Creatividad conserva foto/placement/contexto, referencia CTR y versiones. El coste de producción cambia B una vez; **multiplicador económico 1**, incluso con A/B. No se suman pedidos creativos ni se reescriben resultados anteriores.
- Migración aditiva 0005, `escenario`/`ejecucion`, entradas/revisión/modelos/semilla/huellas y matrices completas persistentes. Predeterminados y entradas explícitas se normalizan para reutilizar la misma ejecución. Sin nuevas dependencias ni recursos gráficos. Método y API: [escenarios.md](escenarios.md).

### Pruebas y operación ejecutadas

| Comando / comprobación | Resultado |
|---|---|
| QA desde volumen vacío `docker compose -p margia-escenarios-qa up -d --build --wait --wait-timeout 180` | Migraciones 0001–0005, seed y servicios saludables en localhost:3002 |
| pytest nuevo inicial / regresión con código montado | 10 passed en 3,38 s / 99 passed en 27,50 s, 1 warning heredado |
| Pruebas tras soporte/diagnóstico y normalización | 11 passed en 4,20 s; reenvío completo añadido, 11 passed en 4,71 s |
| Ruff / lint / TypeScript | Correctos; lint final y comprobación TypeScript en build final |
| Playwright completo `npm.cmd run test:e2e -- --trace off` en QA | 29 passed (3,0 min) |
| Cuatro recorridos afectados finales `tests/escenarios.spec.ts --trace off` | 4 passed (35,9 s), tras normalizar entradas y términos en español |
| Capturas/axe | Diseño/resultado en cuatro tamaños, regresión general y formatos fotográficos conservados; sin infracciones detectadas ni desbordamiento global; revisión manual escritorio/móvil |
| `tests/operacion.py preparar` → reinicio → `verificar`, con `PYTHONPATH=/app` | Hechos, modelos/fechas, Search/geo, pretest/A-B y comparación con matrices/semilla/fecha exacta conservados; reenvío reutilizado sin otra ejecución |
| `tests/operacion.py reset`, solo en QA | 41,601 s; mismo checksum, comparaciones eliminadas/404 y evidencia inicial restaurada |
| `docker compose up -d --build --wait --wait-timeout 180` | Principal actualizada conservando volumen y todos sus datos |
| `./scripts/comprobar.ps1` sobre imagen final principal | **100 passed, 1 warning en 32,49 s**; Ruff y salud correctos |
| `docker compose exec -T backend alembic current` | 0005 (head) |
| `docker compose -p margia-escenarios-qa down` | QA detenida sin borrar volumen; principal con tres servicios saludables y solo localhost:3000 publicado |

Las repeticiones no se suman como pruebas únicas. Muestra de la fixture operativa: cálculo interno 0,0119 s y JSON completo 530.953 bytes; excluye consultas/escritura y no es un benchmark general. Comandos detallados, diagnósticos e incidencias en [validacion.md](validacion.md).

Corregido durante QA: dependencia excesiva del soporte de canales intactos, nombres/imports de Ruff, etiquetas/tabla del desglose en móvil y normalización entero/decimal. El primer Playwright específico dio 3 passed/1 failed (30,9 s) por leer la URL antes de completar la navegación; corregida la espera y repetido el recorrido. No se cuenta como batería satisfactoria.

La API principal confirma cero ejecuciones de QA, MMM bloqueado/no optimizable, modelo creativo original `creatividad-bfce2ee924571d327baa` y checksum `6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d`. No se resetea la principal. C: queda con 2,61 GiB libres, sin ENOSPC ni caída Docker en este corte. Warnings heredados httpx y color Playwright; siguen los límites de transporte, muestras y ausencia de efecto económico creativo identificado.

### Git y continuación

- Backend probado: `6a6fe9e` — «feat: comparar escenarios con réplicas comunes y búsqueda restringida».
- Interfaz probada: `8df5ebd` — «feat: incorporar comparador de escenarios y navegación por evidencia».
- Fetch sin divergencias; push normal correcto (`caf532d..8df5ebd`). `git ls-remote origin refs/heads/main` confirma `8df5ebde6c601fd4f81f52951053a2e6351e0bc0`. Cierre documental separado; sin force ni cambios ajenos o de configuración global.
- **Días 1–4 verificados con sus límites.** Siguiente D5.1: CRUD de borradores, duplicación/archivo, decisiones con motivo y exportaciones CSV/Markdown; persistencia de configuraciones/ejecuciones ya preparada. D5.2: incidencias y restauración. D5.3: recorrido completo con decisión y guion. D6: congelación, A01–A14, rendimiento, auditoría final y presentación. P1/P2 aplazados; no se declara POC terminada.
- Modern Web Guidance `forms` y `responsive-table` aplicadas. Trabajo secuencial sin agentes, subagentes ni delegación.

## 26/11/2026 · Inicio de D5.1: borradores y decisiones trazables

- Contratos permanentes, avances y backlog releídos; `main` limpio en `5fdf611`, origin correcto y fetch sin divergencias. Trabajo propio secuencial, sin agentes.
- Tareas: borradores con revisiones y control de concurrencia, duplicación/archivo sin borrar ejecuciones; aprobación/rechazo con motivo y revalidación de dependencias en servidor; navegación al registro y exportaciones CSV/Markdown desde resultados guardados.
- Pruebas previstas: migración aditiva con conservación del histórico, revisiones/conflictos, ejecuciones inmutables/reutilización, transiciones, datos/modelos obsoletos o bloqueados, exportaciones reconciliadas y escape de texto; regresión pytest/Ruff, lint/TypeScript/build, Playwright/axe y capturas en cuatro tamaños, persistencia/reinicio/reset en pila aislada. Todavía no se declaran ejecutadas para este hito.
- Límites conservados: MMM bloqueado, creatividad con multiplicador económico 1, proyección nacional de 28 días, datos sintéticos y ninguna activación real. Decisiones en modo limitado solo para planes con dependencias defendibles y restricciones satisfechas; mantener no depende de la curva MMM.
- Entorno: C: con unos 400 MB libres frente a 2,61 GiB al cierre anterior. Eliminada únicamente una caché Docker antigua, regenerable y marcada no compartida (`dmrbsxnr81689mxcr0emry1q3`, 1,474 GB); no se han eliminado imágenes, contenedores ni volúmenes. El espacio de Windows aún no aumenta; se comprobará antes del build.
- Modern Web Guidance `forms` y `dialog` consultadas para validación, foco y confirmación de archivo; sin nuevas dependencias de runtime.

## 26/11/2026 · D5.1 cerrado: borradores, decisiones y exportaciones

### Implementado

- Borradores con identidad propia, guardado sin cálculo, revisión inmutable de parámetros y control de concurrencia al editar/ejecutar/archivar. Las configuraciones D4.3 conservan su identidad y se duplican para editar. Archivo con motivo, sin borrar ejecuciones ni decisiones; reenvío idéntico idempotente y cambio de motivo terminal rechazado.
- Migración aditiva **0006**, tablas de revisiones/eventos y recuperación de revisiones históricas. Ejecuciones por revisión/versiones/fuentes, reutilización reproducible y lectura por ID aunque falle el catálogo actual. Resultados, draws y fechas anteriores conservados.
- Decisión terminal por ejecución y plan explícito: mantener, A, B o candidato de rejilla. Aprobar/rechazar exige motivo y congela economía, banda, presupuesto, inputs/modelos/semilla y guardrails del registro. Reenvío idéntico devuelve la misma decisión; cambiarla requiere otra ejecución.
- Revalidación en servidor de snapshot, revisión, integridad, observaciones/calibración temporal, restricciones/riesgo y dependencias específicas. Search actualizado al recortar; MMM habilitado al reinvertir; evidencia creativa al lanzar propuesta. Cambio con esperanza negativa no se aprueba. Mantener y Search respaldado no exigen rehabilitar el MMM. Rechazo disponible con plan bloqueado o fuentes indisponibles.
- CSV/Markdown reales desde el resultado congelado, con trazabilidad, costes, bandas, presupuestos, hipótesis y decisión. CSV UTF-8/BOM/separador `;`, escape de fórmulas en texto y valores negativos numéricos preservados; Markdown/HTML escapado. No ejecutan de nuevo el motor.
- Interfaz integrada: guardar/editar borrador, revisar entradas/resultados previos, duplicar/archivar con diálogo y motivo, registrar decisión y navegar por ID desde el centro, descargar ambos formatos. Fechas de sistema diferenciadas del horizonte sintético, errores recuperables y contexto global conservado.

### Pruebas y operación ejecutadas

| Comando / comprobación | Resultado |
|---|---|
| QA nueva `docker compose -p margia-decisiones-qa up -d --build --wait --wait-timeout 180` con puerto 3002 | Migraciones 0001–0006, seed y tres servicios saludables |
| `pytest tests/test_decisiones.py tests/test_escenarios.py` con código montado, después de salud | 23 passed, 1 warning en 12,47 s |
| Regresión intermedia / casos de decisión y migración ampliados | 112 passed en 35,94 s / 15 passed en 8,27 s, antes de los últimos casos |
| Regresión final exclusiva en QA limpia, `MARGIA_VALIDACION=1`, código montado | **117 passed, 1 warning en 37,74 s**, incluida migración DDL transaccional revertida |
| Ruff / lint / TypeScript / build de producción | Correctos; sin nuevas dependencias ni cambios de recursos gráficos |
| `npm.cmd run test:e2e -- --trace off` contra QA | **34 passed (3,8 min)**, incluidos cinco recorridos nuevos de D5.1 |
| Capturas/axe y revisión manual | Formularios/registro en 1440×900, 1920×1080, 1280×720 y 390×844, diálogo, regresión de módulos y formatos fotográficos; sin infracciones detectadas ni desbordamiento global |
| `tests/operacion.py preparar` → reinicio saludable → `verificar` | Borrador revisado/archivado, ejecución/draws/fecha, decisión y exportaciones CSV/MD exactas conservados; hechos y modelos anteriores también |
| `tests/operacion.py reset`, solo en QA | 33,615 s; mismo checksum y evidencia de arranque, borradores/decisiones/ejecuciones eliminados, exportaciones antiguas 404 |
| `docker compose up -d --build --wait --wait-timeout 180` | Principal actualizada conservando volumen, sin reset |
| `./scripts/comprobar.ps1` en principal | **116 passed, 1 skipped, 1 warning en 37,29 s**, Ruff y salud correctos; se omite deliberadamente la prueba DDL exclusiva de QA |
| `alembic current` / parada QA | `0006 (head)`; QA detenida con volumen conservado, principal saludable y solo localhost:3000 publicado |

Las repeticiones no se suman como pruebas únicas. Incidencias y comandos completos en [validacion.md](validacion.md). Se corrigieron el ancho heredado de radios, foco seguro del diálogo y foco del error tras renderizar, selectores de prueba que incluían el anunciador de Next y una suposición antigua de historial vacío. Una preparación operativa se lanzó por error antes de finalizar pytest: esa superposición se descarta y se repite de forma exclusiva tras reset de QA (40,950 s). No se relaja ningún guardrail para obtener pruebas positivas.

La principal confirma checksum **`6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d`**, modelo creativo original **`creatividad-bfce2ee924571d327baa`**, MMM bloqueado/no optimizable y cero escenarios/ejecuciones/decisiones de QA. C: con aproximadamente **0,39 GiB** libres, sin ENOSPC en las construcciones de este corte; capacidad escasa a vigilar en próximas jornadas. Persisten el warning heredado httpx/TestClient y el aviso de color de Playwright.

### Git y siguiente corte

- Backend: `01b6047` — «feat: versionar escenarios y registrar decisiones y exportaciones».
- Interfaz: `c45ece4` — «feat: integrar borradores, decisiones y descargas en la interfaz».
- Fetch sin divergencias y push normal correcto (`5fdf611..c45ece4`); `git ls-remote origin refs/heads/main` confirma `c45ece447df02262813faa4edb195218f062b0dd`. Cierre documental separado, sin force ni cambios ajenos/globales.
- **Días 1–4 y D5.1 verificados con sus límites.** Próximo **D5.2**: snapshots alternativos de tracking/faltantes, dependencias, bloqueo y restauración sin borrar histórico. **D5.3**: recorrido integrado principal/alternativo y guion 7–10 minutos. **D6**: congelación, aceptación global A01–A14, rendimiento, revisión visual/accesibilidad final, secretos/licencias y presentación. P1/P2 aplazados. No se declara POC terminada.
- Modern Web Guidance `forms` y `dialog` aplicadas; trabajo propio secuencial, sin agentes, subagentes ni delegación.
