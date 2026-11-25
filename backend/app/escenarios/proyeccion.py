"""Referencia nacional estacional observable; sin parámetros del mundo ni futuros."""
import numpy as np


def proyectar_base(semanas, fin_train):
    y = np.array([s["pedidos"] for s in semanas], dtype=float)
    if len(y) < 100 or not 60 <= fin_train <= len(y)-16 or np.any(y <= 0) or not np.isfinite(y).all():
        raise ValueError("La proyección requiere dos años, reserva temporal y pedidos positivos.")
    # Cuatro semanas del mismo tramo de hace 52 semanas, con nivel reciente fijo.
    nivel = float(y[-4:].sum()/y[-56:-52].sum())
    futuro = y[len(y)-52:len(y)-48]*nivel
    errores = []
    for t in range(56, fin_train):
        ratio = y[t-4:t].sum()/y[t-56:t-52].sum()
        errores.append(float(y[t]-y[t-52]*ratio))
    centrados = np.array(errores)-np.mean(errores)
    bloques_error = centrados[(np.arange(len(centrados))[:, None]+np.arange(4)) % len(centrados)].sum(axis=1)
    bajo, alto = np.quantile(bloques_error, [.05, .95])
    reservados = []
    for t in range(fin_train, len(y)-3, 4):
        naive = float(y[t-52:t-48].sum())
        predicho = float(naive*y[t-4:t].sum()/y[t-56:t-52].sum())
        observado = float(y[t:t+4].sum())
        reservados.append(dict(inicio=semanas[t]["inicio"], fin=semanas[t+3]["fin"],
            observado=observado, predicho=predicho, naive=naive,
            p05=float(predicho+bajo), p95=float(predicho+alto), dentro=bool(predicho+bajo <= observado <= predicho+alto)))
    observado = np.array([r["observado"] for r in reservados])
    def metricas(campo):
        error = np.array([r[campo] for r in reservados])-observado
        return dict(mae=float(np.abs(error).mean()), wape=float(np.abs(error).sum()/observado.sum()),
            sesgo=float(error.sum()/observado.sum()))
    return dict(pedidos=float(futuro.sum()), perfil_semanal=futuro.tolist(), nivel_reciente=nivel,
        errores_centrados=centrados.tolist(), estado="limitado",
        fin_errores=semanas[fin_train-1]["fin"], semanas_errores=len(errores),
        validacion=dict(bloques=len(reservados), modelo=metricas("predicho"), naive=metricas("naive"),
            fraccion_dentro_banda=float(np.mean([r["dentro"] for r in reservados])), filas=reservados,
            metodo="Bloques sucesivos de 28 días reservados; el nivel de cada origen solo usa sus cuatro semanas anteriores"),
        metodo="Referencia estacional a 52 semanas con ratio de nivel de las cuatro semanas recientes",
        supuestos=["Horizonte nacional de 28 días; patrón estacional observado, sin anticipar campañas nuevas.",
            "Ticket, margen por pedido y perfil de gasto se fijan desde los últimos 28 días.",
            "Errores históricos de un paso calculados antes del holdout, centrados y remuestreados en bloques de cuatro semanas.",
            "Pocos bloques reservados: el diagnóstico es descriptivo, no una calibración independiente de cobertura.",
            "Bandas de escenarios condicionales; no garantizan cobertura de pedidos futuros."])


def ruido_comun(base, semilla, replicas):
    errores = np.array(base["errores_centrados"])
    rng = np.random.default_rng(np.random.SeedSequence([semilla, 5103]))
    inicios = rng.integers(0, len(errores), size=replicas)
    indices = (inicios[:, None]+np.arange(4)) % len(errores)
    return errores[indices].sum(axis=1), indices
