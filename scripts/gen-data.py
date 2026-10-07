#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Single source of truth for IconGems machine-readable files.
Regenerates: data/catalog.json, llms.txt, llms-full.txt
Run: python3 scripts/gen-data.py
Counts are the verified static fallbacks (page upgrades them live from Iconify).
"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://icongems.kuige.me"
UPDATED = "2026-10-07"

# id, name, author, prefixes, category, palette, count, license, official_url
SETS = [
 ("fluent","Fluent UI System Icons","Microsoft",["fluent"],"ui",0,19876,"MIT","https://github.com/microsoft/fluentui-system-icons"),
 ("material-symbols","Material Symbols","Google",["material-symbols"],"ui",0,15717,"Apache-2.0","https://fonts.google.com/icons"),
 ("ph","Phosphor","Phosphor Icons",["ph"],"ui",0,9072,"MIT","https://phosphoricons.com"),
 ("mdi","Material Design Icons","Pictogrammers",["mdi"],"ui",0,7447,"Apache-2.0","https://pictogrammers.com/library/mdi/"),
 ("tabler","Tabler Icons","Paweł Kuna",["tabler"],"ui",0,6220,"MIT","https://tabler.io/icons"),
 ("solar","Solar","480 Design",["solar"],"ui",0,8706,"CC-BY-4.0","https://solar-icons.com"),
 ("mingcute","MingCute Icon","MingCute Design",["mingcute"],"ui",0,3320,"Apache-2.0","https://www.mingcute.com"),
 ("ri","Remix Icon","Remix Design",["ri"],"ui",0,3188,"Apache-2.0","https://remixicon.com"),
 ("bi","Bootstrap Icons","Bootstrap Team",["bi","bxs","bxl"],"ui",0,3038,"MIT","https://icons.getbootstrap.com"),
 ("lucide","Lucide","Lucide Contributors",["lucide"],"ui",0,1866,"ISC","https://lucide.dev"),
 ("icon-park","IconPark","ByteDance",["icon-park-outline"],"ui",0,2658,"Apache-2.0","https://iconpark.oceanengine.com"),
 ("iconoir","Iconoir","Luca Burgio",["iconoir"],"ui",0,1671,"MIT","https://iconoir.com"),
 ("ion","Ionicons","Ionic",["ion"],"ui",0,1357,"MIT","https://ionic.io/ionicons"),
 ("heroicons","Heroicons","Tailwind Labs",["heroicons"],"ui",0,1288,"MIT","https://heroicons.com"),
 ("fa6","Font Awesome 6 Free","Fonticons",["fa6-solid","fa6-regular","fa6-brands"],"ui",0,2060,"CC-BY-4.0","https://fontawesome.com"),
 ("uil","Unicons","Iconscout",["uil"],"ui",0,1215,"Apache-2.0","https://iconscout.com/unicons"),
 ("ant-design","Ant Design Icons","Ant Design",["ant-design"],"ui",0,848,"MIT","https://ant.design/components/icons"),
 ("gg","css.gg","Astrit",["gg"],"ui",0,704,"MIT","https://css.gg"),
 ("feather","Feather Icons","Cole Bemis",["feather"],"ui",0,286,"MIT","https://feathericons.com"),
 ("line-md","Material Line Icons","Vjacheslav Trushkin",["line-md"],"anim",0,1218,"MIT","https://icon-sets.iconify.design/line-md/"),
 ("svg-spinners","SVG Spinners","Utkarsh Verma",["svg-spinners"],"anim",0,46,"MIT","https://icon-sets.iconify.design/svg-spinners/"),
 ("simple-icons","Simple Icons","Simple Icons Collaborators",["simple-icons"],"brand",0,3464,"CC0-1.0","https://simpleicons.org"),
 ("devicon","Devicon","Devicon Org",["devicon"],"brand",1,1057,"MIT","https://devicon.dev"),
 ("vscode-icons","VSCode Icons","Roberto Huertas",["vscode-icons"],"brand",1,1666,"MIT","https://icon-sets.iconify.design/vscode-icons/"),
 ("codicon","Codicons","Microsoft",["codicon"],"brand",0,653,"CC-BY-4.0","https://microsoft.github.io/vscode-codicons"),
 ("twemoji","Twemoji","Twitter / X",["twemoji"],"emoji",1,3988,"CC-BY-4.0","https://github.com/twitter/twemoji"),
 ("fluent-emoji","Fluent Emoji","Microsoft",["fluent-emoji"],"emoji",1,3126,"MIT","https://github.com/microsoft/fluentui-emoji"),
 ("noto","Noto Emoji","Google",["noto"],"emoji",1,3729,"Apache-2.0","https://github.com/googlefonts/noto-emoji"),
 ("flat-color-icons","Flat Color Icons","Icons8",["flat-color-icons"],"emoji",1,329,"MIT","https://icon-sets.iconify.design/flat-color-icons/"),
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

sets_json=[{"id":i,"name":n,"author":a,"prefixes":p,"category":c,"palette":bool(pl),
  "icon_count_fallback":cnt,"license":lic,"official_url":u,
  "search":f"https://api.iconify.design/search?query=<term>&prefixes={','.join(p)}",
  "svg":f"https://api.iconify.design/{p[0]}/<icon-name>.svg"} for i,n,a,p,c,pl,cnt,lic,u in SETS]
art_json=[{"name":n,"url":u,"license":lic,"formats":f.split(" · "),"aiTraining":(ai or "not specified"),"description":d}
          for n,u,lic,f,ai,d in ART]
total=sum(s[6] for s in SETS)

cat={
 "site":"IconGems","url":SITE+"/","updated":UPDATED,
 "llms":SITE+"/llms.txt","llmsFull":SITE+"/llms-full.txt",
 "description":"Curated catalog of famous open-source icon libraries (searchable & downloadable on IconGems via the Iconify API) and free illustration libraries.",
 "pageMap":{"search_and_download":SITE+"/#finder","icon_libraries":SITE+"/#libs","illustrations":SITE+"/#art","for_ai":SITE+"/#ai","faq":SITE+"/#faq"},
 "quickstart":[
  "Read this catalog to pick a set that fits (check license first).",
  "Search icons: GET https://api.iconify.design/search?query=<term>&prefixes=<prefix(es)>",
  "Get inline SVG: GET https://api.iconify.design/<prefix>/<name>.svg (add ?color=%23hex&height=64)",
  "Embed in web apps via @iconify/react, @iconify/vue or <iconify-icon> web component.",
 ],
 "icon_sets":sets_json,
 "illustrations":art_json,
 "iconify_api":{
   "search":"https://api.iconify.design/search?query=<term>&limit=<n>&prefixes=<comma-separated>",
   "svg":"https://api.iconify.design/<prefix>/<icon>.svg?color=<hex|currentColor>&height=<px>",
   "set_metadata":"https://api.iconify.design/collections?prefixes=<comma-separated>",
   "set_browse":"https://api.iconify.design/collection?prefix=<prefix>",
   "cors":"access-control-allow-origin: *"},
 "license_summary":{"no_attribution":["MIT","Apache-2.0","ISC","CC0-1.0"],"attribution_required":["CC-BY-4.0"],"note":"Verify on the source site before shipping; licenses change."}
}
with open(BASE+'/data/catalog.json','w') as f: json.dump(cat,f,indent=1,ensure_ascii=False)

# ---------- llms.txt (index, per llmstxt.org) ----------
L=[]
L.append("# IconGems\n")
L.append(f"> Free search & download for {total:,}+ open-source SVG icons from 29 famous libraries (Google Material Symbols, Microsoft Fluent, Tabler, Lucide, Phosphor, Font Awesome, Bootstrap, ByteDance IconPark…) plus 16 curated free illustration libraries. Bilingual EN/ZH. Built for designers, developers, PMs — and AI agents: every asset below is machine-readable, key-less and CORS-open.\n")
L.append("## Quick start for agents\n")
L.append("1. Pick a set from the catalog (check `license` first): "+SITE+"/data/catalog.json")
L.append("2. Search: `GET https://api.iconify.design/search?query=<term>&prefixes=<prefix(es)>`")
L.append("3. Get SVG: `GET https://api.iconify.design/<prefix>/<name>.svg?height=64` (`&color=%23hex` to recolor)")
L.append("4. Ship: MIT/Apache/ISC/CC0 sets need no attribution; CC BY 4.0 sets do. Full details in llms-full.txt.\n")
L.append("## Site\n")
L.append(f"- [IconGems]({SITE}/): the human interface — aggregated search, one-click SVG/PNG download, copy-ready React/Vue/HTML/CSS")
L.append("- [llms-full.txt]("+SITE+"/llms-full.txt): this guide with the complete catalog inlined\n")
L.append("## Curated icon sets (29 sets, %s icons, counts as of %s)\n" % (f"{total:,}",UPDATED))
for i,n,a,p,c,pl,cnt,lic,u in SETS:
    L.append(f"- [{n}]({u}): {cnt:,} icons, license {lic}, prefix `{p[0]}`{' + '+str(len(p)-1)+' more' if len(p)>1 else ''} [{c}]")
L.append("")
L.append("## Free illustration libraries (16, license per entry)\n")
for n,u,lic,f,ai,d in ART:
    tag=" ⚠ no AI training" if "prohibited" in ai else ""
    L.append(f"- [{n}]({u}): {lic}{tag} — {d}")
L.append("")
L.append("## Iconify API (open CORS, no key)\n")
L.append("```\nGET /search?query=<term>&limit=<n>&prefixes=<p1,p2>\nGET /<prefix>/<icon>.svg?color=<hex|currentColor>&height=<px>\nGET /collections?prefixes=<p1,p2>   # name, author, license, count, samples per set\nGET /collection?prefix=<p>          # all icon names in a set\nBase: https://api.iconify.design\n```\n")
L.append("## Deep links\n")
L.append(f"- Search results: {SITE}/?q=<term>  ·  Browse one set: {SITE}/?set=<id>\n")
L.append("## Licensing\n")
L.append("- No attribution: MIT, Apache-2.0, ISC, CC0 — most sets above")
L.append("- Attribution required: CC BY 4.0 (Solar, Font Awesome 6 Free, Twemoji, Codicons)")
L.append("- Illustrations: per-entry, see catalog. unDraw prohibits AI/ML training use.")
L.append("- Always verify on the source site before shipping.\n")
L.append("## Contact\n")
L.append("- IconGems is an independent front-end over the Iconify open-source aggregation; all trademarks belong to their owners.")
L.append("- Author: 魁歌 KuiGe — https://kuige.me/")
open(BASE+'/llms.txt','w').write("\n".join(L))

# ---------- llms-full.txt (index + full catalog inlined) ----------
F=list(L)
F.insert(len(F)-2,"## Complete machine catalog\n")
F.insert(len(F)-2,"```json\n"+json.dumps(cat,ensure_ascii=False,indent=1)+"\n```\n")
F.append("\nCounts are static snapshots (%s); the live Iconify API is always authoritative for current numbers." % UPDATED)
open(BASE+'/llms-full.txt','w').write("\n".join(F))

print("catalog.json + llms.txt (%dB) + llms-full.txt (%dB) regenerated" % (
    os.path.getsize(BASE+'/llms.txt'), os.path.getsize(BASE+'/llms-full.txt')))
