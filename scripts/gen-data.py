#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Single source of truth for IconGems machine-readable files.
Regenerates: data/catalog.json, llms.txt, llms-full.txt
Run: python3 scripts/gen-data.py   (after scripts/icons-data.py when icon data changes)

P0 归巢计划：图标计数来自本站快照 data/icon-index.json；所有端点均在本站域名，
不再引用 api.iconify.design / cdn.ipaslogo.com 作为运行时下载来源。
"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://icongems.kuige.me"

# icon snapshot index (built by scripts/icons-data.py) — counts & chunk layout source of truth
IDX = json.load(open(BASE + "/data/icon-index.json"))
UPDATED = IDX.get("generated", "unknown")

# id, name, author, prefixes, category, palette, license, official_url
SETS = [
 ("fluent","Fluent UI System Icons","Microsoft",["fluent"],"ui",0,"MIT","https://github.com/microsoft/fluentui-system-icons"),
 ("material-symbols","Material Symbols","Google",["material-symbols"],"ui",0,"Apache-2.0","https://fonts.google.com/icons"),
 ("ph","Phosphor","Phosphor Icons",["ph"],"ui",0,"MIT","https://phosphoricons.com"),
 ("mdi","Material Design Icons","Pictogrammers",["mdi"],"ui",0,"Apache-2.0","https://pictogrammers.com/library/mdi/"),
 ("tabler","Tabler Icons","Paweł Kuna",["tabler"],"ui",0,"MIT","https://tabler.io/icons"),
 ("solar","Solar","480 Design",["solar"],"ui",0,"CC-BY-4.0","https://solar-icons.com"),
 ("mingcute","MingCute Icon","MingCute Design",["mingcute"],"ui",0,"Apache-2.0","https://www.mingcute.com"),
 ("ri","Remix Icon","Remix Design",["ri"],"ui",0,"Apache-2.0","https://remixicon.com"),
 ("bi","Bootstrap Icons","Bootstrap Team",["bi","bxs","bxl"],"ui",0,"MIT","https://icons.getbootstrap.com"),
 ("lucide","Lucide","Lucide Contributors",["lucide"],"ui",0,"ISC","https://lucide.dev"),
 ("icon-park","IconPark","ByteDance",["icon-park-outline"],"ui",0,"Apache-2.0","https://iconpark.oceanengine.com"),
 ("iconoir","Iconoir","Luca Burgio",["iconoir"],"ui",0,"MIT","https://iconoir.com"),
 ("ion","Ionicons","Ionic",["ion"],"ui",0,"MIT","https://ionic.io/ionicons"),
 ("heroicons","Heroicons","Tailwind Labs",["heroicons"],"ui",0,"MIT","https://heroicons.com"),
 ("fa6","Font Awesome 6 Free","Fonticons",["fa6-solid","fa6-regular","fa6-brands"],"ui",0,"CC-BY-4.0","https://fontawesome.com"),
 ("uil","Unicons","Iconscout",["uil"],"ui",0,"Apache-2.0","https://iconscout.com/unicons"),
 ("ant-design","Ant Design Icons","Ant Design",["ant-design"],"ui",0,"MIT","https://ant.design/components/icons"),
 ("gg","css.gg","Astrit",["gg"],"ui",0,"MIT","https://css.gg"),
 ("feather","Feather Icons","Cole Bemis",["feather"],"ui",0,"MIT","https://feathericons.com"),
 ("line-md","Material Line Icons","Vjacheslav Trushkin",["line-md"],"anim",0,"MIT","https://icon-sets.iconify.design/line-md/"),
 ("svg-spinners","SVG Spinners","Utkarsh Verma",["svg-spinners"],"anim",0,"MIT","https://icon-sets.iconify.design/svg-spinners/"),
 ("simple-icons","Simple Icons","Simple Icons Collaborators",["simple-icons"],"brand",0,"CC0-1.0","https://simpleicons.org"),
 ("devicon","Devicon","Devicon Org",["devicon"],"brand",1,"MIT","https://devicon.dev"),
 ("vscode-icons","VSCode Icons","Roberto Huertas",["vscode-icons"],"brand",1,"MIT","https://icon-sets.iconify.design/vscode-icons/"),
 ("codicon","Codicons","Microsoft",["codicon"],"brand",0,"CC-BY-4.0","https://microsoft.github.io/vscode-codicons"),
 ("twemoji","Twemoji","Twitter / X",["twemoji"],"emoji",1,"CC-BY-4.0","https://github.com/twitter/twemoji"),
 ("fluent-emoji","Fluent Emoji","Microsoft",["fluent-emoji"],"emoji",1,"MIT","https://github.com/microsoft/fluentui-emoji"),
 ("noto","Noto Emoji","Google",["noto"],"emoji",1,"Apache-2.0","https://github.com/googlefonts/noto-emoji"),
 ("flat-color-icons","Flat Color Icons","Icons8",["flat-color-icons"],"emoji",1,"MIT","https://icon-sets.iconify.design/flat-color-icons/"),
]
# name, url, license, formats, aiTrainingNote, desc
ART = [
 ("unDraw","https://undraw.co/","free, no attribution","SVG · PNG","AI/ML training explicitly prohibited","Consistent-style illustrations with live color customizer"),
 ("Open Peeps","https://www.openpeeps.com/","CC0","PNG · SVG","","Hand-drawn people by Pablo Stanley"),
 ("Humaaans","https://humaaans.com/","CC0","SVG","","Mix-and-match human characters"),
 ("DiceBear","https://www.dicebear.com/","open source (per-style)","SVG · PNG · API","","Avatar generator, dozens of styles"),
 ("Storyset","https://storyset.com/","free with attribution (Freepik)","SVG · animated","","Editable animated illustrations"),
 ("DrawKit","https://www.drawkit.com/","free with attribution (free tier)","SVG","","Hand-drawn vector packs"),
 ("ManyPixels","https://www.manypixels.co/gallery","free, no attribution","SVG · PNG","","Monocolor gallery with color picker"),
 ("3dicons","https://www.3dicons.com/","open source, free","PNG · Blender","","Open-source 3D icons by Vijay Verma"),
 ("LottieFiles Free","https://lottiefiles.com/","mixed - check each asset","Lottie · GIF","","Large animated library"),
 ("IRA Design","https://iradesign.io/","MIT","SVG · PSD","","Modular illustration builder by Creative Tim"),
 ("Lukasz Adam","https://lukaszadam.com/illustrations","CC0","SVG","","Free miscellaneous vectors"),
 ("absurd.design","https://absurd.design/","free with attribution (free tier)","SVG","","Surreal line-art"),
 ("Ouch! by Icons8","https://icons8.com/ouch","free with link","PNG · animated","","Vector & 3D illustrations"),
 ("Doodle Ipsum","https://doodleipsum.com/","free (Blush license)","PNG · API","","Doodle API by Blush"),
 ("Shapefest","https://shapefest.com/","free for commercial use","PNG · SVG","","Large 3D shape library"),
 ("illlustrations.co","https://illlustrations.co/","open source, free","PNG","","Open-source illustrations"),
]

