#!/usr/bin/env python3
"""Genera las guías de Universo TERRA a partir de archivos de texto.

Lee cada archivo `contenido/universo/<slug>.md` y escribe en `dist/`:
  - universo/<slug>.html  (página con la plantilla fija y metadatos Open Graph/Twitter/JSON-LD)
  - universo/index.html   (índice con una tarjeta por guía)
  - universo/feed.xml     (feed RSS 2.0 con imagen y texto completo)
  - sitemap.xml           (páginas fijas + guías)

Uso:
  python3 tools/publicar_universo.py              # genera los archivos
  python3 tools/publicar_universo.py --comprobar  # solo comprueba que dist/ está al día

Solo usa la biblioteca estándar de Python 3.8+. El formato de los archivos de
texto está explicado en contenido/universo/LEEME.md.
"""
import argparse
import html
import json
import re
import sys
from datetime import date, datetime, time, timezone
from email.utils import format_datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONTENIDO = RAIZ / "contenido" / "universo"
DIST = RAIZ / "dist"
SALIDA = DIST / "universo"
CONFIG = json.loads((RAIZ / "tools" / "sitio.json").read_text(encoding="utf-8"))
BASE = CONFIG["url_base"].rstrip("/")

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
OBLIGATORIOS = ["titulo", "descripcion", "categoria", "entradilla", "fecha",
                "imagen", "imagen_alt", "pie_imagen", "tarjeta_titulo", "tarjeta_texto"]
TIPOS_IMAGEN = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}


class ErrorContenido(Exception):
    pass


def esc(texto):
    return html.escape(str(texto), quote=True)


def fecha_larga(d):
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def leer_fecha(valor, campo, archivo):
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise ErrorContenido(f"{archivo}: «{campo}» debe tener el formato AAAA-MM-DD (por ejemplo 2026-11-19).")


# ---------------------------------------------------------------- lectura

def leer_articulo(ruta):
    texto = ruta.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not texto.startswith("---\n"):
        raise ErrorContenido(f"{ruta.name}: debe empezar con una cabecera entre líneas «---».")
    try:
        cabecera, cuerpo = texto[4:].split("\n---\n", 1)
    except ValueError:
        raise ErrorContenido(f"{ruta.name}: falta la línea «---» que cierra la cabecera.")

    datos, clave_lista = {}, None
    for n, linea in enumerate(cabecera.split("\n"), start=2):
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        if linea.startswith((" ", "\t")) and linea.strip().startswith("- ") and clave_lista:
            datos[clave_lista].append(linea.strip()[2:].strip())
            continue
        if ":" not in linea:
            raise ErrorContenido(f"{ruta.name}, línea {n}: se esperaba «campo: valor».")
        clave, valor = linea.split(":", 1)
        clave, valor = clave.strip(), valor.strip()
        if valor == "":
            datos[clave], clave_lista = [], clave
        else:
            datos[clave], clave_lista = valor, None

    faltan = [c for c in OBLIGATORIOS if not datos.get(c)]
    if faltan:
        raise ErrorContenido(f"{ruta.name}: faltan los campos {', '.join(faltan)}.")

    art = dict(datos)
    art["slug"] = ruta.stem
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", art["slug"]):
        raise ErrorContenido(f"{ruta.name}: el nombre del archivo solo puede llevar minúsculas, números y guiones.")
    art["fecha"] = leer_fecha(datos["fecha"], "fecha", ruta.name)
    art["revisado"] = leer_fecha(datos["revisado"], "revisado", ruta.name) if datos.get("revisado") else art["fecha"]
    art["orden"] = int(datos.get("orden", 100))
    art["borrador"] = str(datos.get("borrador", "no")).lower() in ("si", "sí", "true", "yes")
    art.setdefault("titulo_seo", f"{datos['titulo']} | {CONFIG['nombre_seccion']}")
    enlaces = []
    for item in datos.get("sigue_explorando", []) or []:
        if "|" not in item:
            raise ErrorContenido(f"{ruta.name}: cada enlace de «sigue_explorando» va como «Texto | /ruta».")
        txt, url = (p.strip() for p in item.split("|", 1))
        enlaces.append((txt, url))
    art["sigue_explorando"] = enlaces

    imagen = SALIDA / art["imagen"]
    if not imagen.is_file():
        raise ErrorContenido(f"{ruta.name}: no encuentro la imagen dist/universo/{art['imagen']}.")
    if imagen.suffix.lower() not in TIPOS_IMAGEN:
        raise ErrorContenido(f"{ruta.name}: la imagen debe ser .jpg, .png o .webp.")
    art["imagen_bytes"] = imagen.stat().st_size
    art["imagen_tipo"] = TIPOS_IMAGEN[imagen.suffix.lower()]
    art["imagen_tam"] = medir_imagen(imagen)

    art["cuerpo_html"] = markdown_a_html(cuerpo, ruta.name)
    return art


