"""Gate A Q2: settlement-identity comparison, Kalshi vs Polymarket US.
A pair is settlement-identical only if SOURCE, TIME and EDGE CASES all match."""
import json,re,collections

K=json.load(open('data/raw/gateA/kalshi/open_markets.json'))
P=json.load(open('data/raw/gateA/pmus/markets_open.json'))
SER={s['ticker']:s for s in json.load(open('data/raw/gateA/kalshi/series_sports.json'))['series']}
LG={'KXMLBGAME':'mlb','KXNFLGAME':'nfl','KXEPLGAME':'epl','KXNBAGAME':'nba'}
MON=dict(zip('JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC'.split(),range(1,13)))

kev=collections.defaultdict(list)
for s,rows in K.items():
    for m in rows: kev[(s,m['event_ticker'])].append(m)
kk={};unparsed=[]
for (s,ev),ms in kev.items():
    mm=re.match(r'^KX\w+GAME-(\d{2})([A-Z]{3})(\d{2})(\d{4})?([A-Z]+)$',ev)
    if not mm: unparsed.append(ev); continue
    yy,mo,dd,_,t=mm.groups(); kk[(LG[s],f"20{yy}-{MON[mo]:02d}-{dd}",t)]=(s,ev,ms)
pg=collections.defaultdict(list)
for m in P:
    if m.get('marketType') not in ('moneyline','drawable_outcome'): continue
    mm=re.match(r'^(aec|atc)-([a-z0-9]+)-([a-z0-9]+)-([a-z0-9]+)-(\d{4}-\d{2}-\d{2})(?:-([a-z0-9]+))?$',m.get('slug',''))
    if mm: pg[(mm.group(2),mm.group(5),(mm.group(3)+mm.group(4)).upper())].append(m)

def window_hours(txt):
    """Extract the postponement/reschedule window, in hours, from rules text."""
    t=txt.lower()
    for pat,mult in [(r'within (\w+|\d+) days?',24),(r'within (\w+|\d+) weeks?',168),(r'(\d+) hours',1)]:
        m=re.search(pat,t)
        if m:
            v=m.group(1)
            words={'one':1,'two':2,'three':3,'four':4,'a':1}
            n=words.get(v, None)
            if n is None:
                try: n=int(v)
                except: continue
            return n*mult
    return None

def k_sources(series):
    return [f"{x.get('name')} <{x.get('url')}>" for x in (SER[series].get('settlement_sources') or [])]

def p_source(desc):
    m=re.search(r'Outcome sourced from ([^.]+)\.',desc or '')
    return m.group(1).strip() if m else None

pairs=sorted(set(kk)&set(pg))
rows=[]
for key in pairs:
    lg,date,teams=key
    s,ev,ms=kk[key]
    km=ms[0]
    ktxt=((km.get('rules_primary') or '')+' '+(km.get('rules_secondary') or ''))
    pm=pg[key][0]; ptxt=pm.get('description') or ''
    ksrc=k_sources(s); psrc=p_source(ptxt)
    kw=window_hours(km.get('rules_secondary') or ''); pw=window_hours(ptxt)
    # SOURCE identical: Polymarket US names exactly one authority, and Kalshi's
    # series list must be that same single authority and nothing else.
    src_ok = bool(psrc) and len(ksrc)==1 and psrc.lower().replace('the ','') in ksrc[0].lower()
    time_ok = (kw is not None and pw is not None and kw==pw)
    kcancel = 'fair price' in ktxt.lower() or 'fair market price' in ktxt.lower()
    pcancel = 'last fair market price' in ptxt.lower()
    edge_ok = (kcancel==pcancel) and time_ok
    rows.append(dict(league=lg,date=date,teams=teams,kalshi=ev,pmus=pm['slug'],
        k_sources='; '.join(ksrc) or '(none)',p_source=psrc or '(none)',
        k_window_h=kw,p_window_h=pw,src_ok=src_ok,time_ok=time_ok,edge_ok=edge_ok,
        identical=src_ok and time_ok and edge_ok))

print("--- RECONCILIATION: pair construction ---")
print(f"Kalshi open game events         : {len(kev)}")
print(f"  parsed into join keys         : {len(kk)}")
print(f"  DROPPED, ticker unparsed      : {len(unparsed)}  reason: doubleheader G1/G2 suffix -> {unparsed}")
print(f"PMUS moneyline/drawable markets : {sum(len(v) for v in pg.values())} in {len(pg)} game keys")
print(f"Pairs matched (league,date,teams): {len(pairs)}")
print(f"Pairs evaluated                 : {len(rows)}   dropped in evaluation: {len(pairs)-len(rows)}")
print()
print("--- WINDOW MISMATCH TABLE ---")
c=collections.Counter((r['league'],r['k_window_h'],r['p_window_h']) for r in rows)
for (lg,k,p),n in sorted(c.items()): print(f"  {lg:4s} kalshi={str(k):>5s}h  pmus={str(p):>5s}h  pairs={n:3d}  {'MATCH' if k==p else 'DIFFER'}")
print()
print("--- SOURCE TABLE ---")
c2=collections.Counter((r['league'],r['k_sources'],r['p_source']) for r in rows)
for (lg,ks,ps),n in sorted(c2.items()): print(f"  {lg:4s} x{n:3d}\n        kalshi: {ks}\n        pmus  : {ps}")
print()
print("--- VERDICT ---")
for f in ['src_ok','time_ok','edge_ok','identical']:
    print(f"  {f:10s} true: {sum(1 for r in rows if r[f]):3d} / {len(rows)}")
json.dump(rows,open('data/raw/gateA/pair_comparison.json','w'),indent=1)
print(f"\nSETTLEMENT-IDENTICAL PAIRS: {sum(1 for r in rows if r['identical'])} of {len(rows)}")
