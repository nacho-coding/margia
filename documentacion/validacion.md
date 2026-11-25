# Validación ejecutada · Fundaciones, Medición y One Search

Fecha: 25/11/2026. Pila real de producción local en Docker Desktop sobre Windows. Cubre Días 1 y 2 y D3.1; los apartados históricos se conservan. No acredita los nuevos experimentos, VOI, creatividad predictiva o escenarios de las fases siguientes, ni validez comercial sobre datos reales.

## Estado de aceptación

| Criterio | Cobertura del incremento | Resultado |
|---|---|---|
| A01 | Compose, PostgreSQL vacío, migración congelada, seed, health, reinicio, reset | Verificado en pila aislada y producción local; ver comandos |
| A02 | Reproducción, checksum canónico, FK, clics/exposición, presupuesto y reconciliación | 39 pytest, incluido universo preservado e históricos experimentales |
| A03 | MMM ajustado, holdout, naive, diagnóstico, curvas con soporte y límites | Verificado como modelo observacional; reparto por canal inestable y recomendaciones bloqueadas |
| A04 | Search cambia resultado, costes, equilibrio, soporte y abstención | Verificado con efecto experimental directo; recuperación no identificada |
| A05–A09 | Nuevos geo, pretest/A-B, optimización, EVPI/EVSI e incidencia | Pendientes de sus fases |
| A10 | Persistencia de fixture de decisión y checksum tras reinicio | Verificado; CRUD de escenarios y decisiones de usuario pendiente |
| A11 | Contexto, módulos descriptivos, MMM, radar → hipótesis → simulación → guardado, errores y abstención | 13 recorridos Playwright; cuatro de Search repetidos tras ajuste móvil |
| A12 | Siete rutas × cuatro tamaños, sin scroll global, axe y revisión visual | 28 capturas reales; revisadas las siete vistas, con centro móvil/escritorio y biblioteca 1920 |
| A13 | CPU, recursos locales, .env ignorado, sin agentes/LLM/API pagada | Inspección de código/configuración y staging; sin tokens/dumps/capturas/dependencias locales publicados |
| A14 | PRD/RFC conservados y publicación normal | Acceso habilitado; fundaciones, MMM y radar/Search publicados hasta c9fd02d, verificado con ls-remote |

## Backend y matemáticas

```powershell
docker compose run --rm --no-deps --volume "${PWD}/backend:/app" backend python -m pytest -q
docker compose run --rm --no-deps --volume "${PWD}/backend:/app" backend ruff check .
```

Batería más reciente: **18 passed, 1 warning**, 27,52 s (con otras comprobaciones locales en marcha). Ruff: **All checks passed**. El warning es una deprecación del adaptador httpx del TestClient de Starlette, no un fallo del servidor; queda pendiente migrar el cliente de pruebas en un incremento de mantenimiento. También se ejecutaron previamente baterías de 17–18 s.

Pruebas de dominio: fixture +12.000 €/−21.000 €, equilibrio 84 %, recorte cero y completo, recuperación 0/1, costes comunes/incrementales, entradas no finitas/negativas y denominadores cero. Pruebas de datos: presupuesto exacto, margen, relaciones, cobertura, coherencia creativo/campaña y gasto de vistas parciales. Misma semilla y versión producen mismo checksum; cambiar orden de inserción no lo modifica. API: periodos válidos/incorrectos, mercado inexistente, idempotencia, nulos, exportación y paginación.

Fallo detectado y corregido: Literal[int] de periodo no aceptaba el string de query con las versiones instaladas. Se valida como entero más conjunto de valores permitidos. No se omitió la prueba fallida.

## Operación y persistencia

Se creó la pila **margia-validacion**, con PostgreSQL y volumen independientes de la demo. Se migró desde vacío y se generó el universo. Un primer intento de reinicio interrumpió la carga todavía no saludable: la transacción se revirtió y la inicialización posterior recuperó el estado; ese intento no se cuenta como prueba de persistencia. Corregido el orden, la prueba con fixture preparada pasó.

```powershell
docker compose -p margia-validacion up -d --wait --wait-timeout 180 db backend
docker compose -p margia-validacion exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py preparar
docker compose -p margia-validacion restart db backend
docker compose -p margia-validacion up -d --wait --wait-timeout 120 db backend
docker compose -p margia-validacion exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py verificar
docker compose -p margia-validacion exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py reset
```

Resultado: fixture de decisión archivada, checksum y 17.520 filas de negocio conservados tras reinicio; confirmación inválida devuelve 422, reset válido elimina la fixture y reconstruye exactamente los conteos/checksum. Reset aislado: **69,408 s** durante otras comprobaciones. La fixture está identificada como prueba; no es una decisión de negocio creada por el usuario.

Manifest final de datos revisado: `6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d`. La primera versión de trabajo tenía otro hash; antes de cerrar el incremento se corrigió la consistencia de categorías y se ordenó el checksum por grano. No existen ejecuciones/modelos de usuario que hayan sido reescritos.

## Frontend, visual y accesibilidad

```powershell
docker compose up -d --build --wait --wait-timeout 180
Set-Location frontend
npm.cmd run lint
npm.cmd run typecheck
npm.cmd run test:e2e
```

Build Next.js de producción con Node 24 en Docker: correcto (compilación y TypeScript). El intento de build dentro del sandbox Windows falló al crear un proceso de PostCSS; no es el entorno de presentación. La compilación Linux de Docker pasó. Lint y typecheck de host también pasan.

Última batería completa tras la revisión final de activos/móvil: **6 passed (1,3 min)**, sin infracciones axe WCAG A/AA detectadas en 28 combinaciones. Los dos contrastes identificados por auditoría se corrigieron: antetítulo y rótulo SEO/SEM. El primer test de error se corrigió para distinguir el aviso de la aplicación del anunciador interno de Next.js.

Capturas locales en `artifacts/qa` (ignoradas por Git), tamaños 1440×900, 1920×1080, 1280×720 y 390×844. Rutas: centro, medición, One Search, creatividad, experimentos, escenarios y fiabilidad. Se inspeccionaron visualmente las siete vistas: centro 1440/1920/móvil, One Search 1280, biblioteca 1440/1920, medición, experimentos, escenarios y fiabilidad en 1440. Las otras combinaciones se capturaron y auditaron automáticamente. Hallazgos corregidos en revisión final: moneda demasiado ancha en KPI móvil, texto «marca cuando» sin espacio al ocultar el salto y etiqueta de canal tapando el wordmark de los activos.

Teclado probado: abrir/cerrar panel, Escape y retorno de foco, navegación móvil, formularios y confirmación inválida. No se ha realizado una auditoría con lector de pantalla humano ni se declara conformidad WCAG completa por axe.

## Modern Web Guidance

Skill del proyecto: `.agents/skills/modern-web-guidance/SKILL.md`; procedencia GoogleChrome/modern-web-guidance, commit fijado en el `skills-lock.json` instalado por el usuario. Se ejecutaron `search` por patrón y `retrieve` de las guías antes de seguir implementando UI. La instalación se conserva sin modificar.

