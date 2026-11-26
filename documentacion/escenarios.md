# Orquestador de escenarios y búsqueda con restricciones

Hitos P0 D4.3–D5.1. Proyección y estimaciones sobre datos enteramente sintéticos. Un único motor compara **base, A conservar ahorro y B reinvertir** y utiliza la misma valoración económica para la rejilla. Las decisiones se registran de forma simulada y nunca activan publicidad. El MMM original conserva su diagnóstico bloqueado; no se fuerza una recomendación de reparto.

## Alcance y referencia

La primera versión trabaja a nivel nacional y con horizonte de 28 días, posterior al corte del snapshot. Los filtros globales de lectura no alteran una ejecución guardada. Un mercado individual no recibe el modelo nacional prorrateado; una comparación nueva requiere todos los mercados. Campañas, creatividad y búsqueda siguen siendo vistas parciales de medios, sin añadir su gasto a la inversión.

El servicio carga negocio y medios por separado, comprueba cobertura de las 104 semanas y obtiene ticket y margen por pedido desde los últimos 28 días observados. Estos dos importes por pedido permanecen fijos en todas las alternativas y réplicas. La base conserva la inversión por canal y el perfil de las cuatro semanas recientes. No se leen parámetros verdaderos ni futuras observaciones del mundo sintético.

Se elige la alternativa contractual de **deltas agregados no solapados**. Los siete canales de demanda usan términos MMM; SEM marca solo interviene en captura mediante Search. Es una aproximación nacional con interacciones limitadas, no un gemelo causal completo ni una predicción regional.

## Base estacional y diagnóstico temporal

Con `y[t]` pedidos nacionales por semana, la proyección de las cuatro semanas posteriores al corte es:

```text
nivel = suma(últimas cuatro semanas) / suma(mismas cuatro semanas de hace 52 semanas)
base_futura[t] = pedidos de esa semana de hace 52 semanas × nivel
N_base = suma de las cuatro semanas futuras
```

