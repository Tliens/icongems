#!/usr/bin/env python3
"""IconGems P0-2 归巢计划：吉祥物原图自托管。

从 cdn.ipaslogo.com 下载 1254px 原 PNG（构建期一次性），转码为 1024px WebP（带 alpha）
存入 ipas/full/。可续跑：已存在且非空的输出直接跳过。失败清单写入
scripts/ipas-full-failures.txt，重跑即可补齐。

运行后站点运行时不再请求 cdn.ipaslogo.com —— 大图全部来自本站。
"""
import io
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FULL = os.path.join(ROOT, 'ipas', 'full')
CDN = 'https://cdn.ipaslogo.com/logos/{}.png'
SIZE = 1024
WORKERS = 8
UA = {'User-Agent': 'icongems-ipas-full/1.0 (+https://icongems.kuige.me/)'}


def one(key: str) -> str:
    out = os.path.join(FULL, f'{key}.webp')
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return 'skip'
    for attempt in range(3):
        try:
            req = urllib.request.Request(CDN.format(key), headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
            img = Image.open(io.BytesIO(raw)).convert('RGBA')
            if img.size != (SIZE, SIZE):
                img = img.resize((SIZE, SIZE), Image.LANCZOS)
            tmp = out + '.tmp'
            img.save(tmp, 'WEBP', quality=88, method=4)
            os.replace(tmp, out)
            return 'ok'
        except Exception as e:  # noqa: BLE001
            if attempt == 2:
                return f'fail {type(e).__name__}: {e}'
            time.sleep(1.5 * (attempt + 1))
    return 'fail retries'


def main() -> int:
    os.makedirs(FULL, exist_ok=True)
    keys = list(json.load(open(os.path.join(ROOT, 'data', 'ipas-logos.json'), encoding='utf-8'))['logos'])
    done = fail = skip = 0
    failures = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(one, k): k for k in keys}
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            if r == 'ok':
                done += 1
            elif r == 'skip':
                skip += 1
            else:
                fail += 1
                failures.append((futs[fut], r))
            if i % 50 == 0 or i == len(keys):
                rate = i / max(time.time() - t0, 1)
                print(f'{i}/{len(keys)}  ok={done} skip={skip} fail={fail}  {rate:.1f}/s  eta={int((len(keys)-i)/max(rate,.01))}s', flush=True)
    if failures:
        with open(os.path.join(ROOT, 'scripts', 'ipas-full-failures.txt'), 'w', encoding='utf-8') as f:
            for k, why in failures:
                f.write(f'{k}\t{why}\n')
        print(f'FAILURES: {len(failures)} → scripts/ipas-full-failures.txt（重跑本脚本即可补齐）')
    print(f'done: ok={done} skip={skip} fail={fail} in {int(time.time()-t0)}s')
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
