# IconGems

A free **resource site where every asset lives on this domain** (P0 归巢 + P1, 2026-10): the complete **IP as Logo mascot library — 3,448 MIT-licensed mascot logos** with **self-hosted 1024px WebP originals**, an **Avatar Studio** (31 DiceBear styles, client-side generation, shareable `?avatar=<style>:<seed>` links), **self-hosted illustrations** (3D Icons CC0 + illlustrations.co MIT, 250 files), and **fully self-hosted snapshots of 131,000+ open-source SVG icons** from 29 famous libraries — local search, hash-chunked SVG data, cross-category batch tray with client-side ZIP. **Zero third-party asset requests at runtime.**

**Live: https://icongems.kuige.me/** · 中文：https://icongems.kuige.me/?lang=zh

## For designers / developers / PMs

- Mascot tab (default): browse/search 3,448 mascots by keyword or category, download self-hosted 1024px WebP or browser-converted PNG, ZIP any filtered batch — all on-page
- Icon tab: search 131,000+ icons **locally** (name index downloaded once, results in milliseconds), filter by library
- Click any icon: copy SVG / React / Vue / HTML / CSS, download SVG, render & download PNG (64–512px)
- Per-set browser with categories, snapshot counts, exact license badges
- Illustrations tab: 250 self-hosted files (3D Icons color/clay variants + illlustrations PNG/SVG) with pack filters, per-variant download, and ZIP batches; a compact license-tagged off-site list remains at the end of the page
- Avatar Studio: 31 styles × unlimited seeds, background colors, SVG/PNG download, share links — all rendered locally by vendored DiceBear ESM (`vendor/dicebear/`, MIT/CC0/CC-BY styles listed in catalog)

## For AI

- [`/llms.txt`](https://icongems.kuige.me/llms.txt) — agent-friendly site guide: local endpoints, the hash-chunk recipe (djb2-utf8 mod K), all 29 sets with licenses
- [`/llms-full.txt`](https://icongems.kuige.me/llms-full.txt) — the complete guide with the full catalog inlined
- [`/data/icon-index.json`](https://icongems.kuige.me/data/icon-index.json) — all icon names grouped by prefix + chunk layout
- [`/icons/<prefix>.<k>.json`](https://icongems.kuige.me/icons/lucide.0.json) — SVG bodies per hash chunk (aliases materialized)
- [`/data/catalog.json`](https://icongems.kuige.me/data/catalog.json) — machine-readable catalog (sets, licenses, chunk layout, endpoints)
- [`/data/ipas-logos.json`](https://icongems.kuige.me/data/ipas-logos.json) — full mascot manifest
- [`/data/illus.json`](https://icongems.kuige.me/data/illus.json) — illustration manifest (250 items, categories, variants)
- robots.txt explicitly welcomes AI crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended…)
- The whole fetch path (robots.txt → llms.txt → index → chunks) works without JavaScript and without leaving this domain

## Data pipeline

- `python3 scripts/icons-data.py` — snapshot all 29 sets (npmmirror/jsDelivr @iconify-json packages → fallback api.iconify.design), materialize aliases, hash-chunk to `icons/<prefix>.<k>.json` (≤512 icons/chunk), build `data/icon-index.json`
- `python3 scripts/ipas-full.py` — download 3,448 original PNGs from cdn.ipaslogo.com (build-time only) → convert to 1024px WebP in `ipas/full/` (resumable; failures listed in scripts/ipas-full-failures.txt)
- `python3 scripts/vendor-dicebear.py` — vendor @dicebear core + 31 style packages into `vendor/dicebear/` (bare imports rewritten to relative paths, no import map needed)
- `python3 scripts/illus-data.py` — build the self-hosted illustration library into `illus/` + `data/illus.json` (resumable)
- `python3 scripts/ipas-data.py` — rebuild `data/ipas-logos.json` (categories keyword-derived)
- `python3 scripts/gen-data.py` — regenerate catalog.json, llms.txt, llms-full.txt from the local snapshot

## Tech

Single-file `index.html` (no build, no dependencies). Theme: auto/light/dark. Bilingual EN/ZH with `?lang=` deep links. Top-level tabs: Mascot Logos (default) ↔ Icon Search (`?tab=icons`). Icon search runs client-side over the local name index; thumbnails/SVG resolve from local hash chunks (browser-cached); PNG export and mascot PNG conversion happen in-browser via canvas; ZIP batches are built client-side (store method). The only runtime external script is the Cloudflare analytics beacon.

Part of [kuige.me](https://kuige.me/) · KuiGe's free tool collection.
