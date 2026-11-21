# Cómo publicar una guía en Universo TERRA

Cada guía es **un archivo de texto** en esta carpeta. Un script lo convierte en la página de la web
con el diseño fijo, y a la vez actualiza el índice de Universo, el feed RSS y el sitemap.

## Pasos

1. Pon la imagen principal (JPG, PNG o WebP, idealmente horizontal de 1200 px o más) en `dist/universo/`.
2. Copia `_plantilla.md` con el nombre de la guía, por ejemplo `lavanda-en-maceta.md`.
   El nombre del archivo será la dirección: `/universo/lavanda-en-maceta.html`.
3. Rellena la cabecera y escribe el cuerpo.
4. Ejecuta desde la raíz del repositorio:

   ```
   python3 tools/publicar_universo.py
   ```

   Si falta un campo o una imagen, el script lo dice en español y no escribe nada.
5. Revisa la página en `dist/universo/` y sube los cambios.

Para comprobar sin escribir nada: `python3 tools/publicar_universo.py --comprobar`.

## Campos de la cabecera

| Campo | Obligatorio | Para qué sirve |
|---|---|---|
| `titulo` | sí | Título grande de la página y del RSS |
| `titulo_seo` | no | Título de la pestaña y de la vista previa. Por defecto «titulo \| Universo TERRA» |
| `descripcion` | sí | Meta descripción, vista previa en redes (Open Graph/Twitter) y RSS. Máximo 160 caracteres |
| `categoria` | sí | Etiqueta dorada sobre el título y categoría del RSS |
| `entradilla` | sí | Frase bajo el título |
| `fecha` | sí | Fecha de publicación, `AAAA-MM-DD`. Ordena el índice y el RSS (más reciente primero) |
| `revisado` | no | Fecha de la última revisión. Por defecto, la de publicación |
| `imagen` | sí | Archivo dentro de `dist/universo/`. Es la imagen de la vista previa en redes |
| `imagen_alt` | sí | Texto alternativo de la imagen |
| `pie_imagen` | sí | Pie bajo la imagen (recuerda indicar si es IA) |
| `tarjeta_titulo`, `tarjeta_texto` | sí | Tarjeta del índice de Universo |
| `sigue_explorando` | no | Lista de enlaces «Texto \| ruta» al final de la guía |
| `orden` | no | Desempata guías con la misma fecha (1 va primero) |
| `borrador` | no | `si` para que no se publique todavía |

## Formato del cuerpo

- `## Apartado` y `### Subapartado` para títulos (no uses `#` solo: el título va en la cabecera).
- Párrafos separados por una línea en blanco. `*cursiva*`, `**negrita**`, `[texto](url)`.
- Listas con `- ` o `1. `.
- Imagen suelta: `![texto alternativo](archivo.jpg "pie de foto")`.
- Desplegable:
  ```
  :::consejo ¿Pregunta?
  Respuesta.
  :::
  ```
- Galería deslizable (solo imágenes dentro):
  ```
  :::galeria
  ![alt](imagen1.jpg "pie")
  ![alt](imagen2.jpg "pie")
  :::
  ```

## Qué genera

- `dist/universo/<slug>.html` con Open Graph, Twitter Card, datos estructurados (BlogPosting y migas) y URL canónica.
- `dist/universo/index.html` con una tarjeta por guía.
- `dist/universo/feed.xml`: RSS 2.0 con imagen (`enclosure` y `media:content`) y el texto completo
  (`content:encoded`), pensado para Metricool, Make u otras automatizaciones.
- `dist/sitemap.xml`.

No edites a mano esos archivos generados: se sobrescriben. La dirección de la web está en
`tools/sitio.json` (`url_base`); al cambiar de dominio, cambia esa línea y vuelve a ejecutar el script.
