#!/usr/bin/env python3
"""IconGems P1：插画首批自托管管道。

包 1 · 3D Icons（CC0，Vijay Verma，3dicons.co）
  源：content/3dicons-meta/*.md 前置元数据（本仓库浅克隆），图片在其官方
  DigitalOcean Spaces CDN（构建期一次性下载 → illus/3dicons/）。
  取 color（主）与 clay（陶土）两种变体。

包 2 · illlustrations.co（MIT，Vijay Verma，realvjy/illlustrations）
  源：content/illlustrations/<no>/ 内的 PNG+SVG 直接复制 → illus/ill/。

产出 data/illus.json 清单。可续跑：已存在文件跳过。
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT3 = os.path.join(ROOT, 'illus', '3d')
OUTI = os.path.join(ROOT, 'illus', 'ill')
UA = {'User-Agent': 'icongems-p1/1.0 (+https://icongems.kuige.me/)'}

SRC3 = os.environ.get('ICON3_SRC') or '/tmp/p1check/3dicons'
SRCI = os.environ.get('ILL_SRC') or '/tmp/p1check/illlustrations'


def clone_if_missing(path, repo, branch):
    if os.path.isdir(path):
        return path
    dst = os.path.join(ROOT, 'scripts', '.cache', os.path.basename(path))
    if not os.path.isdir(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        subprocess.run(['git', 'clone', '--depth', '1', '-b', branch, repo, dst], check=True)
    return dst


def frontmatter(md_path):
    txt = open(md_path, encoding='utf-8').read()
    m = re.match(r'^---\n(.*?)\n---', txt, re.S)
    meta = {}
    if not m:
        return meta
    lines = m.group(1).split('\n')
    for i, line in enumerate(lines):
        if ':' not in line:
            continue
        k, v = line.split(':', 1)
        k, v = k.strip(), v.strip().strip('"')
        if not v and i + 1 < len(lines) and lines[i + 1].lstrip().startswith('- '):
            v = lines[i + 1].lstrip()[2:].strip()
        meta[k] = v
    return meta


def fetch(url, dst):
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        return 'skip'
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    tmp = dst + '.tmp'
    open(tmp, 'wb').write(data)
    os.replace(tmp, dst)
    return 'ok'


def pack_3dicons():
    src = clone_if_missing(SRC3, 'https://github.com/realvjy/3dicons.git', 'develop')
    meta_dir = os.path.join(src, 'content', '3dicons-meta')
    os.makedirs(OUT3, exist_ok=True)
    jobs = []
    items = []
    for f in sorted(os.listdir(meta_dir)):
        if not f.endswith('.md'):
            continue
        fm = frontmatter(os.path.join(meta_dir, f))
        slug = fm.get('file-slug') or f[:-3]
        title = fm.get('title', slug).replace('-', ' ')
        items.append({'p': '3d', 't': title, 's': slug, 'v': [
            {'k': 'color', 'f': f'{slug}.png'},
            {'k': 'clay', 'f': f'{slug}-clay.png'}]})
        base = 'https://3dicons.sgp1.cdn.digitaloceanspaces.com/v1/dynamic'
        color_url = fm.get('color') or f'{base}/color/{slug}-dynamic-color.png'
        clay_url = fm.get('clay') or f'{base}/clay/{slug}-dynamic-clay.png'
        jobs.append((color_url, os.path.join(OUT3, f'{slug}.png')))
        jobs.append((clay_url, os.path.join(OUT3, f'{slug}-clay.png')))
    return jobs, items


def pack_ill():
    src = clone_if_missing(SRCI, 'https://github.com/realvjy/illlustrations.git', 'develop')
    base = os.path.join(src, 'content', 'illlustrations')
    os.makedirs(OUTI, exist_ok=True)
    jobs = []
    items = []
    for d in sorted(os.listdir(base)):
        md = os.path.join(base, d, 'index.md')
        if not os.path.isfile(md):
            continue
        fm = frontmatter(md)
        title = (fm.get('title') or d).replace('NEW ', '')
        cat = fm.get('category', 'misc')
        if cat.startswith('['):
            cat = cat.strip('[]').split(',')[0].strip()
        png, svg = fm.get('png'), fm.get('svg')
        files, sv = [], None
        if png:
            files.append(png.lstrip('./'))
        if svg:
            sv = svg.lstrip('./')
            files.append(sv)
        items.append({'p': 'ill', 't': title, 'c': cat, 's': d, 'f': files, 'svg': sv})
        for fn in files:
            jobs.append((os.path.join(base, d, fn), os.path.join(OUTI, fn), 'copy'))
    return jobs, items


def main():
    j3, i3 = pack_3dicons()
    ji, ii = pack_ill()
    ok = skip = fail = 0
    fails = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {}
        for url, dst in j3:
            futs[ex.submit(fetch, url, dst)] = ('net', dst)
        for src, dst, _kind in ji:
            futs[ex.submit(shutil.copy2, src, dst)] = ('copy', dst)
        for n, fut in enumerate(as_completed(futs), 1):
            kind, dst = futs[fut]
            try:
                r = fut.result()
                if r == 'skip':
                    skip += 1
                else:
                    ok += 1
            except Exception as e:  # noqa: BLE001
                fail += 1
                fails.append((dst, str(e)[:120]))
            if n % 40 == 0:
                print(f'{n}/{len(futs)} ok={ok} skip={skip} fail={fail} {time.time()-t0:.0f}s', flush=True)
    manifest = {
        'v': 1,
        'packs': {
            '3d': {'name': '3D Icons', 'author': 'Vijay Verma', 'lic': 'CC0',
                   'url': 'https://3dicons.co', 'variants': ['color', 'clay']},
            'ill': {'name': 'illlustrations.co', 'author': 'Vijay Verma', 'lic': 'MIT',
                    'url': 'https://illlustrations.co', 'variants': ['png']},
        },
        'items': i3 + ii,
    }
    tmp = os.path.join(ROOT, 'data', 'illus.json.tmp')
    json.dump(manifest, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    os.replace(tmp, os.path.join(ROOT, 'data', 'illus.json'))
    if fails:
        print('FAILURES:')
        for d, why in fails[:10]:
            print(' ', d, why)
        print(f'total failures: {len(fails)}')
    print(f'done: ok={ok} skip={skip} fail={fail}; items: 3dicons={len(i3)} illlustrations={len(ii)}'
          f' in {time.time()-t0:.0f}s')


if __name__ == '__main__':
    sys.exit(main())
