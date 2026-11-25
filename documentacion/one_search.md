# One Search y primer radar de marca

## Evidencia y una sola realidad de negocio

El módulo estima **cambio de pedidos propios por euro ahorrado**, alternativa prevista en MODELOS_MATEMATICOS.md cuando no se identifica recuperación. No deduce sustitución de una correlación SEO/SEM ni utiliza el coeficiente del MMM para SEM marca.

El mecanismo de captura del generador se extrae a `app/datos/captura.py`, manteniendo exactamente el universo original y su checksum `6715…0c9d`. La construcción de históricos usa la misma estructura latente y respuesta de captura. Los estimadores no importan datos/generador ni leen verdad de evaluación.

Se generan una sola vez 12 fixtures históricas identificadas, con 24 mercados, 288 asignaciones y 576 observaciones pre/post. Son ramas experimentales sintéticas sobre el negocio observado: no reescriben los hechos ni se suman a ventas o inversión. Cada periodo tiene 28 días; 12 bloques de 56 días no solapados, terminados antes del corte. Intensidades 0, 25, 50 y 75 %, repetidas tres veces. El recorte cero proporciona placebo.

Los pares se congelan por volumen del primer preperiodo, dentro de los tres estratos. En cada experimento se aleatoriza dentro del par, con probabilidad 0,5 y SeedSequence `[semilla_raíz, 3100, índice]`. Se guarda esa secuencia explícita. El mundo genera pedidos post con Poisson sobre la rama del negocio y, en tratamiento, aplica el ratio de captura con inversión reducida. Utiliza gasto diario medio del periodo: aproximación agregada, no microsimulación diaria. No entrega pedidos contrafactuales al estimador.

## Estimación e incertidumbre

Para cada par: `delta = post_tratamiento - pre_tratamiento * post_control / pre_control`. La tasa por intensidad es suma de deltas / suma de ahorro del brazo tratado. La escala de tamaños se fija con preperiodo; la unidad inferencial es el par, no cada día. Los mismos pares se repiten en los históricos, por lo que el bootstrap remuestrea los 12 pares completos con todas sus intensidades y periodos. Conserva correlación entre intensidades; 400 réplicas CPU, semilla derivada `[raíz, 3101]`. Referencia general de remuestreo: [SciPy bootstrap](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html).

Los percentiles p05/p50/p95 son bandas empíricas condicionadas al diseño y transporte del efecto; pocos conglomerados, sin garantía nominal. No incluyen incertidumbre completa de margen, demanda futura, spillover ni estabilidad temporal. La proporción de réplicas con delta económico negativo es el indicador de riesgo mostrado, no una garantía comercial.

Hay cuatro pares por estrato: se informa muestra insuficiente y se utiliza pooling nacional. Aplicar el efecto a un mercado individual es una hipótesis de transferencia y no habilita recomendación. El placebo promedia por par los recortes cero y utiliza IC t al 95 %; si excluye cero bloquea el modelo. Faltantes, duplicados, preperiodo nulo y ausencia de contraste impiden ajustar.

Entre 25 y 75 % se interpola linealmente la tasa por euro. Fuera de ese soporte se usa el extremo más cercano exclusivamente como hipótesis extrapolada; no se recomienda actuar. Cero es la opción exacta de mantener. Solo se evalúa como contraste comparable el ámbito nacional y horizonte de 28 días. Otros periodos siguen calculándose bajo hipótesis de estabilidad, expresada y sin recomendación.

## Economía, equilibrio y radar

La base se carga desde los mismos agregados de KPIs. Ahorro = inversión SEM marca × recorte. Cambio de pedidos = tasa estimada × ahorro; cambio de margen = cambio de pedidos × margen observado por pedido. Se recalcula inversión total y contribución de la alternativa mediante `contribucion` del dominio común. La cuota común figura en ambas opciones y se cancela; cuota incremental y coste experimental se imputan una sola vez.

El umbral de equilibrio se expresa como **máxima pérdida de pedidos asumible**: `(ahorro - costes_incrementales) / margen_por_pedido`. Puede ser negativo si hace falta ganar pedidos para pagar costes. No se muestra una tasa de recuperación inexistente. Base y alternativa utilizan mismo periodo y draws compartidos de parámetros. El waterfall deriva del backend y reconcilia ahorro + cambio de margen − costes = delta.

Primer radar: una hipótesis de marca completa con ID persistente en el modelo, los 32 grupos elegibles reales, impacto central, banda, riesgo y coste. Los grupos se solapan y no se suman como oportunidades independientes. La prioridad actual tiene una sola candidata; el criterio se explica. Si delta ≤0, riesgo >10 %, placebo o datos bloqueados, ámbito/horizonte no comparables o recorte extrapolado, recomienda mantener/no actuar. Un resultado favorable invita a contrastar en un nuevo experimento; no aprueba ni activa medios. El radar y el simulador llaman a la misma valoración Python.

## Persistencia y API

Migración 0003: `experimento`, `asignacion_experimento`, `observacion_experimento` y `simulacion_search`, con claves y FK por grano. Evidencia y modelo Search se preparan al arrancar, bajo advisory lock, sin regenerar al navegar. No se sobrescriben observaciones al completar los metadatos de semilla del prototipo.

- `GET /api/v1/busqueda/evidencia`: versión, soporte, diagnóstico, históricos y serie descriptiva de clics.
- `GET /api/v1/busqueda/historicos/{id}`: protocolo, asignaciones y observaciones guardadas.
- `POST /api/v1/busqueda/simular`: parámetros validados y evaluación persistida con snapshot, modelo, inputs, semilla y resultados.
- `GET /api/v1/busqueda/simulaciones/{id}`: resultado guardado, sin recalcular.
- `GET /api/v1/oportunidades`: radar calculado con el contexto, sin crear ejecuciones.

La misma evaluación produce el mismo ID; si ya existe se indica reutilización, sin presentarla como ejecución nueva. Reset explícito elimina evaluaciones de usuario y reconstruye evidencias/modelos reproducibles dentro de la transacción.

## Evidencia nueva del laboratorio geográfico

El laboratorio permite diseñar, ejecutar, evaluar y aceptar pruebas nuevas. Una evaluación compatible sustituye la evidencia mediante `search-geo-1.0.0`, conservando versiones y evaluaciones previas. El soporte pasa a ser únicamente la intensidad ejecutada; no se conserva artificialmente la recomendación entre 25 y 75 % de los históricos sustituidos. Las bandas usan draws t del efecto por pares y se identifican en la API. El origen vigente se muestra en One Search y el radar utiliza esa misma versión. La recuperación SEO/directo sigue sin identificarse. Método, supuestos, guardrails, valor de información y límites: [experimentos_geo.md](experimentos_geo.md).