def medir_imagen(ruta):
    """Devuelve (ancho, alto) de un JPEG o PNG, o None si no se puede leer."""
    datos = ruta.read_bytes()
    if datos[:8] == b"\x89PNG\r\n\x1a\n":
        return int.from_bytes(datos[16:20], "big"), int.from_bytes(datos[20:24], "big")
    if datos[:2] == b"\xff\xd8":
        i = 2
        while i < len(datos) - 9:
            if datos[i] != 0xFF:
                i += 1
                continue
            marca = datos[i + 1]
            if marca in (0xC0, 0xC1, 0xC2):
                return int.from_bytes(datos[i + 7:i + 9], "big"), int.from_bytes(datos[i + 5:i + 7], "big")
            i += 2 + int.from_bytes(datos[i + 2:i + 4], "big")
    return None


# ---------------------------------------------------------------- markdown sencillo

def en_linea(texto):
    t = esc(texto)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    return t


RE_IMAGEN = re.compile(r'^!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)$')


def figura(linea):
    m = RE_IMAGEN.match(linea.strip())
    alt, src, pie = m.group(1), m.group(2), m.group(3)
    pie_html = f"<figcaption>{en_linea(pie)}</figcaption>" if pie else ""
    return f'<figure><img src="{esc(src)}" alt="{esc(alt)}" loading="lazy">{pie_html}</figure>'


RE_YOUTUBE_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")


def bloque_youtube(video_id, dentro, archivo):
    """Tarjeta de vídeo sin iframe: no carga nada de YouTube hasta que la persona hace clic.

    :::youtube ID_DE_11_CARACTERES
    ![alt](portada.jpg "Texto del botón")
    :::
    Con «PENDIENTE» en lugar del ID enlaza al canal (útil mientras el vídeo no está subido).
    """
    if len(dentro) != 1 or not RE_IMAGEN.match(dentro[0].strip()):
        raise ErrorContenido(f"{archivo}: «:::youtube» lleva dentro una sola imagen ![alt](portada.jpg \"texto\").")
    if video_id == "PENDIENTE":
        url = next((p for p in CONFIG["perfiles"] if "youtube" in p), "https://www.youtube.com/")
    elif RE_YOUTUBE_ID.match(video_id):
        url = f"https://www.youtube.com/watch?v={video_id}"
    else:
        raise ErrorContenido(f"{archivo}: «{video_id}» no es un ID de YouTube (11 caracteres) ni PENDIENTE.")
    m = RE_IMAGEN.match(dentro[0].strip())
    alt, src, texto = m.group(1), m.group(2), m.group(3) or "Ver en YouTube"
    return (f'<figure class="video"><a href="{esc(url)}" target="_blank" rel="noopener">'
            f'<img src="{esc(src)}" alt="{esc(alt)}" loading="lazy"></a>'
            f'<figcaption><a href="{esc(url)}" target="_blank" rel="noopener">▶ {en_linea(texto)}</a></figcaption></figure>')


