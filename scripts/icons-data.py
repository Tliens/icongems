#!/usr/bin/env python3
"""IconGems P0-1 归巢计划：图标库全量自托管。

1. 拉取 29 个精选库（33 个 prefix）的全量 IconifyJSON（@iconify-json 官方 npm 包；
   npmmirror tarball 为主源，fastly.jsdelivr 直链为备源，api.iconify.design 兜底）。
2. 别名物化（alias → 直接内联父图标 body），按 djb2(name) % K 哈希分片
   （每片 ≤512 个图标）写入 icons/{prefix}.{k}.json —— 每个名字的分片自包含。
3. 生成 data/icon-index.json：按 prefix 分组的全量名称索引 + 每库元数据与精选样例。

可重复执行（源缓存于 scripts/.icons-cache/）。djb2 必须与 index.html 中的
JS 实现逐字节一致（UTF-8 字节流，h = h*33 + b，mod 2^32）。
"""
import io
import json
import math
import os
import sys
import tarfile
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, 'scripts', '.icons-cache')
OUTDIR = os.path.join(ROOT, 'icons')
IDX_PATH = os.path.join(ROOT, 'data', 'icon-index.json')
CHUNK = 512
UA = {'User-Agent': 'icongems-data/1.0 (+https://icongems.kuige.me/)'}

# (id, [prefixes], cat, license, display name) —— 与 index.html SETS 一一对应
SETS = [
    ('fluent', ['fluent'], 'ui', 'MIT', 'Fluent UI System Icons'),
    ('material-symbols', ['material-symbols'], 'ui', 'Apache-2.0', 'Material Symbols'),
    ('ph', ['ph'], 'ui', 'MIT', 'Phosphor'),
    ('mdi', ['mdi'], 'ui', 'Apache-2.0', 'Material Design Icons'),
    ('tabler', ['tabler'], 'ui', 'MIT', 'Tabler Icons'),
    ('solar', ['solar'], 'ui', 'CC BY 4.0', 'Solar'),
    ('mingcute', ['mingcute'], 'ui', 'Apache-2.0', 'MingCute Icon'),
    ('ri', ['ri'], 'ui', 'Apache-2.0', 'Remix Icon'),
    ('bi', ['bi', 'bxs', 'bxl'], 'ui', 'MIT', 'Bootstrap Icons'),
    ('lucide', ['lucide'], 'ui', 'ISC', 'Lucide'),
    ('icon-park', ['icon-park-outline'], 'ui', 'Apache-2.0', 'IconPark'),
    ('iconoir', ['iconoir'], 'ui', 'MIT', 'Iconoir'),
    ('ion', ['ion'], 'ui', 'MIT', 'Ionicons'),
    ('heroicons', ['heroicons'], 'ui', 'MIT', 'Heroicons'),
    ('fa6', ['fa6-solid', 'fa6-regular', 'fa6-brands'], 'ui', 'CC BY 4.0', 'Font Awesome 6 Free'),
    ('uil', ['uil'], 'ui', 'Apache-2.0', 'Unicons'),
    ('ant-design', ['ant-design'], 'ui', 'MIT', 'Ant Design Icons'),
    ('gg', ['gg'], 'ui', 'MIT', 'css.gg'),
    ('feather', ['feather'], 'ui', 'MIT', 'Feather Icons'),
    ('line-md', ['line-md'], 'anim', 'MIT', 'Material Line Icons'),
    ('svg-spinners', ['svg-spinners'], 'anim', 'MIT', 'SVG Spinners'),
    ('simple-icons', ['simple-icons'], 'brand', 'CC0', 'Simple Icons'),
    ('devicon', ['devicon'], 'brand', 'MIT', 'Devicon'),
    ('vscode-icons', ['vscode-icons'], 'brand', 'MIT', 'VSCode Icons'),
    ('codicon', ['codicon'], 'brand', 'CC BY 4.0', 'Codicons'),
    ('twemoji', ['twemoji'], 'emoji', 'CC BY 4.0', 'Twemoji'),
    ('fluent-emoji', ['fluent-emoji'], 'emoji', 'MIT', 'Fluent Emoji'),
    ('noto', ['noto'], 'emoji', 'Apache-2.0', 'Noto Emoji'),
    ('flat-color-icons', ['flat-color-icons'], 'emoji', 'MIT', 'Flat Color Icons'),
]

