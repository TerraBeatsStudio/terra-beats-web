# Mejoras de marca, Universo TERRA, UX inmersiva y YouTube/RGPD — 2026-11-22

- Identidad visual: actualizado el logotipo oficial de TERRA BEATS (Nature & Ambient Music), carrusel interactivo de 4 paisajes con vista ampliada (lightbox), desplegables estilo cristal en «Respirar», halo cian/ámbar y botón flotante minimalista de onda acústica (`44×44 px`).
- Contenido editorial y SEO/GEO: ampliadas `polinizadores.html`, `meditacion-principiantes.md`, `huerto-urbano.md` y `romero.md`; añadidas `sonidos-lluvia-naturaleza-dormir.md`, `guardianes-de-iberia.md` y `transparencia.html`; esquema `FAQPage`, `alt` descriptivos y `<lastmod>` en `sitemap.xml`.
- Universo TERRA y UX interactiva: filtros dinámicos por temática (`?categoria=...`), buscador instantáneo en `/universo/`, guía destacada, tiempo de lectura, barra de progreso, índice rápido (`Contenido de esta guía`), tarjetas relacionadas, escaparate de 3 guías en portada y Modo «Pausa Inmersiva» en `#explorar`.
- Conexión YouTube y analítica RGPD: soporte opcional `youtube_id` (`youtube-nocookie.com`) en `tools/publicar_universo.py`, hueco para `cloudflare_analytics_token` en `tools/sitio.json` y apartado de analítica anónima sin cookies en `transparencia.html`.
- Vitrina «Guardianes de Iberia» (`contenido/universo/guardianes-de-iberia.md`): bloques estructurados `:::especie` con estado UICN por colores, hábitat, dato biológico y módulo visual de firma acústica (Hz).

# Publicación en GitHub Pages con terrabeatsstudio.com — 2026-11-21

- Workflow `.github/workflows/pages.yml` publica `dist/` en GitHub Pages en cada cambio de `main`; `comprobar.yml` verifica Universo en cada PR.
- `dist/CNAME` y todas las URL canónicas, Open Graph, RSS, sitemap y robots apuntan a `https://terrabeatsstudio.com`.
- Pasos de dominio y DNS en `PUBLICAR-WEB.md`. No fusionar hasta tener el dominio comprado y Pages activado.

# Universo TERRA listo para redes — 2026-11-21

- Las guías se escriben como archivos de texto en `contenido/universo/` y `tools/publicar_universo.py` genera la página con plantilla fija, el índice, `universo/feed.xml` (RSS) y `sitemap.xml`. Instrucciones en `contenido/universo/LEEME.md`.
- Cada guía tiene ahora URL canónica, Open Graph, Twitter Card y datos estructurados BlogPosting. La portada enlaza el feed RSS.
- Las 3 guías existentes pasan al nuevo formato sin cambios en su texto visible.
- Limitación: mientras la web sea privada, redes y Metricool no pueden leer el feed ni las vistas previas.

# TERRA BEATS — Interactive space

Updated: 2026-11-16. Existing Site and owner-only audience retained.

## Implemented
- Replaced repetitive presentation sections with a four-tab activity panel.
- Breathing: selectable 3/3, 4/4 and 4/6 second cycles, 1–3 minutes, start/pause/resume/reset, completion count.
- Sound: three generated filtered-noise textures, per-layer and master volume, presets, persistent stop control. Not field recordings. No paid API, autoplay or external media calls.
- Focus: 5/15/25 minute clock based on wall time, pause/resume/reset, optional end tone, optional intention.
- Observation: five sensory prompts, restart and completion.
- Six rotating exploration activities with local favorites.
- Preferences, intention, favorites and completed count stay in localStorage; clear-local-data control included.
- Responsive layout, keyboard-operable tabs and reduced-motion support.

## Validation
- JavaScript syntax check.
- Browser: breathing start/pause, audio start/stop state, focus start/pause/reset, sensory completion, favorites persisted after reload.
- Narrow viewport visual review. Audio browser pipeline initialized successfully; subjective sound quality needs Antonio's listening review.

## Limitations
- Browser storage is local to each device and origin. No cloud sync.
- Timers need the page open. Background audio notification depends on browser/device permissions and suspension.
- Site is still private. Domain chosen for later purchase: terrabeatsstudio.com; not purchased or configured.
