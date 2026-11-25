# Experimentación geográfica y valor de información

## Diseño congelado

El laboratorio trabaja sobre el mismo snapshot de AUREL. KPI primario: pedidos propios. No usa atribución como demanda ni cambia el negocio observado. Cada nueva prueba guarda hipótesis, objetivo, mercados, recorte, preperiodo, duración, costes, límite de pérdida, semilla, modelo previo y eventos de estado con hora real. El calendario experimental es simulado y se muestra aparte.

Se admiten 8–24 mercados distintos, en número par, preperiodos de 28/56/84 días y post de 14/28/42/56 días. El preperiodo termina en el corte; el post empieza al día siguiente. Un diseño no contiene observaciones futuras. Se normalizan tres variables pre: logaritmo del volumen, crecimiento entre mitades y variabilidad diaria relativa. Emparejamiento voraz determinista por distancia euclídea estandarizada, con desempate por ID; no se afirma optimalidad global. RNG `SeedSequence([semilla, 3201])`, un control y un tratamiento por par, probabilidad 0,5.

Placebo pre: diferencia entre segundas mitades, normalizada por ratio de primeras mitades. El MDE aproxima la dispersión de esas diferencias, con suelo de ruido Poisson y escala raíz de duración. Se informa alfa 5 % y potencia objetivo 80 %; no se promete potencia real. Se advierte potencia insuficiente si el efecto absoluto de referencia de la evidencia previa queda por debajo del MDE. El MDE y las parejas se calculan antes de generar el post.

## Mundo y estimador separados

`app/experimentos/servicio.py` coordina el ciclo; `app/datos/mundo_geo.py` conoce el mecanismo de captura compartido con el generador. Los estimadores de `app/modelos` no importan `app/datos`, protegido por la prueba AST existente.

Al ejecutar, el mundo repite el perfil diario de los últimos 28 días, con ruido lognormal común (escala 0,015), por mercado (0,01) y Poisson de pedidos. El gasto tratado se reduce diariamente, en céntimos; los controles mantienen inversión. El ratio de captura usa el mismo mecanismo, estructura de mercados y escala monetaria del universo original. Streams `[semilla, 3202]` y `[semilla, 3203, índice_mercado]`. Es una **rama sintética condicionada**, no una predicción comercial, ni observación del futuro real.

Se guardan pre/post por mercado, pedidos y gasto/presupuesto; no se entrega verdad latente al estimador ni se suman estos hechos a KPIs. El estimador solo recibe asignaciones y observaciones guardadas. Para cada par:

`d_i = post_T − (pre_T / pre_C) × post_C`.

El contrafactual es estimado, no el contrafactual verdadero del mundo. Efecto total tratado `D = Σ d_i`; error `SE(D) = √n × sd(d_i)`. IC 95 % `D ± t(0,975; n−1) × SE(D)`. Tasa por euro `τ = Σ d_i / Σ ahorro_i`; error linealizado por pares usando residuos `d_i − τ × ahorro_i`. Los días no cuentan como réplicas. La tabla muestra pre equivalente al horizonte post, ambos brazos, contrafactual, diferencia y ahorro.

