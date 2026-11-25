import copy

import pytest
from pydantic import ValidationError
from sqlalchemy import func, select

from app.api.consultas import snapshot_actual
from app.api.contratos import ParametrosSearch
from app.datos.historia_search import construir_historia
from app.dominio.economia import comparar_captura
from app.modelos.search import ajustar_search, respuesta_recorte
from app.modelos.search_servicio import filas_experimentales, search_actual
from app.persistencia.tablas import AsignacionExperimento, Experimento, ObservacionExperimento


def test_historia_reproducible_fk_aleatorizacion_y_mundo_conservado(mundo):
    assert mundo.manifiesto["checksum"] == "6715a0eb83a485c083b145e237a124a5923da2b742d119f415fda4b131780c9d"
    tablas = mundo.tablas
    gasto = [f for f in tablas["medios_diarios"] if f["canal_id"] == "sem_marca"]
    entradas = (tablas["negocio_diario"], gasto, tablas["mercado"], mundo.manifiesto["id"], 260725)
    historia = construir_historia(*entradas)
    assert historia == construir_historia(*entradas)
    experimentos, asignaciones, observaciones = historia
    assert len(experimentos) == 12 and len(asignaciones) == 288 and len(observaciones) == 576
    assert all(e["semilla"] == 260725 and e["protocolo"]["seed_sequence"] == [260725, 3100, i] for i, e in enumerate(experimentos))
    assert max(e["fin"] for e in experimentos).isoformat() < mundo.manifiesto["corte"]
    assert all(a["probabilidad"] == .5 for a in asignaciones)
    for e in experimentos:
        unidad = [a for a in asignaciones if a["experimento_id"] == e["id"]]
        assert sum(a["brazo"] == "tratamiento" for a in unidad) == 12
        for par in {a["par_id"] for a in unidad}:
            assert {a["brazo"] for a in unidad if a["par_id"] == par} == {"control", "tratamiento"}
    assert all(o["gasto_cent"] <= o["presupuesto_cent"] for o in observaciones)
    assert all("contrafactual" not in o for o in observaciones)
    assert construir_historia(*entradas[:-1], 1) != historia


def test_economia_base_delta_costes_comunes_y_sin_doble_ahorro():
    base = (10_000, 500_000, 100_000, 60_000, .5, -240)
    r = comparar_captura(*base, plataforma=6000)
    assert r["delta"] == pytest.approx(12_000)
    assert r["perdida_maxima_pedidos"] == pytest.approx(480)
    assert r["alternativa"]["contribucion"]-r["base"]["contribucion"] == pytest.approx(r["delta"])
    assert sum(p["importe"] for p in r["desglose"][:-1]) == pytest.approx(r["delta"])
    comun = comparar_captura(*base, plataforma=6000, plataforma_comun=True)
    assert comun["delta"] == pytest.approx(18_000)
    assert comparar_captura(100, 5000, 1000, 500, 0, 0)["delta"] == 0
    assert comparar_captura(100, 5000, 1000, 500, 0, 0, plataforma=600)["delta"] == -600
    assert comparar_captura(*base, experimento=100_000)["delta"] < 0
    with pytest.raises(ValueError):
        comparar_captura(10, 100, 100, 200, 1, 0)


def _fixture_pares(tasa):
    filas = []
    for i in range(12):
        for corte in (0, .25, .5, .75):
            ahorro = 4000*corte
            filas.append(dict(experimento=f"fixture-{corte}", par=f"p{i}", recorte=corte, estrato=f"e{i%3}",
                pre_t=2000, pre_c=2000, post_t=2000+tasa*ahorro, post_c=2000, ahorro=ahorro))
    return filas


@pytest.mark.parametrize("tasa", [0, -.01, -.1])
def test_estimador_nulo_negativo_y_semilla(tasa):
    datos = _fixture_pares(tasa)
    modelo = ajustar_search(datos, 1)
    assert modelo["tasas"] == pytest.approx([tasa]*3)
    assert modelo == ajustar_search(datos, 1)
    assert modelo["recuperacion"] is None
    assert respuesta_recorte(modelo, 0)[0] == 0
    assert respuesta_recorte(modelo, .5)[0] == pytest.approx(tasa)
    assert modelo["placebo"]["ic95"] == [0, 0]
    with pytest.raises(ValueError):
        ajustar_search(datos+datos[:1], 1)
    with pytest.raises(ValueError):
        respuesta_recorte(modelo, 1.1)


