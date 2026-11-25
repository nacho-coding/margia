# Creatividad: biblioteca y pretest contextual

Hito D4.1 del backlog. Datos enteramente sintéticos; corte 31/10/2026. Este incremento prepara una hipótesis visual y la guarda. La prueba A/B, su actualización y la aplicación de un efecto económico pertenecen a D4.2–D4.3.

## Datos y alcance

Se conservan los 80 registros creativos, las 12 composiciones originales y sus 28 días parciales de observación (04–31/10/2026). Reutilizar una composición en varios registros no añade diseños independientes. No se regenera el negocio ni se cambian los conteos para favorecer al predictor.

El estimador recibe exclusivamente impresiones, clics, conversiones observadas, frecuencia, canal, audiencia y atributos del creativo/campaña. No importa el mundo sintético ni lee la verdad latente. Categoría, tono y CTA están ligados en estos datos: se codifican como **un paquete**, sin atribuirles efectos independientes. No se extraen características de píxeles.

La biblioteca permite filtrar canal, categoría, audiencia y objetivo, y ordenar por ID, inversión, CTR o CVR. El único formato observado, cuadrado 1:1, se informa como tal. Los filtros globales de fecha y mercado seleccionan observaciones; el modelo nacional persistido no se reentrena ni se convierte en un modelo local al navegar. Ausencia de observaciones produce estado vacío.

## Modelo y denominadores

Versión `creatividad-1.0.0`, semilla raíz 260725. Regresión logística binomial con NumPy/SciPy en CPU:

```text
y_i = clics; n_i = impresiones
p_i = expit(x_i · beta)
L(beta) = sum[n_i · log(1 + exp(x_i · beta)) - y_i · (x_i · beta)]
          + 10/2 · sum[beta_j² para j distinto del intercepto]
```

Se usa `logaddexp` para estabilidad y L-BFGS-B con gradiente analítico. Ridge 10 fijada antes de la evaluación; no se optimiza con el holdout. Canal, paquete y audiencia tienen codificación con referencia; frecuencia se estandariza solo con train. Los conteos pesan por exposición, sin promediar CTR de filas con denominadores distintos.

CVR es exclusivamente una referencia **observada de train por canal**, suma de conversiones / suma de clics. Son conversiones atribuidas del registro creativo, no pedidos únicos ni demanda adicional. No se entrena un predictor CVR ni se transforma CTR en ventas.

## Validación sin compartir composiciones ni campañas

Los grupos son componentes conectados por ruta del activo y campaña. Se reserva determinísticamente un grupo por canal, ordenado por ID y sin consultar resultados. Entrenan los grupos restantes en los primeros 21 días; el holdout usa solo grupos reservados en los últimos siete. Las filas del cruce contrario de fechas/grupos se excluyen de ambas particiones.

| Partición | Fechas | Filas | Composiciones | Campañas |
|---|---|---:|---:|---:|
| Train | 04–24/10/2026 | 1.176 | 8 | 40 |
| Holdout | 25–31/10/2026 | 168 | 4 | 20 |
| Excluidas | Cruce de ventana y grupo | 896 | — | — |

Los grupos, campañas e identificadores de train y holdout son disjuntos. El ajuste final conserva exactamente train: no se reajusta con el holdout tras medir. Pruebas de alteración de los clics reservados comprueban que ni parámetros ni réplicas cambian; sí puede cambiar el diagnóstico de aceptación.

Referencia naive: CTR por canal calculado solo con train, con suavizado `(clics + 0,5) / (impresiones + 1)`. Se evalúan ambos sobre las mismas filas reservadas.

| Métrica por impresión del holdout | Modelo | Referencia por canal |
|---|---:|---:|
| Pérdida logarítmica | 0,069705 | 0,070046 |
| Error absoluto ponderado de CTR | 0,4160 puntos porcentuales | 0,4621 puntos porcentuales |
| CTR predicho agregado | 1,2489 % | 1,1530 % |

