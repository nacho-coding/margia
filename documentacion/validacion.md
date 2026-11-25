# Validación ejecutada · Fundaciones y Medición

Fecha: 25/11/2026. Pila real de producción local en Docker Desktop sobre Windows. Incluye evidencia histórica del Día 1 y el incremento D2.1–D2.2 al final del documento. No acredita D2.3–D5 ni validez comercial sobre datos reales.

## Estado de aceptación

| Criterio | Cobertura del incremento | Resultado |
|---|---|---|
| A01 | Compose, PostgreSQL vacío, migración congelada, seed, health, reinicio, reset | Verificado en pila aislada y producción local; ver comandos |
| A02 | Reproducción, checksum canónico, FK, clics/exposición, presupuesto y reconciliación | 26 tests pytest pasan en la batería actual, incluidos los de MMM |
| A03 | MMM ajustado, holdout, naive, diagnóstico, curvas con soporte y límites | Verificado como modelo observacional; reparto por canal inestable y recomendaciones bloqueadas |
| A04–A09 | Search causal, geo, pretest/A-B, optimización, EVPI/EVSI e incidencia | Pendientes; solo aritmética contractual unitaria y vistas descriptivas |
| A10 | Persistencia de fixture de decisión y checksum tras reinicio | Verificado; CRUD de escenarios y decisiones de usuario pendiente |
| A11 | Contexto, medios/búsqueda/creatividad, filtros, detalles, exportación, reintento, reset protegido y lectura del MMM | Playwright: nueve recorridos pasan en el incremento de Medición |
| A12 | Siete rutas × cuatro tamaños, sin scroll global, axe y revisión visual | 28 capturas reales; revisadas las siete vistas, con centro móvil/escritorio y biblioteca 1920 |
| A13 | CPU, recursos locales, .env ignorado, sin agentes/LLM/API pagada | Inspección de código/configuración y staging; sin tokens/dumps/capturas/dependencias locales publicados |
| A14 | PRD/RFC conservados y commits locales | Push bloqueado por permisos de GitHub al último intento |

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
