# data/raw/gateA/

`pair_comparison.json` is the one file under `data/` that is committed. It is the
74 scored pairs written by `src/compare_pairs.py` on its 2026-08-29 run, kept as
that run wrote it.

## Its `src_ok` and `edge_ok` fields are superseded

An audit on 2026-09-03 found two errors in the scoring code that produced them.
Both are fixed in the committed script, and this file was not rewritten.

- `src_ok` reads `true` on 27 of the 74 rows, all NFL. The test matched the
  Polymarket US source name against the whole Kalshi `settlement_sources` entry,
  URL included, and `nfl` appears in `https://www.nfl.com/` and nowhere in the
  name `the Governing League`. On the names alone the corrected figure is 0 of
  74, and no row here should read `true`.
- `edge_ok` reads `false` on all 74 rows. The test was ANDed with the time test,
  which is `false` on all 74, so the column repeated the time column and measured
  nothing of its own. On the edge-case term alone both venues fall back to a
  last-fair-price construct, and the corrected figure is 74 of 74.

`time_ok` (0 of 74), `identical` (0 of 74) and every other field are as scored
and are unaffected. The headline, 0 of 74 pairs settlement-identical, is
unchanged.

The file cannot be regenerated here, because the three files `compare_pairs.py`
reads are not committed. The correction dated 2026-09-03 at the foot of
[`../../../notes/gateA.md`](../../../notes/gateA.md) states what changed. The
corrected figures were derived from this file's own `k_sources` and `p_source`
fields and from the rules text quoted verbatim in that file's §2c and §2f.
`../../../notes/compare_pairs.log` carries the same notice about the two figures
the run printed.
