# MMM nacional de pedidos · mmm-1.0.1

Este documento describe el estimador implementado, sin modificar los contratos de producto. Es un ajuste observacional sobre datos sintéticos, no evidencia comercial ni identificación causal de cada canal.

## Datos, ámbito y particiones

- Negocio y medios se agregan por separado desde PostgreSQL; nunca se multiplican pedidos al unir granos diferentes. Se verifica la cobertura diaria de todos los mercados y canales antes de ajustar.
- 104 bloques consecutivos de siete días, desde 03/11/2024 hasta 31/10/2026. Los dos primeros días del universo de 730 días no forman una semana y quedan fuera del ajuste.
- Objetivo: pedidos propios nacionales por semana. Entrenamiento: 84 semanas, hasta 13/06/2026. Holdout: 20 semanas, 14/06/2026–31/10/2026.
- Validación rolling: entrenar hasta 27/12/2025 y validar 12 semanas hasta 21/03/2026; entrenar hasta 21/03/2026 y validar 12 semanas hasta 13/06/2026. Ninguna ventana utiliza el holdout para seleccionar parámetros.
- Los filtros de 28/56/90/365 días muestran únicamente semanas completas contenidas: 4/8/12/52 semanas. Las métricas de diagnóstico conservan su partición original. La tabla de atribución mantiene todos los días solicitados; no se deben comparar totales de coberturas distintas como si fueran idénticos.
- La evaluación es condicional a la inversión y promoción observadas de cada semana del holdout. No es un pronóstico ex ante con inversión o calendario comercial desconocidos.
- Mercado individual: respuesta `aplicable=false`, con motivo y sin series, curvas ni asignación nacional. La atribución sí se filtra. No se prorratea ni se reentrena un modelo no identificable.

## Ajuste y diagnóstico

Siete canales de generación de demanda; SEM marca se excluye como término predictor de demanda y sigue presente en gasto y atribución. Adstock `a[t] = x[t] + lambda * a[t-1]`, stock inicial cero y gasto dividido por su media de entrenamiento. Hill `a/(a+k)`, pendiente 1 fija. Se utilizan intercepto, tendencia, dos armónicos anuales y promoción agregada. No se utilizan demanda proxy, atribuciones, verdad latente ni futuras observaciones experimentales.

Grid de 12 configuraciones: persistencia semanal `{0; 0,3; 0,6}`, semisaturación normalizada `{0,5; 1,5}` y penalización `{0,01; 1}`. Se minimiza el WAPE medio de las dos ventanas rolling. Cada ventana aprende sus propias escalas. Ajuste final sobre 84 semanas con escalas de esas 84 semanas; el modelo no se reajusta sobre el holdout después de evaluar.

Mínimos cuadrados acotados de SciPy (`lsq_linear`, BVLS) sobre matriz aumentada de regularización: intercepto sin penalizar, controles con peso 0,05 y medios con peso 1. Intercepto y efectos de medios no negativos; controles estacionales y tendencia libres. La normalización del objetivo usa su media de entrenamiento. Se verifica convergencia. Referencias consultadas: [SciPy: mínimos cuadrados con cotas](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.lsq_linear.html) y [validación temporal de Forecasting: Principles and Practice](https://otexts.com/fpp3/toolbox.html#time-series-cross-validation).

El baseline de comparación es naive estacional de 52 semanas. Se guardan MAE, WAPE y sesgo, autocorrelación residual de retardo 1, correlación máxima entre medios, condición de matriz estandarizada, variación de gasto, cobertura empírica de banda y sensibilidad del reparto. Las configuraciones a un 10 % del mejor WAPE rolling se reajustan en train para comparar masa asignada por canal. Sensibilidad = máximo rango de esa masa dividido por su media, con suelo del 1 % de pedidos totales de entrenamiento para evitar divisiones por términos casi cero.

Reglas demo configurables en `Configuracion`: bloquear si no mejora naive; correlación ≥0,98; condición >100.000/no finita; variación mínima <0,02; sensibilidad >1; baseline/predicción no positivos. Si no falla ninguna regla, el estado sigue siendo limitado por su naturaleza observacional. `optimizable=false` hasta que exista calibración y orquestador; no hay aprobación de decisiones implementada todavía.

## Bandas y límites estadísticos

80 refits CPU con bootstrap circular de residuos centrados de entrenamiento, bloques de cuatro semanas y semilla derivada de la semilla del snapshot. Se conserva el vector completo de coeficientes de cada réplica, manteniendo su covariación. La forma y la penalización elegidas permanecen fijas; no se vuelven a seleccionar en cada réplica.

Refitear sobre una señal ya regularizada produce otra contracción. Desde mmm-1.0.1 los errores de refit se centran alrededor del vector ajustado y los coeficientes de medios negativos se truncan a cero. Esto define una distribución empírica de escenarios condicionales; **no es un IC calibrado**. La truncación introduce asimetría cerca de cero. No se incluye incertidumbre de selección, endogeneidad, interacciones no modeladas ni cambios estructurales. No se debe interpretar la estrechez de una banda condicional como certeza del reparto.

La banda predictiva p05–p95 añade residuos de train a los draws conjuntos de parámetros. La cobertura de holdout se mide y se muestra; no se garantiza nominalmente. Las bandas de curvas y de asignación por canal solo utilizan coeficientes, sin ruido de proceso. La versión mmm-1.0.0 del prototipo permanece en PostgreSQL si se entrenó en ese volumen; no se sobrescribe. Un reset explícito elimina el estado demo y reconstruye la versión vigente.

## Reconciliación y lectura económica

Cada semana conserva `baseline + suma(componentes) = predicho` y `predicho + residual = observado`, con tolerancia de coma flotante. El residual no se distribuye artificialmente entre canales. La tabla accesible conserva los valores que utiliza el gráfico.

Las curvas son una respuesta de siete días con el stock anterior a la última semana fijo. Soporte sombreado: mínimo/máximo de inversión semanal en train. Trazo discontinuo: extrapolación hipotética. Se devuelve la derivada analítica en pedidos modelados por euro adicional. No se interpreta como iROAS, beneficio ni efecto causal.

La valoración descriptiva del término usa el margen observado por pedido de cada semana. `saldo_modelado = margen_asignado - inversión_del_canal`, mediante el dominio económico compartido. Bandas con margen por pedido fijo, sin incertidumbre de margen. No son contribuciones incrementales identificadas; no se suman al KPI observado ni autorizan recortes. SEM marca se evalúa por separado en el futuro estimador One Search.

## Persistencia y uso

El arranque ejecuta migración 0002 y prepara una sola vez el artefacto de la versión vigente bajo advisory lock. Guarda snapshot, checksum de observaciones, checksum del snapshot, versión/configuración, semilla, coeficientes/replicas, particiones, diagnósticos, series y curvas. ID derivado de contenido y snapshot; consultas sin reentrenamiento. Reiniciar conserva la fecha de creación. Reset genera primero y reconstruye observaciones y modelo en una misma transacción; un fallo no deja un universo a medias.

Endpoints: `GET /api/v1/modelos`, `GET /api/v1/modelos/mmm?dias=28`, `GET /api/v1/modelos/{id}/curvas?canal=meta`. El endpoint de curvas requiere el ID vigente del snapshot activo; no acepta SEM marca. Los artefactos anteriores se conservan para trazabilidad en la base, aunque la API de este incremento solo expone la versión vigente.

Resultados realmente ejecutados y advertencias: [validacion.md](validacion.md). Próximo trabajo: evidencia Search y primer radar económico; la calidad predictiva conjunta no sustituye esa evidencia.
