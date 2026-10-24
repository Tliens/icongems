#!/usr/bin/env python3
"""IconGems P1：vendor DiceBear ESM 到 vendor/dicebear/（零构建、纯相对导入）。

来源优先级：/tmp/p1check 本地缓存 → npmmirror registry 下载。
全部 31 个风格包许可为 MIT 或 CC0（styles/<s>/package/LICENSE）。
core 与风格包均只使用相对导入，唯一的裸导入可能是 @dicebear/core
（由 index.html 顶部 import map 兜底映射到 vendor/dicebear/core/index.js）。
"""
import io
import json
import os
import re
import shutil
import sys
import tarfile
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'vendor', 'dicebear')
CACHE = '/tmp/p1check'  # 本轮探测缓存（可选）

STYLES = ['adventurer', 'adventurer-neutral', 'avataaars', 'avataaars-neutral', 'big-ears',
          'big-ears-neutral', 'big-smile', 'bottts', 'bottts-neutral', 'croodles',
          'croodles-neutral', 'dylan', 'fun-emoji', 'glass', 'icons', 'identicon', 'initials',
          'lorelei', 'lorelei-neutral', 'micah', 'miniavs', 'notionists', 'notionists-neutral',
          'open-peeps', 'personas', 'pixel-art', 'pixel-art-neutral', 'rings', 'shapes',
          'thumbs', 'toon-head']


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'icongems-p1/1.0'})
    return urllib.request.urlopen(req, timeout=60).read()


def copy_js(src_dir, dst_dir):
    n = 0
    for root, _, files in os.walk(src_dir):
        rel = os.path.relpath(root, src_dir)
        target = dst_dir if rel == '.' else os.path.join(dst_dir, rel)
        os.makedirs(target, exist_ok=True)
        for f in files:
            if f.endswith(('.js', '.json')) and not f.endswith('.d.ts'):
                shutil.copy2(os.path.join(root, f), os.path.join(target, f)); os.utime(os.path.join(target, f), None)
                n += 1
    return n


def latest_version(pkg, major=9):
    d = json.loads(get(f'https://registry.npmmirror.com/@dicebear/{pkg}'))
    vs = [v for v in d.get('versions', {}) if re.fullmatch(rf'{major}\.\d+\.\d+', v)]
    vs.sort(key=lambda s: [int(x) for x in s.split('.')])
    return vs[-1]


def fetch_package(pkg, ver, dst):
    meta = json.loads(get(f'https://registry.npmmirror.com/@dicebear/{pkg}/{ver}'))
    with tarfile.open(fileobj=io.BytesIO(get(meta['dist']['tarball'])), mode='r:gz') as tf:
        tf.extractall(dst)
    return os.path.join(dst, 'package')


def main():
    os.makedirs(OUT, exist_ok=True)
    total = 0
    # core
    core_dst = os.path.join(OUT, 'core')
    if os.path.exists(os.path.join(CACHE, 'core', 'lib')):
        n = copy_js(os.path.join(CACHE, 'core', 'lib'), core_dst)
        print(f'core: {n} files (cache)')
    else:
        tmp = os.path.join(OUT, '.tmp-core')
        shutil.rmtree(tmp, ignore_errors=True)
        pkg_dir = fetch_package('core', latest_version('core'), tmp)
        n = copy_js(os.path.join(pkg_dir, 'lib'), core_dst)
        shutil.rmtree(tmp)
        print(f'core: {n} files (registry)')
    total += n
    # styles
    for s in STYLES:
        src = os.path.join(CACHE, 'styles', s, 'package', 'lib')
        dst = os.path.join(OUT, s)
        if os.path.isdir(src):
            n = copy_js(src, dst)
            print(f'{s}: {n} files (cache)')
        else:
            tmp = os.path.join(OUT, '.tmp-' + s)
            shutil.rmtree(tmp, ignore_errors=True)
            pkg_dir = fetch_package(s, latest_version(s), tmp)
            n = copy_js(os.path.join(pkg_dir, 'lib'), dst)
            shutil.rmtree(tmp)
            print(f'{s}: {n} files (registry)')
        total += n
    # 裸导入改写：@dicebear/core → 相对路径（不依赖浏览器 import map 支持）
    core_root = os.path.join(OUT, 'core')
    fixed = 0
    for root, _, files in os.walk(OUT):
        if root == core_root:
            continue
        for f in files:
            if not f.endswith('.js'):
                continue
            path = os.path.join(root, f)
            txt = open(path, encoding='utf-8').read()
            if '@dicebear/core' not in txt:
                continue
            rel = os.path.relpath(core_root, root)
            # import 语句里把包名换成指向 core/index.js 的相对路径
            new = txt.replace("'@dicebear/core'", f"'{rel}/index.js'").replace('"@dicebear/core"', f'"{rel}/index.js"')
            open(path, 'w', encoding='utf-8').write(new)
            fixed += 1
    # 裸导入审计（必须为零）
    bare = set()
    for root, _, files in os.walk(OUT):
        for f in files:
            if not f.endswith('.js'):
                continue
            for m in re.finditer(r"""from\s+['"]([^'"]+)['"]""", open(os.path.join(root, f), encoding='utf-8').read()):
                spec = m.group(1)
                if not spec.startswith('.') and spec != '@dicebear/core':
                    bare.add(spec)
    size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(OUT) for f in fs)
    print(f'total: {total} files, {size/1024/1024:.1f} MB → vendor/dicebear/')
    if bare:
        print('UNEXPECTED bare imports:', bare)
        return 1
    print('bare imports: only @dicebear/core (mapped via import map) ✓')
    return 0


if __name__ == '__main__':
    sys.exit(main())
