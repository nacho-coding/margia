# MARGIA · Especificación de producto v1.0

## 1. Visión y propuesta comercial
MARGIA (Marketing Decision Intelligence), lema «Cada decisión tiene un valor», es una capa de inteligencia de decisiones de marketing inspirada en la integración semántica y los workflows de plataformas de decisión empresariales. No es una copia de Palantir ni otro dashboard. Conecta tres disciplinas: medición de medios (MMM, atribución descriptiva, incrementalidad), One Search (SEO y SEM) y creatividad basada en datos, en un mismo gemelo comercial temporal. Añade radar económico, simulación, valor de la información y fiabilidad. No se presenta como producto oficial de una consultora ni como caso real.

Objetivo: demostrar que se puede detectar una oportunidad, evaluar su impacto económico e incertidumbre, decidir si conviene experimentar, ejecutar el experimento sintético, aprender, optimizar la asignación y registrar la decisión. La métrica principal es contribución incremental neta, no ROAS atribuido. La POC debe parecer producto final sin pretender estar lista para producción. El coste de la solución y de experimentar forman parte de las decisiones.

## 2. Alcance y usuarios
Una sola empresa ficticia de retail omnicanal, nombre provisional AUREL Retail (marca inventada para la demo; no usar marcas reales). 24 mercados sintéticos de España, ecommerce y tiendas, categorías moda/hogar/belleza. Usuarios de vista: dirección de marketing, analista de medición, responsable de búsqueda, responsable creativo. No son roles de seguridad reales. Sin onboarding, multitenancy, IoT, edge, logística, inventario, personal, energía, 3D, conectores reales, activación de medios, chatbot ni LLM local. Sin datos personales. Solo contexto comercial agregado. P0 es obligatorio para recorrido; P1 mejora si sobra tiempo; P2 futuro.

## 3. Ontología y ciclo de decisión
Marca → mercado → canal → campaña → grupo de búsqueda/creatividad → observación temporal. Una campaña tiene presupuesto, fechas, objetivo, canal, categoría y creatividades compatibles. Mercado y día son ejes comunes; consulta y creativo son granularidades distintas, no se cruzan sin evidencia. Venta propia única es la verdad económica; métricas atribuidas son observaciones de plataforma separadas. Experimento → asignación → observaciones → estimación → versión de modelo → decisión. Escenario → snapshot inmutable → cambios → ejecución → métricas/bandas → recomendación → aprobación/rechazo → decisión registrada → evaluación. No se crean subgemelos.

Estados de decisión: oportunidad, hipótesis, en evaluación, experimento diseñado, experimento simulado, evaluado, aprobado/rechazado, archivado. Transiciones válidas en API, registro temporal y motivo. Aprobar solo registra decisión simulada; nunca activa publicidad. Un experimento crea evidencia sintética nueva, actualiza versión de estimación y no reescribe resultados previos.

## 4. Pantallas y requisitos funcionales

### P0 Centro de decisiones y radar (/)
Cabecera con empresa, periodo, estado del dato, etiqueta demo y botón de reset con confirmación en ajustes. KPIs reconciliados: inversión, ventas netas, pedidos únicos, margen bruto, contribución tras marketing, oportunidad prioritaria. Comparativa con periodo anterior equivalente. Serie demanda/ventas/inversión con unidades separadas. Radar de oportunidades calculado desde datos y modelos: reducir marca, reasignar medios, probar creatividad; prioridad por impacto esperado, riesgo, coste y suficiencia de evidencia. No sumar oportunidades solapadas. Cada tarjeta abre una hipótesis preconfigurada con identificadores reales. Historial de decisiones recientes.

### P0 Medición (/medicion)
Tabla por canal con gasto, impresiones/clics cuando correspondan, conversiones atribuidas, ROAS atribuido, contribución incremental estimada y marginal, intervalo/limitaciones. Gráfico de descomposición de baseline + efectos modelados + residual; total reconciliado con predicción, no forzar que coincida con observado. Curvas de respuesta y saturación con rango observado, comparación temporal, diagnóstico holdout y sensibilidad. Selector canal, periodo y mercado cuando la granularidad lo permite; no recalcular un modelo no identificable por filtro. Mostrar MMM simplificado y atribución descriptiva, no MTA causal ni atribución individual. Abrir escenario desde canal.

### P0 One Search (/one-search)
Grupos de consultas: marca pura, marca + producto, genéricas, competencia/contexto; dispositivo opcional. Tabla de clics SEO/SEM, impresiones, posición orgánica, CPC, gasto, conversiones atribuidas y riesgo de sustitución. Gráfico SEO/SEM histórico y comparación por mercado. Simulador de recorte de marca por grupo elegible (0–100%, limitado al soporte observado para recomendaciones), tasa de recuperación estimada con intervalo, conversiones propias esperadas, ahorro, pérdida de margen, punto de equilibrio, coste incremental y contribución neta. Mostrar cuándo no actuar. Diseñar experimento desde la misma hipótesis. No asumir SEO absorbe todo ni cruzar consultas Search Console con ventas individuales.

