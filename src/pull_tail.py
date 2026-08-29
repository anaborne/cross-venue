import json, os, ssl, time, urllib.request, certifi, sys
CTX=ssl.create_default_context(cafile=certifi.where())
OUT="data/raw/gateA/pmus/tail"; os.makedirs(OUT,exist_ok=True)
START=int(sys.argv[1]); PAGE=500
rows=[]; pages=0; off=START
while True:
    u=f"https://gateway.polymarket.us/v1/markets?limit={PAGE}&offset={off}"
    req=urllib.request.Request(u,headers={"User-Agent":"cross-venue-gateA/1.0"})
    for a in range(5):
        try:
            raw=urllib.request.urlopen(req,timeout=30,context=CTX).read(); break
        except Exception:
            if a==4: raise
            time.sleep(2**a)
    open(f"{OUT}/offset_{off:07d}.json","wb").write(raw)
    b=json.loads(raw).get("markets",[]); pages+=1; rows.extend(b)
    if not b: break
    off+=PAGE; time.sleep(0.25)
ids={r.get("id") for r in rows}
print(f"\n--- RECONCILIATION: /v1/markets tail from offset {START} ---")
print(f"pages fetched     : {pages}")
print(f"rows retrieved    : {len(rows)}")
print(f"unique ids        : {len(ids)}")
print(f"duplicates        : {len(rows)-len(ids)}")
print(f"null id           : {sum(1 for r in rows if r.get('id') is None)}")
json.dump(rows,open("data/raw/gateA/pmus/markets_tail.json","w"))
print("written           : data/raw/gateA/pmus/markets_tail.json")
