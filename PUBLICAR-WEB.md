# Publicar la web en GitHub Pages con terrabeatsstudio.com

La web es estática (`dist/`), así que GitHub Pages la sirve gratis. Cada cambio que entra en `principal`
dispara `.github/workflows/pages.yml`, que comprueba que Universo está regenerado y publica `dist/`.

## 1. Requisito de GitHub

GitHub Pages es gratis solo en **repositorios públicos**. Para un repositorio privado hace falta un
plan de pago (GitHub Pro o superior). Elige una de las dos opciones antes de activar Pages.
El repositorio no contiene claves secretas (`dist/terra/config.js` está vacío).

## 2. Comprar el dominio

Compra `terrabeatsstudio.com` en el registrador que elijas (Cloudflare Registrar o Porkbun).
Activa la privacidad WHOIS (gratis en ambos) y la renovación automática.

## 3. Activar Pages en GitHub

1. Repositorio → **Settings → Pages**.
2. En *Build and deployment → Source* elige **GitHub Actions**.
3. En *Custom domain* escribe `terrabeatsstudio.com` y guarda.
4. Recomendado: en **Settings (de tu cuenta) → Pages → Add a domain**, verifica el dominio
   para que nadie más pueda usarlo en GitHub (te pide un registro TXT).

## 4. Registros DNS (en el panel del registrador)

| Tipo | Nombre | Valor |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| AAAA | @ | 2606:50c0:8000::153 |
| AAAA | @ | 2606:50c0:8001::153 |
| AAAA | @ | 2606:50c0:8002::153 |
| AAAA | @ | 2606:50c0:8003::153 |
| CNAME | www | terrabeatsstudio.github.io |

En Cloudflare, deja estos registros en modo **«Solo DNS» (nube gris)** para que GitHub pueda emitir
el certificado HTTPS.

## 5. Últimos pasos

1. Espera a que Settings → Pages diga que el DNS es correcto (de minutos a 24 h).
2. Marca **Enforce HTTPS**.
3. Fusiona el PR. El workflow publica la web en `https://terrabeatsstudio.com`.
4. Google Search Console: añade la propiedad del nuevo dominio y envía `https://terrabeatsstudio.com/sitemap.xml`.
   La etiqueta de verificación actual de la portada era para la dirección antigua.

## Si cambia el dominio

Cambia `url_base` en `tools/sitio.json`, sustituye la dirección en `dist/index.html`, `dist/faq.html`,
`dist/polinizadores.html`, `dist/robots.txt` y `dist/CNAME`, y ejecuta `python3 tools/publicar_universo.py`.