Supuestos: pares independientes, tendencias comparables, ausencia de spillover y estabilidad temporal. IC aproximado con pocos conglomerados. [NIST: comparaciones pareadas](https://www.itl.nist.gov/div898/handbook/prc/section3/prc311.htm), [intervalos pareados](https://www.itl.nist.gov/div898/handbook/prc/section3/prc312.htm).

## Evaluación, guardrails y actualización

Transiciones: diseñado → simulado → evaluado → aceptado. POST repetido reutiliza el estado guardado; no vuelve a generar observaciones. Los históricos de arranque son inmutables. Diseño repetido con mismos parámetros, snapshot y modelo devuelve el mismo ID. El protocolo no se edita tras diseñar; se puede crear otro diseño.

La evaluación permite actualizar únicamente con:

- Los 24 mercados, al menos ocho pares y horizonte post de 28 días.
- Intervención no nula y ahorro positivo.
- IC del placebo que contiene cero y máxima diferencia de crecimiento entre parejas ≤15 puntos porcentuales.
- Límite inferior del IC que no supera la pérdida de pedidos preespecificada (5 % por defecto).
- Semiancho del IC ≤5 % del contrafactual tratado e integridad del snapshot sin bloqueo.

Un resultado negativo puede actualizar si es informativo y supera guardrails; no exige significación ni efecto favorable. Un nulo experimental con recorte cero no identifica tasa por euro y no actualiza. Cobertura parcial, horizonte incompatible, mala identificación o pérdida excesiva producen abstención y conservan evidencia.

Aceptar requiere que el modelo vigente siga siendo el usado al diseñar. Crea `search-geo-1.0.0` con 400 draws t de la tasa linealizada, seed `[semilla, 3204]`, referencia al experimento y modelo anterior. **Sustituye**, sin pooling, porque las ramas sobre los mismos mercados/calendario no son pruebas independientes. Conserva modelo y evaluaciones anteriores. El soporte nuevo es exclusivamente la intensidad ejecutada; fuera de ella se muestra hipótesis sin recomendación. Evidencia idéntica a la vigente reutiliza esa versión; una copia de evidencia antigua no sobrescribe la vigente ni estrecha bandas.

La cadena de sustitución determina el modelo actual, no el reloj ni el orden de inserción. Fiabilidad comprueba cobertura de la evidencia vigente; faltantes bloquean evaluaciones económicas afectadas. No se desbloquea el MMM ni se aprueban decisiones de medios.

## EVPI, EVSI y costes

Alternativas disponibles: mantener y recortar. Reinversión requiere el orquestador del Día 4. Desde `geo-1.0.1`, el prior conserva las 400 réplicas Search en la intensidad de la prueba, equiponderadas, incluidas sus colas. La primera revisión usaba 40 cuantiles y podía omitir una cola adversa pequeña; se corrige sin recalcular protocolos previos guardados. El prior empírico sigue siendo aproximado y no equivale a posterior causal calibrado.

Todas las utilidades, también las del brazo tratado durante la prueba, llaman a `comparar_captura` y al dominio económico común. Sin información: máximo de utilidad esperada. EVPI: esperanza del máximo con información perfecta menos el máximo anterior. EVSI: máximo posterior esperado ante una muestra, menos valor sin información.

Likelihood: `y | τ ~ Normal(τ, SE_tasa_diseño)`, con error previsto a partir del MDE. Bayes discreto y cuadratura Gauss-Hermite de 41 nodos con `scipy.special.roots_hermitenorm`, pesos normalizados por `√(2π)`. Ruido cero distingue únicamente estados con señales diferentes. Resultado acotado a `[0, EVPI]` por redondeo numérico, con tamaño de la corrección comunicado; desvío >0,01 € invalida recomendación. Esa corrección no estima el error total de integración ni garantiza convergencia. [Documentación primaria de SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.roots_hermitenorm.html).

Horizonte: días de prueba + 28 días de decisión posterior, bajo estabilidad condicional. Comparador: mejor acción actual en ambos periodos. Coste de oportunidad = máximo de cero y beneficio esperado de esa acción durante la prueba menos beneficio esperado del brazo tratado. Incluye esperar y pérdida/ganancia durante el test. Valor neto = EVSI − coste explícito de prueba − coste de oportunidad. La pérdida esperada durante el test se muestra como riesgo y **no se resta otra vez**. La cuota incremental se imputa en el periodo de decisión; no se anualizan beneficios.

Ámbito parcial, horizonte distinto de 28 días, intensidad no observada exactamente o prior bloqueado generan valoración exploratoria sin recomendación. EVSI depende del likelihood aproximado; EVPI se etiqueta como cota. La fixture +80.000/−60.000 € verifica EV actual 10.000 €, EVPI 30.000 €, límites y efecto del ruido/coste. No se ajustan datos para que experimentar compense: el diseño por defecto puede recomendar no gastar en la prueba.

## Persistencia y API

Se reutilizan las tablas de migración 0003 y el JSON de protocolo, sin modificación del DDL ni regeneración del universo. Advisory lock serializa mutaciones con el reset. Las transiciones tienen evento con hora real; fechas de calendario simulado, snapshot y semilla son independientes de esa hora.

- `GET /api/v1/experimentos`: catálogo de pruebas, mercados y parámetros por defecto.
- `POST /api/v1/experimentos/disenar`: protocolo, parejas, MDE y valor de información guardados.
- `GET /api/v1/experimentos/{id}`: protocolo, estado, asignaciones, observaciones y evaluación.
- `POST /api/v1/experimentos/{id}/ejecutar`, `/evaluar`, `/aceptar`: transiciones validadas.

Reinicio conserva la prueba, evaluación y versión vigente sin ejecutar de nuevo. Reset explícito elimina ramas/actualizaciones de usuario y restaura los 12 históricos y modelo Search original; no cambia el checksum del negocio. Las pruebas de API nuevas revierten su transacción; Playwright y pruebas operativas de aceptación/reset se ejecutan en una pila de QA aislada.