# per-set counts & chunk layout straight from the local snapshot
byp = IDX["byPrefix"]
def set_meta(sid):
    return IDX["sets"].get(sid, {})

sets_json=[]
for i,n,a,p,c,pl,lic,u in SETS:
    m=set_meta(i)
    sets_json.append({"id":i,"name":n,"author":a,"prefixes":p,"category":c,"palette":bool(pl),
      "icon_count":m.get("cnt"),"license":lic,"official_url":u,
      "data":[{ "prefix":pm["p"],"chunks":pm["k"],"icons":pm["n"],
                "json":f"{SITE}/icons/{pm['p']}.<0..{pm['k']-1}>.json"} for pm in m.get("prefixes",[])],
      "search_url":f"{SITE}/?q=<term>",
      "browse_url":f"{SITE}/?set={i}"})
art_json=[{"name":n,"url":u,"license":lic,"formats":f.split(" · "),"aiTraining":(ai or "not specified"),"description":d,"offsite":True}
          for n,u,lic,f,ai,d in ART]
total=IDX["total"]

# mascot library (IP as Logo) — derived from data/ipas-logos.json
ipas=json.load(open(BASE+"/data/ipas-logos.json"))
ipas_json={
 "id":"ip-as-logo","name":"IP as Logo","author":"s1dashu / ipaslogo.com",
 "license":"MIT","official_url":"https://ipaslogo.com/",
 "skill_url":"https://github.com/s1dashu/ip-as-logo-skill",
 "logo_count":ipas["count"],"categories":ipas["cats"],"category_counts":ipas["cat_counts"],
 "original_webp_1024_hosted":SITE+"/ipas/full/<key>.webp",
 "preview_webp_512_hosted":SITE+"/ipas/display/<key>.webp",
 "manifest":SITE+"/data/ipas-logos.json",
 "manifest_shape":"{logos: {<key>: [category, background-color]}}, key = <hash>-<slug>",
 "note":"Rounded neo-skeuomorphic mascot logos, MIT. Every file (512px previews and 1024px originals) is self-hosted by IconGems; PNG export is converted in the browser from the local WebP. Categories are keyword-derived (source category API unreachable from CN networks).",
}

