"""Generador estructural reproducible; no contiene resultados de estimadores.

Las plataformas observan atribución solapada. Los pedidos propios se generan
una sola vez. Búsqueda y creatividad reparten parte del gasto, nunca lo suman.
"""
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np

from app.datos.captura import estructura_mercados, probabilidades_captura

VERSION = "mundo-1.0.0"
SEMILLA = 260725
CORTE = date.fromisoformat(os.environ.get("DEMO_CORTE", "2026-10-31"))
CANALES = [
    ("sem_marca", "SEM marca", "captura", "#23806A"),
    ("sem_generico", "SEM genérico", "demanda", "#4279B0"),
    ("meta", "Meta", "demanda", "#8267A7"),
    ("tiktok", "TikTok", "demanda", "#B07C4D"),
    ("youtube", "YouTube", "demanda", "#647BA2"),
    ("display", "Display", "demanda", "#82918A"),
    ("tv", "TV", "demanda", "#48675B"),
    ("crm", "CRM", "demanda", "#A48A50"),
]


@dataclass
class Mundo:
    tablas: dict[str, list[dict]]
    manifiesto: dict
    verdad_evaluacion: dict


def repartir(total: int, pesos: np.ndarray) -> np.ndarray:
    """Mayor resto: céntimos exactos, desempate estable y sin importes negativos."""
    valores = np.asarray(pesos, dtype=float)
    if total < 0 or np.any(valores < 0) or not np.isfinite(valores).all() or valores.sum() <= 0:
        raise ValueError("Reparto no válido.")
    cuotas = total * valores / valores.sum()
    enteros = np.floor(cuotas).astype(np.int64)
    faltan = total - int(enteros.sum())
    orden = np.argsort(-(cuotas - enteros).ravel(), kind="stable")
    enteros.ravel()[orden[:faltan]] += 1
    return enteros