NICE = {'home', 'user', 'star', 'heart', 'search', 'settings', 'bell', 'camera', 'rocket',
        'check', 'mail', 'cloud', 'fire', 'sun', 'moon', 'play', 'lock', 'cart', 'gift',
        'code', 'book', 'flag', 'music', 'wifi', 'phone', 'edit', 'plus', 'close', 'menu',
        'eye', 'smile', 'chat', 'shield', 'time', 'calendar', 'trash', 'download', 'upload',
        'bolt', 'gem', 'diamond', 'crown', 'key', 'plane', 'car', 'dog', 'cat', 'panda',
        'fox', 'coffee', 'cake', 'bulb', 'tool', 'folder', 'image', 'video', 'mic', 'tag',
        'link', 'map', 'pin', 'globe', 'zap', 'like', 'love', 'info', 'warn', 'fire-flame'}


def djb2(s: str) -> int:
    h = 5381
    for b in s.encode('utf-8'):
        h = ((h * 33) + b) & 0xFFFFFFFF
    return h


def fetch(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def get_source(prefix: str) -> dict:
    os.makedirs(CACHE, exist_ok=True)
    cache_path = os.path.join(CACHE, f'{prefix}.json')
    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 500:
        return json.load(open(cache_path, encoding='utf-8'))
    data = None
    errs = []
    for attempt, loader in enumerate((
        lambda: json.loads(fetch(f'https://fastly.jsdelivr.net/npm/@iconify-json/{prefix}@latest/icons.json')),
        lambda: json.loads(fetch(f'https://cdn.jsdelivr.net/npm/@iconify-json/{prefix}@latest/icons.json')),
        lambda: tarball_icons(prefix),
        lambda: json.loads(fetch(f'https://api.iconify.design/{prefix}.json')),
    )):
        try:
            data = loader()
            if data and data.get('icons'):
                break
        except Exception as e:  # noqa: BLE001
            errs.append(f'{type(e).__name__}: {e}')
        time.sleep(1 + attempt)
    if not data or not data.get('icons'):
        raise RuntimeError(f'{prefix}: all sources failed — {errs}')
    tmp = cache_path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    os.replace(tmp, cache_path)
    return data


def tarball_icons(prefix: str) -> dict:
    meta = json.loads(fetch(f'https://registry.npmmirror.com/@iconify-json/{prefix}/latest', 30))
    tb = fetch(meta['dist']['tarball'])
    with tarfile.open(fileobj=io.BytesIO(tb), mode='r:gz') as tf:
        for m in tf.getmembers():
            if m.name.rstrip('/').endswith('icons.json'):
                return json.loads(tf.extractfile(m).read())
    raise RuntimeError(f'{prefix}: no icons.json in tarball')


def process_prefix(prefix: str) -> dict:
    src = get_source(prefix)
    icons = src.get('icons', {})
    aliases = src.get('aliases', {})
    hidden = set(src.get('hidden', []))
    W = src.get('width') or src.get('height') or 24
    H = src.get('height') or src.get('width') or 24

    # 别名物化：alias 直接内联父图标（父可能也是别名，链式解析）
    merged = dict(icons)
    for name, al in aliases.items():
        parent = al.get('parent')
        if parent in merged:
            p = merged[parent]
            merged[name] = {
                'body': p['body'],
                **({'width': al['width']} if al.get('width') else {}),
                **({'height': al['height']} if al.get('height') else {}),
            }
    names = sorted(n for n in merged if n not in hidden)
    K = max(1, math.ceil(len(names) / CHUNK))
    buckets = [{} for _ in range(K)]
    for n in names:
        buckets[djb2(n) % K][n] = merged[n]

    for k, bucket in enumerate(buckets):
        out = {'prefix': prefix, 'width': W, 'height': H, 'chunks': K, 'icons': bucket}
        if k == 0:
            cats = {c: [n for n in ns if n in merged] for c, ns in (src.get('categories') or {}).items()}
            cats = {c: ns for c, ns in cats.items() if ns}
            if cats:
                out['categories'] = cats
        tmp = os.path.join(OUTDIR, f'{prefix}.{k}.json.tmp')
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
        os.replace(tmp, os.path.join(OUTDIR, f'{prefix}.{k}.json'))

    # 样例：偏向常见词，并尽量集中在一个分片 → 每张库卡片的样例条只需 1 次请求
    def score(n: str) -> int:
        s = 0
        if n in NICE:
            s += 6
        elif any(n == w or n.startswith(w + '-') or n.endswith('-' + w) or f'-{w}-' in n for w in NICE):
            s += 3
        if len(n) <= 12:
            s += 1
        return s
    by_chunk = {}
    for n in names:
        if score(n) > 0:
            by_chunk.setdefault(djb2(n) % K, []).append(n)
    samples = []
    if by_chunk:
        best_k = max(by_chunk, key=lambda k: sum(score(n) for n in by_chunk[k]))
        cand = sorted(by_chunk[best_k], key=lambda n: (-score(n), len(n), n))
        samples = cand[:12]
    if len(samples) < 6:  # 兜底：直接取片 0 的短名
        samples = sorted(names, key=lambda n: (len(n), n))[:12]
    return {'p': prefix, 'k': K, 'n': len(names), 'samples': samples}


def main() -> None:
    os.makedirs(OUTDIR, exist_ok=True)
    # 清掉旧版本可能遗留的多余分片（重新分片时 K 变小）
    old = {f for f in os.listdir(OUTDIR) if f.endswith('.json') or f.endswith('.tmp')}
    keep = set()
    sets_meta = {}
    total = 0
    for sid, prefixes, cat, lic, name in SETS:
        pm = []
        for p in prefixes:
            t0 = time.time()
            m = process_prefix(p)
            for k in range(m['k']):
                keep.add(f'{p}.{k}.json')
            pm.append(m)
            total += m['n']
            print(f'  {p}: {m["n"]:>6} icons → {m["k"]:>2} chunks  ({time.time()-t0:.1f}s)', flush=True)
        sets_meta[sid] = {'n': name, 'lic': lic, 'cat': cat, 'cnt': sum(m['n'] for m in pm),
                          'prefixes': [{'p': m['p'], 'k': m['k'], 'n': m['n']} for m in pm],
                          'samples': pm[0]['samples']}
    for f in old - keep:
        os.remove(os.path.join(OUTDIR, f))
    index = {
        'v': 2, 'chunked': True, 'chunkSize': CHUNK, 'hash': 'djb2-utf8-mod32',
        'generated': time.strftime('%Y-%m-%d'),
        'total': total,
        'sets': sets_meta,
        'byPrefix': {},
    }
    for sid, prefixes, *_ in SETS:
        for pm in sets_meta[sid]['prefixes']:
            index['byPrefix'][pm['p']] = {'k': pm['k'], 'n': pm['n'], 'set': sid}
    names_by_prefix = {}
    for p in index['byPrefix']:
        ns = set()
        for k in range(index['byPrefix'][p]['k']):
            d = json.load(open(os.path.join(OUTDIR, f'{p}.{k}.json'), encoding='utf-8'))
            ns.update(d['icons'].keys())
        names_by_prefix[p] = sorted(ns)
    index['names'] = names_by_prefix
    tmp = IDX_PATH + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, separators=(',', ':'))
    os.replace(tmp, IDX_PATH)
    size = os.path.getsize(IDX_PATH) / 1024 / 1024
    print(f'index: {total:,} icons, {len(names_by_prefix)} prefixes, {size:.1f} MB → {IDX_PATH}')


if __name__ == '__main__':
    sys.exit(main())