| Guía aplicada | Regla concreta consultada | Decisión en el código |
|---|---|---|
| `css-layout` | “Do NOT use `overflow: hidden` to mask layout issues” | Grid con `minmax(0,1fr)`, propiedades lógicas y KPI fluido; el desbordamiento se corrige en su origen. |
| `dialog` | “The browser returns it to the invoker.” | Paneles `<dialog>` con showModal, título único, cierre seguro y retorno de foco nativo; contención en modal/backdrop. |
| `navigation-drawer` | “swipe gesture is handled natively by the browser” | Navegación móvil independiente en dialog, scroll-snap e IntersectionObserver; sin gesto JS de puntero. |
| `responsive-table` | “Add a `tabindex="0"` attribute to the container” | Tabla semántica, caption/scope, cabeceras sticky y región de scroll propia accesible con teclado. |
| `accessibility` | “Use `:focus-visible` when styling focus indicators” | Foco visible, labels, títulos de ruta, alternativas a gráficos y revisión con axe/teclado. |
| `forms` | “DON'T disable submit buttons to block validation” | Confirmación con required/pattern, mensajes asociados y submit activo hasta enviar; se evita el doble envío durante el cálculo. |
| `performance` | “DO use dynamic imports” | Carga modular y diferida de ECharts, imágenes dimensionadas, SVG locales y fuentes locales; sin polling pesado. |

Se consultó también `sortable-table`, pero no se aplicó su comportamiento de reordenado nativo: One Search ordena mediante selector y consulta paginada al backend. La guía no se acredita como cambio implementado. No se añaden polyfills de overlays innecesarios ni APIs de IA del navegador.

## Mediciones y límites

- Primer seed: 247.562 registros en **41,364 s**. Seed aislado después de una interrupción: **53,831 s**. Son mediciones locales, no garantías.
- Muestra de memoria en reposo: frontend **40,25 MiB**, backend **70,73 MiB**, PostgreSQL **113,4 MiB**; no incluye Docker Desktop/VM ni picos de generación.
- No se ha medido aún navegación caliente con una distribución de latencias ni simulación de 200 draws: esta última no está implementada.
- Modelos, banda de incertidumbre, radar estimado y decisiones de usuario continúan pendientes del backlog. El centro no fabrica oportunidad económica.

## Comprobación final de scripts

- `reset_demo.ps1 -Confirmar`: estado restablecido, hash canónico esperado, **53,75 s** en la demo local.
- `detener.ps1` y `iniciar.ps1 -SinBuild`: parada sin borrar volumen, recreación saludable y checksum `6715…0c9d` conservado.
- `comprobar.ps1`: **18 passed, 1 warning en 15,26 s**, Ruff correcto y salud lista. Se corrigió el intento de escribir cachés en `/app` sin permisos: las comprobaciones usan `pytest -p no:cacheprovider` y `ruff --no-cache`; no se amplían privilegios del contenedor.
- Función de URL comprobada con puerto predeterminado 3000 y override temporal 8081. No se ha probado un despliegue completo en puerto alternativo.
- `npm ls --depth=0`: árbol directo coherente; lint y typecheck sin errores/avisos en la última ejecución.
- Pila aislada detenida conservando su volumen; la demo principal permanece arrancada.
- `iniciar.ps1` con build completo: comprobado tras la parada/arranque; todos los servicios saludables. No se han modificado parámetros de seguridad de Windows ni instalado Python en el host.

## 25/11/2026 · Incremento D2.1–D2.2

### Resultado del ajuste real

Versión `mmm-1.0.1`, artefacto `mmm-4246cd7b830a0a9f7cfc`, semilla 260725 y snapshot original con checksum `6715…0c9d`. Entrenamiento hasta 13/06/2026, evaluación reservada 14/06/2026–31/10/2026. Protocolo, fórmulas, versiones y límites en [modelo_mmm.md](modelo_mmm.md).

| Diagnóstico | Resultado ejecutado |
|---|---|
| Semanas / train / holdout | 104 / 84 / 20 |
| WAPE train | 1,3783 % |
| WAPE holdout | 1,5583 % |
| WAPE naive estacional en holdout | 3,1699 % |
| MAE holdout | 135,09 pedidos por semana |
| Sesgo holdout | −0,6772 % |
| Correlación máxima entre términos de medios | 0,5412 |
| Condición de diseño normalizado | 5,9471 |
| Variación mínima de gasto | 0,1775 |
| Sensibilidad del reparto entre configuraciones comparables | 5,6253; supera umbral 1 |
| Cobertura empírica de banda p05–p95 | 19/20 semanas de holdout (95 %) |
| Tiempo batch observado en la demo | 0,153 s; no incluye seed |
| Estado | **Bloqueado para recomendaciones**, por reparto inestable |

No se relajaron los umbrales tras ver los datos. La predicción conjunta mejora naive, condicionada a inversión/promoción observadas en holdout; no es un pronóstico ex ante ni identifica contribuciones causales. Las bandas de coeficientes con forma fija no reflejan la inestabilidad entre formas: no se usan para autorizar decisiones. No hay optimizador ni aprobación implementados en este incremento.

### Pruebas y compilación

```powershell
docker compose up -d --build --wait --wait-timeout 180
./scripts/comprobar.ps1
Set-Location frontend
npm.cmd run lint
npm.cmd run typecheck
npm.cmd run test:e2e
```

- Build final Next.js en Docker: compilación, TypeScript y generación de rutas correctos; tres servicios saludables. El arranque principal migra desde 0001 a 0002 conservando los hechos.
- `comprobar.ps1`: **26 passed, 1 warning en 22,74 s**, Ruff correcto y salud lista. Se mantiene el warning de deprecación httpx/TestClient ya documentado, sin añadir dependencias nuevas.
- Pruebas nuevas: curvas acotadas y marginal, agregación sin duplicar pedidos, semanas completas, ausencia de SEM marca en efectos, particiones, seed, descomposición, bandas no degeneradas, política de abstención, persistencia idempotente, API y rechazo de modelo/canal inexistentes. Alterar objetivos y multiplicar por 100 el gasto del holdout deja intactos parámetros, selección, escalas y refits de train. Inspección AST impide importar el generador o leer su fixture de verdad desde modelos.
- Lint y typecheck de frontend: sin errores. **Playwright final: 9 passed (1,5 min)**. Comprueba cifras de API, cambio de vista/canal, soporte, tablas, metodología con Escape/retorno de foco, periodo sin reentrenar, rechazo del modelo por mercado, error/reintento y regresión del Día 1.
- Capturas finales: 28 combinaciones de siete rutas en 1440×900, 1920×1080, 1280×720 y 390×844, con espera explícita a los dos canvas y sin skeleton. Axe no detecta infracciones de las etiquetas WCAG A/AA utilizadas; cero scroll horizontal global. No equivale a auditoría completa de accesibilidad.
- Inspeccionadas imágenes de Medición en las cuatro resoluciones a lo largo de las iteraciones, además de descomposición y drawer; la corrección final elimina el rótulo monetario extremo recortado del eje. `artifacts/qa/mmm-descomposicion.png` y `mmm-metodologia.png` complementan las capturas por tamaño. No se suben a Git.

### Persistencia, migración y reset aislados

Pila `margia-mmm-qa` con volumen nuevo y sin frontend publicado. Migración completa desde PostgreSQL vacío, seed y entrenamiento saludables. Después se actualiza a la revisión de bandas vigente antes de preparar la prueba operativa.

