# TERRA BEATS Studio — web

Web estática servida tal cual desde `dist/` (GitHub Pages, dominio terrabeatsstudio.com).
No hay npm ni paso de compilación: se edita el HTML/CSS/JS de `dist/` directamente.
Todo en español. Objetivo: gastar pocos tokens, así que lee solo lo que la tarea necesite.

## Estructura
- `dist/` — la web publicada.
  - `index.html` portada (herramientas, experiencias), `faq.html`, `polinizadores.html`.
  - `terra/` — reproductor TERRA (`index.html`, `app.js`, `style.css`); se incrusta con `terra-embed.js`.
  - `universo/` — guías. **Los `.html`, `index.html` y `feed.xml` son generados**: no editarlos a mano.
  - `assets/` — imágenes, fuentes y logos (binarios).
- `contenido/universo/*.md` — fuente de las guías. Formato en `contenido/universo/LEEME.md`.
- `tools/publicar_universo.py` — genera Universo, feed y `dist/sitemap.xml`. Config en `tools/sitio.json`.
- `.github/workflows/` — `comprobar.yml` (en cada PR) y `pages.yml` (publica al fusionar en `main`).
- Docs: `PUBLICAR-WEB.md` (dominio y Pages), `BRAND-ASSETS.md` (origen de assets), `CHANGELOG.md`.

## Comandos
- Regenerar Universo: `python3 tools/publicar_universo.py`
- Comprobar que `dist/` está al día (lo mismo que la CI): `python3 tools/publicar_universo.py --comprobar`
- Vista previa local: `python3 -m http.server 8000 -d dist` y abrir http://localhost:8000
- Solo biblioteca estándar de Python 3.8+. No hay dependencias que instalar.

## Estilos: dos capas CSS
1. **Base**: `<style>` en línea dentro de cada página (variables `:root` claras, layout, pie de página).
2. **Marca**: hojas externas cargadas después, que sobrescriben la base.
   - `brand.css` (tema oscuro, `:root` de marca, fuentes Montserrat). Se enlaza con `?v=AAAAMMDD-N`:
     sube ese número al cambiarlo para romper la caché.
   - Complementos de la portada: `tools.css`, `experiencias.css`, `motion.css`.
   - Universo usa solo `universo/editorial.css`; TERRA usa `terra/style.css`.
- Los cambios de aspecto global van en `brand.css`, no en los `<style>` en línea.
- El CSS está minificado en pocas líneas muy largas: busca con `grep -o` y un selector concreto
  en vez de leer el archivo entero.

## Qué no hace falta leer
- `dist/assets/**`, `dist/universo/*.jpg`, `*.webp`, `*.ttf`, `OFL.txt` (binarios o licencia).
- `dist/universo/*.html`, `feed.xml`, `sitemap.xml`: salidas del script; cambia el `.md` y regenera.
- `.openai/` (configuración de otro hosting), `.git/`.
- `BRAND-ASSETS.md` y `CHANGELOG.md`, salvo que la tarea trate de assets o historial.
- `.claude/settings.json` bloquea la lectura de los binarios pesados.

## Reglas
- Si tocas `contenido/universo/` o `tools/sitio.json`, ejecuta el script y sube también `dist/`;
  si no, la CI falla.
- Las imágenes de paisaje son recreaciones con IA y así se indican en la web: no lo cambies.
- `dist/terra/config.js` va vacío: nunca metas claves.
