# Pruebas A/B creativas

Implementación P0 D4.2. Todos los datos son sintéticos. La prueba aprende respuesta de clics en un contexto congelado; no activa publicidad ni identifica pedidos propios, ingresos o beneficio incremental.

## Protocolo y mundo

Desde una selección o pretest guardado se eligen un control y uno o dos tratamientos del mismo pretest. Se congelan canal, categoría, audiencia, frecuencia, recursos, hashes, versiones, textos, modelo histórico, aprendizaje previo, hipótesis, tamaño, calendario, costes y semilla. La validación del servidor impide brazos duplicados, recursos ajenos, campos adicionales y resultados suministrados por el cliente.

El diseño admite 500–200.000 impresiones por brazo y 7, 14 o 28 días. El MDE se calcula antes de ejecutar desde la referencia histórica contextual. El calendario simulado comienza al día siguiente del corte del snapshot; no depende del reloj del ordenador. Los eventos conservan por separado la hora real de la acción.

`app/datos/mundo_ab.py`, versión `mundo-ab-1.0.0`, crea una rama al pulsar **Ejecutar prueba sintética**. No hay resultados futuros en el diseño ni en una lectura. La unidad aleatorizada es una oportunidad sintética independiente con una sola impresión. Cada fecha contiene el mismo número de oportunidades y presupuesto por brazo, con restos distribuidos de forma determinista; una permutación asigna cada oportunidad a exactamente un brazo.

El mecanismo reutiliza el CTR base por categoría/promoción y el CVR del generador original mediante `respuesta_creativa.py`. Extraer esas expresiones no altera el universo ni su RNG: el checksum de los 247.562 hechos originales se conserva. Los efectos visuales latentes son modestos, fijados por recurso y semilla raíz antes de asignar, sin analizar píxeles ni prometer una propuesta ganadora. Audiencia y frecuencia delimitan el transporte del modelo, pero este mundo P0 no añade efectos latentes específicos de esas dos variables. No se interpreta como eficacia real de una fotografía.

Substreams: 4200 para efectos latentes por recurso; 4201 para asignación; 4202 para resultados, ambos por fecha; 4205 para draws del estimador. La semilla inicial de prueba es raíz + 4203. El estimador no importa el mundo ni recibe sus tasas verdaderas. Un parámetro de efectos controlados solo existe en fixtures Python, nunca en HTTP.

Por fecha se guarda la asignación completa, comprimida como bytes de índices de brazo con zlib/base64, número de unidades y SHA-256. La API devuelve su resumen; el CSV descarga cada oportunidad, brazo y probabilidad marginal de asignación. Se verifican hash, calendario, brazos, exclusividad y reconciliación de exposiciones antes de evaluar/aceptar. Las observaciones diarias agregan impresiones, clics, conversiones y coste; no se suman a ventas ni medios observados.

## Tasas, contrastes e incertidumbre

KPI primario: `CTR = clics / impresiones`. CVR secundario: `conversiones / clics`, con `null` cuando no hay clics. No se compara causalmente la conversión entre personas seleccionadas de forma diferente por haber hecho clic.

Para cada tasa se calcula el intervalo Wilson bilateral nominal 95 %. Ceros y tasas unitarias conservan límites válidos; sin denominador no se inventa una tasa. Las pruebas numéricas contrastan la implementación con [SciPy, proportion_ci](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats._result_classes.BinomTestResult.proportion_ci.html).

Cada contraste previsto es tratamiento menos control. Con tasas `pt`, `pc` e intervalos Wilson `[Lt, Ut]`, `[Lc, Uc]`, el intervalo Newcombe sin corrección de continuidad es:

```text
delta = pt - pc
inferior = delta - sqrt((pt - Lt)^2 + (Uc - pc)^2)
superior = delta + sqrt((Ut - pt)^2 + (pc - Lc)^2)
```

