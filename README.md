# IconGems

A free **resource site** (downloads happen right here — outbound links are a tiny end-of-page list): the complete **IP as Logo mascot library — 3,448 MIT-licensed mascot logos** ([ipaslogo.com](https://ipaslogo.com/)) with original 1254×1254 PNG one-click download, self-hosted 512px WebP previews and client-side ZIP batches — plus free search & download for 100,000+ open-source SVG icons from famous libraries (Google Material Symbols, Microsoft Fluent, Tabler, Lucide, Phosphor, Font Awesome, Bootstrap, Remix Icon, IconPark, Ionicons, Heroicons and more).

**Live: https://icongems.kuige.me/** · 中文：https://icongems.kuige.me/?lang=zh

## For designers / developers / PMs

- Mascot tab (default): browse/search 3,448 mascots by keyword or category, download original PNG / WebP per logo, ZIP any filtered batch — all on-page
- Icon tab: aggregated search across 200+ open-source sets via the Iconify API
- Click any icon: copy SVG / React / Vue / HTML / CSS, download SVG, render & download PNG
- Per-set browser, live icon counts, exact license badges
- Free illustration libraries stay as a compact, license-tagged link list at the end of the page

## For AI

- [`/llms.txt`](https://icongems.kuige.me/llms.txt) — agent-friendly site guide (llmstxt.org format): quick-start recipe, the mascot manifest endpoints, all 29 curated sets with licenses & prefixes, API reference
- [`/llms-full.txt`](https://icongems.kuige.me/llms-full.txt) — the complete guide with the full catalog inlined
- [`/data/catalog.json`](https://icongems.kuige.me/data/catalog.json) — machine-readable catalog (mascot library, sets, licenses, endpoints, page map)
- [`/data/ipas-logos.json`](https://icongems.kuige.me/data/ipas-logos.json) — full mascot manifest: `{key: [category, bg]}` for all 3,448 logos
- robots.txt explicitly welcomes AI crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended…)
- `Dataset` JSON-LD for structured discovery
- The whole fetch path (robots.txt → llms.txt → catalog/API) works without JavaScript

## Data pipeline

- `python3 scripts/ipas-data.py` — rebuild `data/ipas-logos.json` (categories & names derived from the source manifest; Supabase category API is unreachable from CN networks)
- `bash scripts/ipas-fetch.sh` — (re)fetch all 3,448 WebP previews into `ipas/display/` (~31 MB, self-hosted)
- `python3 scripts/gen-data.py` — regenerate catalog.json, llms.txt, llms-full.txt

## Tech

Single-file `index.html` (no build, no dependencies). Theme: auto/light/dark. Bilingual EN/ZH with `?lang=` deep links. Top-level tabs: Mascot Logos (default) ↔ Icon Search (`?tab=icons`). Mascot previews are self-hosted WebP; mascot originals stream from cdn.ipaslogo.com (open CORS) as blobs; ZIP batches are built in-browser (store method). Icon search & downloads fetch live from api.iconify.design (open CORS, no key).

Part of [kuige.me](https://kuige.me/) · KuiGe's free tool collection.
