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