CHUNK_RECIPE = ("Icon data is hash-chunked: for icon <prefix>:<name>, k = djb2_utf8(name) % K "
 "(K = byPrefix.<prefix>.k in the index; djb2_utf8: h=5381; for each UTF-8 byte b: h=(h*33+b) mod 2^32). "
 "Fetch "+SITE+"/icons/<prefix>.<k>.json and read .icons[<name>] = {body, width?, height?}; "
 "set-level width/height are the fallback dimensions. SVG = <svg xmlns viewBox=\"0 0 W H\"> + body + </svg>.")

cat={
 "site":"IconGems","url":SITE+"/","updated":UPDATED,
 "llms":SITE+"/llms.txt","llmsFull":SITE+"/llms-full.txt",
 "selfHosted":True,
 "description":"Resource site where every asset lives on this domain: the full IP as Logo mascot library (3,448 MIT-licensed logos, 1024px originals self-hosted) plus complete snapshots of 29 famous open-source icon libraries (searchable & downloadable locally, no third-party API) and a curated list of free illustration libraries (off-site links, clearly labelled).",
 "pageMap":{"mascot_logos":SITE+"/#mascots","search_and_download":SITE+"/#finder","icon_libraries":SITE+"/#libs","more_resources":SITE+"/#more","for_ai":SITE+"/#ai","faq":SITE+"/#faq"},
 "quickstart":[
  "Mascots: read "+SITE+"/data/ipas-logos.json → 512px preview /ipas/display/<key>.webp → 1024px original /ipas/full/<key>.webp (all on this site, MIT).",
  "Icon names: GET "+SITE+"/data/icon-index.json (names grouped by prefix + per-set chunk layout).",
  "Icon SVG data: "+CHUNK_RECIPE,
  "Embed in web apps via @iconify/react, @iconify/vue or <iconify-icon> web component (npm packages use the same prefixes).",
  "Check the license field before shipping; CC BY 4.0 sets need attribution.",
 ],
 "mascot_logos":ipas_json,
 "icon_sets":sets_json,
 "icon_index":{ "url":SITE+"/data/icon-index.json","total_icons":total,"prefixes":len(byp),
   "chunked":True,"chunkSize":IDX.get("chunkSize",512),"hash":"djb2-utf8-mod32","recipe":CHUNK_RECIPE},
 "illustrations":art_json,
 "license_summary":{"no_attribution":["MIT","Apache-2.0","ISC","CC0-1.0"],"attribution_required":["CC-BY-4.0"],"note":"Verify on the source site before shipping; licenses change."}
}
with open(BASE+'/data/catalog.json','w') as f: json.dump(cat,f,indent=1,ensure_ascii=False)