Holdout: 75.561 impresiones, 989 clics, CTR observado 1,3089 %. Train: 574.117 impresiones y 6.618 clics. Son resultados de esta muestra, no valores fijados en la interfaz ni garantías de generalización. El modelo mejora modestamente la referencia en pérdida logarítmica y permanece **limitado** por muestra, confusión y transporte. Si no mejora esa pérdida o faltan ocho grupos de train, se bloquea y el pretest sirve la referencia por canal, sin bandas del predictor rechazado.

## Incertidumbre y soporte

200 refits de grupos completos de composición/campaña, estratificados por canal, con substream `SeedSequence([semilla, 4101])`. Las mismas réplicas de parámetros sirven las tres propuestas. P05–p95 son bandas de parámetros condicionadas a esta muestra; no incorporan variabilidad de nuevos clics ni identifican causalidad. Solo el 19,05 % de las tasas de las filas reservadas cae dentro: se muestra ese diagnóstico, sin llamarlo cobertura predictiva.

Frecuencia observada en train: 1,21–4,50. Se advierte cuando el contexto sale de ese rango o usa una combinación aditiva no observada; las audiencias ajenas al canal se rechazan. La POC conserva resultados adversos y advertencias. No se deriva un ranking económico de estas asociaciones.

## Tres composiciones y brief

Nueve SVG originales locales: hogar, moda y belleza × espacio, marco y detalle. `scripts/generar_variantes.mjs` reutiliza los productos de las composiciones originales con tres jerarquías visuales. Son activos precreados, no imágenes generadas al pulsar el formulario. Textos, CTA y tono se mantienen comparables dentro del perfil. Procedencia/licencia en [licencias.md](licencias.md).

El formulario recoge canal, perfil, audiencia, frecuencia, impresiones y objetivo. Python calcula CTR contextual, bandas y esperanza de clics (`impresiones × CTR`), y compone el brief mediante reglas. Las tres propuestas comparten **la misma referencia**: no hay efecto diferencial visual identificado ni ganador predictivo. La banda de esperanza no es un intervalo de conteos futuros.

Guardar una propuesta crea una selección inmutable, consultable al recargar y en el historial. Es una hipótesis para una prueba futura; no activa medios ni modifica ventas. `multiplicador_demanda=1`, `efecto_identificado=false`. No se incorpora todavía a un escenario ni se simula una actualización A/B inexistente.

## Persistencia y API

- `modelo` conserva parámetros, 200 réplicas, esquema, soporte, particiones, métricas, checksum, versión y semilla. El arranque lo prepara bajo advisory lock compartido con reset; GET no entrena.
- Migración aditiva 0004: `pretest_creativo` y `seleccion_creativa`, con FK e índice único de selección por evaluación/variante.
- La evaluación guarda inputs y resultado por contenido. Repetir contenido devuelve el mismo ID y declara reutilización. La selección valida pertenencia a la evaluación.
- Recursos con `version_recurso=variantes-1.0.0`. Tras publicar, las rutas de esos SVG se conservan: un rediseño deberá crear ruta y versión nuevas para que una evaluación antigua mantenga su composición.
- El reset explícito reconstruye los hechos/modelos reproducibles y elimina evaluaciones y selecciones de usuario. Un reinicio conserva modelos y resultados sin reentrenar.

| Método | Ruta `/api/v1` | Acción |
|---|---|---|
| GET | `/creativos` | Biblioteca agregada y paginada |
| GET | `/creativos/pretest` | Catálogo, valores iniciales y diagnóstico del modelo |
| POST | `/creativos/evaluar` | Calcular y guardar referencia/brief |
| GET | `/creativos/evaluaciones/{id}` | Consultar resultado inmutable |
| POST | `/creativos/selecciones` | Guardar hipótesis de variante |
| GET | `/creativos/selecciones/{id}` | Consultar selección |
| GET | `/creativos/historial` | Últimas diez evaluaciones y selecciones |

Pruebas realmente ejecutadas y operación aislada en [validacion.md](validacion.md). Fuentes primarias del cálculo: [SciPy minimize](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html), [expit](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.expit.html) y [GLM binomial con denominadores](https://www.statsmodels.org/stable/generated/statsmodels.genmod.generalized_linear_model.GLM.html); statsmodels no se añade como dependencia.
