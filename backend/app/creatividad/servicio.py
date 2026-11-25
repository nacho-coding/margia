import hashlib
import json
import time

from fastapi import HTTPException
from sqlalchemy import func, select, text

from app.api.consultas import snapshot_actual
from app.api.creatividad_contratos import ParametrosPretest
from app.modelos.creatividad import VERSION, entrenar_creatividad, predecir_contexto
from app.persistencia.tablas import (
    Campana,
    Canal,
    CreatividadDiaria,
    Creativo,
    Modelo,
    PretestCreativo,
    SeleccionCreativa,
)

ESTILOS = [("espacio", "Espacio para el producto", "Bodegón y jerarquía tipográfica"),
           ("marco", "Una selección enmarcada", "Encuadre y separación del mensaje"),
           ("detalle", "El detalle como protagonista", "Producto ampliado y lectura editorial")]


def variantes_de(perfil):
    categoria = perfil["categoria"]
    return [dict(id=f"{categoria}-{vid}", categoria=categoria, nombre=nombre, composicion=composicion,
        asset=f"/assets/creatividad/pretest-{categoria}-{vid}.svg", tono=perfil["tono"], cta=perfil["cta"],
        version_recurso="variantes-1.0.0", licencia="Original MARGIA · CC BY 4.0") for vid, nombre, composicion in ESTILOS]


def observaciones(db, snapshot):
    filas = db.execute(select(CreatividadDiaria, Creativo, Campana).join(Creativo, CreatividadDiaria.creativo_id == Creativo.id)
        .join(Campana, Creativo.campana_id == Campana.id).where(CreatividadDiaria.snapshot_id == snapshot.id,
            CreatividadDiaria.fecha <= snapshot.corte).order_by(CreatividadDiaria.fecha, Creativo.id, CreatividadDiaria.mercado_id)).all()
    return [dict(id=c.id, asset=c.asset, campana=p.id, canal=p.canal_id, fecha=o.fecha.isoformat(), mercado=o.mercado_id,
        categoria=p.categoria, tono=c.atributos["tono"], cta=c.atributos["cta"], audiencia=c.atributos["audiencia"],
        frecuencia=o.frecuencia, impresiones=o.impresiones, clics=o.clics, conversiones=o.conversiones) for o, c, p in filas]


def asegurar_creatividad(db, snapshot):
    db.execute(text("SELECT pg_advisory_xact_lock(260725)"))
    existente = db.scalar(select(Modelo).where(Modelo.snapshot_id == snapshot.id, Modelo.version == VERSION))
    if existente:
        return existente
    inicio = time.perf_counter()
    filas = observaciones(db, snapshot)
    resultado = entrenar_creatividad(filas, snapshot.semilla)
    mid = "creatividad-"+hashlib.sha256(f"{snapshot.id}:{VERSION}:{resultado['checksum_datos']}".encode()).hexdigest()[:20]
    resultado.update(id=mid, snapshot=snapshot.id, corte=snapshot.corte.isoformat(), filas_observadas=len(filas),
        perfiles=[dict(categoria=c, tono=t, cta=a) for c, t, a in sorted({(f["categoria"], f["tono"], f["cta"]) for f in filas})],
        segundos_ajuste=round(time.perf_counter()-inicio, 3))
    modelo = Modelo(id=mid, snapshot_id=snapshot.id, version=VERSION,
                    checksum_datos=resultado["checksum_datos"], resultado=resultado)
    db.add(modelo)
    db.flush()
    return modelo


def actual(db, snapshot):
    m = db.scalar(select(Modelo).where(Modelo.snapshot_id == snapshot.id, Modelo.version == VERSION))
    if not m:
        raise HTTPException(503, "El modelo creativo todavía no está preparado. Comprueba el arranque y reintenta.")
    return m


