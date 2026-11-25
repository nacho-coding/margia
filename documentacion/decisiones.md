# Decisiones de implementación

## 25/11/2026 · Fundaciones

1. Se conserva el checkout y la rama `main`: repositorio inicial de documentación, limpio, con HEAD igual al remoto. No se reescribe historia. Se intentará push normal y se respetará cualquier protección del servidor.
2. Monolito modular con Next.js/TypeScript, FastAPI/SQLAlchemy/Alembic y **PostgreSQL en Docker**. Ninguna base alternativa, LLM, GPU ni API pagada. Un único proxy de API del mismo origen; solo el frontend publica puerto en `127.0.0.1`.
3. El Día 1 entrega datos observados sintéticos e integridad. MMM, recuperación causal, radar económico, experimentos y optimización no se inventan para completar pantallas: sus rutas explican el estado hasta sus incrementos.
4. Se fija el corte de demo en **31/10/2026**, 730 días desde 01/11/2024, independiente del reloj. Dos bloques de 365 días con 4,8 M€ cada uno. Históricos de búsqueda (28 días), campañas (7 días) y creatividad (28 días, cobertura parcial) se declaran con su cobertura; no se rellenan ausencias con ceros.
5. Importes almacenados en céntimos enteros; cocientes sin denominador se devuelven como `null`. Economía compartida en Python. JS solo presenta formatos, gráficos e interacción.
6. El seed queda separado de futuros estimadores. La verdad latente del generador se guarda en fixture de evaluación separado; la API no expone parámetros verdaderos como estimaciones. La reproducción se valida por checksum lógico, excluyendo timestamps.
7. Activos locales originales en SVG, con procedencia explícita; tipografía Inter local bajo OFL. Se usa la skill Sites en su ruta **local-only**: sin registro ni publicación en hosting externo. Prevalece la instrucción explícita de no delegar sobre sugerencias opcionales de la skill.
8. No se interpreta ausencia de historial como historial vacío con resultados inventados. El centro muestra la próxima acción y el estado de evidencia, sin importes de oportunidad hasta tener un estimador.

## Fuentes técnicas consultadas

