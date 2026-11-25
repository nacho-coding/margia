# MARGIA · Sistema visual y experiencia v1.0

## Dirección artística
Producto B2B premium: terminal de decisiones, editorial financiera y precisión analítica. Inspiración conceptual en herramientas profesionales de inteligencia empresarial, sin copiar marcas ni interfaces. No heredar la torre ni la estética de grandes almacenes. Identidad propia, sobria, memorable y moderna. Diseñar primero escritorio 1440×900 y 1920×1080; usable a 1280×720, tablet y móvil en lectura. El centro debe parecer una aplicación real, no landing page ni plantilla genérica.

## Identidad
Wordmark MARGIA en mayúsculas, espaciado moderado; monograma M geométrico original formado por dos líneas ascendentes y convergentes, SVG accesible. Descriptor Marketing Decision Intelligence y lema «Cada decisión tiene un valor». Logo claro/oscuro, favicon, sin logo de terceros. Preferencia por modo claro de trabajo y navegación oscura; modo oscuro global P1 solo si acabado consistente.

Tokens CSS: fondo #F4F6F5, superficie #FFFFFF, superficie secundaria #EAF0ED, texto #172722, texto secundario #52645C, borde #D5DED9, navegación #102F29, navegación secundaria #183B33, primario #176B57, hover #125342, acento oro #C9A969 (ornamental), texto oro accesible #785B23, positivo #18734F, advertencia #94600D, negativo #B53C42, info #306A9D. Series: verde #23806A, azul #4279B0, violeta #8267A7, cobre #B07C4D, gris #82918A; color no es único indicador. Contraste WCAG AA, números tabulares. Tipografía Hanken Grotesk o Inter local con licencia, titulares editoriales discretos opcionales EB Garamond; fallbacks system-ui. Sin fuentes remotas obligatorias.

## Layout
Shell persistente: sidebar 224–240 px colapsable, logo y navegación agrupada (Decidir / Comprender / Experimentar / Gobernar); topbar con breadcrumbs, filtros globales, snapshot, periodo y etiqueta «Datos sintéticos». Área principal con ancho fluido y padding 24–32 px, rejilla de 12 columnas. Evitar tarjetas gigantes vacías, exceso de bordes redondeados o sombras, gradientes, neón, iconos decorativos y textos de marketing dentro de paneles. Radio 4–8 px, separadores finos, espacio 4/8/12/16/24/32. Tipografía 13–15 px cuerpo, 11–12 etiquetas, 22–30 cabeceras, 26–36 KPIs. Densidad legible. CTA verde; secundario borde; peligro explícito. Iconos lineales consistentes. Drawer lateral para metodología, detalle de entidad y supuestos; diálogos para confirmación. No abusar de modales.

## Componentes obligatorios
- KPI: valor, unidad, periodo, delta con base de comparación, definición accesible; sin falsos decimales.
- Tablas: sticky header, orden, filtros, paginación, alineación numérica, estados vacío/error; exportar donde sea útil.
- Gráficos ECharts o equivalente: tooltips, leyenda, ejes, unidades, intervalos y línea baseline; colores consistentes por canal; sin doble eje engañoso. Formato € español y fechas dd/mm/aaaa; distinguir % de puntos porcentuales.
- Waterfall económico con base, ahorro, cambio de margen, coste y neto; cada barra deriva de resultado API. Curvas de saturación con rango observado sombreado y extrapolación marcada. Comparador A/B lado a lado, no ocultar escenarios negativos.
- Evidencia: etiquetas neutras «Observado sintético», «Estimación», «Hipótesis», «Experimento simulado», «Datos insuficientes»; tooltip con fuente/versionado. Rojo solo para riesgo/error, verde para estado favorable. Mostrar intervalo y fecha de corte.
- Radar: tarjetas compactas con impacto, incertidumbre, coste, próxima acción y enlace; ranking explicable. Progreso de decisión mediante pasos.
- Creatividad: cuadrícula de imágenes locales coherentes con marca ficticia, detalle de composición y atributos, comparación de tres variantes. Usar assets originales generados durante desarrollo si herramienta disponible; si no, diseños publicitarios SVG/CSS con producto/escena estilizados de alta calidad, no placeholders vacíos. Registrar procedencia/licencia. No usar imágenes aleatorias remotas. Alt text.
- Experimentos: comparación pre/post, control/tratamiento, gráfico de efecto con banda, equilibrio de mercados y guardrails. No inventar un mapa preciso; un gráfico de mercados o mapa esquemático explícito basta.
- Fiabilidad: bandeja de incidencias con causa, modelo afectado y acción; estado bloqueado visible en módulos dependientes.

## UX
Una acción primaria por pantalla, filtros persistentes con reset, formularios con rangos/unidades y validación inmediata, navegación por entidad y conservar contexto al volver. Carga con skeleton discreto; error con mensaje útil y reintento; avisos accesibles. No mostrar pantalla vacía mientras el backend calcula; ejecución con estado real y cancelación solo si implementada. Animaciones 120–200 ms y reduced-motion. Teclado, foco, aria-labels, tablas accesibles, sin información solo por color. Evitar scroll horizontal global; tablas densas pueden tener scroll propio.

## Aceptación visual
Usar skill de UX/UI y revisión visual si disponible, sin delegar a agentes. Capturar pantallas reales con Playwright en 1440×900, 1920×1080 y 1280×720; revisar clipping, contraste, espaciado, tipografía, estados y gráficos. Revisar centro, One Search, experimento, creatividad, escenarios y fiabilidad. Probar móvil básico. Guardar capturas de QA localmente o en artefactos ligeros; no subir imágenes pesadas ni archivos sin licencia. No declarar calidad visual por build exitoso. El día 6 corregir defectos antes de añadir funciones.