def markdown_a_html(texto, archivo):
    lineas = texto.strip("\n").split("\n")
    partes, i = [], 0
    while i < len(lineas):
        linea = lineas[i]
        quitada = linea.strip()
        if not quitada:
            i += 1
            continue
        # Bloques especiales :::consejo / :::galeria ... :::
        if quitada.startswith(":::"):
            tipo, _, titulo = quitada[3:].partition(" ")
            fin = next((j for j in range(i + 1, len(lineas)) if lineas[j].strip() == ":::"), None)
            if fin is None:
                raise ErrorContenido(f"{archivo}: el bloque «:::{tipo}» no tiene un «:::» de cierre.")
            dentro = [l for l in lineas[i + 1:fin] if l.strip()]
            if tipo == "consejo":
                cuerpo = "".join(f"<p>{en_linea(l.strip())}</p>" for l in dentro)
                partes.append(f'<details class="tip"><summary>{en_linea(titulo.strip() or "Un consejo")}</summary>{cuerpo}</details>')
            elif tipo == "galeria":
                malas = [l for l in dentro if not RE_IMAGEN.match(l.strip())]
                if malas:
                    raise ErrorContenido(f"{archivo}: dentro de «:::galeria» solo van imágenes ![alt](archivo \"pie\").")
                figs = "".join(figura(l) for l in dentro)
                partes.append(f'<div class="gallery" tabindex="0" aria-label="Galería desplazable de {len(dentro)} imágenes">{figs}</div>')
            elif tipo == "youtube":
                partes.append(bloque_youtube(titulo.strip(), dentro, archivo))
            else:
                raise ErrorContenido(f"{archivo}: bloque desconocido «:::{tipo}» (usa consejo, galeria o youtube).")
            i = fin + 1
            continue
        if quitada.startswith("### "):
            partes.append(f"<h3>{en_linea(quitada[4:])}</h3>")
            i += 1
            continue
        if quitada.startswith("## "):
            partes.append(f"<h2>{en_linea(quitada[3:])}</h2>")
            i += 1
            continue
        if quitada.startswith("# "):
            raise ErrorContenido(f"{archivo}: no uses «# » en el cuerpo; el título va en la cabecera. Usa «## ».")
        if RE_IMAGEN.match(quitada):
            partes.append(figura(quitada))
            i += 1
            continue
        if quitada.startswith(("- ", "* ")):
            items = []
            while i < len(lineas) and lineas[i].strip().startswith(("- ", "* ")):
                items.append(f"<li>{en_linea(lineas[i].strip()[2:])}</li>")
                i += 1
            partes.append(f"<ul>{''.join(items)}</ul>")
            continue
        if re.match(r"^\d+\. ", quitada):
            items = []
            while i < len(lineas) and re.match(r"^\d+\. ", lineas[i].strip()):
                items.append(f"<li>{en_linea(lineas[i].strip().split(' ', 1)[1])}</li>")
                i += 1
            partes.append(f"<ol>{''.join(items)}</ol>")
            continue
        # Párrafo: líneas seguidas hasta una línea vacía o un bloque nuevo
        trozos = []
        while i < len(lineas) and lineas[i].strip() and not re.match(r"^(#{1,3} |- |\* |\d+\. |:::|!\[)", lineas[i].strip()):
            trozos.append(lineas[i].strip())
            i += 1
        partes.append(f"<p>{en_linea(' '.join(trozos))}</p>")
    return "".join(partes)


# ---------------------------------------------------------------- plantillas

def url_absoluta(ruta):
    return ruta if ruta.startswith("http") else f"{BASE}{ruta}"