def catalogo(db):
    snapshot = snapshot_actual(db)
    m = actual(db, snapshot).resultado
    canales = [dict(id=c.id, nombre=c.nombre, audiencias=sorted({s["audiencia"] for s in m["soporte"] if s["canal"] == c.id}))
               for c in db.scalars(select(Canal).where(Canal.id.in_(m["referencias"])).order_by(Canal.nombre))]
    publicos = {k: v for k, v in m.items() if k not in ("parametros", "draws")}
    return dict(modelo=publicos, canales=canales, perfiles=m["perfiles"], defecto=ParametrosPretest(),
        variantes=[v for p in m["perfiles"] for v in variantes_de(p)],
        formatos=["Cuadrado 1:1"], objetivos=["Consideración", "Captación"],
        audiencias=sorted(m["schema"]["niveles"]["audiencia"]),
        alcance="Estimación nacional con contexto del pretest. Los filtros globales seleccionan observaciones de la biblioteca; no reentrenan.")


def evaluar(db, entrada):
    db.execute(text("SELECT pg_advisory_xact_lock(260725)"))
    snapshot = snapshot_actual(db)
    modelo = actual(db, snapshot)
    m = modelo.resultado
    perfil = next((p for p in m["perfiles"] if p["categoria"] == entrada.categoria), None)
    if not perfil:
        raise HTTPException(422, "No hay perfil observado para la categoría elegida.")
    if not any(s["canal"] == entrada.canal and s["audiencia"] == entrada.audiencia for s in m["soporte"]):
        raise HTTPException(422, "Selecciona una audiencia observada en el canal elegido.")
    numero_filas = db.scalar(select(func.count()).select_from(CreatividadDiaria).where(CreatividadDiaria.snapshot_id == snapshot.id))
    if numero_filas != m["filas_observadas"]:
        raise HTTPException(409, "La cobertura creativa ha cambiado. Revisa la fuente antes de evaluar.")
    contexto = dict(perfil, canal=entrada.canal, audiencia=entrada.audiencia, frecuencia=entrada.frecuencia)
    try:
        referencia = predecir_contexto(m, contexto)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    referencia.update(clics_esperados=referencia["ctr"]*entrada.impresiones,
        clics_p05=referencia["p05"]*entrada.impresiones if referencia["p05"] is not None else None,
        clics_p95=referencia["p95"]*entrada.impresiones if referencia["p95"] is not None else None,
        cvr_observado=m["referencias"][entrada.canal]["cvr"],
        cvr_clics=m["referencias"][entrada.canal]["clics"],
        cvr_conversiones=m["referencias"][entrada.canal]["conversiones"])
    variantes = [dict(v,
        ctr_referencia=referencia["ctr"], p05=referencia["p05"], p95=referencia["p95"],
        clics_referencia=referencia["clics_esperados"], efecto_diferencial_identificado=False,
        multiplicador_demanda=1.0) for v in variantes_de(perfil)]
    motivos = referencia["motivos"]+["El histórico no permite distinguir estas composiciones: no hay un ganador predictivo."]
    ctr_es = f"{referencia['ctr']*100:.2f}".replace(".", ",")+" %"
    nombre_canal = db.get(Canal, entrada.canal).nombre
    resultado = dict(snapshot=snapshot.id, modelo=modelo.id, version=VERSION, semilla=m["semilla"],
        entradas=entrada.model_dump(), estado="bloqueado" if m["estado"] == "bloqueado" else "hipotesis",
        evidencia="Pretest estadístico de contexto; composiciones originales precreadas", ganador=None,
        motivos=motivos, referencia=referencia, variantes=variantes,
        brief=dict(metodo="Plantilla determinista basada en contexto y diagnóstico; sin generación IA en ejecución",
            objetivo=entrada.objetivo,
            texto=f"Explorar tres jerarquías visuales para {entrada.categoria} en {nombre_canal}, {entrada.audiencia}. Mantener el tono {perfil['tono'].lower()} y el CTA «{perfil['cta']}». La referencia contextual es {ctr_es} de CTR; validar la composición mediante una prueba aleatoria.",
            reglas=["Marca ficticia AUREL; producto reconocible y CTA legible, sin marcas de terceros.",
                "Mantener producto, CTA, tono y exposición comparables al contrastar composiciones.",
                "Las cifras son referencia del contexto; no atribuir diferencias a píxeles ni prometer ventas.",
                "La selección expresa una hipótesis. La respuesta económica permanece sin cambio hasta evidencia compatible."]),
        advertencias=m["advertencias"]+["Los activos son locales y precreados; el formulario no genera imágenes ni modifica sus textos.",
            "La referencia de clics es esperanza condicional, no un intervalo de conteos futuros."])
    pid = "pretest-"+hashlib.sha256(json.dumps(resultado, sort_keys=True).encode()).hexdigest()[:24]
    existente = db.get(PretestCreativo, pid)
    if not existente:
        db.add(PretestCreativo(id=pid, snapshot_id=snapshot.id, modelo_id=modelo.id, entradas=entrada.model_dump(), resultado=resultado))
        db.commit()
    return dict(id=pid, **resultado, reutilizada=existente is not None)


