# Creatividad: biblioteca y pretest contextual

Método del hito D4.1 del backlog. Datos enteramente sintéticos; corte 31/10/2026. Prepara una hipótesis visual y la guarda. La extensión A/B y su aprendizaje de CTR, implementados en D4.2, se describen en [experimentos_ab.md](experimentos_ab.md). Orquestación de escenarios pendiente en D4.3; efecto sobre pedidos propios todavía no identificado.

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

## Catálogo fotográfico y adaptación por plataforma

Revisión solicitada por el usuario tras D4.1: nueve fotografías sintéticas originales, generadas con **Imagegen integrada durante el desarrollo**, para hogar, moda y belleza × producto en contexto, material de cerca y escena cotidiana. Se incluyen localmente en `frontend/public/assets/creatividad/fotografia-v2`, con versión `fotografia-2.0.0`. No son fotografías de personas ni productos reales. Los prompts exactos se conservan en [creatividad_prompts.json](creatividad_prompts.json); procedencia/licencia en [licencias.md](licencias.md).

`scripts/preparar_imagenes.mjs` transcodifica los originales a WebP sin cambiar su contenido, utilizando Sharp ya fijado en el lockfile de Next. Nueve archivos, 1.047.498 bytes en total, máximo 169.146 bytes; 1086×1448 cada uno. El manifiesto `backend/app/creatividad/imagenes.json` guarda dimensiones, bytes y SHA-256. Se rechaza sobrescribir un recurso versionado con bytes diferentes. Las rutas absolutas de los PNG originales permanecen solo en el artefacto local ignorado `artifacts/qa/imagenes-generadas.json`, no en Git.

La API construye 36 propuestas posibles (tres perfiles × tres escenas × cuatro placements) con una única fuente de textos, recursos, CTA, origen y formato. La vista aplica una composición HTML/CSS versionada, `composicion-2.0.0`; no necesita canvas, vídeo ni fuentes remotas. Los lienzos elegidos para esta demo son:

| Plataforma | Formato de la vista | Tratamiento |
|---|---|---|
| Meta | Feed 4:5 | Fotografía editorial, marca y mensaje sobre pie claro |
| TikTok | In-feed 9:16 | Gancho breve sobre la escena, encuadre vertical y espacio para interfaz |
| Display | Banner adaptable 1200:628, aproximadamente 1,91:1 | Producto a la derecha, mensaje y CTA separados |
| YouTube | Apertura in-stream 16:9 | Marca y titular en panel lateral, escena panorámica |

Referencias primarias consultadas: [Meta, imagen de feed](https://en-gb.facebook.com/business/ads-guide/update/image/facebook-feed/outcome-awareness), [TikTok, in-feed y zonas seguras](https://ads.tiktok.com/resources/help/article/tiktok-auction-in-feed-ads?lang=en-GB), [Google, display adaptable](https://support.google.com/google-ads/answer/7005917?hl=es) y [YouTube, formatos de vídeo](https://support.google.com/google-ads/answer/13547298?hl=es). Son maquetas de composición; las dimensiones del lienzo son referencias de presentación, no una exportación publicitaria validada. TikTok y YouTube muestran fotogramas estáticos, sin afirmar que exista vídeo reproducible.

La biblioteca conserva `asset` y los hechos históricos; añade `vista_previa` como **recreación visual** adaptada al canal del registro. Se identifica tanto en las tarjetas como en el detalle, que permite consultar el SVG histórico. No se atribuye a las fotografías nuevas el CTR/CVR del registro ni se cambia el grano de entrenamiento.

## Preparación de ejemplo y brief

El formulario recoge canal, perfil, audiencia, frecuencia, impresiones y objetivo. «Generar propuestas de ejemplo» prepara tres escenas del catálogo elegido: carga/decodifica las imágenes reales en el navegador y solicita la evaluación al backend, con estados anunciados y error recuperable. Se identifica discretamente como simulación con recursos precreados; no se fingen llamadas IA, porcentajes ni tiempos de generación. Los controles se bloquean solo mientras esa preparación está en curso. Cambiar plataforma o perfil retira las propuestas anteriores hasta preparar el contexto nuevo.

Python calcula CTR contextual, bandas y esperanza de clics (`impresiones × CTR`), y compone el brief por reglas con el placement. Las tres propuestas comparten **la misma referencia**: no hay efecto diferencial visual identificado ni ganador predictivo. El formato adaptado tampoco tiene observaciones propias, y el CTR contextual no estima su efecto. La banda de esperanza no es un intervalo de conteos futuros.

Guardar una propuesta crea una selección inmutable, consultable al recargar y en el historial. Es una hipótesis que enlaza al diseño A/B; no activa medios ni modifica ventas. `multiplicador_demanda=1`, `efecto_identificado=false`. No se incorpora todavía a un escenario.

## Aprendizaje experimental posterior

D4.2 añade una prueba A/B real dentro del mundo sintético: protocolo congelado, dos o tres brazos, asignación aleatoria, observaciones nuevas, denominadores, costes, intervalos y aceptación con guardrails. No identifica un efecto real de las fotografías fuera de esta demo. El pretest muestra el CTR experimental actualizado en una sección separada solo cuando coinciden contexto y recursos exactos; no reescribe el resultado histórico ni cambia el predictor `creatividad-1.0.0`.

El aprendizaje conserva conteos y versiones, acepta evidencia nula/adversa compatible y sustituye sin acumular ramas dependientes. El multiplicador económico permanece en 1 incluso después de aceptar: un cambio de CTR/CVR no identifica pedidos propios ni contribución. Método, inferencia, API y límites en [experimentos_ab.md](experimentos_ab.md). La integración de escenarios sigue en D4.3.

## Persistencia y API

- `modelo` conserva parámetros, 200 réplicas, esquema, soporte, particiones, métricas, checksum, versión y semilla. El arranque lo prepara bajo advisory lock compartido con reset; GET no entrena.
- Migración aditiva 0004: `pretest_creativo` y `seleccion_creativa`, con FK e índice único de selección por evaluación/variante.
- La evaluación guarda inputs y resultado por contenido. Repetir contenido devuelve el mismo ID y declara reutilización. La selección valida pertenencia a la evaluación.
- Se conservan los nueve SVG `variantes-1.0.0` y sus rutas para las evaluaciones antiguas. El renderer mantiene esa presentación cuando faltan metadatos de placement; no se migra ni se modifica el JSON guardado.
- Las evaluaciones nuevas guardan `fotografia-2.0.0`, `composicion-2.0.0`, texto y placement, con IDs distintos por canal. Tras publicar, un rediseño deberá crear ruta, versión y renderer nuevos conservando los anteriores. Los resultados y selecciones antiguos siguen consultables.
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
