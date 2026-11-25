"""Exposiciones nuevas de una rama A/B. Nunca se añaden a ventas propias."""
import base64
import hashlib
import json
import zlib
from datetime import date, timedelta

import numpy as np

from app.datos.respuesta_creativa import CVR, ctr_base, promocion

VERSION_MUNDO_AB = "mundo-ab-1.0.0"


def efectos_visuales(contexto, variantes, semilla_mundo):
    # Efectos latentes modestos fijados antes de asignar, sin analizar píxeles.
    efectos = []
    for v in variantes:
        clave = json.dumps(dict(canal=contexto["canal"], categoria=contexto["categoria"],
            asset=v["asset"], version=v.get("version_recurso", "original")), sort_keys=True)
        codigo = int.from_bytes(hashlib.sha256(clave.encode()).digest()[:4], "little")
        rng = np.random.default_rng(np.random.SeedSequence([semilla_mundo, 4200, codigo]))
        efectos.append(float(np.clip(rng.normal(0, .12), -.25, .25)))
    return efectos


def ejecutar_mundo_ab(contexto, variantes, inicio, dias, impresiones, presupuesto_cent, semilla,
                      semilla_mundo, *, efectos_fixture=None):
    """Cada posición es una oportunidad independiente, con un único brazo y resultado.

    efectos_fixture solo sirve a pruebas explícitas; no existe en el contrato HTTP.
    """
    efectos = efectos_visuales(contexto, variantes, semilla_mundo) if efectos_fixture is None else efectos_fixture
    brazos = [v["id"] for v in variantes]
    categoria = ["hogar", "moda", "belleza"].index(contexto["categoria"])
    asignaciones, observaciones = [], []
    for d in range(dias):
        fecha = date.fromisoformat(inicio)+timedelta(days=d)
        n = impresiones//dias+(d < impresiones % dias)
        gasto = presupuesto_cent//dias+(d < presupuesto_cent % dias)
        rng_asignacion = np.random.default_rng(np.random.SeedSequence([semilla, 4201, d]))
        asignados = rng_asignacion.permutation(np.repeat(np.arange(len(brazos), dtype=np.uint8), n))
        rng_resultado = np.random.default_rng(np.random.SeedSequence([semilla, 4202, d]))
        tasas = np.clip(ctr_base(categoria, promocion(fecha))*np.exp(efectos), 1e-6, .99)
        clic = rng_resultado.random(len(asignados)) < tasas[asignados]
        conversion = clic & (rng_resultado.random(len(asignados)) < CVR)
        bruto = asignados.tobytes()
        asignaciones.append(dict(fecha=fecha.isoformat(), unidades=len(asignados),
            codificacion="zlib+base64; un byte por oportunidad, índice del brazo",
            datos=base64.b64encode(zlib.compress(bruto)).decode(), sha256=hashlib.sha256(bruto).hexdigest()))
        for i, brazo in enumerate(brazos):
            mascara = asignados == i
            observaciones.append(dict(fecha=fecha.isoformat(), brazo=brazo, impresiones=int(mascara.sum()),
                clics=int(clic[mascara].sum()), conversiones=int(conversion[mascara].sum()), gasto_cent=int(gasto)))
    return asignaciones, observaciones


def decodificar(asignacion):
    bruto = zlib.decompress(base64.b64decode(asignacion["datos"]))
    if len(bruto) != asignacion["unidades"] or hashlib.sha256(bruto).hexdigest() != asignacion["sha256"]:
        raise ValueError("Asignación comprimida incompleta o alterada.")
    return np.frombuffer(bruto, dtype=np.uint8)
