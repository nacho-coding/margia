# Datos sintéticos · Contrato v1.0

## Universo
Una empresa ficticia AUREL Retail, 24 mercados, dos años completos de histórico diario (730 días con fecha de corte fija configurable), 104 semanas de modelado, 28 días futuros por defecto. Semilla raíz 260725, subsemillas derivadas mediante SeedSequence de NumPy; no usar hash() de Python como semilla. Moneda EUR, timezone Europe/Madrid, ventas netas sin IVA, devoluciones ya descontadas. Fecha de corte de demo independiente de reloj real. Objetivo de gasto anual 4,8 M€; distribuir por canal, estacionalidad y pulsos; normalizar presupuestos antes de generar efectos. Ocho canales: SEM marca, SEM genérico, Meta, TikTok, YouTube, display, TV y CRM (coste CRM separado y explícito); SEO/directo son fuentes de captura no pagadas, no sumar como inversión. 120 campañas, 50 grupos de consulta, 80 registros creativos, 8 cohortes agregadas, 12 experimentos históricos (metas flexibles); 150–300k filas objetivo, no fabricar joins cartesianos. Perfil ligero 50–100k filas si limita CPU.

## Tablas y granularidad
IDs estables, FK, claves únicas por grano, fecha, versión y snapshot donde proceda. Dinero en céntimos o decimal; floats en cálculo, redondeo de presentación. Ausente no equivale a cero.

| Tabla | Grano / campos esenciales |
|---|---|
| mercado | id, nombre ficticio, tamaño, región, grupo comparabilidad |
| canal | id, nombre, tipo, coste variable, restricciones |
| campana | id, canal, objetivo, categoría, inicio, fin, presupuesto |
| creativo | id, campaña compatible, asset local, formato, atributos, fecha, licencia |
| grupo_busqueda | id, intención, elegibilidad recorte, grupo marca, dispositivo opcional |
| negocio_diario | fecha × mercado: pedidos únicos, ventas netas, coste mercancía, margen, visitas propias, promociones, festivo, demanda proxy |
| medios_diarios | fecha × mercado × canal: gasto, impresiones/clics si aplicable, conversiones/ingresos atribuidos por fuente, modelo atribución, ventana |
| campana_diaria | fecha × mercado × campaña: distribución reconciliada de gasto canal cuando disponible |
| busqueda_diaria | fecha × mercado × grupo × fuente SEO/SEM: impresiones, clics, posición orgánica, gasto SEM, atribución SEM cuando disponible, competencia proxy |
| creatividad_diaria | fecha × mercado × activo × campaña: exposición, clics, conversiones atribuidas, gasto asignado, audiencia agregada, frecuencia |
| experimento | id, hipótesis, tipo, KPI, fecha, coste, protocolo, snapshot, semilla, estado |
| asignacion | experimento × unidad aleatorizada: brazo, par, probabilidad |
| observacion_experimento | experimento × unidad × periodo: KPI propio, exposición, coste, guardrails |
| estimacion | modelo/experimento, target, unidad, periodo, valor, intervalo, supuestos, evidencia, versión |
| snapshot | id, fecha corte, versión generador, semilla, checksums, estado |
| escenario | id, snapshot, parámetros, revisión, estado |
| ejecucion | id, escenario/revisión, versiones modelos, semilla, resultados, bandas, advertencias |
| decision | id, ejecución, estado, motivo, timestamp, evidencia |
| incidencia | snapshot, fuente, regla, severidad, alcance, acción |
| modelo | id, versión, features, train/holdout, diagnóstico, parámetros, estado |

Los agregados de campaña, creatividad y búsqueda son vistas parciales del gasto de medios, no gasto adicional. Reconciliar donde cobertura completa; marcar parciales. No unir búsqueda y creativo a nivel fila ni construir usuario ficticio enlazado a Search Console. Los pedidos únicos se generan una vez en negocio_diario, no sumando conversiones de plataformas.

## Generador estructural
1. Calendario con estacionalidad semanal/anual, festivos, promociones, tendencia y shocks conocidos; heterogeneidad de mercados y categorías, correlación moderada de gasto entre canales con pulsos independientes para identificación.
2. Adstock + saturación por canal de generación de demanda. Demanda base + efecto de campañas; SEM marca captura demanda ya generada, no se suma como demanda independiente. Repartir intenciones en marca pura, marca producto y genérica.
3. Para oportunidades de marca: probabilidades mutuamente excluyentes de captura pagada, orgánica, directa y pérdida, condicionadas por cobertura SEO, competencia, gasto y mercado. Reducir SEM puede desplazar una parte a SEO y otra perderse. Diferentes mercados con diferente sustitución. Preservar masa de oportunidades y conversión no negativa.
4. Creatividad: atributos con efectos modestos, contexto canal/audiencia/promoción, frecuencia y ruido; asignación histórica parcialmente sesgada y algunos tests aleatorios. No hacer que toda variante nueva gane. Afecta respuesta del canal correspondiente, no añade conversiones por separado.
5. Generar pedidos propios por proceso estocástico controlado, AOV y margen coherentes. Crear señales publicitarias y atribuciones solapadas a partir del estado latente (con ruido, ventanas, coberturas); distinguir fuente. No forzar que sumen ventas.
6. Generar experimentos históricos con distintas intensidades de recorte y mercados; guardar controles, resultados nulos/negativos y positivos. Datos de entrenamiento hasta corte; futuras observaciones solo disponibles tras ejecutar experimento.
7. Dos snapshots alternativos: ruptura de tracking con cambio de escala en conversiones registradas y faltantes de inversión en mercados. Mantener verdad sintética de pedidos aparte cuando proceda. Mostrar origen y alcance, no interpolar silenciosamente.
8. Guardar manifiesto, checksum lógico, conteos, distribución, rangos y parámetros verdaderos en fixture de evaluación separado. El ajuste de modelos no puede leer parámetros verdaderos ni futuros. El motor de mundo sintético sí los utiliza para generar observaciones, separado del estimador.

## Validaciones y calidad
No negativos salvo ajustes explícitos, clicks ≤ impresiones donde comparables, tasas en [0,1], costes reconciliados, FK completas, fechas coherentes, margen = ventas - coste, gasto anual dentro de tolerancia definida. Semilla y versión iguales producen mismo checksum lógico salvo metadatos de ejecución. Test de fugas train/test; no usar variables posteriores al tratamiento. Registrar faltantes por denominador esperado y duplicados antes de deduplicar. Los cambios de tracking no implican cambio real de ventas.

## Persistencia y operación
SQLAlchemy/Alembic; índices fecha/mercado/canal y snapshot, consultas agregadas paginadas. Precargar datos una vez de forma idempotente; no regenerar al refrescar navegador. Reset con confirmación elimina/archiva solo estado demo y reconstruye desde semilla. Exportación de datos sintéticos y manifiesto sin secretos. No subir grandes dumps a Git: código generador y fixtures pequeñas son suficientes.
