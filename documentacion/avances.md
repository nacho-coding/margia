# Avances y evidencia ejecutada

## 25/11/2026 · Inicio del Día 1

### Inspección

- Leídos íntegramente los ocho Markdown de raíz: AGENTS, README, ESPECIFICACION_MARGIA, DESIGN, DATOS_SINTETICOS, MODELOS_MATEMATICOS, PLAN_DESARROLLO y PROMPT_CODEX.
- `git status --short --branch`: `main...origin/main`, sin cambios iniciales.
- `git remote -v`: origin `https://github.com/nacho-coding/margia.git`.
- `git log -5 --oneline`: último commit `ccf1a64`.
- `git ls-remote origin refs/heads/main`: HEAD remoto `ccf1a645e152d05ae649d285477ebfb5ee715886`, igual al local (ejecución con acceso de red).
- Node `v26.13.1`, npm `11.20.0`, Docker CLI `29.9.3`, Compose `v5.7.1`. Los alias Windows `python`/`py` no contienen un intérprete utilizable; Python se ejecutará en contenedor.
- Docker Desktop inicialmente detenido; se ha iniciado con `Start-Process ... -WindowStyle Hidden`. Salud todavía pendiente de verificar.
- La red de la consola aislada no resuelve GitHub; se utiliza escalación de red autorizada para dependencias y Git. No se han leído ni mostrado credenciales.

### Tareas y pruebas previstas del incremento

Backlog completo en [backlog.md](backlog.md). Primer incremento: Compose de producción, migraciones y seed; tests de reproducibilidad/FK/reconciliación y economía, API y reinicio; shell/centro y vistas descriptivas; typecheck/build y capturas reales en cuatro resoluciones. No se declara ninguna de estas verificaciones como ejecutada todavía.

### Pendientes y riesgos

- Comprobar motor Docker, descargas y permisos de Git push.
- Medir generación y memoria; ajustar cobertura parcial explícita si hace falta.
- Modelos y recorrido causal completo reservados a D2–D5. No implementados al inicio.

## 25/11/2026 · Cierre técnico del Día 1

### Incremento funcional entregado

- Docker Desktop operativo. PostgreSQL 18, FastAPI/Python 3.13 y Next.js 16/React 19 en producción local, imágenes por digest y paquetes por lockfile. Solo `127.0.0.1:3000` publicado.
- 247.562 registros sintéticos: 730 días de negocio/medios, 24 mercados, ocho canales, 120 campañas, 50 grupos de búsqueda, 80 registros creativos y 12 diseños SVG locales originales. Coberturas parciales visibles.
- API única de KPIs, atribución, búsqueda, biblioteca, integridad y exportación. Filtros de periodo/mercado conservados en URL. No se suman atribuciones como pedidos ni gastos de vistas parciales como inversión nueva.
- Shell visual con navegación por ámbitos, centro económico real, tablas paginadas de Search, biblioteca y detalles, fiabilidad, metodología y reset explícito. Experimentación/escenarios señalados como en desarrollo, sin botones de ejecución ficticios.
- Leídos PRD.md y RFC.md íntegros; se conserva su commit local ajeno `e6b3f97`. Sin cambios a esos documentos.
- Aplicada Modern Web Guidance instalada por el usuario: búsqueda/lectura de guías y revisión de implementación. Fuentes/licencias y correspondencia de guías documentadas. Instalación local de la skill conservada e ignorada en Git; `skills-lock.json` fija su procedencia.

### Comandos y resultados realmente ejecutados

