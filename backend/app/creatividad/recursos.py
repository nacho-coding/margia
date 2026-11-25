"""Catálogo visual versionado. No cambia hechos ni estima efectos de imágenes nuevas."""
import json
import re
from pathlib import Path

MANIFIESTO = json.loads(Path(__file__).with_name("imagenes.json").read_text(encoding="utf-8"))
IMAGENES = {i["id"]: i for i in MANIFIESTO["imagenes"]}
VERSION_PRESENTACION = "composicion-2.0.0"
PLATAFORMAS = {
    "meta": dict(id="meta", nombre="Meta", ubicacion="Feed", relacion="4:5", ancho=1440, alto=1800,
        tratamiento="Fotografía editorial y mensaje de colección", tipo="Imagen de feed"),
    "tiktok": dict(id="tiktok", nombre="TikTok", ubicacion="In-feed vertical", relacion="9:16", ancho=1080, alto=1920,
        tratamiento="Gancho breve, producto en escena y espacio para la interfaz", tipo="Fotograma de ejemplo"),
    "display": dict(id="display", nombre="Display", ubicacion="Banner adaptable", relacion="1.91:1", ancho=1200, alto=628,
        tratamiento="Producto y mensaje separados, llamada a la acción visible", tipo="Maqueta de banner"),
    "youtube": dict(id="youtube", nombre="YouTube", ubicacion="In-stream horizontal", relacion="16:9", ancho=1920, alto=1080,
        tratamiento="Apertura panorámica con marca y promesa visual", tipo="Fotograma de apertura"),
}
ESCENAS = [
    ("espacio", "Producto en contexto", "Escena editorial con luz natural"),
    ("marco", "El material, de cerca", "Fotografía de producto y detalle de texturas"),
    ("detalle", "Una escena cotidiana", "Producto en uso y gesto natural"),
]
TEXTOS = {
    "hogar": ["Objetos que perduran.", "El arte de vivir despacio.", "Haz espacio para lo esencial."],
    "moda": ["Lo esencial te acompaña.", "El detalle se siente.", "Hecho para tus días."],
    "belleza": ["Tu pausa cotidiana.", "Sencillamente, cuidado.", "Un momento para ti."],
}
GANCHOS = {
    "hogar": ["Un rincón. Otra sensación.", "Mira de cerca.", "Así empieza un hogar."],
    "moda": ["Tu próximo esencial.", "La textura lo dice todo.", "Un gesto. Tu estilo."],
    "belleza": ["Tu ritual empieza aquí.", "Los pequeños detalles.", "Una pausa para cuidarte."],
}
ALTS = {
    "hogar": ["Jarrón verde con ramas de olivo sobre una consola de roble con luz de ventana",
        "Detalle de un jarrón cerámico verde sobre piedra clara", "Manos colocando ramas de olivo en un jarrón sobre una mesa de madera"],
    "moda": ["Persona adulta con camisa de lino arena y pantalón claro en un patio soleado",
        "Camisa de lino arena doblada sobre travertino con botones y textura visibles", "Manos ajustando el puño de una camisa de lino en una calle de piedra"],
    "belleza": ["Frasco cosmético de vidrio ámbar y caja clara sobre piedra junto a una toalla",
        "Frasco cuentagotas ámbar sobre piedra con una gota de agua", "Manos aplicando una gota cosmética junto a un frasco ámbar"],
}


def variantes_de(perfil, canal):
    categoria = perfil["categoria"]
    plataforma = PLATAFORMAS[canal]
    return [dict(id=f"{canal}-{categoria}-{vid}-v2", categoria=categoria, canal=canal,
        nombre=nombre, composicion=composicion, **{k: v for k, v in IMAGENES[f"{categoria}-{vid}"].items() if k != "id"},
        alt=ALTS[categoria][i]+". Imagen sintética.", tono=perfil["tono"], cta=perfil["cta"],
        plataforma=plataforma, version_recurso=MANIFIESTO["version"], version_presentacion=VERSION_PRESENTACION,
        texto=dict(antetitulo=f"Colección {categoria}", titular=(GANCHOS if canal == "tiktok" else TEXTOS)[categoria][i],
            apoyo="Una selección para tus días.", cta=perfil["cta"]),
        origen=MANIFIESTO["origen"], licencia="Recurso sintético MARGIA · Imagegen · CC BY 4.0")
        for i, (vid, nombre, composicion) in enumerate(ESCENAS)]


def vista_biblioteca(asset, categoria, canal, atributos):
    # Recreación ilustrativa: el identificador de composición histórica sigue intacto.
    numero = int(re.search(r"aurel-(\d+)\.svg$", asset).group(1))
    perfil = dict(categoria=categoria, tono=atributos["tono"], cta=atributos["cta"])
    return dict(variantes_de(perfil, canal)[((numero-1)//3) % 3],
        recreacion=True, asset_observado=asset,
        alcance="Recreación visual para la demo; las métricas corresponden al registro histórico, no a esta fotografía.")