```powershell
docker compose -p margia-mmm-qa up -d --build --wait --wait-timeout 180 db backend
docker compose -p margia-mmm-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py preparar
docker compose -p margia-mmm-qa restart db backend
docker compose -p margia-mmm-qa up -d --wait --wait-timeout 120 db backend
docker compose -p margia-mmm-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py verificar
docker compose -p margia-mmm-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py reset
docker compose -p margia-mmm-qa down
```

Reinicio: conserva fixture de decisión, negocio, checksum, resultado completo del MMM y fecha de creación, sin reentrenar. Reset: elimina la fixture y reconstruye mismo hash de datos y resultado completo del MMM (salvo tiempo real de ajuste), con nueva fecha de creación; API consultable. **43,841 s**. Pila detenida sin eliminar volumen; demo principal conservada y saludable. El script exige `MARGIA_VALIDACION=1` y se ejecuta solo en la pila aislada.

### Defectos detectados y corregidos

1. Test de agregación comparaba DATE con VARCHAR: se pasa `date`; repetición completa satisfactoria. Primera batería: 25 passed, 1 failed.
2. Bootstrap del prototipo reajustaba una señal regularizada y contraía de nuevo los coeficientes. Revisión de tabla/curva detecta bandas desplazadas; corrección versionada mmm-1.0.1 con errores de refit centrados y truncación, explicada sin presentarla como IC calibrado. Artefacto anterior conservado en la demo.
3. Primera QA capturó skeleton antes de cargar el módulo de gráficos en algunas resoluciones; ahora espera canvas. Se repiten las 28 capturas y la auditoría.
4. Una prueba esperaba `9.572`, pero Intl es-ES muestra `9572` para esa magnitud: se utiliza el mismo formateador de localización, sin tocar el dato. Primera batería UI: 8 passed, 1 failed; repetida y satisfactoria.
5. Etiqueta extrema del eje monetario recortada en móvil: se evita el máximo redundante y se activa ocultación de solapamientos. Build y nueve recorridos repetidos tras corregir.

### Mediciones y pendientes

15 lecturas consecutivas de `GET /api/v1/modelos/mmm?dias=28` a través del proxy local: mínimo **22,10 ms**, mediana **23,79 ms**, máximo **288,78 ms**. Incluye el primer acceso de la muestra; no es latencia de navegación completa ni benchmark bajo carga controlada. Muestra de RAM durante QA: web **84,96 MiB**, API **96,23 MiB**, DB **102,8 MiB**; no es pico ni incluye VM/Docker Desktop.

D2.3 permanece pendiente: falta evidencia Search para radar económico, seguida de geo/valor de información y escenarios. No se declara cerrado el Día 2 completo ni candidata final. Publicación: reintentado `git push origin main`, mismo 403 para `ignaciofontal`; se conservan commits locales, remoto y cambios previos.

Modern Web Guidance se volvió a consultar antes de implementar UI: `search "responsive data table"`, `retrieve "responsive-table,accessibility"`, versión de skill `2026_11_16-268fb9ea`. Apliqué regiones de scroll con teclado (“Add a `tabindex="0"` attribute to the container”) y alternativas tabulares de ambos gráficos (“Provide semantic data tables as alternatives”). Se reutiliza el drawer nativo probado; no se añadieron librerías ni agentes.

## 25/11/2026 · D2.3 y dependencia D3.1 verificados

Modelo `search-1.0.0`, ID `search-90c0cd70be0bef7b8d7a`, hipótesis `hip-marca-90c0cd70be0bef7b8d7a`. Los 12 históricos, 288 asignaciones y 576 observaciones se almacenan y etiquetan como arranque sintético. Los estimadores no leen la verdad ni el generador (prueba AST conservada). El checksum de los hechos sigue exactamente en `6715…0c9d`, probado después de extraer el mecanismo compartido de captura.

Resultado observado con contexto nacional de 28 días, recorte del 50 % y costes nuevos cero:

| Magnitud | Resultado calculado |
|---|---|
| Ahorro | 34.898,03 € |
| Cambio de pedidos propios | −420,77 pedidos esperados |
| Cambio de margen | −18.401,94 € |
| Delta de contribución | 16.496,09 € |
| Banda p05–p95 | −7.104,57 € a 39.307,73 € |
| Réplicas negativas | 9,5 % de 400 draws de parámetros |
| Recuperación SEO/directo | No identificada; se utiliza efecto total por euro |

El resultado no implica actuar: invita a contrastar, explicita pérdidas posibles y permite costes que cambian el signo. Cuota incremental 100.000 €: delta −83.503,91 € y mantener; cuota común se cancela en la comparación. Fuera del soporte, un mercado individual u otro horizonte se señalan como hipótesis sin recomendación. No se ha relanzado ni suavizado el MMM bloqueado para justificar el radar.

### Comandos realmente ejecutados

```powershell
docker compose up -d --build --wait --wait-timeout 180
docker compose run --rm --no-deps --volume "${PWD}/backend:/app" backend python -m pytest -q -p no:cacheprovider
docker compose exec -T backend ruff check --no-cache .
Set-Location frontend
npm.cmd run lint
npm.cmd run typecheck
npm.cmd run test:e2e
npm.cmd run test:e2e -- tests/search.spec.ts
```

- Última batería Python completa: **39 passed, 1 warning en 29,10 s**; una ejecución previa pasó en 18,48 s. Ruff final correcto. Se mantiene la deprecación conocida httpx/TestClient. No hay dependencias nuevas.
- Pruebas nuevas: hash del mundo inalterado, semilla y subsemillas, aleatorización por par, FK/granos, exclusión de contrafactuales del estimador, nulo/negativo, placebo adverso, pocos pares, bandas no degeneradas, recorte 0/100/fuera de rango, cuota común/incremental, casos negativos, reconciliación, persistencia/ID, API y rechazo de hipótesis inventada.
- Build final de producción, TypeScript y lint correctos. Regresión completa: **13 passed (1,8 min)**, sin errores JS en el recorrido probado. Incluye vínculo al ID, foco en simulador, resultado de API, costes que cambian decisión, cuota común, recorte cero, extrapolación, formulario inválido, históricos con 48 observaciones y error/reintento con foco conservado.
- QA: 28 capturas generales de siete rutas × cuatro tamaños, cuatro paneles de evaluación y un resultado negativo, además de las capturas de metodología MMM. Axe en las combinaciones y en los resultados Search sin infracciones detectadas; sin scroll horizontal global. Inspección manual de centro, resultados escritorio/móvil y waterfall negativo. Las tablas densas conservan scroll propio. No se declara auditoría humana de lector de pantalla.
- Se corrigieron leyenda SEO/SEM sobre fechas y solapamiento de etiquetas del waterfall móvil. Las capturas de panel evitan artefactos de composición de la sidebar sticky en screenshot de página completa ya desplazada. Los cuatro recorridos afectados se repiten tras el ajuste de rótulos; resultado final en avances.

### Arranque vacío, persistencia y reset

```powershell
docker compose -p margia-search-qa up -d --build --wait --wait-timeout 180 db backend
docker compose -p margia-search-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py preparar
docker compose -p margia-search-qa restart db backend
docker compose -p margia-search-qa up -d --wait --wait-timeout 120 db backend
docker compose -p margia-search-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py verificar
docker compose -p margia-search-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py reset
docker compose -p margia-search-qa down
```