Se limita a [-1, 1]. Para `k` contrastes se usan Wilson con alfa `0,05/k`: Bonferroni para los dos contrastes contra control cuando hay tres brazos. Se muestra como **IC familiar nominal 95 % aproximado**, no garantía exacta de cobertura. No se contrasta tratamiento contra tratamiento ni se selecciona después una comparación favorable. Método primario: [Newcombe (1998)](https://pubmed.ncbi.nlm.nih.gov/9595617/).

El MDE usa la aproximación al nulo para brazos de igual tamaño:

```text
MDE_absoluto = (z[1-alfa/(2k)] + z[0,80]) * sqrt(2*p_ref*(1-p_ref)/n)
MDE_relativo = MDE_absoluto / p_ref
```

Es planificación aproximada, no una potencia real demostrada. Los intervalos presuponen oportunidades independientes y tasas aproximadamente estables. El calendario equilibrado reduce confusión temporal, pero el mecanismo puede variar con promociones; no se modelan usuarios repetidos, clusters reales, spillover, parada anticipada ni inferencia secuencial.

El modelo de respuesta guarda 200 draws `Beta(clics+0,5, no_clics+0,5)` por brazo, con prior Jeffreys. Su media es `(clics+0,5)/(impresiones+1)` y sus percentiles p05–p95 describen incertidumbre de parámetros condicionada a los conteos. **No son los IC frecuentistas de los contrastes, intervalos predictivos de nuevos clics ni 200 experimentos independientes.** No hay selección de semilla para favorecer el resultado.

## Validez, costes y versiones

Se comprueban cobertura de todas las fechas/brazos, conteos ordenados `0 ≤ conversiones ≤ clics ≤ impresiones`, duplicados, presupuesto y exposición congelados y equilibrio diario. Se exigen al menos 30 clics y 30 no clics en cada brazo para guardar aprendizaje. Es un guardrail conservador de esta POC, no una prueba de potencia. Con pocos datos se muestran las tasas/intervalos y se conserva el aprendizaje anterior. Un resultado nulo o adverso puede ser evidencia válida: la significación positiva no es un requisito de aceptación.

El coste total es medios por brazo × número de brazos + producción total, esta última una sola vez. El presupuesto es un input de diseño; no se aprende una subasta ni una curva CPM. No se convierte CTR/CVR en ventas únicas ni se presenta rentabilidad causal de la prueba. `multiplicador_demanda=1` y `efecto_economico_identificado=false`, incluso tras aceptar.

Estados persistentes: diseñado → simulado → evaluado → aceptado. Repetir una acción completada devuelve su resultado guardado y declara reutilización. Advisory lock común con reset serializa las mutaciones. Las asignaciones y observaciones se cotejan también contra sus huellas de evaluación antes de aceptar.

`creatividad-ab-1.0.0` guarda un artefacto por evidencia y contexto exacto, con conteos, contrastes, draws, semilla, checksum y modelo anterior. Se **sustituye** evidencia, sin pooling entre ramas que pueden compartir oportunidades/mecanismo. Una copia idéntica reutiliza la versión sin estrechar incertidumbre; un diseño anterior a una actualización no puede sobrescribirla. La cadena de modelos determina el vigente sin usar timestamps; una cadena ambigua se bloquea. Los modelos anteriores siguen consultables.

El pretest presenta el CTR experimental en una sección separada cuando coinciden snapshot, canal, audiencia, frecuencia, categoría y recursos/textos versionados. No altera el JSON guardado ni el predictor histórico `creatividad-1.0.0`; las propuestas no probadas mantienen su referencia histórica. No se transporta a otros contextos ni se declara efecto económico. Orquestación de escenarios/optimización permanece en D4.3.

## Persistencia, API e interfaz

Se reutilizan `experimento` (tipo `ab_creativo`, protocolo JSON) y `modelo`, sin migración ni dependencias nuevas. Los catálogos geo y A/B filtran su tipo. El reinicio conserva protocolo, observaciones y artefactos; reset explícito elimina pruebas/aprendizaje de usuario y reconstruye el universo inicial. La comprobación operativa se ejecuta en una pila Docker aislada.

| Método | Ruta bajo `/api/v1/creativos` | Acción |
|---|---|---|
| GET | `/pruebas` | Catálogo, valores de diseño e historial |
| POST | `/pruebas/disenar` | Congelar protocolo y calcular MDE/coste |
| GET | `/pruebas/{id}` | Consultar estado, observaciones y evaluación guardados |
| POST | `/pruebas/{id}/ejecutar` | Crear asignaciones/observaciones nuevas; cuerpo `{}` |
| POST | `/pruebas/{id}/evaluar` | Estimar desde conteos; cuerpo `{}` |
| POST | `/pruebas/{id}/aceptar` | Guardar versión si es compatible; cuerpo `{}` |
| GET | `/pruebas/{id}/asignaciones.csv` | Exportar oportunidades realmente asignadas |
| GET | `/aprendizaje/{pretest_id}` | Aprendizaje vigente del contexto exacto |
| GET | `/aprendizaje/modelos/{id}` | Consultar también versiones anteriores |

La pestaña Pruebas A/B enlaza desde la selección y desde el laboratorio. Ofrece protocolo editable antes de guardar, fotografía local del contexto, acciones por estado, denominadores, gráfico de intervalos con tabla alternativa, observaciones/CSV e historial. Python calcula todas las cifras; React solo presenta y formatea. Los filtros globales conservan la prueba en URL sin reejecutarla. Formularios nativos con límites, fieldset/legend, foco en errores/estado y bloqueo solo durante trabajo real. Resultados de QA y límites en [validacion.md](validacion.md).
