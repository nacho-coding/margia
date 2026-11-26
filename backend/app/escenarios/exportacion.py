"""Exportaciones de una ejecución congelada; no calculan ni revalidan decisiones."""
import csv
import html
import io
import json

from fastapi.responses import Response
from sqlalchemy import select

from app.escenarios.decisiones import PLANES, ejecucion, plan_guardado, serializar
from app.persistencia.tablas import Decision

METRICAS = dict(pedidos="Pedidos propios", ventas="Ventas netas", coste_directo="Coste directo",
    margen="Margen bruto", inversion="Medios", creatividad="Producción creativa",
    experimento="Experimento pendiente", plataforma="Plataforma", otros="Otros costes",
    contribucion="Contribución neta")


def celda(valor):
    if isinstance(valor, str):
        # Texto controlado por el usuario también puede abrirse en una hoja de cálculo.
        return "'"+valor if valor.lstrip().startswith(("=", "+", "-", "@")) or valor.startswith(("\t", "\r", "\n")) else valor
    if isinstance(valor, bool):
        return "sí" if valor else "no"
    if isinstance(valor, (int, float)):
        return str(valor).replace(".", ",")
    return "n/d" if valor is None else json.dumps(valor, ensure_ascii=False, sort_keys=True)


def md(valor):
    texto = html.escape(str(valor), quote=False)
    for caracter in ("\\", "`", "*", "_", "{", "}", "[", "]", "(", ")", "#", "+", "!", "|"):
        texto = texto.replace(caracter, "\\"+caracter)
    return texto.replace("\r", " ").replace("\n", " · ")


def exportar(db, eid, formato):
    e = ejecucion(db, eid)
    decision = db.scalar(select(Decision).where(Decision.ejecucion_id == eid))
    evidencia = "Datos sintéticos · proyección y estimaciones condicionales · ninguna activación publicitaria"
    metadatos = dict(evidencia=evidencia, ejecucion=e.id, escenario=e.escenario_id, revision=e.revision,
        snapshot=e.snapshot_id, nombre=e.entradas["nombre"], creado=e.creado.isoformat(),
        inicio=e.resultado["inicio"], fin=e.resultado["fin"], semilla=e.semilla, motor=e.version,
        checksum_fuentes=e.checksum_fuentes, traza_draws=e.resultado["traza_draws"]["checksum"],
        replicas=e.resultado["replicas"], entradas=e.entradas, modelos=e.modelos,
        metodo=e.resultado["metodo"], advertencias=e.resultado["advertencias"])
    if formato == "csv":
        salida = io.StringIO(newline="")
        escritor = csv.writer(salida, delimiter=";", quoting=csv.QUOTE_ALL)
        escritor.writerow(["seccion", "plan", "magnitud", "valor", "unidad"])
        for k, v in metadatos.items():
            escritor.writerow(["trazabilidad", "", k, celda(v), ""])
        for key, _ in PLANES:
            p = plan_guardado(e, key)
            if p is None:
                escritor.writerow(["resultado", key, "estado", "Sin candidato", ""])
                continue
            for k, v in p["metricas"].items():
                escritor.writerow(["economia", key, k, celda(v), "pedidos" if k == "pedidos" else "EUR"])
            for k in ("delta", "ahorro_bruto", "reinversion", "ahorro_conservado", "coste_incremental"):
                escritor.writerow(["economia", key, k, celda(p[k]), "EUR"])
            for k, v in p["bandas"]["delta"].items():
                escritor.writerow(["banda_delta", key, k, celda(v), "proporción" if k == "probabilidad_perdida" else "EUR"])
            for k, v in p["presupuestos"].items():
                escritor.writerow(["presupuesto", key, k, celda(v), "EUR"])
            for k in ("recorte_pct", "reinversion_pct", "factible", "elegible", "restricciones", "motivos", "creatividad", "multiplicador_demanda"):
                escritor.writerow(["condiciones", key, k, celda(p[k]), "%" if k.endswith("_pct") else ""])
        if decision:
            for k, v in serializar(decision).items():
                escritor.writerow(["decision", decision.evidencia.get("plan", ""), k, celda(v), ""])
        contenido, extension, tipo = "\ufeff"+salida.getvalue(), "csv", "text/csv"
    else:
        lineas = ["# MARGIA · Comparación guardada", "", md(e.entradas["nombre"]), "", evidencia+".", "",
            "## Trazabilidad", ""]
        for k, v in metadatos.items():
            lineas.append(f"- **{md(k)}:** {md(json.dumps(v, ensure_ascii=False, sort_keys=True) if isinstance(v, (dict, list)) else v)}")
        lineas += ["", "## Base y alternativas", "", "| Magnitud | Base | Ahorro | Reinversión | Candidato |",
            "|---|---:|---:|---:|---:|"]
        planes = [plan_guardado(e, k) for k, _ in PLANES]
        for k, nombre in METRICAS.items():
            valores = [md(celda(p["metricas"][k])) if p else "n/d" for p in planes]
            lineas.append(f"| {nombre} ({'pedidos' if k == 'pedidos' else 'EUR'}) | "+" | ".join(valores)+" |")
        for k, nombre in (("media", "Delta esperado (EUR)"), ("p05", "p05 delta (EUR)"), ("p50", "p50 delta (EUR)"),
                          ("p95", "p95 delta (EUR)"), ("probabilidad_perdida", "Probabilidad de pérdida (proporción)")):
            lineas.append(f"| {nombre} | "+" | ".join(md(celda(p["bandas"]["delta"][k])) if p else "n/d" for p in planes)+" |")
        for key, nombre in PLANES:
            p = plan_guardado(e, key)
            lineas += ["", "### "+nombre, ""]
            if p is None:
                lineas.append("La búsqueda no encontró candidato elegible.")
                continue
            for k in ("recorte_pct", "reinversion_pct", "delta", "ahorro_bruto", "reinversion", "ahorro_conservado", "coste_incremental", "factible", "elegible", "restricciones", "motivos", "presupuestos", "creatividad", "multiplicador_demanda"):
                lineas.append(f"- **{k}:** {md(celda(p[k]))}")
        lineas += ["", "## Decisión registrada", ""]
        if decision:
            lineas += [f"- **ID:** {md(decision.id)}", f"- **Estado / plan:** {decision.estado} / {decision.evidencia['plan']}",
                f"- **Fecha de sistema:** {decision.creado.isoformat()}", "- **Motivo:** "+md(decision.motivo),
                "- **Guardrails al registrar:** "+md(celda(decision.evidencia["guardrails"]))]
        else:
            lineas.append("Esta ejecución aún no tiene una decisión registrada.")
        contenido, extension, tipo = "\n".join(lineas)+"\n", "md", "text/markdown"
    return Response(contenido, media_type=tipo, headers={
        "Content-Disposition": f'attachment; filename="margia-{e.id}.{extension}"', "Cache-Control": "no-store"})