def checksum_logico(tablas: dict[str, list[dict]]) -> str:
    digest = hashlib.sha256()
    for nombre in sorted(tablas):
        digest.update(nombre.encode())
        # Orden canónico por grano, independiente del orden de inserción de SQL.
        claves = ("id",) if "id" in tablas[nombre][0] else tuple(
            k for k in ("snapshot_id", "fecha", "mercado_id", "canal_id", "campana_id",
                        "creativo_id", "grupo_id", "fuente") if k in tablas[nombre][0])
        for fila in sorted(tablas[nombre], key=lambda f: tuple(str(f[k]) for k in claves)):
            digest.update(json.dumps(fila, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"), default=str).encode())
            digest.update(b"\n")
    return digest.hexdigest()


def generar(semilla: int = SEMILLA, corte: date = CORTE) -> Mundo:
    streams = np.random.SeedSequence(semilla).spawn(5)
    estructura, medios_rng, negocio_rng, busqueda_rng, creativo_rng = [
        np.random.default_rng(s) for s in streams
    ]
    fechas = [corte - timedelta(days=729 - t) for t in range(730)]
    snapshot = f"aurel-{corte.isoformat()}-{semilla}-{VERSION}"
    regiones = ["Norte", "Centro", "Este", "Sur", "Oeste", "Insular"]
    tamanos, recuperacion = estructura_mercados(estructura)
    mercados = [dict(id=f"m{i+1:02}", nombre=f"{regiones[i//4]} · {i%4+1:02}",
                     region=regiones[i//4], tamano=round(float(tamanos[i]), 6),
                     grupo=f"estrato-{i%3+1}") for i in range(24)]
    canales = [dict(id=c[0], nombre=c[1], tipo=c[2], color=c[3]) for c in CANALES]
    campanas = [dict(id=f"cam-{j:03}-{k:02}", canal_id=c[0],
                     nombre=f"{c[1]} · {['Hogar', 'Moda', 'Belleza'][k%3]} · {k+1:02}",
                     categoria=["hogar", "moda", "belleza"][k%3], objetivo="Consideración" if j > 1 else "Captación",
                     inicio=fechas[0], fin=corte) for j, c in enumerate(CANALES) for k in range(15)]
    creativos = [dict(id=f"cre-{i+1:03}", campana_id=f"cam-{2+i%4:03}-{i%15:02}",
                      nombre=f"{['Objetos que perduran', 'Una pausa cotidiana', 'Esenciales de temporada', 'Tu próxima historia'][i%4]} · {i+1:02}",
                      asset=f"/assets/creatividad/aurel-{i%12+1:02}.svg", formato="Cuadrado 1:1",
                      atributos=dict(categoria=["hogar", "moda", "belleza"][i%3],
                                     tono=["Editorial", "Cercano", "Funcional"][i%3],
                                     cta=["Descubre la colección", "Hazlo tuyo", "Ver selección"][i%3],
                                     composicion="Producto y tipografía", audiencia=f"Cohorte {i%8+1:02}",
                                     reutilizacion=f"Composición {i%12+1:02}; variante de registro {i//12+1}"),
                      licencia="Original MARGIA · CC BY 4.0") for i in range(80)]
    grupos = [dict(id=f"q{i+1:02}", nombre=("Aurel" if i < 16 else "Aurel producto" if i < 32 else "Selección genérica") + f" · {i+1:02}",
                   intencion="Marca pura" if i < 16 else "Marca + producto" if i < 32 else "Genérica",
                   elegible=i < 32) for i in range(50)]

    tiempo = np.arange(730)
    estacional = 1 + 0.19*np.cos(2*np.pi*(tiempo-35)/365) + 0.09*np.sin(2*np.pi*tiempo/7)
    promocion = np.array([f.month == 11 and f.day >= 20 or f.month == 6 and f.day <= 12 for f in fechas])
    participacion = np.array([0.20, 0.16, 0.21, 0.08, 0.10, 0.07, 0.14, 0.04])
    pulsos = medios_rng.lognormal(0, 0.22, (105, 8))[tiempo//7]
    pesos = (estacional[:, None, None] * tamanos[None, :, None]
             * participacion[None, None, :] * pulsos[:, None, :]
             * medios_rng.uniform(.88, 1.12, (730, 24, 8)))
    gasto = np.zeros((730, 24, 8), dtype=np.int64)
    for bloque in (0, 365):
        gasto[bloque:bloque+365] = repartir(480_000_000, pesos[bloque:bloque+365])
    stock = np.zeros((24, 8))
    respuesta = np.zeros((730, 24))
    # SEM marca es captura; coeficiente de generación de demanda exactamente cero.
    coef = np.array([0, 9, 13, 5, 7, 3, 8, 4])
    escala = gasto.mean(axis=(0, 1)) / 100
    for t in range(730):
        stock = gasto[t] / 100 + .48*stock
        hill = stock / (stock + 2.1*escala)
        respuesta[t] = (hill*coef).sum(axis=1)*tamanos
    base = (32*estacional[:, None] + 7*promocion[:, None]
            + 2.5*tiempo[:, None]/730)*tamanos
    oportunidades = (base + respuesta) * .30
    p_paid, p_org, p_direct, p_loss = probabilidades_captura(gasto[:, :, 0], escala[0]*100, recuperacion[None, :])
    assert np.all(p_loss >= 0)
    media_pedidos = (base + respuesta)*.70 + oportunidades*(p_paid+p_org+p_direct)
    pedidos = negocio_rng.poisson(media_pedidos)
    aov = negocio_rng.normal(9200, 750, (730, 24)).clip(6000, 13000)
    ventas = np.rint(pedidos*aov).astype(np.int64)
    coste = np.rint(ventas*negocio_rng.uniform(.48, .57, (730, 24))).astype(np.int64)
    negocios, medios, campana_diaria, busquedas, creatividad = [], [], [], [], []
    conv = np.zeros((730, 24, 8), dtype=np.int64)
    atribucion = np.array([.26, .19, .24, .08, .07, .10, .09, .16])
    for t, fecha in enumerate(fechas):
        for m, mercado in enumerate(mercados):
            comun = dict(snapshot_id=snapshot, fecha=fecha, mercado_id=mercado["id"])
            negocios.append(dict(**comun, pedidos=int(pedidos[t, m]), ventas_cent=int(ventas[t, m]),
                                 coste_cent=int(coste[t, m]), margen_cent=int(ventas[t, m]-coste[t, m]),
                                 visitas=int(pedidos[t, m]*negocio_rng.uniform(22, 32)),
                                 promocion=bool(promocion[t]), demanda_proxy=round(float(base[t, m]+negocio_rng.normal(0, 2)), 4)))
            for j, c in enumerate(CANALES):
                euros = gasto[t, m, j]/100
                impresiones = None if c[0] == "tv" else int(euros*medios_rng.uniform(150, 240))
                clics = None if impresiones is None else int(impresiones*medios_rng.uniform(.008, .028))
                atribuidas = int(medios_rng.poisson(pedidos[t, m]*atribucion[j]))
                conv[t, m, j] = atribuidas
                medios.append(dict(**comun, canal_id=c[0], gasto_cent=int(gasto[t, m, j]),
                                   impresiones=impresiones, clics=clics, conversiones=atribuidas,
                                   ingresos_cent=int(round(atribuidas*aov[t, m]*medios_rng.uniform(.90, 1.10))),
                                   fuente="Panel sintético · atribución de plataforma", ventana_dias=7 if j != 6 else 28))
                if t >= 723:
                    for k, asignado in enumerate(repartir(int(gasto[t, m, j]), np.arange(1, 16))):
                        campana_diaria.append(dict(**comun, campana_id=f"cam-{j:03}-{k:02}", gasto_cent=int(asignado)))
            if t >= 702:
                asignaciones = {}
                for canal_idx, indices in ((0, range(32)), (1, range(32, 50))):
                    asignados = repartir(int(gasto[t, m, canal_idx]), np.ones(len(indices)))
                    for i, asignado in zip(indices, asignados, strict=True):
                        asignaciones[i] = int(asignado)
                for i, grupo in enumerate(grupos):
                    cuota = .30/32 if i < 32 else .70/18
                    demanda = max(20, int((base[t, m]+respuesta[t, m])*cuota*busqueda_rng.uniform(60, 100)))
                    for fuente in ("SEO", "SEM"):
                        impresiones = demanda
                        tasa = (.10+.12*recuperacion[m]) if fuente == "SEO" else .15
                        clics = int(busqueda_rng.binomial(impresiones, tasa))
                        busquedas.append(dict(**comun, grupo_id=grupo["id"], fuente=fuente,
                                              impresiones=impresiones, clics=clics,
                                              gasto_cent=asignaciones[i] if fuente == "SEM" else 0,
                                              conversiones=int(busqueda_rng.binomial(clics, .035)) if fuente == "SEM" else None,
                                              posicion=round(float(1.2+5*(1-recuperacion[m])+busqueda_rng.uniform(0, .8)), 2) if fuente == "SEO" else None,
                                              competencia=round(float(1-recuperacion[m]), 4)))
        if t >= 702:
            # Una sola plaza observada por activo/día; cobertura deliberadamente parcial.
            for i, creativo in enumerate(creativos):
                m = (i + t) % 24
                j = 2+i%4
                asignado = int(gasto[t, m, j] // 25)
                exposiciones = max(100, int(asignado/100*170))
                ctr = .012 + .002*(i%3-1) + .0015*promocion[t]
                clics = int(creativo_rng.binomial(exposiciones, ctr))
                creatividad.append(dict(snapshot_id=snapshot, fecha=fecha, mercado_id=mercados[m]["id"],
                                        creativo_id=creativo["id"], impresiones=exposiciones, clics=clics,
                                        conversiones=int(creativo_rng.binomial(clics, .035)),
                                        gasto_cent=asignado, frecuencia=round(float(creativo_rng.uniform(1.2, 4.5)), 2)))

    tablas = dict(mercado=mercados, canal=canales, campana=campanas, creativo=creativos,
                  grupo_busqueda=grupos, negocio_diario=negocios, medios_diarios=medios,
                  campana_diaria=campana_diaria, busqueda_diaria=busquedas,
                  creatividad_diaria=creatividad)
    manifiesto = dict(id=snapshot, version=VERSION, semilla=semilla, corte=corte.isoformat(),
                     inicio=fechas[0].isoformat(), checksum=checksum_logico(tablas),
                     conteos={k: len(v) for k, v in tablas.items()}, moneda="EUR", zona="Europe/Madrid",
                     gasto_bloque_365_eur=[int(gasto[:365].sum())/100, int(gasto[365:].sum())/100],
                     coberturas=dict(negocio=730, medios=730, busqueda=28, campanas=7,
                                     creatividad="28 días; mercados parciales por activo"),
                     evidencia="Observado sintético", licencia="Datos sintéticos originales · CC BY 4.0")
    verdad = dict(recuperacion=recuperacion.tolist(), coeficientes_demanda=coef.tolist(),
                  captura={"min_probabilidad": float(p_loss.min()), "max_error_masa": float(np.abs(p_paid+p_org+p_direct+p_loss-1).max())})
    return Mundo(tablas, manifiesto, verdad)
