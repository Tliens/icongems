# IconGems

Free search & download for 100,000+ open-source SVG icons from famous libraries — Google Material Symbols, Microsoft Fluent, Tabler, Lucide, Phosphor, Font Awesome, Bootstrap, Remix Icon, IconPark (ByteDance), Ionicons, Heroicons and more — plus a curated, license-verified directory of free illustration libraries (unDraw, Open Peeps, Humaaans, DiceBear…).

**Live: https://icongems.kuige.me/** · 中文：https://icongems.kuige.me/?lang=zh

## For designers / developers / PMs

- Aggregated search across 200+ open-source sets via the Iconify API
- Click any icon: copy SVG / React / Vue / HTML / CSS, download SVG, render & download PNG
- Per-set browser, live icon counts, exact license badges
- Curated illustration library directory with license summaries

## For AI

- [`/llms.txt`](https://icongems.kuige.me/llms.txt) — agent-friendly site guide
- [`/data/catalog.json`](https://icongems.kuige.me/data/catalog.json) — full machine-readable catalog (sets, licenses, endpoints)
- Iconify API cheatsheet with open CORS — same endpoints the page itself uses

## Tech

Single-file `index.html` (no build, no dependencies). Theme: auto/light/dark. Bilingual EN/ZH with `?lang=` deep links. Search results and downloads are fetched live from api.iconify.design (open CORS, no key); curated counts fall back to bundled data. Codename: **螭吻 (Chiwen)** — the ninth dragon son who swallows everything and spits it back as one library.

Part of [kuige.me](https://kuige.me/) · KuiGe's free tool collection.