| Comando | Resultado |
|---|---|
| `docker compose up -d --build --wait --wait-timeout 180` | Tres servicios saludables, build de producción correcto |
| `scripts/iniciar.ps1` | Arranque completo probado; muestra URL real, sin exponer la clave local |
| `scripts/detener.ps1` + `scripts/iniciar.ps1 -SinBuild` | Conserva volumen y checksum |
| `scripts/comprobar.ps1` | 18 pytest pasan en 15,26 s; Ruff correcto; health listo |
| `docker compose … python -m pytest -q` | Baterías adicionales de reproducibilidad, economía, integridad y API pasan; una deprecación httpx en TestClient |
| `npm.cmd run test:e2e` | Última regresión: 6 passed (1,3 min); filtros, paginación, detalle, exportación, errores, foco y móvil |
| `npm.cmd run lint` / `typecheck` / `npm ls --depth=0` | Sin errores; árbol directo compatible |
| QA 7 rutas × 4 tamaños | 28 capturas reales; cero infracciones axe detectadas tras corregir contrastes; inspección visual de siete vistas |
| Pila `margia-validacion` desde PostgreSQL vacío | Migración y seed probados, fixture de decisión persiste tras reinicio; reset reconstruye mismos conteos/hash |
| `scripts/reset_demo.ps1 -Confirmar` | Reset principal correcto en 53,75 s; alineado con generador final |
| `git diff --cached --check` y revisión de exclusiones | Se corrige whitespace del DDL; .env, dependencias, dumps, cachés y capturas excluidos |

Hash lógico final: `6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d`. Primer seed medido: 41,364 s; reset aislado bajo carga: 69,408 s. Muestra de RAM en reposo: web 40,25 MiB, API 70,73 MiB, DB 113,4 MiB; no es pico ni memoria total de Docker/VM. Pila aislada detenida; demo principal disponible.

### Defectos encontrados y corregidos

- Query de periodo como Literal[int]: rechazaba el valor textual; convertido a entero validado contra el conjunto permitido.
- Build dentro del sandbox Windows no podía crear el proceso PostCSS; validación de producción realizada en Docker Linux, con éxito.
- Compatibilidad de TS 7 / ESLint 10: se fijan TS 6.0.3 y ESLint 9.39.5 con sus plugins compatibles. Queda aviso de fin de soporte de ESLint 9 en el instalador; revisar cuando Next admita la cadena completa nueva.
- Contraste del antetítulo y rótulo SEO/SEM, moneda en tarjetas móviles, espacio al ocultar un salto de línea y etiqueta sobre el wordmark creativo: corregidos y recapturados.
- Coherencia de categoría de creativo/campaña y checksum independiente del orden de inserción: corregidos, probados y demo reconstruida antes de cerrar versión inicial.
- Cachés de pytest/Ruff intentaban escribir en `/app` dentro del contenedor sin privilegios. Script corregido para desactivar esas cachés, sin elevar usuario.
- La primera prueba operativa se lanzó antes de seed saludable y con script no incorporado; se repitió con readiness, ruta y PYTHONPATH correctos. Solo la repetición satisfactoria cuenta como evidencia.

### Git y bloqueo de publicación

- Commit original de PRD/RFC conservado: `e6b3f97`.
- Primer hito probado: `c7f86dc` — «feat: crear base PostgreSQL y API reproducible con pruebas económicas».
- Interfaz probada: `64502e5` — «feat: conectar interfaz MARGIA con filtros y revisión visual accesible». Cierre documental consultable con `git log -4 --oneline`.
- No había identidad Git configurada; los commits de esta sesión usan identidad de herramienta `Codex <codex@openai.com>` solo en el comando, sin modificar la identidad global del usuario.
- `git push origin main`: GitHub devuelve 403, «Permission to nacho-coding/margia.git denied to ignaciofontal». El conector confirma permiso **read** para esa cuenta. Intento con propietario y credenciales no interactivas: no hay credencial disponible. No se cambia remoto ni se usa force.
- El usuario elige habilitar escritura para `ignaciofontal`; se facilita enlace de colaboradores y se indica aceptar la invitación. El conector disponible no incluye añadir colaboradores. **Reintento de cierre ejecutado: mismo 403**. El último HEAD remoto observado sigue en `ccf1a64`; no se declara que el PRD/RFC o el código estén subidos. Los cambios quedan confirmados localmente, preparados para push normal cuando la cuenta tenga escritura efectiva.

### Próximo incremento

Día 2, D2.1–D2.3: agregación semanal, MMM regularizado con holdout y baseline, diagnóstico, curvas y primer radar económico. La economía aritmética ya está probada; la recuperación de Search y el flujo geo → creatividad → optimización → decisión aún no están implementados. No hay candidata v0.1.0-demo ni etiqueta final.

Evidencia detallada y límites: [validacion.md](validacion.md). Backlog actualizado: [backlog.md](backlog.md). No se han utilizado agentes, LLM locales, GPU ni APIs de pago obligatorias.