def consultar(db, pid):
    p = db.get(PretestCreativo, pid)
    if not p or p.snapshot_id != snapshot_actual(db).id:
        raise HTTPException(404, "La evaluación creativa no pertenece al snapshot activo.")
    return dict(id=p.id, **p.resultado, reutilizada=True)


def seleccion(db, sid, reutilizada=True):
    s = db.get(SeleccionCreativa, sid)
    if not s:
        raise HTTPException(404, "La selección creativa no existe.")
    p = consultar(db, s.pretest_id)
    return dict(id=s.id, pretest_id=s.pretest_id, variante_id=s.variante_id, snapshot=p["snapshot"], modelo=p["modelo"],
        evidencia="Hipótesis creativa guardada; sin activación de medios", multiplicador_demanda=1.0,
        efecto_identificado=False, motivo="La composición requiere validación experimental antes de aplicar un efecto económico.",
        reutilizada=reutilizada)


def seleccionar(db, entrada):
    db.execute(text("SELECT pg_advisory_xact_lock(260725)"))
    p = consultar(db, entrada.pretest_id)
    if entrada.variante_id not in {v["id"] for v in p["variantes"]}:
        raise HTTPException(422, "La variante no pertenece a la evaluación elegida.")
    sid = "sel-creativa-"+hashlib.sha256(f"{entrada.pretest_id}:{entrada.variante_id}".encode()).hexdigest()[:24]
    existe = db.get(SeleccionCreativa, sid) is not None
    if not existe:
        db.add(SeleccionCreativa(id=sid, pretest_id=entrada.pretest_id, variante_id=entrada.variante_id))
        db.commit()
    return seleccion(db, sid, existe)


def historial(db):
    snapshot = snapshot_actual(db)
    evaluaciones = db.scalars(select(PretestCreativo).where(PretestCreativo.snapshot_id == snapshot.id)
                             .order_by(PretestCreativo.creado.desc(), PretestCreativo.id).limit(10)).all()
    return dict(filas=[dict(id=p.id, entradas=p.entradas, modelo=p.modelo_id, fecha=p.creado.isoformat(),
        selecciones=[dict(id=s.id, variante_id=s.variante_id) for s in db.scalars(select(SeleccionCreativa)
            .where(SeleccionCreativa.pretest_id == p.id).order_by(SeleccionCreativa.creado.desc(), SeleccionCreativa.id))]) for p in evaluaciones])


if __name__ == "__main__":
    from app.persistencia.db import SessionLocal
    with SessionLocal.begin() as db:
        m = asegurar_creatividad(db, snapshot_actual(db))
        print(json.dumps(dict(modelo=m.id, version=m.version, estado=m.resultado["estado"], segundos=m.resultado["segundos_ajuste"])))