def cabecera_comun(titulo, descripcion, canonica, imagen_url, imagen_alt, tipo_og, extra_meta="", json_ld=None, tam=None):
    tam_meta = ""
    if tam:
        tam_meta = f'<meta property="og:image:width" content="{tam[0]}"><meta property="og:image:height" content="{tam[1]}">'
    ld = f'<script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False)}</script>' if json_ld else ""
    return (
        '<!doctype html><html lang="es"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="description" content="{esc(descripcion)}">'
        f"<title>{esc(titulo)}</title>"
        f'<link rel="canonical" href="{canonica}">'
        f'<link rel="alternate" type="application/rss+xml" title="{esc(CONFIG["nombre_seccion"])}" href="{BASE}/universo/feed.xml">'
        '<meta name="theme-color" content="#07131f">'
        f'<link rel="icon" type="image/svg+xml" href="{CONFIG["logo"]}">'
        '<meta name="robots" content="index,follow,max-image-preview:large">'
        f'<meta property="og:type" content="{tipo_og}">'
        f'<meta property="og:locale" content="{CONFIG["locale_og"]}">'
        f'<meta property="og:site_name" content="{esc(CONFIG["nombre_sitio"])}">'
        f'<meta property="og:title" content="{esc(titulo)}">'
        f'<meta property="og:description" content="{esc(descripcion)}">'
        f'<meta property="og:url" content="{canonica}">'
        f'<meta property="og:image" content="{imagen_url}">'
        f"{tam_meta}"
        f'<meta property="og:image:alt" content="{esc(imagen_alt)}">'
        f"{extra_meta}"
        '<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:title" content="{esc(titulo)}">'
        f'<meta name="twitter:description" content="{esc(descripcion)}">'
        f'<meta name="twitter:image" content="{imagen_url}">'
        f'<meta name="twitter:image:alt" content="{esc(imagen_alt)}">'
        f"{ld}"
        '<link rel="stylesheet" href="editorial.css"></head><body>'
        '<header class="top"><a href="/" aria-label="Volver al inicio de TERRA BEATS">'
        f'<img src="{CONFIG["logo"]}" alt="TERRA BEATS Studio"></a>'
        '<nav aria-label="Navegación"><a href="/">Inicio</a><a href="/universo/">Universo TERRA</a></nav></header>'
    )


PIE = ('<footer class="foot">TERRA BEATS · Naturaleza, sonido y presencia · Naturaleza que se siente</footer>'
       '<script src="/terra-embed.js" defer></script></body></html>\n')


def momento(d):
    return datetime.combine(d, time(9, 0), tzinfo=timezone.utc)


def pagina_articulo(art):
    canonica = f"{BASE}/universo/{art['slug']}.html"
    imagen_url = f"{BASE}/universo/{art['imagen']}"
    publicado, revisado = art["fecha"].isoformat(), art["revisado"].isoformat()
    org_id = f"{BASE}/#organization"
    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BlogPosting",
                "@id": f"{canonica}#articulo",
                "headline": art["titulo"],
                "description": art["descripcion"],
                "image": {"@type": "ImageObject", "url": imagen_url, "caption": art["imagen_alt"]},
                "datePublished": publicado,
                "dateModified": revisado,
                "inLanguage": CONFIG["idioma"],
                "articleSection": art["categoria"],
                "mainEntityOfPage": canonica,
                "author": {"@id": org_id},
                "publisher": {"@type": "Organization", "@id": org_id, "name": CONFIG["nombre_sitio"],
                              "logo": {"@type": "ImageObject", "url": url_absoluta(CONFIG["logo"])},
                              "sameAs": CONFIG["perfiles"]},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{BASE}/"},
                    {"@type": "ListItem", "position": 2, "name": CONFIG["nombre_seccion"], "item": f"{BASE}/universo/"},
                    {"@type": "ListItem", "position": 3, "name": art["titulo"], "item": canonica},
                ],
            },
        ],
    }
    extra = (f'<meta property="article:published_time" content="{publicado}">'
             f'<meta property="article:modified_time" content="{revisado}">'
             f'<meta property="article:section" content="{esc(art["categoria"])}">')
    enlaces = art["sigue_explorando"] or [("Todas las guías", "/universo/")]
    enlaces_html = "".join(f'<a href="{esc(u)}">{esc(t)}</a>' for t, u in enlaces)
    return (
        cabecera_comun(art["titulo_seo"], art["descripcion"], canonica, imagen_url, art["imagen_alt"],
                       "article", extra, json_ld, art["imagen_tam"])
        + '<main class="wrap"><article class="article"><div class="hero">'
        f'<span class="tag">{esc(art["categoria"])}</span>'
        f"<h1>{esc(art['titulo'])}</h1>"
        f'<p class="lead">{en_linea(art["entradilla"])}</p>'
        f'<p class="notice">Revisado el <time datetime="{revisado}">{fecha_larga(art["revisado"])}</time></p></div>'
        f'<figure><img src="{esc(art["imagen"])}" alt="{esc(art["imagen_alt"])}">'
        f'<figcaption>{en_linea(art["pie_imagen"])}</figcaption></figure>'
        f"{art['cuerpo_html']}"
        f'<div class="links"><strong>Sigue explorando</strong><br>{enlaces_html}</div>'
        "</article></main>" + PIE
    )