La referencia mantiene el patrón anual observado, ajusta su nivel reciente y no anticipa nuevas campañas, precios, promociones o cambios de captura. El desplazamiento es de 52 semanas, 364 días, conservando el día de la semana. No usa los controles o el reparto del MMM bloqueado para determinar el nivel base. El enfoque parte del benchmark [naive estacional de Forecasting: Principles and Practice](https://otexts.com/fpp3/simple-methods.html); el ajuste multiplicativo de nivel es una decisión explícita de esta POC.

Se calculan errores de predicción de un paso con orígenes anteriores al final de train del MMM. Cada origen usa exclusivamente su pasado y el nivel de sus cuatro semanas previas. En el universo probado hay 28 errores semanales hasta el 13/06/2026. Se centran y se remuestrean bloques circulares completos de cuatro semanas; no se tratan días como réplicas independientes. Es una aproximación de errores históricos que presupone estabilidad, inspirada en [intervalos por remuestreo de residuos](https://otexts.com/fpp3/prediction-intervals.html), sin prometer cobertura nominal.

La fórmula se fija antes de consultar cinco bloques posteriores reservados, de 28 días cada uno, entre 14/06 y 31/10/2026. Para cada origen se permite conocer sus observaciones anteriores, sin mirar el bloque que predice. Resultado calculado: WAPE **1,2100 %**, MAE **419,584 pedidos por bloque**, sesgo **−0,2876 %**. Naive estacional sin ajuste: WAPE **2,5781 %**, MAE **894 pedidos**. Cuatro de cinco totales quedan dentro de la banda de errores, **80 % descriptivo**; cinco bloques no calibran su cobertura. No se reajusta la fórmula ni se cambia semilla para mejorar estos resultados. El estado de la proyección permanece limitado.

## Cambios de demanda y captura

Para un presupuesto de demanda propuesto `B[j]`, cada semana conserva la proporción de gasto del perfil de referencia del canal. Se reconstruye el stock inicial desde todas las semanas de gasto observado, normalizadas con la escala aprendida en train. Después se avanza por las cuatro semanas futuras:

```text
a[j,t] = gasto[j,t] / escala_train[j] + persistencia × a[j,t−1]
h[j,t] = a[j,t] / (a[j,t] + k)
delta_demanda = suma_j coeficiente[j] × suma_t(h_propuesta[j,t] − h_base[j,t])
```

La forma Hill tiene pendiente 1, como el artefacto guardado. No se reutiliza como proyección de cuatro semanas una curva de siete días con stock fijo. SEM marca se rechaza si aparece entre los canales de demanda.

La captura utiliza el estimador Search vigente, sin deducir recuperación SEO/directo de atribución:

```text
ahorro = inversión_SEM_marca_referencia × recorte
delta_captura = ahorro × tasa_de_pedidos_por_euro(recorte)
delta_pedidos = delta_demanda + delta_captura
```

La tasa y sus réplicas se interpolan dentro del soporte experimental. Fuera de soporte se conserva el comportamiento hipotético del simulador Search, sin habilitar recomendación. Al aceptar un geo, el soporte puede restringirse a su intensidad concreta.

La partición mantiene fijo el perfil de captura al valorar demanda y el nivel base al valorar Search. No estima la interacción entre ambas intervenciones, recuperación orgánica, elasticidad de precios ni cambios de ticket/margen. Esos supuestos se muestran en el método. La alternativa A coincide con la valoración puntual One Search con el mismo recorte, margen por pedido y costes; una prueba comprueba esa equivalencia.

## Costes y creatividad

`comparar_plan` en el dominio económico valora todas las alternativas. El contrato histórico `comparar_captura` delega en él conservando su respuesta anterior. No hay lógica económica en JavaScript.

```text
I_propuesta = I_base − ahorro_SEM + reinversión
M_propuesta = M_base + delta_pedidos × margen_por_pedido
contribución = margen − medios − producción − experimento − plataforma − otros
delta = contribución_propuesta − contribución_base
```

Ventas y coste directo se derivan con el mismo ticket/margen fijo y reconcilian con el margen. El ahorro se refleja en medios, sin sumarlo de nuevo. El waterfall muestra ahorro SEM, reinversión, cambio de margen, costes y neto, con signos y offsets calculados por backend.

La cuota común figura en base y alternativas y se cancela en el delta. Una contratación nueva se imputa a las alternativas aunque su recorte sea cero; la opción mantener conserva el negocio actual sin contratar. Los costes de experimento y otros son incrementales del periodo de cada alternativa. Solo se introducen costes pendientes, sin cobrar de nuevo pruebas ya realizadas.

Una selección guardada conserva ID, recurso, texto, placement, contexto y versiones históricas/A-B. Su canal debe coincidir con el destino de B. El CTR experimental del contexto exacto se consulta como referencia de clics; **no se transforma en pedidos propios**. `multiplicador_demanda=1`, también con A/B favorable. El coste de lanzar esa propuesta se carga una vez en B. La búsqueda puede conservar las creatividades actuales: los candidatos sin lanzamiento no pagan producción nueva. Las ejecuciones anteriores conservan la referencia que utilizaron aunque cambie el aprendizaje.

## Doscientas réplicas compartidas

Una sola selección reproducible de draws sirve base, A, B y todos los candidatos. Substreams `SeedSequence([semilla, 5101/5102/5103])`: coeficientes MMM, vector Search y errores de proceso. Semilla inicial: raíz + 5100. Referencia primaria de la API: [NumPy Generator](https://numpy.org/doc/stable/reference/random/generator.html).

- MMM: se remuestrean filas completas de sus 80 refits guardados, preservando la correlación entre coeficientes. No se hacen 200 ajustes nuevos.
- Search: se conserva el vector de intensidades de cada una de sus 400 réplicas; todas las alternativas usan el mismo índice por draw.
- Proceso: el mismo error aditivo de cuatro semanas se añade a la base de cada draw y a sus alternativas. Con ticket/margen fijo se cancela en el delta. No se inventa ruido independiente por política.

Se asume independencia entre las familias MMM, Search y error base porque no hay una dependencia conjunta estimada. Se guardan índices, stock inicial, resultados completos por réplica y una huella común en PostgreSQL. La API publica el resumen y huella, excluyendo las matrices internas.

Se calculan media, p05/p50/p95 y fracción de draws con `delta < 0`. Son bandas y riesgo **condicionados a modelos y supuestos**, sin incertidumbre completa de selección, transporte o interacciones. La estimación puntual y la media de draws se etiquetan por separado. No se eliminan draws adversos para mejorar el resultado; una distribución físicamente inválida se rechaza.

## Restricciones, soporte y búsqueda

El usuario fija techo total de medios, recorte máximo de marca, riesgo máximo y mínimos/máximos por canal de demanda. La reinversión manual es una fracción del ahorro de SEM destinada a un canal; el remanente se conserva. Presupuestos no negativos, sin aumentar SEM ni contabilizarlo como demanda. Producción y otros costes aparecen aparte del techo de medios.

Para un cambio de canal, el intervalo admisible del presupuesto total se obtiene intersectando los factores que mantienen **cada semana** entre el mínimo/máximo observado en train. No basta con comprobar el total mensual. El estado actual es además un punto de referencia permitido aunque salga de ese soporte: si el canal no cambia, su delta es exactamente cero y no necesita transportar una curva MMM.

En la muestra actual Display y TikTok tienen alguna semana reciente fuera del soporte de cambios. Se pueden conservar intactos al evaluar Search; eso no habilita modificaciones fuera de soporte. Los límites iniciales incluyen la envolvente del soporte y el punto actual, pero cualquier valor distinto del actual vuelve a comprobarse contra el soporte semanal. La regresión detectó y corrigió el bloqueo excesivo de opciones Search por canales intactos; no se relaja ningún umbral del MMM.

La rejilla determinista considera mantener, las intensidades Search disponibles y el recorte solicitado dentro de soporte/límite, fracciones de ahorro 25/50/75/100 % más la solicitada, y un canal de reinversión cada vez. Todas se valoran con el mismo motor/draws. Se maximiza contribución esperada entre los candidatos factibles, con evidencia suficiente y riesgo dentro del límite. Mantener gana los empates; si ninguna acción mejora una base elegible, se conserva. No se afirma óptimo global ni se exploran repartos simultáneos entre varios canales.

**En la demo real el MMM sigue bloqueado/no optimizable.** La búsqueda excluye reinversión y compara solo mantener/ahorro Search cuando su propia evidencia lo permite. B se calcula y muestra como hipótesis con motivos; no entra como recomendación. La búsqueda completa con curvas habilitadas se verifica mediante una fixture explícita que no se carga en producción ni puede activarse por HTTP.

Si ninguna opción cumple límites, evidencia y riesgo se devuelve `sin_candidato`, sin convertir la base en una solución factible. Puede existir una solución fuera de esta rejilla; el mensaje no declara inviabilidad global del problema. Con datos críticos bloqueados se impide una ejecución nueva y se permite consultar las guardadas.

## Persistencia e integración

Migración aditiva **0005**, tablas `escenario` y `ejecucion`. Configuración, revisión, snapshot, versiones, semilla, huella de fuentes y resultado quedan congelados. El ID por contenido permite reutilizar una ejecución idéntica; el servidor devuelve `reutilizada=true` y no vuelve a calcular. Una versión de evidencia distinta crea otra ejecución, conservando la configuración y resultados anteriores. Advisory lock compartido con reset serializa escrituras.

Los valores predeterminados también se validan/normalizan antes de obtener el ID. Reenviar las entradas completas guardadas conserva el mismo resultado, sin crear una ejecución adicional por representar un importe como entero o decimal.

La pantalla muestra base/A/B, denominadores, costes, bandas, waterfall con tabla alternativa, presupuestos por canal, candidato/auditoría de rejilla, selección fotográfica e historial. Los enlaces desde Search y creatividad llevan IDs reales; medición conserva el canal. Si la evaluación Search de origen es antigua, se conservan su ID/modelo de origen y sus parámetros, calculando con la evidencia vigente explícitamente indicada.

| Método | Ruta bajo `/api/v1` | Acción |
|---|---|---|
| GET | `/escenarios` | Catálogo, referencia, límites, selecciones e historial; sin MC ni optimización |
| GET | `/escenarios?seleccion={id}&simulacion={id}` | Recuperar contexto/inputs desde registros guardados |
| POST | `/escenarios/ejecutar` | Comparar, buscar candidato y guardar/reutilizar ejecución |
| GET | `/escenarios/ejecuciones/{id}` | Recuperar el resultado inmutable |

El reinicio conserva draws, referencias y fecha exacta sin reejecutar. Reset explícito elimina configuraciones/ejecuciones de usuario y reproduce el mismo universo; se comprueba exclusivamente en QA aislada. El checksum original permanece intacto. Pruebas reales, incidencias y resultados en [validacion.md](validacion.md).

## Borradores y revisiones (D5.1)

La migración aditiva **0006** añade `escenario.editable`, `revision_escenario` y `evento_escenario`. Recupera la revisión de las configuraciones existentes, conservando parámetros, resultados y fechas. Las configuraciones D4.3 siguen siendo de solo lectura y se pueden duplicar. Un borrador nuevo tiene ID propio y revisión 1; guardar parámetros distintos crea otra revisión inmutable. Guardar los mismos no incrementa la revisión.

Editar, ejecutar y archivar exigen la revisión esperada. El lock transaccional común con reset y la comparación de revisión evitan sobrescribir otra edición: conflicto HTTP 409, sin pérdida de entradas. Ejecutar un borrador incluye su ID, revisión, parámetros normalizados, versiones y huella de fuentes en la identidad del resultado. Una lectura o un guardado no ejecuta MC. La comparación rápida conserva el endpoint y los IDs D4.3.

Estados del escenario: `borrador → archivado`, o `evaluado → archivado` para configuraciones históricas. Ejecutar un borrador conserva su carácter editable; la ejecución captura la revisión concreta. Archivar exige motivo de 10–1.000 caracteres, registra fecha de sistema y no borra revisiones, ejecuciones o decisiones. Reenvío idéntico de archivo sin efecto adicional; cambiar el motivo ya registrado devuelve 409. Para continuar, duplicar. No hay borrado físico individual: el CRUD usa archivo para conservar trazabilidad. Reset explícito sigue siendo el único borrado conjunto.

El catálogo muestra los últimos 50 escenarios del snapshot activo y las últimas 30 ejecuciones. El detalle recupera todas las revisiones/ejecuciones del escenario, también archivado. Los resultados y decisiones por ID se pueden consultar aunque ya no pertenezcan al snapshot activo; esa lectura histórica no autoriza una aprobación nueva.

## Decisiones y guardrails

Se elige uno de cuatro planes guardados: base, A, B o candidato de la rejilla. Solo existe una decisión terminal por ejecución: `aprobado` o `rechazado`, con motivo obligatorio de 10–1.000 caracteres. Un reenvío idéntico devuelve el mismo registro; cambiar plan, resolución o motivo devuelve 409. Para reconsiderar se prepara otra ejecución, mediante una revisión nueva o una copia. La decisión conserva entradas, snapshot, revisión, modelos, semilla, periodo, huellas, métricas, presupuesto, banda y guardrails al registrar.

Antes de aprobar se revalidan en servidor snapshot activo, integridad crítica, archivo/revisión del borrador, versión del motor, huella de observaciones y calibración temporal de la base. Cada plan conserva sus restricciones, soporte y límite de probabilidad de pérdida. Un cambio de contribución esperada negativa no se aprueba aunque se tolere todo el riesgo; mantener sigue disponible cuando es factible.

La dependencia es específica: recortar exige Search vigente/no bloqueado y dentro de soporte; reinvertir exige MMM vigente/optimizable/no bloqueado; lanzar creatividad exige que siga coincidiendo su recurso y evidencia de contexto. El bloqueo del MMM no veta mantener ni una alternativa Search que cumpla sus propias comprobaciones. Los motivos limitantes del plan se conservan: no se habilitan por el simple hecho de escribir una justificación.

La base y las bandas continúan siendo proyecciones/estimaciones condicionales, sin garantía causal. La aprobación limitada registra la decisión simulada y su evidencia; no certifica rentabilidad real ni activa campañas. Se permite registrar un rechazo/abstención incluso con plan bloqueado, sin candidato o fuentes actualmente indisponibles. Las decisiones anteriores permanecen terminales aunque cambie el estado actual; el detalle identifica los guardrails **al registrar**.

## Exportaciones y navegación

CSV UTF-8 con BOM y separador `;`, cifras numéricas con coma decimal, filas de trazabilidad/economía/bandas/presupuestos/condiciones y decisión si existe. Markdown con comparación por columnas, inputs, fuentes/versiones/semilla, supuestos y decisión. Ambas exportaciones leen el resultado congelado: no calculan ni entrenan. El mismo registro produce el mismo archivo; una decisión posterior añade su registro sin alterar las métricas. Los textos libres se protegen contra fórmulas CSV y se escapan para Markdown/HTML; los importes negativos conservan su tipo numérico.

La interfaz permite guardar antes de ejecutar, editar/duplicar/archivar con motivo, revisar entradas/resultados previos, aprobar/rechazar y abrir la decisión por ID desde el centro o la comparación. Descargas reales desde el proxy del mismo origen. Formularios nativos, errores con foco y entradas conservadas, diálogo modal nativo con foco inicial seguro y retorno al invocador. Las fechas del registro son del sistema, separadas del horizonte sintético.

| Método | Ruta bajo `/api/v1` | Acción |
|---|---|---|
| POST | `/escenarios` | Guardar borrador, sin ejecutar |
| GET / PATCH | `/escenarios/{id}` | Consultar o editar con `{revision, parametros}` |
| POST | `/escenarios/{id}/ejecutar` | Ejecutar la revisión esperada |
| POST | `/escenarios/{id}/duplicar` | Copiar parámetros con nombre nuevo |
| POST | `/escenarios/{id}/archivar` | Archivar con revisión y motivo |
| GET / POST | `/escenarios/ejecuciones/{id}/decision` | Consultar guardrails/decisión o registrar `{plan, estado, motivo}` |
| GET | `/escenarios/ejecuciones/{id}/exportar?formato=csv` | CSV; `md` para Markdown |
| GET | `/decisiones` y `/decisiones/{id}` | Historial y detalle inmutable |

La tabla `decision` previa se reutiliza con unicidad por ejecución; su FK histórica sigue siendo lógica para conservar la fixture operativa inicial sin ejecución. La API siempre comprueba la existencia del resultado y solo escribe decisiones sobre él. No se incorporan usuarios, RBAC ni activación externa. D5.2 mantiene pendientes snapshots de incidencia/restauración; D5.3 el recorrido integrado final y guion, y D6 la aceptación global.
