"""Orquestador de deltas agregados. Solo recibe observaciones y modelos guardados."""
import hashlib
import json

import numpy as np

from app.dominio.economia import comparar_plan, waterfall
from app.escenarios.proyeccion import proyectar_base, ruido_comun
from app.modelos.mmm import CONTROLES, adstock, hill
from app.modelos.search import respuesta_recorte

VERSION_ESCENARIOS = "escenarios-1.0.0"
REPLICAS = 200


def huella(valor):
    return hashlib.sha256(json.dumps(valor, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def banda(valores):
    a = np.asarray(valores, dtype=float)
    if not np.isfinite(a).all():
        raise ValueError("La distribución contiene valores no finitos.")
    p05, p50, p95 = np.quantile(a, [.05, .5, .95])
    return dict(media=float(a.mean()), p05=float(p05), p50=float(p50), p95=float(p95))


def soportes(semanas, mmm):
    perfiles = {c: [float(s["gasto"][c]) for s in semanas[-4:]] for c in semanas[-1]["gasto"]}
    limites = []
    for c in mmm["curvas"]:
        perfil = np.array(perfiles[c["id"]])
        if np.any(perfil <= 0):
            raise ValueError("Falta un perfil semanal positivo para el soporte de inversión.")
        # El total solo es admisible si TODAS las semanas mantienen su soporte.
        total = float(perfil.sum())
        minimo = float(np.ceil(total*np.max(c["minimo"]/perfil)*100-1e-6)/100)
        maximo = float(np.floor(total*np.min(c["maximo"]/perfil)*100+1e-6)/100)
        limites.append(dict(canal=c["id"], nombre=c["nombre"], color=c["color"], actual=total,
            minimo=min(total, minimo, maximo), maximo=max(total, minimo, maximo),
            soporte_minimo=minimo, soporte_maximo=maximo, actual_fuera_soporte=not minimo <= total <= maximo,
            semanal_minimo=c["minimo"], semanal_maximo=c["maximo"]))
    return perfiles, limites


class MotorEscenarios:
    def __init__(self, semanas, mmm, search, referencia, entradas, creatividad=None):
        self.semanas, self.mmm, self.search = semanas, mmm, search
        self.ref, self.e, self.creatividad = referencia, entradas, creatividad
        self.canales = list(mmm["parametros"]["canales"])
        if "sem_marca" in self.canales or len(set(self.canales)) != len(self.canales):
            raise ValueError("La captura SEM marca no puede figurar entre los canales de demanda.")
        self.perfiles, self.soporte = soportes(semanas, mmm)
        self.presupuestos = {c: float(sum(p)) for c, p in self.perfiles.items()}
        if abs(sum(self.presupuestos.values())-referencia["inversion"]) > .011:
            raise ValueError("La inversión de referencia no reconcilia con sus canales.")
        fin_train = next((i+1 for i, s in enumerate(semanas) if s["fin"] == mmm["train_fin"]), 0)
        self.base = proyectar_base(semanas, fin_train)
        if referencia["pedidos"] <= 0:
            raise ValueError("Faltan pedidos de referencia para fijar ticket y margen.")
        self.aov = referencia["ventas"]/referencia["pedidos"]
        self.margen_pedido = referencia["margen"]/referencia["pedidos"]
        ruido, indices_proceso = ruido_comun(self.base, entradas["semilla"], REPLICAS)
        self.n_draws = self.base["pedidos"]+ruido
        if np.any(self.n_draws <= 0):
            raise ValueError("La referencia produce escenarios de pedidos no positivos; revisar la proyección.")
        p = mmm["parametros"]
        self.escala = np.array(p["escala_gasto"])
        self.persistencia, self.k = p["persistencia"], p["k"]
        observado = np.array([[s["gasto"][c] for c in self.canales] for s in semanas])
        self.stock_inicial = adstock(observado/self.escala, self.persistencia)[-1]
        self.carga_base = self.cargas(self.presupuestos)
        coef = np.array(p["bootstrap_coeficientes"])
        if coef.ndim != 2 or coef.shape[1] != len(CONTROLES)+len(self.canales) or not np.isfinite(coef).all():
            raise ValueError("Artefacto MMM incompatible con las curvas y sus réplicas.")
        rng_mmm = np.random.default_rng(np.random.SeedSequence([entradas["semilla"], 5101]))
        rng_search = np.random.default_rng(np.random.SeedSequence([entradas["semilla"], 5102]))
        idx_mmm = rng_mmm.integers(0, len(coef), size=REPLICAS)
        self.idx_search = rng_search.integers(0, len(search["draws"]), size=REPLICAS)
        self.betas = coef[idx_mmm, len(CONTROLES):]
        self.beta = np.array(p["coeficientes"])[len(CONTROLES):]
        self.traza = dict(replicas=REPLICAS, substreams=[5101, 5102, 5103],
            indices_mmm=idx_mmm.tolist(), indices_search=self.idx_search.tolist(), indices_proceso=indices_proceso.tolist(),
            stock_inicial=self.stock_inicial.tolist())
        self.traza["checksum"] = huella(self.traza)

    def cargas(self, presupuestos):
        stock = self.stock_inicial.copy()
        cargas = np.zeros(len(self.canales))
        for t in range(4):
            gasto = np.array([self.perfiles[c][t]*presupuestos[c]/sum(self.perfiles[c]) for c in self.canales])
            stock = gasto/self.escala+self.persistencia*stock
            cargas += hill(stock, self.k)
        return cargas

    def restricciones(self, presupuestos, recorte):
        motivos = []
        if sum(presupuestos.values()) > self.e["presupuesto_total"]+1e-6:
            motivos.append("La inversión supera el techo total de medios.")
        if recorte*100 > self.e["recorte_max_pct"]+1e-8:
            motivos.append("El recorte supera el máximo permitido.")
        for limite in self.e["limites"]:
            gasto = presupuestos[limite["canal"]]
            if not limite["minimo"]-1e-6 <= gasto <= limite["maximo"]+1e-6:
                motivos.append(f"{limite['canal']}: inversión fuera de sus límites.")
        for limite in self.soporte:
            cambiado = abs(presupuestos[limite["canal"]]-self.presupuestos[limite["canal"]]) > 1e-6
            if cambiado and not limite["soporte_minimo"]-1e-6 <= presupuestos[limite["canal"]] <= limite["soporte_maximo"]+1e-6:
                motivos.append(f"{limite['canal']}: alguna semana queda fuera del soporte observado.")
        return motivos

    def evaluar(self, nombre, recorte, fraccion=0., canal=None, *, base=False, lanzar_creatividad=False):
        ahorro = self.presupuestos["sem_marca"]*recorte
        reinversion = ahorro*fraccion
        presupuestos = dict(self.presupuestos)
        presupuestos["sem_marca"] -= ahorro
        if reinversion:
            if canal not in self.canales:
                raise ValueError("La reinversión solo puede destinarse a un canal de demanda.")
            presupuestos[canal] += reinversion
        cargas = self.cargas(presupuestos)-self.carga_base
        delta_demanda = float(cargas @ self.beta)
        demanda_draws = self.betas @ cargas
        tasa, draws_search = respuesta_recorte(self.search, recorte)
        delta_captura = ahorro*tasa
        captura_draws = ahorro*draws_search[self.idx_search]
        delta_n = delta_demanda+delta_captura
        delta_draws = demanda_draws+captura_draws
        activa = bool(lanzar_creatividad and self.creatividad and canal == self.creatividad["canal"])
        produccion = self.e["coste_produccion"] if activa else 0.
        plataforma = self.e["cuota_plataforma"] if not base or self.e["plataforma_comun"] else 0.

        def valorar(n, dn):
            return comparar_plan(float(n), float(n)*self.margen_pedido, self.ref["inversion"], float(dn), ahorro, reinversion,
                ventas=float(n)*self.aov, creatividad=produccion,
                experimento=self.e["coste_experimento"] if not base else 0., plataforma=plataforma,
                plataforma_comun=True if base else self.e["plataforma_comun"], otros=self.e["otros_costes"] if not base else 0.)

        punto = valorar(self.base["pedidos"], delta_n)
        draws = [valorar(n, dn) for n, dn in zip(self.n_draws, delta_draws, strict=True)]
        deltas = [r["delta"] for r in draws]
        riesgo = float(np.mean(np.array(deltas) < -1e-8))
        restricciones = self.restricciones(presupuestos, recorte)
        motivos = []
        if recorte:
            motivos += self.search["motivos"]
            if self.search["estado"] == "bloqueado":
                motivos.append("La evidencia Search está bloqueada.")
            if not self.search["soporte"][0] <= recorte <= self.search["soporte"][-1]:
                motivos.append("Recorte fuera del soporte experimental Search.")
        if reinversion and (self.mmm["estado"] == "bloqueado" or not self.mmm["optimizable"]):
            motivos.append("La reinversión depende de un MMM no habilitado para asignar inversión.")
            motivos += self.mmm["motivos"]
        if riesgo > self.e["riesgo_max_pct"]/100+1e-12:
            motivos.append("La probabilidad de pérdida supera el límite de riesgo.")
        limites = {k: banda([r["alternativa"][k] for r in draws]) for k in ("pedidos", "ventas", "margen", "contribucion")}
        limites["delta"] = dict(**banda(deltas), probabilidad_perdida=riesgo)
        return dict(nombre=nombre, recorte_pct=recorte*100, reinversion_pct=fraccion*100, canal=canal,
            presupuestos=presupuestos, metricas=punto["alternativa"], delta=punto["delta"],
            delta_pedidos=delta_n, delta_demanda=delta_demanda, delta_captura=delta_captura,
            ahorro_bruto=ahorro, reinversion=reinversion, ahorro_conservado=ahorro-reinversion,
            coste_incremental=punto["costes_incrementales"], bandas=limites,
            factible=not restricciones, restricciones=restricciones, motivos=sorted(set(motivos)),
            elegible=not restricciones and not motivos and riesgo <= self.e["riesgo_max_pct"]/100+1e-12,
            creatividad=self.creatividad if activa else None, multiplicador_demanda=1.,
            desglose=waterfall([("Ahorro SEM marca", ahorro), ("Reinversión en demanda", -reinversion),
                ("Cambio de margen", punto["cambio_margen"]), ("Costes incrementales", -punto["costes_incrementales"])], punto["delta"]),
            draws=[dict(indice=i, base=r["base"], alternativa=r["alternativa"], delta=r["delta"],
                delta_demanda=float(demanda_draws[i]), delta_captura=float(captura_draws[i])) for i, r in enumerate(draws)])

    def optimizar(self, base):
        demanda_habilitada = self.mmm["estado"] != "bloqueado" and self.mmm["optimizable"]
        recortes = sorted({c for c in [*self.search["soporte"], self.e["recorte_pct"]/100]
            if 0 < c <= self.e["recorte_max_pct"]/100 and self.search["soporte"][0] <= c <= self.search["soporte"][-1]})
        fracciones = sorted({.25, .5, .75, 1., self.e["reinversion_pct"]/100}-{0.}) if demanda_habilitada else []
        candidatos = [(0., 0., None)]+[(c, 0., None) for c in recortes]
        candidatos += [(r, f, c) for r in recortes for f in fracciones for c in self.canales]
        mejor, auditoria = None, []
        for recorte, fraccion, canal in candidatos:
            try:
                p = base if recorte == 0 else self.evaluar("Alternativa de la rejilla", recorte, fraccion, canal,
                    lanzar_creatividad=bool(fraccion))
            except ValueError as error:
                auditoria.append(dict(recorte_pct=recorte*100, reinversion_pct=fraccion*100, canal=canal,
                    factible=False, elegible=False, motivo=str(error)))
                continue
            auditoria.append(dict(recorte_pct=recorte*100, reinversion_pct=fraccion*100, canal=canal,
                factible=p["factible"], elegible=p["elegible"], media_delta=p["bandas"]["delta"]["media"],
                riesgo=p["bandas"]["delta"]["probabilidad_perdida"], motivos=p["restricciones"]+p["motivos"]))
            if p["elegible"] and (mejor is None or p["bandas"]["delta"]["media"] > mejor["bandas"]["delta"]["media"]+1e-8):
                mejor = p
        if mejor:
            mantener = mejor["recorte_pct"] == 0
            recomendacion = "Mantener la estrategia actual" if mantener else "Contrastar la alternativa de ahorro" if not mejor["reinversion"] else "Contrastar la reinversión propuesta"
            motivo = "Ninguna alternativa elegible mejora mantener dentro del riesgo permitido." if mantener else "Mayor contribución esperada entre los candidatos elegibles de esta rejilla; requiere validar transporte."
            estado = "limitado" if not demanda_habilitada else "evaluado"
        else:
            recomendacion, motivo, estado = "Revisar las restricciones", "Ningún candidato de la rejilla cumple simultáneamente límites, evidencia y riesgo. La base se conserva como referencia, no como solución factible.", "sin_candidato"
        return dict(estado=estado, recomendacion=recomendacion, motivo=motivo, mejor=mejor,
            demanda_habilitada=bool(demanda_habilitada), candidatos=len(candidatos),
            factibles=sum(a["factible"] for a in auditoria), elegibles=sum(a["elegible"] for a in auditoria),
            metodo="Rejilla determinista de recortes, fracciones de ahorro y un canal de destino cada vez; sin promesa de óptimo global",
            limite="Reinversión excluida por el diagnóstico MMM; búsqueda limitada a mantener y ahorro Search." if not demanda_habilitada else "Solo se compara la rejilla; no se exploran repartos simultáneos entre varios canales.",
            auditoria=auditoria)

    def ejecutar(self):
        base = self.evaluar("Base · mantener", 0., base=True)
        recorte = self.e["recorte_pct"]/100
        ahorro = self.evaluar("A · conservar ahorro", recorte)
        reinversion = self.evaluar("B · reinvertir", recorte, self.e["reinversion_pct"]/100,
            self.e["canal_reinversion"], lanzar_creatividad=True)
        return dict(base=base, ahorro=ahorro, reinversion=reinversion, optimizacion=self.optimizar(base),
            proyeccion={k: v for k, v in self.base.items() if k != "errores_centrados"},
            referencia=self.ref, replicas=REPLICAS, traza_draws=self.traza,
            metodo="Deltas agregados de demanda y captura separados, valorados por el comparador económico común",
            advertencias=["Demanda de siete canales MMM y captura SEM marca se separan; SEM no se suma como generador de pedidos.",
                "Se fija el perfil de captura al valorar demanda y el nivel base al valorar Search: interacción demanda/captura no identificada.",
                "Parámetros MMM conjuntos remuestreados de sus refits; Search conserva su vector de intensidades por réplica. Independencia entre familias no estimada.",
                "Mismas réplicas y perturbación aditiva de proceso en base/A/B y toda la rejilla. Ese ruido común se cancela en el delta; no se modela ruido específico de cada política.",
                "P05/p50/p95 son escenarios condicionales, no IC causales ni garantías de cobertura. Ticket y margen por pedido fijos.",
                "El aprendizaje CTR no identifica pedidos propios: multiplicador de demanda 1; producción se imputa una sola vez.",
                "La proyección y los deltas exigen estabilidad temporal; ninguna propuesta activa publicidad ni registra aprobación."])