def pagina_indice(articulos):
    ind = CONFIG["indice"]
    canonica = f"{BASE}/universo/"
    imagen_url = f"{BASE}/universo/{ind['imagen']}"
    json_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "@id": f"{canonica}#coleccion",
        "url": canonica,
        "name": ind["titulo_seo"],
        "description": ind["descripcion"],
        "inLanguage": CONFIG["idioma"],
        "hasPart": [{"@type": "BlogPosting", "headline": a["titulo"], "url": f"{BASE}/universo/{a['slug']}.html"}
                    for a in articulos],
    }
    tarjetas = "".join(
        '<article class="card">'
        f'<img src="{esc(a["imagen"])}" alt="" loading="lazy"><div class="card-body">'
        f'<span class="tag">{esc(a["categoria"])}</span><h2>{esc(a["tarjeta_titulo"])}</h2>'
        f'<p>{en_linea(a["tarjeta_texto"])}</p><a href="{a["slug"]}.html">Leer la guía</a></div></article>'
        for a in articulos
    )
    return (
        cabecera_comun(ind["titulo_seo"], ind["descripcion"], canonica, imagen_url, ind["imagen_alt"],
                       "website", json_ld=json_ld, tam=medir_imagen(SALIDA / ind["imagen"]))
        + '<main class="wrap"><div class="hero">'
        f'<span class="tag">{esc(ind["etiqueta"])}</span><h1>{esc(ind["titulo"])}</h1>'
        f'<p class="lead">{esc(ind["entradilla"])}</p><p class="notice">{esc(ind["aviso"])}</p></div>'
        f'<h2>Empieza a descubrir</h2><div class="grid">{tarjetas}</div>'
        f'<p class="notice">{esc(ind["aviso_final"])}</p></main>' + PIE
    )


def feed_rss(articulos):
    ind = CONFIG["indice"]
    ultima = max((a["revisado"] for a in articulos), default=date(2026, 1, 1))
    items = []
    for a in articulos:
        url = f"{BASE}/universo/{a['slug']}.html"
        img = f"{BASE}/universo/{a['imagen']}"
        contenido = (f'<p><img src="{img}" alt="{esc(a["imagen_alt"])}"></p>'
                     f'<p>{en_linea(a["entradilla"])}</p>{a["cuerpo_html"]}')
        contenido = re.sub(r'(src|href)="(?!https?:|/|#|mailto:)([^"]+)"',
                           lambda m: f'{m.group(1)}="{BASE}/universo/{m.group(2)}"', contenido)
        contenido = re.sub(r'(src|href)="/(?!/)', f'\\1="{BASE}/', contenido)
        items.append(
            "<item>"
            f"<title>{esc(a['titulo'])}</title>"
            f"<link>{url}</link>"
            f'<guid isPermaLink="true">{url}</guid>'
            f"<pubDate>{format_datetime(momento(a['fecha']))}</pubDate>"
            f"<category>{esc(a['categoria'])}</category>"
            f"<description>{esc(a['descripcion'])}</description>"
            f"<content:encoded><![CDATA[{contenido}]]></content:encoded>"
            f'<enclosure url="{img}" length="{a["imagen_bytes"]}" type="{a["imagen_tipo"]}"/>'
            f'<media:content url="{img}" medium="image" type="{a["imagen_tipo"]}"/>'
            "</item>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" '
        'xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:media="http://search.yahoo.com/mrss/">'
        "<channel>"
        f"<title>{esc(CONFIG['nombre_seccion'])} · {esc(CONFIG['nombre_sitio'])}</title>"
        f"<link>{BASE}/universo/</link>"
        f"<description>{esc(ind['descripcion'])}</description>"
        f"<language>{CONFIG['idioma']}</language>"
        f"<lastBuildDate>{format_datetime(momento(ultima))}</lastBuildDate>"
        f'<atom:link href="{BASE}/universo/feed.xml" rel="self" type="application/rss+xml"/>'
        f"<image><url>{BASE}/universo/{ind['imagen']}</url><title>{esc(CONFIG['nombre_seccion'])}</title>"
        f"<link>{BASE}/universo/</link></image>"
        + "".join(items)
        + "</channel></rss>\n"
    )


