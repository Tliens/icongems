#!/bin/bash
# Fetch all IP as Logo display-512 webp images into ipas/display/.
# Reads keys from data/ipas-logos.json (regenerate via scripts/ipas-data.py first).
# Retries failures; verifies RIFF/WEBP magic bytes. Safe to re-run (skips existing).
set -u
cd "$(dirname "$0")/.."
mkdir -p ipas/display

python3 -c "
import json
d = json.load(open('data/ipas-logos.json'))
print('\n'.join(d['logos']))" > /tmp/ipas-keys.txt

TOTAL=$(wc -l < /tmp/ipas-keys.txt | tr -d ' ')
echo "fetching $TOTAL display images -> ipas/display/"

fetch_one() {
  key="$1"
  out="ipas/display/${key}.webp"
  [ -s "$out" ] && return 0
  for attempt in 1 2 3; do
    curl -sf --http1.1 -m 30 --retry 1 -o "$out" "https://cdn.ipaslogo.com/display-512/${key}.webp" && return 0
    sleep $((attempt * 2))
  done
  echo "FAIL $key" >> /tmp/ipas-fail.txt
  rm -f "$out"
  return 1
}
export -f fetch_one

: > /tmp/ipas-fail.txt
xargs -P 16 -I {} bash -c 'fetch_one "$@"' _ {} < /tmp/ipas-keys.txt

# byte-level verification (RIFF....WEBP magic); refetch anything invalid
python3 - << 'EOF'
import json, os, subprocess
d = json.load(open('data/ipas-logos.json'))
retry = [k for k in d['logos']
         if not os.path.exists(f'ipas/display/{k}.webp')
         or b'WEBP' not in open(f'ipas/display/{k}.webp','rb').read(12)]
for k in retry:
    subprocess.run(['bash','-c',f'curl -sf --http1.1 -m 30 -o "ipas/display/{k}.webp" "https://cdn.ipaslogo.com/display-512/{k}.webp"'])
bad = [k for k in d['logos']
       if b'WEBP' not in open(f'ipas/display/{k}.webp','rb').read(12)] if all(
       os.path.exists(f'ipas/display/{k}.webp') for k in d['logos']) else ['missing files']
print('refetched:', len(retry), '| still bad:', len(bad), bad[:10])
exit(1 if bad else 0)
EOF

OK=$(ls ipas/display | wc -l | tr -d ' ')
echo "present: $OK / $TOTAL"
echo OK