### P0 Laboratorio de experimentos (/experimentos)
Lista histórica y nuevo experimento. Formularios objetivo, hipótesis, KPI primario (pedidos o contribución), mercados, tratamiento, periodo, límites de riesgo, coste. Emparejar mercados según preperiodo, asignar aleatoriamente dentro de pares con semilla, mostrar equilibrio, calendario y MDE aproximado; advertir spillover y potencia insuficiente. Ejecutar en universo sintético, guardar asignaciones y observaciones, comparar control/tratamiento y contrafactual, estimar efecto y bandas, mostrar limitaciones y guardrails. Aceptar resultado, actualizar modelo One Search solo si compatible y evidencia suficiente; si no, abstenerse. Fechas simuladas no confundir con tiempo del sistema. Botón para preparar prueba A/B creativa con la misma estructura.

### P0 Inteligencia creativa (/creatividad)
Biblioteca visual de al menos 12 activos originales utilizables, con metadatos y miniaturas locales; 80 registros objetivo, reutilizar composiciones de forma explícita si hace falta. Filtros canal, formato, objetivo, categoría, audiencia, periodo. Detalle con imagen, atributos etiquetados (mensaje, CTA, composición, tono, promoción), impresiones, CTR, CVR, coste y contexto. Diferenciar métricas observadas sintéticas de estimaciones. Precampaña: seleccionar brief y comparar tres variantes con modelo ligero de respuesta entrenado en histórico, incertidumbre y reglas de marca; generar brief/recomendaciones mediante plantillas deterministas basadas en datos, no afirmar generación IA en runtime. Los activos nuevos pueden estar precreados durante desarrollo, su puntuación se calcula realmente. Postcampaña: comparar resultados, controlar confusores mediante segmentación o prueba aleatoria, registrar hipótesis aprendida y actualizar versión si hay datos. Enviar variante elegida al escenario de reinversión. P1 editor simple de brief y exportación, análisis de fatiga por frecuencia. No hacer promesas causales a partir de correlación visual.

### P0 Laboratorio de escenarios (/escenarios)
Crear, editar borrador, duplicar, ejecutar, comparar, guardar y archivar. Baseline inmutable, horizonte de 28 días por defecto, alternativas A ahorro y B reinversión, controles de presupuesto por canal, recorte SEM de marca, variante creativa, coste de experimento y cuota de plataforma configurable. Validación de rangos, restricción de inversión y no doble conteo. Optimizar contribución esperada con límites y riesgo; opción conservar ahorro. Resultados: inversión, ventas, pedidos, margen, costes, contribución neta, diferencia frente a base, incertidumbre, probabilidad de pérdida y waterfall reconciliado. Mostrar inputs, semilla, versiones y fecha de corte. Exportar CSV y Markdown. Botón aprobar/rechazar con motivo; persistir y navegar a decisión.

### P0 Fiabilidad (/fiabilidad)
Inventario de fuentes sintéticas, fecha de corte, cobertura, duplicados, frescura, coherencia, cambios de tracking, drift y diagnóstico de modelos. Estados por fuente y modelo (válido, limitado, bloqueado). Botón «Simular incidencia de medición» crea snapshot alternativo con faltantes o ruptura de tracking; no altera baseline original. Bloquear recomendaciones afectadas, mantener histórico y análisis no afectados, explicar requisito de recuperación. Botón restaurar snapshot sano. No utilizar semáforos decorativos.

### P0 Valor de información integrado en experimentos
Comparar actuar, no actuar y experimentar; coste explícito, valor esperado de información, riesgo y recomendación. P1 vista dedicada de cartera de experimentos ordenada por valor neto, si cabe.

### P0 Historial y contexto común
Filtros globales fecha y mercado aplicables por contrato; el usuario siempre ve snapshot y escenario activo. Historial accesible desde centro y escenarios. Vista de relaciones sencilla mediante grafo opcional P1; no es necesaria para el núcleo. Navegación cruzada mediante ID, no copiar datos a pantallas independientes. Estados carga, vacío, error, insuficiencia y éxito. Todos los controles visibles cumplen función.

## 5. Recorrido de presentación (7–10 minutos)
1. Abrir centro; explicar dinero y evidencia, no tecnología.
2. Entrar en oportunidad de marca: atribución alta no implica incrementalidad alta.
3. Probar recorte de 50%, variar supuestos y ver punto de equilibrio.
4. Diseñar experimento geográfico, calcular si merece la pena, ejecutar y evaluar el resultado sintético.
5. Actualizar estimación; comparar ahorrar frente a reinvertir en creatividad; evaluar tres propuestas.
6. Ejecutar optimización y comparar A/B con base, incluyendo costes y riesgo. Aprobar decisión simulada, guardar y exportar.
7. Introducir problema de tracking; mostrar abstención y restaurar. Cerrar con contribución económica y coste de solución.

Demo alternativa: mercado con escasa cobertura orgánica o experimento insuficiente → conservar SEM/no actuar. Nunca forzar que el producto recomiende recortar.

## 6. Criterios de producto
Una misma campaña/mercado/periodo tiene los mismos datos en todas las vistas. Modificar parámetros cambia cálculos y persistencia, no solo texto. Base/A/B comparables sobre misma foto y semilla. Resultados reproducibles y trazables. Al recargar o reiniciar Docker se conservan decisiones. Reset explícito restaura mundo reproducible. Toda hipótesis, observación sintética, estimación y resultado experimental está etiquetada. La aplicación no se considera acabada sin recorrido probado y revisión visual.
