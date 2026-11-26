# MARGIA
**Marketing Decision Intelligence · Cada decisión tiene un valor.**

MARGIA es una prueba de concepto avanzada de un gemelo digital comercial de marketing: conecta medición de medios, One Search (SEO + SEM), inteligencia creativa, experimentación y optimización económica sobre un único estado del negocio. El objetivo es decidir dónde invertir, dónde reducir inversión, cuándo experimentar y cómo aprender de los resultados.

**Estado:** Días 1–4 y D5.1 implementados: PostgreSQL, datos reproducibles, centro económico, MMM nacional, radar/One Search, geo y valor de información, creatividad fotográfica/A-B, comparador base/ahorro/reinversión, borradores con revisiones, decisiones con motivo y exportaciones CSV/Markdown. Costes, incertidumbre, restricciones y abstención explícitos. El MMM mantiene bloqueado el reparto por canal: la reinversión es una hipótesis y la búsqueda automática se limita a las opciones respaldadas por Search. Quedan incidencias/restauración, recorrido integrado/guion y congelación/QA final. Verificaciones ejecutadas y límites en [validación](documentacion/validacion.md). No es una implantación productiva ni evidencia comercial real.

## Contrato de desarrollo

| Archivo | Finalidad |
|---|---|
| [AGENTS.md](AGENTS.md) | Instrucciones permanentes para Codex; trabajo secuencial, sin agentes adicionales. |
| [ESPECIFICACION_MARGIA.md](ESPECIFICACION_MARGIA.md) | Visión, alcance, modelo de producto, pantallas y recorridos. |
| [DESIGN.md](DESIGN.md) | Identidad visual, UX/UI y aceptación visual. |
| [DATOS_SINTETICOS.md](DATOS_SINTETICOS.md) | Universo ficticio, granularidad, generador y contratos de datos. |
| [MODELOS_MATEMATICOS.md](MODELOS_MATEMATICOS.md) | Modelos, simulación, experimentación, incertidumbre y economía. |
| [PLAN_DESARROLLO.md](PLAN_DESARROLLO.md) | Arquitectura, tareas, fases, pruebas, Git y entrega. |
| [PROMPT_CODEX.md](PROMPT_CODEX.md) | Orden inicial para desarrollar el proyecto. |
| [PRD.md](PRD.md) | Requisitos funcionales/no funcionales y aceptación de producto. |
| [RFC.md](RFC.md) | Arquitectura objetivo y contratos de implementación. |
| [Backlog](documentacion/backlog.md) | Seis jornadas con prioridades, criterios y estado. |
| [Validación](documentacion/validacion.md) | Pruebas realmente ejecutadas, mediciones y límites. |

## Principios

- Interfaz, documentación y comunicación en español.
- Una empresa ficticia, datos sintéticos, cálculos reales y resultados reproducibles.
- Sin agentes adicionales, sin IA generativa local, sin GPU requerida ni servicios de pago obligatorios.
- Producto web de aspecto premium y recorrido funcional de extremo a extremo, no una colección de dashboards.
- Sin datos privados, credenciales, información de clientes, logos de terceros ni documentos corporativos internos en GitHub. Este repositorio es público en el momento de su inicialización.

## Repositorio

`https://github.com/nacho-coding/margia.git`

Para obtener la documentación inicial: `git clone https://github.com/nacho-coding/margia.git`. Si ya existe una carpeta local vacía llamada margia, ejecutar desde ella `git clone https://github.com/nacho-coding/margia.git .`.

## Arranque local en Windows

Requisito: Docker Desktop iniciado con contenedores Linux y Docker Compose. El primer arranque descarga imágenes oficiales y paquetes; tras construir, la aplicación opera sin servicios externos. No necesitas Python, PostgreSQL ni Node instalados en Windows para utilizarla.

Desde la raíz del proyecto, en PowerShell:

```powershell
./scripts/iniciar.ps1
```