- [Next.js en Docker, salida standalone](https://docs.docker.com/guides/nextjs/).
- [FastAPI en contenedores](https://fastapi.tiangolo.com/deployment/docker/).
- [Política de versiones PostgreSQL](https://www.postgresql.org/support/versioning/).

Las versiones efectivamente instaladas se fijan en lockfiles e imágenes; consultar el manifiesto técnico y los comandos en avances.

## Incorporación de PRD y RFC durante el desarrollo

Se leen íntegramente PRD.md (376 líneas) y RFC.md (637 líneas), añadidos en el commit ajeno `e6b3f97`. Se conserva ese commit y los documentos sin cambios. Son consistentes con la rebanada vertical del Día 1 y el backlog existente. Su matriz RF/RNF se incorporará a validación. El puerto 8080 del RFC es una propuesta; se mantiene 3000 configurable, seleccionado antes de recibir el RFC. No altera ningún contrato funcional.

La skill Modern Web Guidance instalada por el usuario se aplica a todo el frontend: guías `css-layout`, `dialog`, `navigation-drawer`, `responsive-table`, `accessibility`, `forms` y `performance`. Se conserva sin cambios la instalación del usuario. Se evita cualquier API de IA del navegador; las guías se usan solo para plataforma web.

Compatibilidad comprobada: Next 16.4.6 / React 19.3.1; TypeScript 6.0.3 y ESLint 9.39.5. Se descartan TS 7 y ESLint 10 por límites de los plugins de Next. Imágenes de Node 24, Python 3.13 y PostgreSQL 18 fijadas por digest; dependencias transitivas en lockfiles.

## 25/11/2026 · Medición y abstención

1. MMM de pedidos nacional sobre semanas completas, siete canales de demanda y SEM marca fuera del predictor. Los modelos no importan el generador ni leen `demanda_proxy` o verdad de evaluación. Agregación, validación temporal, transformación, curvas y valoración económica se calculan en Python.
2. 84 semanas de train, dos validaciones rolling previas y 20 semanas finales reservadas. No se reajusta con holdout tras medir ni se reentrena con los filtros. Un mercado no recibe el modelo nacional prorrateado. El alcance de semanas completas se explicita cuando difiere de los días de atribución.
3. Se mantiene el resultado adverso: WAPE mejora frente a naive, pero el reparto por canal es sensible entre configuraciones casi empatadas. Umbral de sensibilidad 1; medido 5,625. El estado bloqueado se decide en backend, sin relajar el umbral para producir una oportunidad favorable.
4. Bandas empíricas de escenarios condicionales con refit por bloques; se explica la ausencia de garantía de cobertura e interpretación causal. La revisión visual detectó segunda contracción de ridge: mmm-1.0.1 centra errores de refit y trunca medios a cero, conservando la versión anterior. No se presentan esos percentiles como IC causal.
5. Se conserva la hipótesis observada del centro y se mantiene **D2.3 pendiente**. Un radar ordenado por impacto económico requiere estimación Search/evidencia experimental, que aún no existe; no se deriva recuperación de atribución ni de SEO. Prevalecen veracidad y contrato matemático sobre la secuencia orientativa que situaba el radar antes de D3.1.
6. Artefacto JSON pequeño en PostgreSQL, con inputs, semilla, checksum y versión. Se prepara al arrancar; las lecturas son consultas de un ajuste guardado. Reset atómico incluye el modelo; no hay job o ejecución nueva fingida al navegar.
7. Se reaplican guías `responsive-table` y `accessibility`: tablas semánticas con scroll propio enfocable, alternativas de datos para ambos gráficos y metodología en el drawer nativo existente. La QA espera a los canvas, tras detectar capturas prematuras con skeleton. No se añaden librerías ni fuentes remotas.

## 25/11/2026 · Dependencia resuelta y Día 2 cerrado

1. La dependencia de D2.3 se resuelve dentro del hito: evidencia histórica y simulador Search se implementan antes de cerrar el radar. La decisión anterior de aplazarlo queda superada; no se sacrifica rigor ni se deja la tarea arrastrada.
2. Se usa la alternativa contractual de cambio total de pedidos por euro ahorrado. Recuperación SEO/directo no identificada, devuelta como `null`. Efectos por consulta tampoco identificados: la hipótesis afecta SEM marca completo y referencia sus 32 grupos reales, sin sumar suboportunidades.
3. Los 12 históricos son fixtures explícitas, almacenadas una vez y consultables con asignaciones/observaciones. Mismo mecanismo de captura del mundo original, checksum preservado y ningún pedido experimental añadido a ventas propias. Datos posteriores solo en ramas históricas previas al corte; no se fingen nuevos experimentos del usuario.
4. Bootstrap de 12 pares completos para no tratar días o mercados repetidos como réplicas independientes. Pooling nacional por muestra pequeña de cuatro pares por estrato; mercado individual e intensidades/horizontes no comparables son hipótesis sin recomendación. Nuevos geo y VOI mantienen su hito propio.
5. Una misma función Python valora base, ahorro, margen y costes para radar y simulador. Cuota común se cancela en el delta; costes nuevos se imputan una vez. El waterfall respeta cambios de signo (`stackStrategy: all`) y sus tooltips presentan importes con signo, no alturas absolutas.
6. Formularios con validación nativa y backend, coste explícito, aviso de parámetros modificados, foco de error y prevención de doble envío solo durante POST real. La evaluación queda guardada; mismo contenido reutiliza ID y lo declara.
7. GitHub: el usuario concede escritura a `ignaciofontal`; fetch sin divergencia y push normal de los siete commits anteriores correcto, hasta `ea9a8ab`. Se conserva `main` y origin; el bloqueo 403 queda resuelto.

## 25/11/2026 · Experimentos geo y valor de información

1. Se sigue la numeración operativa del backlog: D3.1 Search (incluye simulador), D3.2 geo y D3.3 información; corresponde a los puntos D3.1–D3.4 del plan raíz, sin cambiar su alcance.
2. Las nuevas observaciones son ramas posteriores al corte sobre el mismo mundo, condicionadas al perfil diario observado. No se presentan como futuro real ni alteran los hechos. El estimador ve brazos observados; el orquestador vive fuera de `app/modelos`, después de que la regresión AST detectara y rechazara un acoplamiento inicial con el mundo.
3. Se elige pedidos propios como KPI primario P0. IC por pares con t, MDE aproximado y guardrails explícitos. No se trata significación como requisito para aprender: un efecto adverso o compatible con cero puede ser evidencia válida.
4. La actualización **sustituye**, sin acumular supuesta independencia entre ramas de los mismos mercados. Modelos anteriores y ejecuciones Search son inmutables. Copias idénticas reutilizan versión; diseños obsoletos no sobrescriben evidencia vigente. El soporte se restringe a la intensidad realmente probada.
5. EVSI discreto con likelihood normal y error derivado del diseño, junto a EVPI como cota. Dos acciones disponibles (mantener/recortar); reinvertir sigue en D4. Se compara el mismo horizonte y se resta una sola vez coste de prueba y oportunidad de esperar. No se anualizan ahorros ni se bonifican pérdidas para favorecer experimentar.
6. Se reutiliza el esquema 0003: protocolo y eventos JSON, asignaciones/observaciones y artefactos de modelo. Sin nuevas dependencias, servicios ni migración innecesaria. Persistencia/reset se verifican en una pila Docker aislada.
7. Modern Web Guidance `forms`: radios nativos para duraciones, fieldset/legend, errores solo al enviar, foco en error/estado y bloqueo de envío únicamente durante POST. Se mantiene validación de servidor y acceso local con proxy del mismo origen.

## 25/11/2026 · Pretest creativo contextual (D4.1)

1. El histórico original solo tiene 28 días, 12 composiciones reutilizadas y categoría/tono/CTA ligados. Prevalecen veracidad y contratos matemáticos sobre un ranking visual atractivo: se codifica un paquete observado, sin efectos independientes ni características de píxeles. No se regenera el universo para favorecer una validación.
2. Modelo binomial de clics con denominador impresiones, ridge fija y holdout simultáneo por grupo conectado de composición/campaña y por fecha. Los cruces incompatibles se excluyen; no se reajusta con holdout. Referencia por canal y diagnóstico adverso conservados. Bandas por grupos expresamente condicionales, sin promesa de cobertura predictiva o causal.
3. Tres variantes por cada perfil como SVG originales precreados, con productos del catálogo existente. Comparten CTR contextual: no hay ganador predictivo identificado. CVR solo observado en train por canal; ni conversiones atribuidas ni CTR se convierten en demanda propia. Multiplicador económico 1.
4. El usuario puede guardar una propuesta como hipótesis inmutable para la prueba posterior. D4.2 A/B y D4.3 orquestador/optimización siguen pendientes. La numeración es la del backlog; no se declara completo el Día 4 ni se relaja el bloqueo del MMM.
5. Migración 0004 aditiva, modelo al arranque, resultados por contenido y recursos versionados. Se conservan las rutas publicadas; un rediseño futuro crea otra ruta/versión. Reset explícito elimina hipótesis y reconstruye el mismo mundo; nunca se usa para limpiar la demo principal durante QA.
6. Modern Web Guidance `forms`: etiquetas, límites y validación nativa/API, textarea redimensionable para el objetivo, foco de error/resultado y acciones de al menos 48 px. Solo se deshabilita durante POST real. No hay nuevas dependencias de runtime, IA, agentes ni servicios externos.

## 25/11/2026 · Fotografía y preparación por plataforma

1. El usuario solicita más realismo y permite una preparación simulada. Se generan nueve imágenes con Imagegen durante el desarrollo y se guardan localmente. La interfaz simula la preparación de propuestas, con recursos precreados identificados, sin fingir una llamada generativa en runtime. Los estados corresponden a carga/decodificación y evaluación reales; sin contadores de progreso inventados.
2. Meta 4:5, TikTok 9:16, Display 1200:628 y YouTube 16:9 tienen composición, encuadre y jerarquía propios. Los dos canales de vídeo muestran fotogramas estáticos de ejemplo, sin controles de reproducción inertes ni supuesta activación. Especificaciones oficiales consultadas y límites en creatividad.md.
3. Fotografías y maquetas son recursos nuevos, no observaciones. La biblioteca conserva el asset histórico y devuelve una recreación marcada. El estimador, las particiones y el checksum del negocio no cambian; la adaptación de formato no identifica un efecto adicional. Multiplicador económico 1.
4. Nuevas rutas y versiones `fotografia-2.0.0` / `composicion-2.0.0`, con textos y placement guardados. El renderer conserva el SVG de evaluaciones anteriores. El script de empaquetado impide cambiar bytes de una ruta versionada existente. Sin migraciones ni nuevas dependencias.
5. Modern Web Guidance: proporciones reservadas con `aspect-ratio`, tipografía relativa al contenedor, una sola imagen prioritaria, lazy normal para miniaturas fuera de pantalla y respeto a reduced-motion. WebP transcodificado con Sharp existente; aproximadamente 1 MB total. No se publican los PNG pesados de generación ni sus rutas locales.