# ---------- llms.txt (index, per llmstxt.org) ----------
L=[]
L.append("# IconGems\n")
L.append(f"> A free RESOURCE site where every asset lives on this domain: 3,448 MIT-licensed mascot logos from IP as Logo (1024px originals self-hosted, browser-side PNG export, ZIP batches) plus complete self-hosted snapshots of {total:,} open-source SVG icons from 29 famous libraries (Google Material Symbols, Microsoft Fluent, Tabler, Lucide, Phosphor, Font Awesome, Bootstrap, ByteDance IconPark…). Bilingual EN/ZH. Machine-readable end to end — search, SVG and PNG resolve with zero third-party requests.\n")
L.append("## Quick start for agents\n")
L.append("1. Mascot logos (MIT): manifest "+SITE+"/data/ipas-logos.json → preview `"+SITE+"/ipas/display/<key>.webp` → 1024px original `"+SITE+"/ipas/full/<key>.webp`")
L.append("2. Icon names & chunk layout: `GET "+SITE+"/data/icon-index.json`")
L.append("3. Icon SVG data: `GET "+SITE+"/icons/<prefix>.<k>.json` — "+CHUNK_RECIPE)
L.append("4. Build SVG: `<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 W H\">{body}</svg>` (mono sets: add fill=\"currentColor\" or your color)")
L.append("5. Ship: MIT/Apache/ISC/CC0 assets need no attribution; CC BY 4.0 sets do. Full details in llms-full.txt.\n")
L.append("## Site\n")
L.append(f"- [IconGems]({SITE}/): the human interface — mascot library (default tab), local icon search, one-click SVG/PNG download, copy-ready React/Vue/HTML/CSS")
L.append("- [llms-full.txt]("+SITE+"/llms-full.txt): this guide with the complete catalog inlined\n")
L.append("## Mascot logos — IP as Logo (3,448, MIT, categories keyword-derived, fully self-hosted)\n")
L.append(f"- Manifest (category + background color per logo): {SITE}/data/ipas-logos.json")
L.append("- Previews (512px WebP, hosted here): "+SITE+"/ipas/display/<key>.webp")
L.append("- Originals (1024px WebP with alpha, hosted here; PNG export converts in-browser): "+SITE+"/ipas/full/<key>.webp")
L.append("- Source project: https://ipaslogo.com/ · skill: https://github.com/s1dashu/ip-as-logo-skill\n")
L.append("## Curated icon sets (29 sets, %s icons, self-hosted snapshot of %s)\n" % (f"{total:,}",UPDATED))
for i,n,a,p,c,pl,lic,u in SETS:
    m=set_meta(i); cnt=m.get("cnt",0)
    L.append(f"- [{n}]({u}): {cnt:,} icons, license {lic}, prefix `{p[0]}`{' + '+str(len(p)-1)+' more' if len(p)>1 else ''} [{c}]")
L.append("")
L.append("## Free illustration libraries (16 off-site links at the end of the page — per-entry license)\n")
for n,u,lic,f,ai,d in ART:
    tag=" ⚠ no AI training" if "prohibited" in ai else ""
    L.append(f"- [{n}]({u}): {lic}{tag} — {d} (off-site)")
L.append("")
L.append("## Local data endpoints (all on this domain, CORS-open, no key)\n")
L.append("```\nGET /data/icon-index.json            # all icon names grouped by prefix + chunk layout\nGET /icons/<prefix>.<k>.json         # SVG bodies, hash chunk (see recipe in quick start)\nGET /data/ipas-logos.json            # mascot manifest: {logos: {<key>: [category, bg]}}\nGET /ipas/display/<key>.webp         # mascot 512px preview\nGET /ipas/full/<key>.webp            # mascot 1024px original\nBase: "+SITE+"\n```\n")
L.append("## Deep links\n")
L.append(f"- Search results: {SITE}/?q=<term>  ·  Browse one set: {SITE}/?set=<id>\n")
L.append("## Licensing\n")
L.append("- No attribution: MIT, Apache-2.0, ISC, CC0 — all mascot logos + most icon sets above")
L.append("- Attribution required: CC BY 4.0 (Solar, Font Awesome Free, Twemoji, Codicons)")
L.append("- Illustrations: per-entry, see catalog (off-site links). unDraw prohibits AI/ML training use.")
L.append("- Always verify on the source site before shipping.\n")
L.append("## Contact\n")
L.append("- IconGems is an independent site over open-source icon data (Iconify open format), fully self-hosted; all trademarks belong to their owners.")
L.append("- Author: 魁歌 KuiGe — https://kuige.me/")
open(BASE+'/llms.txt','w').write("\n".join(L))

# ---------- llms-full.txt (index + full catalog inlined) ----------
F=list(L)
F.insert(len(F)-2,"## Complete machine catalog\n")
F.insert(len(F)-2,"```json\n"+json.dumps(cat,ensure_ascii=False,indent=1)+"\n```\n")
F.append("\nIcon counts are self-hosted snapshots (%s); rerun scripts/icons-data.py to refresh." % UPDATED)
open(BASE+'/llms-full.txt','w').write("\n".join(F))

print("catalog.json + llms.txt (%dB) + llms-full.txt (%dB) regenerated (total %s icons, %s)" % (
    os.path.getsize(BASE+'/llms.txt'), os.path.getsize(BASE+'/llms-full.txt'), f"{total:,}", UPDATED))