El script crea `.env` con una contraseña aleatoria local si no existe, construye las imágenes y espera a que los tres servicios estén saludables. **Abrir [MARGIA local](http://localhost:3000).** Solo se publica `127.0.0.1:3000`; PostgreSQL y FastAPI se mantienen en redes de Docker.

Parar conservando los datos y volver a arrancar sin recompilar:

```powershell
./scripts/detener.ps1
./scripts/iniciar.ps1 -SinBuild
```

La inversión y las ventas no se regeneran al refrescar ni al reiniciar. Para reconstruir únicamente esta demo, incluidas sus decisiones:

```powershell
./scripts/reset_demo.ps1
```

Exige escribir `RESTABLECER DEMO`; `-Confirmar` sirve para pruebas operativas explícitas. No uses `down -v` como comando de parada: elimina persistencia. El puerto se puede configurar con `MARGIA_PORT` en `.env`; los scripts muestran/usan ese puerto. El cambio de corte requiere restablecer explícitamente el universo y no conserva decisiones previas: mantener el corte probado para esta entrega.

## Qué se puede utilizar

- Centro de decisiones: cinco KPIs desde PostgreSQL, comparación equivalente, serie diaria, detalle de definición, filtros de mercado/periodo y CSV. Primer radar de marca con impacto estimado, riesgo, costes y enlace a la hipótesis real.
- Medición: atribución por plataforma separada del MMM nacional; 104 semanas, dos ventanas rolling y 20 semanas finales reservadas, referencia estacional, descomposición reconciliada, bandas empíricas, curvas y marginal con soporte. Los filtros visuales no reentrenan; un mercado individual no recibe un modelo nacional desglosado artificialmente. [Método y límites](documentacion/modelo_mmm.md).
- One Search: consultas SEO/SEM, serie de clics, históricos consultables y simulador de recorte 0–100 %, costes y cuota común/incremental, bandas, equilibrio y opción no actuar. Estima cambio total de pedidos por euro ahorrado; la recuperación SEO/directo no está identificada. Soporte experimental 25/50/75 %; mercado individual y otros horizontes se marcan como hipótesis. [Método y límites](documentacion/one_search.md).
- Experimentos: diseño geo con mercados, preperiodo, duración, coste, riesgo y semilla; parejas aleatorizadas, equilibrio, placebo y MDE. EVPI/EVSI con coste y oportunidad de esperar. Ejecuta una rama sintética nueva, estima efecto e IC por pares y permite sustituir Search solo con evidencia compatible, conservando versiones. Tras sustituir, el soporte se restringe a la intensidad ejecutada. [Método y límites](documentacion/experimentos_geo.md).
- Creatividad: 80 registros y 12 composiciones históricas; biblioteca con recreaciones fotográficas, filtros, ordenación y detalle con denominadores. Nueve fotografías sintéticas locales, tres propuestas por perfil adaptadas a Meta, TikTok, Display y YouTube, brief por reglas y selección guardada. Preparación simulada con carga real del catálogo, sin servicio generativo en ejecución. Modelo binomial de CTR validado por composición/campaña y fecha; las propuestas comparten referencia histórica, sin ganador visual identificado por ese predictor. [Método y límites](documentacion/creatividad.md).
- A/B creativo: diseño congelado desde el pretest, dos o tres brazos, oportunidades aleatorias y observaciones nuevas. MDE aproximado, denominadores, IC Wilson/Newcombe, multiplicidad, costes y CSV de asignaciones. Acepta aprendizaje de CTR compatible, también nulo o adverso, y conserva versiones por contexto; no acumula ramas dependientes. El pretest muestra la referencia experimental separada del histórico. Más clics no identifican pedidos/beneficio: multiplicador económico 1. [Método y límites](documentacion/experimentos_ab.md).
- Fiabilidad: cobertura, integridad de claves y margen, diagnóstico del MMM; manifiesto y checksum. Configuración: reset explícito que reconstruye también el modelo.
- Escenarios: proyección nacional de 28 días, base/A ahorro/B reinversión, presupuesto por canal y costes comparables, 200 réplicas compartidas, bandas y riesgo, waterfall reconciliado y búsqueda determinista con restricciones/opción mantener. Selección creativa con recurso, aprendizaje y coste de producción; multiplicador económico 1. Ejecuciones inmutables con historial y enlaces por ID desde Search, medición y creatividad. El MMM bloqueado excluye reinversión de la búsqueda automática. [Método y límites](documentacion/escenarios.md).
- Borradores y decisiones: guardar sin ejecutar, editar con control de revisión, duplicar y archivar con motivo conservando resultados. Aprobación/rechazo terminal sobre un plan con evidencia congelada; el servidor revalida datos, dependencias, soporte, restricciones y riesgo. Historial por ID desde centro/escenarios y descargas CSV/Markdown reales. Aprobar registra una decisión simulada; nunca activa publicidad.

Universo observado: 247.562 registros, 24 mercados ficticios, 730 días de negocio y medios, corte fijo 31/10/2026, semilla 260725. El MMM usa 728 días en semanas completas; dos días iniciales quedan fuera del ajuste. Búsqueda cubre los últimos 28 días; campañas, siete; creatividad, 28 días con mercados parciales por activo. Todas las fuentes son sintéticas.

Se añaden 12 históricos experimentales de arranque, 288 asignaciones y 576 observaciones pre/post en tablas separadas. Son ramas sintéticas explícitas del mismo negocio; no se suman a ventas/inversión ni cambian el checksum original. El laboratorio guarda las nuevas pruebas aparte de esas fixtures. El arranque conserva pruebas, modelos y evaluaciones; el reset explícito elimina actualizaciones de usuario y reconstruye la evidencia de arranque.

El catálogo fotográfico añade nueve WebP generados con Imagegen durante el desarrollo (tres perfiles × tres escenas, aproximadamente 1 MB en total). Se componen localmente en cuatro formatos; TikTok y YouTube muestran fotogramas estáticos de ejemplo. Las métricas de biblioteca pertenecen a los registros históricos, no a esas fotografías nuevas. Las doce composiciones históricas y los nueve SVG de pretests anteriores se conservan para consultar resultados antiguos sin cambiarlos. Modelo, evaluaciones y selecciones sobreviven al reinicio; el reset elimina las hipótesis de usuario y reproduce el modelo.

## Verificación

```powershell
./scripts/comprobar.ps1
```

Ejecuta salud, pytest y Ruff dentro de Docker. Para las pruebas de frontend se necesita Node compatible (la imagen usa Node 24):

```powershell
Set-Location frontend
npm.cmd ci
npx.cmd playwright install chromium
npm.cmd run lint
npm.cmd run typecheck
npm.cmd run test:e2e
```

Las pruebas usan la aplicación Docker en `127.0.0.1:3000`. Capturas y reportes locales en `artifacts/qa`, excluidos de Git. Pruebas de este incremento, versiones, resultados, advertencias y cobertura: [validación](documentacion/validacion.md). El alcance pendiente permanece en el backlog; no se declara terminada la POC completa.

Para QA con aceptación de evidencia y reset se utiliza una pila aislada. En PowerShell, desde la raíz: `$env:MARGIA_PORT='3002'` y `docker compose -p margia-decisiones-qa up -d --build --wait --wait-timeout 180`. Desde `frontend`, `$env:MARGIA_QA_URL='http://127.0.0.1:3002'` y `npm.cmd run test:e2e -- --trace off`. Los recorridos crean/aceptan pruebas geo/A-B y guardan hipótesis/comparaciones/decisiones; sus fixtures Python revierten las transacciones. No ejecutar pytest y Playwright escribiendo simultáneamente en la misma base. La prueba que cambia temporalmente el esquema exige `MARGIA_VALIDACION=1` **solo en QA**; las comprobaciones normales la omiten. Al terminar: `docker compose -p margia-decisiones-qa down` desde la raíz, sin `-v`, y eliminar las variables temporales de la sesión si se continúa usando esa consola. Para repetir las fixtures operativas, utilizar una pila nueva: su preparación inserta el identificador fijo `qa-persistencia`.

Contratos disponibles: [OpenAPI](http://localhost:3000/api/openapi.json), [documentación de API](http://localhost:3000/api/documentacion). Procedencia/licencias: [recursos](documentacion/licencias.md). Arquitectura implementada: [arquitectura](documentacion/arquitectura.md).