def sitemap(articulos):
    urls = [(f"{BASE}{p}", None) for p in CONFIG["paginas_fijas"]]
    ultima = max((a["revisado"] for a in articulos), default=None)
    urls.append((f"{BASE}/universo/", ultima))
    urls += [(f"{BASE}/universo/{a['slug']}.html", a["revisado"]) for a in articulos]
    cuerpo = "".join(
        f"<url><loc>{u}</loc>" + (f"<lastmod>{d.isoformat()}</lastmod>" if d else "") + "</url>"
        for u, d in urls
    )
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{cuerpo}</urlset>\n')


# ---------------------------------------------------------------- principal

def generar():
    archivos = sorted(p for p in CONTENIDO.glob("*.md") if p.name.upper() != "LEEME.MD" and not p.name.startswith("_"))
    articulos, avisos = [], []
    for ruta in archivos:
        art = leer_articulo(ruta)
        if art["borrador"]:
            avisos.append(f"{ruta.name}: es un borrador, no se publica.")
            continue
        if len(art["descripcion"]) > 160:
            avisos.append(f"{ruta.name}: la descripción tiene {len(art['descripcion'])} caracteres; mejor 160 o menos.")
        articulos.append(art)
    articulos.sort(key=lambda a: (-a["fecha"].toordinal(), a["orden"], a["slug"]))

    salidas = {SALIDA / f"{a['slug']}.html": pagina_articulo(a) for a in articulos}
    salidas[SALIDA / "index.html"] = pagina_indice(articulos)
    salidas[SALIDA / "feed.xml"] = feed_rss(articulos)
    salidas[DIST / "sitemap.xml"] = sitemap(articulos)

    sueltos = {p for p in SALIDA.glob("*.html")} - set(salidas)
    for p in sorted(sueltos):
        avisos.append(f"dist/universo/{p.name} no tiene archivo de texto en contenido/universo/; revísalo.")
    return salidas, avisos


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--comprobar", action="store_true", help="no escribe nada; falla si dist/ no está al día")
    args = parser.parse_args()
    try:
        salidas, avisos = generar()
    except ErrorContenido as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    for a in avisos:
        print(f"Aviso: {a}")

    desfasados = [p for p, t in salidas.items() if not p.exists() or p.read_text(encoding="utf-8") != t]
    if args.comprobar:
        for p in desfasados:
            print(f"Desfasado: {p.relative_to(RAIZ)}")
        print("Todo al día." if not desfasados else "Ejecuta python3 tools/publicar_universo.py")
        return 1 if desfasados else 0
    for p in desfasados:
        p.write_text(salidas[p], encoding="utf-8")
        print(f"Escrito: {p.relative_to(RAIZ)}")
    print(f"Listo: {len(salidas) - 3} guías, índice, feed RSS y sitemap.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
