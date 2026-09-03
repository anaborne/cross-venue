"""Raw-first paginated pull of the public Polymarket US gateway.

Every page goes to disk before anything parses it, and the walk ends with a
reconciliation block (pages, rows retrieved, unique ids, duplicates, null ids).
"""
import json, os, ssl, sys, time, urllib.request
import certifi

CTX = ssl.create_default_context(cafile=certifi.where())

BASE = "https://gateway.polymarket.us"
OUT  = "data/raw/gateA/pmus"
RATE = 0.25  # 4 rps, the rate I run these APIs at. See METHOD.md.

def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "cross-venue-gateA/1.0"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
                return r.read()
        except Exception as e:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)

def walk(resource, key, page=500, cap=1000000):
    os.makedirs(f"{OUT}/{resource}", exist_ok=True)
    offset, pages, rows = 0, 0, []
    seen_ids = set()
    while True:
        raw = get(f"/v1/{resource}?limit={page}&offset={offset}")
        fn = f"{OUT}/{resource}/offset_{offset:06d}.json"
        with open(fn, "wb") as f:
            f.write(raw)
        batch = json.loads(raw).get(key, [])
        pages += 1
        rows.extend(batch)
        for r in batch:
            seen_ids.add(r.get("id"))
        print(f"  offset={offset:6d} returned={len(batch):4d} cum={len(rows):6d} uniq={len(seen_ids):6d}")
        # Terminate ONLY on an empty page. A short page is not the end of the
        # collection: /v1/markets?offset=2000 returns 499 rows because id 2451
        # is absent, and terminating there truncated a first pull at 2,499 of
        # a far larger universe.
        if not batch:
            break
        # Hitting the cap on a non-empty page means the walk is short. It raises
        # here, so that a truncated collection cannot reach the reconciliation
        # block below and be reported there as a complete run.
        if offset >= cap:
            raise RuntimeError(f"cap {cap} reached at offset {offset} on a non-empty page; walk is truncated")
        offset += page
        time.sleep(RATE)
    return rows, pages, seen_ids

if __name__ == "__main__":
    resource = sys.argv[1]; key = sys.argv[2]
    t0 = time.time()
    rows, pages, ids = walk(resource, key)
    print(f"\n--- RECONCILIATION: /v1/{resource} ---")
    print(f"pages fetched      : {pages}")
    print(f"rows retrieved     : {len(rows)}")
    print(f"unique ids         : {len(ids)}")
    print(f"duplicate rows     : {len(rows) - len(ids)}")
    print(f"rows with null id  : {sum(1 for r in rows if r.get('id') is None)}")
    print(f"elapsed            : {time.time()-t0:.1f}s")
    with open(f"{OUT}/{resource}_all.json", "w") as f:
        json.dump(rows, f)
    print(f"written            : {OUT}/{resource}_all.json")