def test_modelo_real_toma_observaciones_y_replicas_por_unidad(db):
    snapshot = snapshot_actual(db)
    datos, experimentos = filas_experimentales(db, snapshot)
    modelo = search_actual(db, snapshot).resultado
    assert len(datos) == 144 and len(experimentos) == 12
    nuevo = ajustar_search(datos, snapshot.semilla)
    assert nuevo["tasas"] == modelo["tasas"]
    assert nuevo["draws"] == modelo["draws"]
    assert modelo["pares"] == 12
    assert all(i["p05"] < i["p95"] for i in modelo["intervalos"])
    assert db.scalar(select(func.count()).select_from(Experimento)) == 12
    assert db.scalar(select(func.count()).select_from(AsignacionExperimento)) == 288
    assert db.scalar(select(func.count()).select_from(ObservacionExperimento)) == 576
    insuficiente = [f for f in datos if f["par"] in ("par-01", "par-02")]
    with pytest.raises(ValueError):
        ajustar_search(insuficiente, 1)
    alterado = copy.deepcopy(datos)
    for f in alterado:
        if f["recorte"] == 0:
            f["post_t"] += 500
    assert ajustar_search(alterado, 1)["estado"] == "bloqueado"


@pytest.mark.parametrize("datos", [{"recorte_pct": -1}, {"recorte_pct": 101},
    {"cuota_plataforma": -1}, {"cuota_plataforma": float("nan")}, {"coste_experimento": float("inf")}, {"r": .92}])
def test_validacion_inputs(datos):
    with pytest.raises(ValidationError):
        ParametrosSearch(**datos)


def test_api_simulador_radar_reproducible_guardado_y_abstencion(client):
    evidencia = client.get("/api/v1/busqueda/evidencia").json()
    modelo = evidencia["modelo"]
    assert len(evidencia["serie"]) == 28 and modelo["recuperacion"] is None
    assert len(modelo["grupos"]) == 32
    assert len(modelo["historicos"]) == 12
    historico = client.get("/api/v1/busqueda/historicos/"+modelo["historicos"][0]["id"]).json()
    assert len(historico["observaciones"]) == 48
    assert len(historico["asignaciones"]) == 24
    uri = "/api/v1/busqueda/simular"
    inputs = dict(recorte_pct=50, hipotesis=modelo["hipotesis"])
    primero = client.post(uri, json=inputs)
    assert primero.status_code == 200, primero.text
    a = primero.json()
    b = client.post(uri, json=inputs).json()
    assert a["id"] == b["id"] and b["reutilizada"]
    assert a["resultado"] == b["resultado"]
    assert client.get("/api/v1/busqueda/simulaciones/"+a["id"]).json()["resultado"] == a["resultado"]
    r = a["resultado"]
    radar = client.get("/api/v1/oportunidades").json()
    assert radar["filas"][0]["id"] == modelo["hipotesis"]
    assert radar["filas"][0]["impacto"] == r["delta"]
    assert r["delta"] == pytest.approx(r["ahorro"]+r["cambio_margen"]-r["costes_incrementales"])
    assert r["banda"]["p05"] < r["banda"]["p95"] and 0 <= r["banda"]["probabilidad_perdida"] <= 1
    assert client.post(uri, json={"recorte_pct": 0}).json()["resultado"]["delta"] == 0
    completo = client.post(uri, json={"recorte_pct": 100}).json()["resultado"]
    assert completo["extrapolado"] and completo["estado"] == "hipotesis"
    caro = client.post(uri, json={"recorte_pct": 50, "cuota_plataforma": 100000}).json()["resultado"]
    assert caro["delta"] < 0 and caro["banda"]["probabilidad_perdida"] == 1
    assert "Mantener" in caro["recomendacion"]
    local = client.post(uri+"?mercado=m01", json=inputs).json()["resultado"]
    assert local["estado"] == "hipotesis" and local["motivos"]
    assert client.post(uri, json={"recorte_pct": 101}).status_code == 422
    assert client.post(uri, json={"hipotesis": "inventada"}).status_code == 404
    assert client.get("/api/v1/busqueda/simulaciones/inventada").status_code == 404
