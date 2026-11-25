from sqlalchemy import func, select

from app.datos.seed import inicializar
from app.persistencia.tablas import NegocioDiario, Snapshot


def test_salud_contexto_y_seed_idempotente(client, db):
    assert client.get("/api/v1/health").json()["base_datos"] == "PostgreSQL"
    contexto = client.get("/api/v1/contexto").json()
    assert contexto["evidencia"] == "Observado sintético"
    assert len(contexto["mercados"]) == 24
    assert inicializar()["accion"] == "conservado"
    assert db.scalar(select(func.count()).select_from(Snapshot)) == 1


def test_kpis_fuente_unica_filtros_y_reconciliacion(client, db):
    globales = client.get("/api/v1/kpis?dias=28").json()
    metricas = {m["id"]: m for m in globales["metricas"]}
    assert metricas["contribucion"]["valor"] == metricas["margen"]["valor"]-metricas["inversion"]["valor"]
    assert sum(c["inversion"] for c in globales["canales"]) == metricas["inversion"]["valor"]
    assert sum(d["pedidos"] for d in globales["serie"]) == metricas["pedidos"]["valor"]
    assert len(globales["serie"]) == 28
    local = client.get("/api/v1/kpis?dias=28&mercado=m01").json()
    assert local["metricas"][0]["valor"] < globales["metricas"][0]["valor"]
    assert client.get("/api/v1/kpis?dias=30").status_code == 422
    assert client.get("/api/v1/kpis?mercado=m99").status_code == 422
    assert "Parámetros" in client.get("/api/v1/kpis?dias=0").json()["detail"]
    assert db.scalar(select(func.count()).select_from(NegocioDiario)) == 17520


def test_vistas_paginacion_y_cobertura(client):
    busca = client.get("/api/v1/busqueda?intencion=Marca%20pura&pagina=2").json()
    assert busca["total"] == 16 and busca["pagina"] == 2
    assert all(f["intencion"] == "Marca pura" for f in busca["filas"])
    assert client.get("/api/v1/busqueda?orden=sql").status_code == 422
    creatividad = client.get("/api/v1/creativos?canal=meta&pagina=100").json()
    assert creatividad["pagina"] == creatividad["paginas"]
    assert creatividad["total"] == 20
    assert all(f["canal"] == "Meta" for f in creatividad["filas"])
    assert "parcial" in creatividad["cobertura"]
    assert client.get("/api/v1/creativos?categoria=sin-datos").status_code == 422


def test_fiabilidad_exportacion_y_reset_protegido(client):
    calidad = client.get("/api/v1/fiabilidad").json()
    assert calidad["estado"] == "limitado"
    assert calidad["reglas"][0]["valor"] == 100
    assert calidad["reglas"][1]["valor"] == 0
    assert client.get("/api/v1/decisiones").json()["filas"] == []
    exportacion = client.get("/api/v1/exportar/negocio.csv?mercado=m01")
    assert exportacion.status_code == 200
    assert len(exportacion.text.splitlines()) == 29
    assert "Observado sintético" in exportacion.text
    assert client.post("/api/v1/demo/reset", json={"confirmacion": "si"}).status_code == 422
    assert client.get("/api/v1/demo/manifiesto").json()["checksum"] == calidad["checksum"]