Pila nueva desde PostgreSQL vacío, migraciones 0001–0003, seed, MMM e históricos/Search correctos. Reinicio conserva decisión fixture, hechos, MMM, modelo Search y evaluación guardada exactos. Reset reconstruye mismos hechos y ambos modelos (MMM salvo duración), elimina evaluación y fixture; **52,718 s**. Pila aislada detenida conservando volumen; demo principal conservada.

Skill `forms`: inputs con label, ayuda de soporte, min/max/required, validación también en API y submit habilitado para mostrar errores. Solo se bloquea durante POST válido (“DON'T disable submit buttons to block validation”). Resultados anunciados y errores con foco; sin llamadas IA, agentes ni servicios externos de runtime. Método y límites completos: [one_search.md](one_search.md).

## 25/11/2026 · Laboratorio geo y valor de información (D3.2–D3.3)

### Backend y pruebas matemáticas

- Batería del código final con volumen de código: **61 passed, 1 warning en 29,98 s**. Verificador oficial `./scripts/comprobar.ps1` contra producción: **61 passed, 1 warning en 25,39 s**, salud y Ruff correctos.
- Con la base de QA conteniendo una prueba aceptada y Search actualizado: **61 passed, 1 warning en 19,54 s**, Ruff correcto. Los tests geo revierten una transacción exterior incluso cuando los POST confirman sus savepoints; no eliminan el estado de usuario al salir. Las pruebas históricas filtran por su origen, sin exigir que el usuario no haya creado pruebas nuevas.
- Cobertura nueva: emparejamiento/asignación por semilla, preperiodo completo, unidades y observaciones por par, efecto nulo/adverso/positivo, IC no degenerado, exclusión de verdad/generador en estimadores, mercado/horizonte insuficientes, guardrail de pérdida, transiciones y repetición de POST. Modelo nuevo por sustitución, rechazo de diseño obsoleto, copia idéntica sin estrechar incertidumbre, versiones y evaluaciones antiguas conservadas. Faltantes de evidencia vigente bloquean Search.
- EVPI/EVSI: fixture contractual +80k/−60k con mantener 0, EV actual 10k y EVPI 30k; señal perfecta/ruidosa/no informativa, límites `0 ≤ EVSI ≤ EVPI`, prueba cara negativa, coste y oportunidad imputados una vez. No se representa el error de corrección numérica como garantía de convergencia del likelihood aproximado.

Comandos principales, desde la raíz:

```powershell
docker compose up -d --build --wait --wait-timeout 180
./scripts/comprobar.ps1
docker compose -p margia-geo-qa run --rm --no-deps --volume "${PWD}/backend:/app" backend python -m pytest -q -p no:cacheprovider
docker compose -p margia-geo-qa run --rm --no-deps --volume "${PWD}/backend:/app" backend ruff check --no-cache .
```

### Operación aislada realmente ejecutada

Pila `margia-geo-qa` desde PostgreSQL vacío, frontend solo en `127.0.0.1:3002`. Migraciones 0001–0003, seed y modelos correctos. Seed observado **39,109 s**, MMM **0,176 s** (muestras de arranque, no benchmark general).

```powershell
$env:MARGIA_PORT='3002'
docker compose -p margia-geo-qa up -d --build --wait --wait-timeout 180
docker compose -p margia-geo-qa cp backend/tests/operacion.py backend:/app/tests/operacion.py
docker compose -p margia-geo-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py preparar
docker compose -p margia-geo-qa restart db backend
docker compose -p margia-geo-qa up -d --wait --wait-timeout 120 db backend
docker compose -p margia-geo-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py verificar
docker compose -p margia-geo-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py reset
```

Reinicio conserva hechos, checksum, decisión fixture, MMM, Search original, evaluación Search antigua, diseño, asignaciones, observaciones, evaluación geo y versión vigente con misma fecha de creación. No reentrena ni vuelve a ejecutar el experimento. Reset: **41,342 s**, elimina pruebas/actualizaciones y recupera los 12 históricos y Search original; mismo checksum `6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d`. La demo principal se conserva.

Al cerrar: `docker compose -p margia-geo-qa down`, sin eliminar volumen. `docker compose ps` confirma los tres servicios principales saludables y únicamente `127.0.0.1:3000` publicado. Código publicado con push normal a `origin/main`; cierre documental separado.

### Hallazgos corregidos sin cambiar los resultados

1. Primera regresión backend: **57 passed, 1 failed**. La prueba AST rechazó que un servicio dentro de `app/modelos` importara el mundo. Se mueve la coordinación a `app/experimentos`; el estimador sigue sin importar generador/verdad. Regresión posterior correcta.
2. Al añadir el gráfico explícito del IC, una prueba de UI seguía esperando un solo canvas: **15 passed, 1 failed**. Se actualiza para comprobar los dos gráficos.
3. Tras aceptar geo, una prueba de Search buscaba una advertencia literal exclusiva de los históricos: **15 passed, 1 failed** en esa regresión. Se comprueba la explicación común de recuperación no identificada; se mantienen fuentes y advertencias de cada versión.
4. Comprobación con evidencia nueva: **60 passed, 1 failed** por exigir riesgo 100 % con cuota 100.000 €. El resultado real era **99,75 %**, conservado. Se prueba el desplazamiento exacto del coste en delta y bandas y la monotonía del riesgo; no se truncan draws ni se cambian cifras para que pase.
5. Leyenda del gráfico pre/post sobre etiquetas y excesiva altura del IC: se fija posición de leyenda, margen del eje y especificidad CSS de la altura. Titular móvil conserva espacio al ocultar el salto. Se revisan capturas reales, sin declarar QA solo por build.
6. Contraste visual/API tras aceptar geo: 40 cuantiles omitían una cola adversa del 0,5 % y mostraban EVPI cero. `geo-1.0.1` conserva las 400 réplicas. Se añade fixture de un estado adverso entre 400 (EVPI/EVSI perfecto 150 €), sin recortar colas ni reescribir protocolos guardados.

Tras corregir el prior completo: **61 passed, 1 warning en 22,07 s**, Ruff correcto. Muestra de diseño + persistencia con evidencia geo vigente: **0,651 s**, 400 estados, EVPI **38,3356 €**, EVSI **0,5434 €**, corrección de límites numéricos **0 €**. Es una muestra local CPU, no garantía general ni cota del error total de integración.

### Frontend y cierre visual

```powershell
Set-Location frontend
npm.cmd run lint
npm.cmd run typecheck
$env:MARGIA_QA_URL='http://127.0.0.1:3002'
npm.cmd run test:e2e
npm.cmd run test:e2e -- tests/geo.spec.ts
```

- Lint y TypeScript finales sin errores ni advertencias. Build Next.js de producción correcto en Docker; tres servicios principales saludables.
- Regresión completa final de interfaz: **16 passed (2,0 min)**. Incluye centro, exportación/filtros, biblioteca, MMM, Search, laboratorio y actualización/consulta de la evidencia. Después de corregir el prior en `geo-1.0.1`, se repiten los recorridos afectados: **3 passed (27,2 s)**. Pruebas geo en la imagen definitiva, secuenciales: **22 passed, 1 warning en 5,90 s**.
- La primera repetición final mezcló por error pytest y Playwright escribiendo en la misma pila de QA: 21 passed, 1 failed por interferencia de fixtures. Ambos procesos terminaron; se repite pytest sin concurrencia y pasa. Esa ejecución fallida no cuenta como evidencia satisfactoria.
- 28 capturas generales (siete rutas × 1440×900, 1920×1080, 1280×720 y 390×844), cuatro del resultado geo y cuatro del resultado Search más su caso negativo. Axe sin infracciones detectadas en las combinaciones probadas; sin scroll horizontal global. Inspección manual de diseño, resultado, intervalo, leyenda y móvil. No se declara auditoría humana de lector de pantalla.
- Modern Web Guidance `forms`: radios nativos con fieldset/legend para duraciones, controles con label y límites, validación adicional en API, error con foco y estado anunciado. He mantenido envío habilitado para mostrar errores y lo bloqueo solo durante POST válido (“DON'T disable submit buttons to block validation”). Fuente/licencia ya registrada, sin dependencias de runtime nuevas.

Se mantiene el aviso heredado httpx/TestClient y el aviso de entorno `NO_COLOR`/`FORCE_COLOR` de Playwright. Sin nuevas dependencias, IA, GPU ni agentes. La optimización del reparto MMM sigue bloqueada; no se relajan umbrales para el siguiente orquestador. Método completo: [experimentos_geo.md](experimentos_geo.md).

## 25/11/2026 · Biblioteca y pretest creativo contextual (D4.1)

### Cálculo y API

- Pruebas específicas nuevas: **12 passed, 1 warning en 2,41 s**. Batería completa con código montado: **73 passed, 1 warning en 22,92 s**. Verificador oficial contra la imagen final de producción, `./scripts/comprobar.ps1`: **73 passed, 1 warning en 25,94 s**, Ruff y salud correctos.
- Validación de conteos binomiales y denominadores desiguales, disjunción de activos/campañas/fechas/IDs, alteración del holdout sin cambiar parámetros ni réplicas, reproducibilidad, bandas acotadas, advertencia de extrapolación y fallback al naive al bloquearse. Inputs inválidos, referencias CVR, escala de clics, tres variantes sin efecto identificado, ID/reutilización, selección ajena rechazada, historial y hechos sin cambios. Filtros, ordenación y vacío real.
- Las fixtures de API creativa usan una transacción exterior y savepoints: los POST guardan de verdad dentro de ella y al salir se revierten. Las pruebas operativas de persistencia usan su pila aislada. No se mezclan escritores pytest/Playwright sobre la misma base.
- Modelo `creatividad-bfce2ee924571d327baa`, `creatividad-1.0.0`, limitado. Ajuste observado 1,043 s en la principal y 1,017 s en la pila de QA; muestras locales CPU, no benchmark general. Particiones, métricas y baja fracción de tasas cubiertas por bandas de parámetros en [creatividad.md](creatividad.md).

### Producción y operación aislada

Pila nueva `margia-creatividad-qa` desde PostgreSQL vacío: migraciones 0001–0004, seed y tres modelos preparados. Actualización aditiva de la principal conservando el volumen y el checksum. Comandos ejecutados, desde la raíz:

```powershell
$env:MARGIA_PORT='3002'
docker compose -p margia-creatividad-qa up -d --build --wait --wait-timeout 180
docker compose -p margia-creatividad-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py preparar
docker compose -p margia-creatividad-qa restart db backend
docker compose -p margia-creatividad-qa up -d --wait --wait-timeout 120 db backend
docker compose -p margia-creatividad-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py verificar
docker compose -p margia-creatividad-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py reset
$env:MARGIA_PORT='3000'
docker compose up -d --build --wait --wait-timeout 180
./scripts/comprobar.ps1
```

Reinicio conserva modelo creativo (incluida fecha de creación), parámetros/réplicas, pretest y selección exactos; también hechos, decisión fixture, MMM, geo y Search. Reset en QA: **42,154 s**, elimina evaluaciones/selecciones y reproduce el modelo excepto duración/fecha de ajuste. Mantiene el checksum original `6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d` y restaura la evidencia Search inicial. La principal no se resetea.

Al terminar se ejecuta `docker compose -p margia-creatividad-qa down`, sin `-v`. El volumen se conserva; `docker compose ps` confirma principal saludable y solo 127.0.0.1:3000 publicado. GET de contexto/pretest confirma checksum intacto, modelo creativo vigente y nueve variantes.

### Interfaz y recursos

```powershell
node scripts/generar_variantes.mjs
Set-Location frontend
npm.cmd run lint
npm.cmd run typecheck
$env:MARGIA_QA_URL='http://127.0.0.1:3002'
npm.cmd run test:e2e -- tests/creatividad.spec.ts
npm.cmd run test:e2e
```

- Generadas nueve composiciones SVG locales con licencia/procedencia registrada, sin alterar las doce observadas. Lint/TypeScript finales correctos. Build Next.js final correcto en Docker para QA y principal.
- Primer recorrido específico: **4 passed (21,5 s)**. Tras ajustes visuales, regresión completa final: **20 passed (2,2 min)**. Incluye todos los recorridos anteriores y formulario → cifras reales de API → selección → recarga, metodología/teclado, filtros/vacío, contexto global sin reentrenar, error/reintento con inputs y foco, validación nativa y extrapolación.
- Capturas generales en 1440×900, 1920×1080, 1280×720 y 390×844, más pretest en los cuatro tamaños y comparadores moda/belleza. Axe sin infracciones en las combinaciones probadas, sin desbordamiento horizontal global. Inspección manual de pretest escritorio/móvil y recursos; el objetivo pasa a textarea para leerlo completo y los controles nuevos tienen al menos 48 px. No se declara auditoría humana de lector de pantalla.
- Modern Web Guidance `forms`: he aplicado labels, validación nativa y API, textarea redimensionable, foco/estado y el criterio “DON'T disable submit buttons to block validation”; solo se bloquea durante POST real. Sin dependencias de runtime nuevas.

### Incidencia de entorno y límites

Un rebuild intermedio falló al sincronizar caché Turbopack (`I/O error`, `spawn EIO`), seguido de caída del motor Docker. C: tenía solo 1,47 GiB libres; no se establece una causalidad definitiva con ese espacio. Los intentos operativos mientras el motor estaba caído fallaron antes de ejecutar y no cuentan como pruebas. Se recuperó mediante `docker desktop restart --timeout 45`, con recuperación automática de PostgreSQL. Se inspeccionó `docker system df` y se eliminaron por ID únicamente 37 registros recuperables de compilación de MARGIA del día, 1,63 GB de caché regenerable; sin eliminar volúmenes, imágenes de usuario ni datos. Build y operación repetidos satisfactoriamente después. C: continúa con alrededor de 1,3 GiB libres: riesgo de entorno para compilaciones futuras, no resuelto por compactación ni borrados globales.

Se conservan el warning conocido httpx/TestClient y el de entorno `NO_COLOR`/`FORCE_COLOR`. Predictor observacional limitado, CVR observado, composiciones empatadas por falta de identificación y multiplicador 1. A/B y efecto en escenarios pendientes. Sin agentes, LLM ni GPU.

## 25/11/2026 · Revisión fotográfica y formatos por plataforma

### Recursos y catálogo

- Imagegen integrada ejecutada durante el desarrollo: nueve escenas sintéticas fotográficas de hogar, moda y belleza. Revisadas las salidas generadas y las vistas reales de la aplicación. Sin fotos externas, modelos locales ni llamadas IA de runtime. Los prompts exactos se conservan en [creatividad_prompts.json](creatividad_prompts.json).
- `node scripts/preparar_imagenes.mjs`, dos pasadas: nueve WebP, **1.047.498 bytes** en total, máximo **169.146 bytes**, 1086×1448. Verificación independiente de los nueve SHA-256 y tamaños contra el manifiesto correcta. El script impide sustituir un recurso versionado con bytes diferentes. PNG originales y sus rutas locales fuera de Git.
- 36 combinaciones de perfil/escena/placement en API; Meta 4:5, TikTok 9:16, Display 1200:628 y YouTube 16:9. Biblioteca con recreaciones marcadas, formato histórico conservado y enlace al SVG original. Modelo `creatividad-1.0.0`, parámetros y checksum del negocio intactos; formatos/fotografías nuevos sin efecto identificado.

### Comandos y resultados

```powershell
docker compose run --rm --no-deps --volume "${PWD}/backend:/app" backend python -m pytest -q -p no:cacheprovider
docker compose run --rm --no-deps --volume "${PWD}/backend:/app" backend ruff check --no-cache .
$env:MARGIA_PORT='3002'
docker compose -p margia-creatividad-qa up -d --build --wait --wait-timeout 180
# Desde frontend:
npm.cmd run lint
npm.cmd run typecheck
$env:MARGIA_QA_URL='http://127.0.0.1:3002'
npm.cmd run test:e2e -- tests/creatividad.spec.ts
npm.cmd run test:e2e -- --trace off
# Desde la raíz:
$env:MARGIA_PORT='3000'
docker compose up -d --build --wait --wait-timeout 180
./scripts/comprobar.ps1
```

- Backend con código montado: **78 passed, 1 warning en 22,63 s**. Verificador oficial contra la imagen final de producción: **78 passed, 1 warning en 22,69 s**, salud y Ruff correctos. Nuevas pruebas de cada placement, recurso/metadatos, CTR compartido/multiplicador 1, asset histórico sin cambios y consulta/selección de una fixture de evaluación SVG anterior sin migrarla.
- Lint y TypeScript correctos. Builds finales de QA y principal correctos. No se añaden dependencias ni migraciones.
- Recorridos específicos iniciales: **6 passed (40,4 s)**. Tras corregir encuadre de Meta y semántica del componente, regresión completa final: **22 passed (2,1 min)**, con `--trace off`. Todos los recorridos matemáticos/funcionales y las auditorías/capturas permanecen activos; solo se desactiva la grabación de trazas por espacio.
- QA nueva: preparación con imágenes retenidas por la prueba de red, estado real visible, controles bloqueados durante trabajo, fallo de imagen/reintento con foco, inputs conservados, cambio de canal que retira resultados anteriores y ejecución en modo reduced-motion. Cuatro placements en escritorio/móvil, dimensiones reales del lienzo contrastadas con ratio y ancho natural de la foto; tres perfiles, selección y recarga.
- Capturas generales de siete rutas en cuatro tamaños; pretest en 1440×900, 1920×1080, 1280×720 y 390×844, más las cuatro plataformas en 1440/390 y comparadores de moda/belleza. Axe sin infracciones detectadas en las combinaciones probadas; sin desbordamiento horizontal global. Inspección manual de biblioteca, Meta, TikTok, banner, YouTube móvil y fotografías. No es una auditoría humana de lector de pantalla.

### Incidencias de QA y límites

Una regresión completa previa dio **21 passed, 1 failed**: `ENOSPC` al guardar capturas/trazas, con C: casi lleno; no se cuenta como satisfactoria. Se eliminó únicamente `frontend/.next` tras comprobar la ruta absoluta dentro del workspace (36,96 MiB de caché regenerable) y se repitió la batería sin trazas. Las capturas y las comprobaciones de accesibilidad se mantuvieron. C: continúa con unos 130 MiB libres: riesgo de entorno aún abierto; no se borraron volúmenes, datos ni recursos generados. No hubo caída del motor Docker en este corte.

La primera captura de un comparador móvil mostraba un artefacto de composición del enlace fijo de salto; se pasa a capturar la página completa desde arriba y se revisa la salida. El encuadre Meta se fija con área fotográfica/pie de texto estables para no tapar la base del producto. Se mantienen SVG y resultados antiguos, sin atribuirles las fotos nuevas.

Modern Web Guidance: he aplicado `optimize-image-priority`, una única imagen prioritaria y lazy normal para miniaturas fuera de pantalla (“Only use `fetchpriority=\"high\"` on at most 1-2 critical images”); `responsive-design`, proporción reservada y tipografía relativa al contenedor (“Use `aspect-ratio` for media elements”). Los fotogramas son estáticos, la preparación es una simulación identificada y el CTR sigue siendo contextual. A/B, escenarios y demás fases mantienen su backlog.

Persistencia repetida con la imagen final en la pila aislada: `tests/operacion.py preparar`, `restart db backend`, `up -d --wait --wait-timeout 120 db backend` y `tests/operacion.py verificar`, todos con resultado correcto. Conserva modelo/fecha, pretest completo (incluidos texto, recurso y plataforma), selección, hechos, MMM y Search/geo sin reentrenar. No se repite reset en esta revisión visual; su comprobación del hito D4.1 permanece registrada arriba. Al terminar, `docker compose -p margia-creatividad-qa down`, sin `-v`; principal saludable y solo localhost:3000 publicado. GET de contexto/pretest confirma checksum original, mismo modelo y 36 propuestas disponibles.

## 25/11/2026 · A/B creativo (D4.2)

### Matemáticas, mundo y API

```powershell
docker compose -p margia-ab-qa exec -T backend python -m pytest -q -p no:cacheprovider tests/test_ab.py
docker compose -p margia-ab-qa exec -T backend ruff check --no-cache .
$env:MARGIA_PORT='3000'
docker compose up -d --build --wait --wait-timeout 180
./scripts/comprobar.ps1
```

- Específicas contra imagen QA final de backend: **11 passed, 1 warning en 2,30 s**. Verificador oficial contra imagen principal: **89 passed, 1 warning en 27,98 s**, Ruff y salud correctos. Una batería previa con código montado dio 89 passed en 29,69 s; no sustituye la comprobación oficial posterior. No se añaden paquetes ni migraciones.
- Wilson contrastado con SciPy para ceros, tasas unitarias y conteos intermedios. Diferencias nulas, positivas y adversas; intervalos válidos y más amplios al corregir multiplicidad. MDE disminuye al aumentar exposición y aumenta con dos contrastes; producción imputada una vez.
- Asignación completa por oportunidad, exclusividad, equilibrio por fecha, reconciliación, reproducibilidad y hash alterado. Observaciones posteriores al corte solo tras ejecutar; el cliente no puede inyectar ganador/efectos. Estimador separado del mundo por la regresión AST existente.
- API: transiciones/idempotencia, recurso ajeno/duplicado rechazado, 150.000 oportunidades exportadas con su cabecera, catálogos geo/A/B separados, muestra insuficiente, huellas alteradas tras ejecutar/evaluar, conservación del JSON histórico y de pedidos/checksum.
- Aprendizaje: 200 draws por brazo, contexto exacto, efecto nulo/adverso aceptable, copias sin acumulación ni reducción de bandas, rechazo de diseños obsoletos, modelo anterior inmutable y consultas de versiones. Multiplicador económico 1 incluso con mejora de CTR.

El checksum original continúa en `6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d`. Extraer las expresiones CTR/CVR a un mecanismo compartido no altera el generador `mundo-1.0.0`; la rama nueva tiene versión `mundo-ab-1.0.0`. Predictor histórico `creatividad-1.0.0` y recursos fotográficos/SVG publicados conservados.

### Navegador, interfaz y accesibilidad

```powershell
# Desde frontend, contra QA aislada:
npm.cmd run lint
npm.cmd run typecheck
$env:MARGIA_QA_URL='http://127.0.0.1:3002'
npm.cmd run test:e2e -- tests/ab.spec.ts --trace off
npm.cmd run test:e2e -- --trace off
```

- Lint y TypeScript correctos. Builds Next.js de producción correctos en QA y principal. Regresión completa: **25 passed (3,0 min)**, con screenshots y axe activos, sin grabación de trazas. Tras el ajuste de espaciado, los tres recorridos A/B vuelven a pasar: **3 passed (29,7 s)**. No se suman estos recorridos repetidos como pruebas únicas adicionales.
- Tras aclarar las tarjetas históricas y compilar la interfaz final, se repiten todos los recorridos afectados: `npm.cmd run test:e2e -- tests/ab.spec.ts tests/creatividad.spec.ts --trace off`, **9 passed (1,3 min)**, incluidas las capturas/axe del diseño/resultado A/B y las cuatro plataformas. Lint final vuelve a pasar. El build final incluye comprobación TypeScript; el backend no cambia tras sus 89 pruebas.
- Flujo real: generar propuestas → guardar selección → diseñar tres brazos → MDE/costes de API → ejecutar → 42 filas diarias → evaluar dos contrastes → aceptar → recargar → consultar aprendizaje del pretest. El cambio de periodo conserva ID/estado sin reejecutar y no cambia el checksum. Sin errores JavaScript en el recorrido comprobado.
- Validación nativa de muestra, fallo HTTP recuperable con foco e inputs conservados, abstención por conteos escasos y descarga real de CSV de 1.000 oportunidades. Ningún botón de aceptación cuando falta evidencia; las acciones corresponden al estado persistido.
- Diseño y resultado capturados en **1440×900, 1920×1080, 1280×720 y 390×844**, además de toda la regresión visual anterior. Axe WCAG A/AA/2.1 AA sin infracciones detectadas en los tamaños probados y sin desbordamiento global. Revisión manual de formulario/resultado de escritorio y móvil; fotografía local, gráfico con tabla alternativa y tablas con scroll propio. No equivale a auditoría humana de lector de pantalla.
- La primera captura del diseño era prematura: `every()` sobre imágenes aún inexistentes no esperaba el formulario. Se añaden esperas por encabezado y foto real antes de capturar. Se corrige también un valor CSS de espaciado de etiquetas y se aclara en las tarjetas que su referencia pertenece al predictor histórico, separada del aprendizaje A/B.
- Modern Web Guidance `forms`: he aplicado radios/checkboxes nativos, fieldset/legend, límites nativos y de API, errores al enviar con foco, textarea redimensionable y submit bloqueado solo durante trabajo real, siguiendo “DON'T disable submit buttons to block validation”. La guía completa se consultó antes de modificar la interfaz.

### Persistencia y reset aislados

```powershell
$env:MARGIA_PORT='3002'
docker compose -p margia-ab-qa up -d --build --wait --wait-timeout 180
docker compose -p margia-ab-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py preparar
docker compose -p margia-ab-qa restart db backend
docker compose -p margia-ab-qa up -d --wait --wait-timeout 120 db backend
docker compose -p margia-ab-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py verificar
docker compose -p margia-ab-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py reset
```

Pila nueva `margia-ab-qa`, distinta de los volúmenes QA anteriores. Preparación, reinicio y verificación correctos: hechos, MMM, Search/geo, pretest, selección, protocolo/observaciones A/B, modelo completo y fecha exacta conservados sin reentrenar ni reejecutar. El reset tarda **44,807 s**, reproduce el checksum, elimina las pruebas/modelos A/B de usuario y devuelve 404 para sus IDs; restaura la evidencia inicial. No se resetea la principal. No se ejecutan pytest y Playwright mutando simultáneamente la misma base.

### Incidencias y límites del corte

El primer build de QA detectó props incorrectas al reutilizar `ModuleLink` en el enlace del laboratorio; corregidas al contrato real de ese componente antes de las pruebas satisfactorias. El primer comando operativo omitió `PYTHONPATH=/app` y falló al importar `app`, antes de preparar fixtures; se repitió correctamente con el entorno documentado. Ninguno de esos intentos se cuenta como satisfactorio.

C: comenzó con 106,5 MiB libres. `Get-VHD` no obtuvo permisos Hyper-V; no se modificó/compactó el disco. TRIM de Docker informó 6,9 MiB y no solucionó el espacio. Tras verificar la ruta absoluta se eliminó exclusivamente la caché regenerable de descargas npm `_cacache` (2.525,3 MiB), conservando `_npx`, paquetes instalados, configuración, proyectos y volúmenes. Se recuperaron **2,57 GiB** libres. No hubo ENOSPC ni caída de Docker en los builds/QA de este corte; sigue siendo un entorno con poco margen para acumular imágenes/cachés.

Avisos heredados httpx/TestClient y `NO_COLOR`/`FORCE_COLOR`. Inferencia nominal aproximada, oportunidades independientes, prior/percentiles condicionados, CVR seleccionado por clic, efectos latentes ilustrativos y transporte estricto. No se identifica beneficio, no se acumulan ramas y no se relaja el bloqueo de sensibilidad del MMM. D4.3, D5 y D6 pendientes; no se declara la aceptación completa A01–A14. Método y fuentes primarias en [experimentos_ab.md](experimentos_ab.md). Trabajo secuencial sin agentes.

Cierre operativo: `docker compose -p margia-ab-qa down`, sin `-v`, correcto; los tres servicios principales siguen saludables en localhost:3000. GET de contexto/pretest/pruebas confirma el mismo checksum y predictor histórico y cero pruebas A/B de QA en la principal. Espacio final C: **2,58 GiB** libres. La interfaz final se despliega con `docker compose up -d --build --no-deps --wait --wait-timeout 120 frontend`; el backend conserva la imagen de sus 89 pruebas.

## 25/11/2026 · Orquestador y búsqueda de escenarios (D4.3)

### Backend, datos y matemáticas

```powershell
$env:MARGIA_PORT='3002'
docker compose -p margia-escenarios-qa up -d --build --wait --wait-timeout 180
docker compose -p margia-escenarios-qa exec -T backend python -m pytest -q -p no:cacheprovider tests/test_escenarios.py
docker compose -p margia-escenarios-qa exec -T backend ruff check --no-cache .
$env:MARGIA_PORT='3000'
docker compose up -d --build --wait --wait-timeout 180
./scripts/comprobar.ps1
docker compose exec -T backend alembic current
```

- Migraciones 0001–0005 correctas desde volumen QA vacío; 0005 aditiva aplicada también sobre la principal conservando sus datos. `alembic current`: **0005 (head)**. Sin dependencias/lockfiles nuevos.
- Primera batería nueva: **10 passed, 1 warning en 3,38 s**; regresión entonces completa con código montado: **99 passed, 1 warning en 27,50 s**. Tras corregir la dependencia de canales intactos y añadir su regresión: **11 passed, 1 warning en 4,20 s** en QA. La normalización de predeterminados añade una aserción de reenvío completo: **11 passed en 4,71 s** con código montado. Ruff final correcto.
- Verificador oficial contra la imagen final principal: **100 passed, 1 warning en 32,49 s**, Ruff y salud correctos. Los resultados anteriores son checkpoints; no se suman a las 100 pruebas únicas.
- Contratos: N/ventas/coste/margen/contribución reconciliados por draw, nulo con delta cero en las 200 réplicas, cuota común/contratación, producción/prueba/otros una vez, semilla, stock inicial con fórmula cerrada, sin SEM en demanda, ausencia de mundo/verdad, soporte semanal y presupuesto. Rejilla habilitada por fixture explícita, mejor candidato factible y caso negativo/riesgo excesivo/sin candidato. El artefacto MMM real no se modifica ni habilita.
- API: GET sin crear ejecuciones, POST idéntico y reenvío de configuración completa reutilizan ID/resultado, calendario posterior al corte, selección/canal/recursos/versiones, equivalencia puntual con Search, aprendizaje posterior que crea otra ejecución conservando la anterior, validación y bloqueo crítico que permite consultar histórico. Fixtures aisladas por transacción/savepoint.

Proyección: cinco bloques reservados entre 14/06 y 31/10, WAPE **1,2100 %** frente a **2,5781 %** del naive estacional; MAE **419,584** frente a **894 pedidos/bloque**, sesgo **−0,2876 %**. Cuatro de cinco totales en banda, **80 % descriptivo**; estado limitado y sin garantía de cobertura. Errores calculados solo hasta train, sin fuga. Fórmula, unidades, hipótesis y fuentes primarias en [escenarios.md](escenarios.md).

### Interfaz y navegador

```powershell
# Desde frontend, contra QA aislada:
npm.cmd run lint
npm.cmd run typecheck
$env:MARGIA_QA_URL='http://127.0.0.1:3002'
npm.cmd run test:e2e -- tests/escenarios.spec.ts --trace off
npm.cmd run test:e2e -- --trace off
```

- Lint y TypeScript correctos; lint final repetido y build final con TypeScript. Builds de producción QA y principal correctos.
- Regresión completa: **29 passed (3,0 min)**. Tras normalizar entradas y ajustar términos a español, los cuatro recorridos afectados se repiten con validación de producción sin propuesta y enlace desde medición: **4 passed (35,9 s)**. Sin contar repeticiones como pruebas únicas.
- Search guardado → contexto por ID → comparación → búsqueda limitada → tabla/waterfall/método → recarga y cambio global sin reejecutar. Creatividad con A/B → selección/foto → B con coste de producción: cambiar CTR no cambia pedidos; el coste sí cambia el delta una vez. Medición conserva el canal real al enlazar.
- Validación nativa, error HTTP recuperable con foco/inputs, ámbito nacional y techo cero con ausencia de candidato; la base no se declara factible por defecto. Ninguna aprobación ni activación fingida.
- Diseño/resultado en **1440×900, 1920×1080, 1280×720 y 390×844**; regresión general y cuatro plataformas fotográficas conservadas. Axe WCAG A/AA/2.1 AA sin infracciones detectadas ni desbordamiento global. Revisión manual escritorio/móvil: etiquetas del gráfico legibles, importes del desglose visibles en móvil, tablas comparativas con scroll local y cabeceras fijas. No es auditoría humana de lector de pantalla.
- Modern Web Guidance: he aplicado `forms` con validación nativa/API, fieldset/legend, foco y bloqueo solo durante POST (“DON'T disable submit buttons to block validation”); `responsive-table`, cabeceras semánticas/fijas y scroll enfocable con propiedades lógicas/z-index (“Use logical properties and explicit z-index values”). Se mantiene comparación por columnas en las tablas densas.

### Operación y conservación de historia

```powershell
$env:MARGIA_PORT='3002'
docker compose -p margia-escenarios-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py preparar
docker compose -p margia-escenarios-qa restart db backend
docker compose -p margia-escenarios-qa up -d --wait --wait-timeout 120 db backend
docker compose -p margia-escenarios-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py verificar
docker compose -p margia-escenarios-qa exec -T -e PYTHONPATH=/app -e MARGIA_VALIDACION=1 backend python tests/operacion.py reset
docker compose -p margia-escenarios-qa down
```

Preparación, reinicio y verificación correctos: modelos/fechas originales, hechos, Search/geo, pretest/A-B y comparación exacta, incluidas las matrices internas de 200 réplicas. Reenvío de entradas completas devuelve la misma ejecución sin calcular otra. Reset aislado **41,601 s**: mismo checksum, evidencia inicial restaurada y comparaciones de usuario eliminadas/404. QA detenida sin `-v`; principal sin reset y con tres servicios saludables, solo localhost:3000 publicado.

Muestra operativa guardada: cálculo interno de la comparación **0,0119 s**, resultado JSON completo **530.953 bytes**. No incluye consultas/escritura ni es un benchmark general de la rejilla habilitada. La matriz de rendimiento completa permanece en D6.

### Incidencias, límites y estado final

- Primera revisión: el soporte del MMM se aplicaba también a Display/TikTok intactos fuera de train, descartando incorrectamente el ahorro Search. Se separa conservación del punto actual de cambios: estos siguen validándose por semana. Nueva regresión lo verifica; no se relaja el diagnóstico de sensibilidad.
- Primer Playwright específico: **3 passed, 1 failed (30,9 s)** por leer la URL antes de finalizar la navegación desde Search. El enlace funcionaba; se añade espera de URL real. No se cuenta esa batería como satisfactoria. También se corrigen etiquetas solapadas/tabla de desglose en móvil, advertidas en revisión manual, y estilo de nombres/imports detectado por Ruff antes de los resultados finales.
- Se valida también el valor predeterminado de cada campo para evitar IDs diferentes entre números enteros/decimales al reenviar una configuración guardada. Regresión y prueba operativa de reutilización correctas.

La API principal confirma checksum **`6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d`**, modelo creativo **`creatividad-bfce2ee924571d327baa`**, MMM **bloqueado/no optimizable** y cero ejecuciones de QA. C: con **2,61 GiB** libres al cierre, sin ENOSPC ni caída de Docker en este corte. Se conservan warnings heredados httpx/TestClient y color Playwright. Revisión del nuevo código sin coincidencias de patrones de credenciales/datos privados; la auditoría completa sigue en D6.

**Días 1–4 verificados con sus límites.** D5 CRUD/decisiones/exportaciones, incidencias/restauración y recorrido integrado/guion; D6 congelación, A01–A14, rendimiento, accesibilidad final y presentación. No se declara POC acabada. Sin agentes ni delegación.
