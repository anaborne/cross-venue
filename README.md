# cross-venue: are Kalshi and Polymarket US game moneylines the same contract?

This is the working repository for C5, one study in a series I run against US
prediction markets. The one before it is published at
<https://github.com/anaborne/kalshi-temperature-calibration>. C5 asked whether a
game-moneyline contract on Kalshi and the same game on Polymarket US are the
same contract (same settlement source, same settlement time, same edge-case
rules), so that a position on both legs is actually hedged. Where the rules
differ, the position is a bet on the difference.

## Status: Gate A complete, C5 killed

Gate A (venue independence, settlement identity, read path) ran 2026-08-27/28,
read-only, $0, no orders, no snapshots, no gap computed. The write-up with
per-claim confidence marks is in [`notes/gateA.md`](notes/gateA.md).

0 of 74 pairs are settlement-identical. Settlement source matches on 27/74,
settlement time on 0/74, edge cases on 0/74. Every pair fails on the same clause
in the same direction. Kalshi resolves a postponed game to a fair price if it is
not played within 48 hours / two days (43 MLB, 27 NFL, 4 EPL), and Polymarket US
waits two weeks on 74 of 74. The pre-committed kill threshold was 30
settlement-identical pairs. 0 < 30. C5 dies at Gate A.

The sample was drawn (74 pairs, against a 40-pair minimum) before the criteria
were applied and was not adjusted. Four MLB doubleheader events were dropped as
unparsed and are an open item.

## PLAN.md was committed after Gate A ran

`PLAN.md` was not in this repository while Gate A ran. I ran the gate against the
three questions and the §6 kill threshold (30) as I had written them down before
the pull, and the plan file itself was committed on 2026-08-28, after the gate
reported, from that same plan text. Three things could not be checked against the
file at the time: its definition of the universe and of a tradeable pair, the
exact wording of §6 beyond the threshold number, and the maker-rebate figure it
flags as unconfirmed. `notes/gateA.md` §0 records that gap as it stood, and a
dated correction at the foot of that file records the file's arrival.

Read `PLAN.md` as the record of what I committed to before the pull, with the
caveat that the ordering rests on the threshold having been written down first
and not on the file's commit date. `PLAN.md`'s Provenance section says the same
thing about itself.

## Layout

| path | what |
|---|---|
| `METHOD.md` | how I work here, and the Kalshi and Polymarket US API behaviour I checked, with the date on each item |
| `notes/gateA.md` | the Gate A write-up |
| `notes/compare_pairs.log` | stdout of the `src/compare_pairs.py` run that produced the 0/74 |
| `src/pull_pmus.py` | raw-first paginated pull of `gateway.polymarket.us/v1/{resource}`; terminates only on an empty page |
| `src/pull_tail.py` | resumes the same walk from a given offset |
| `src/compare_pairs.py` | joins Kalshi open game events to Polymarket US moneyline markets on `(league, date, teams)` and scores source / time / edge-case identity |
| `data/raw/gateA/pair_comparison.json` | the 74 scored pairs, written by `compare_pairs.py`; the one file under `data/` that is committed |

`data/` is otherwise gitignored. The raw pull behind Gate A is ~570 MB on the
working machine under `data/raw/gateA/`. It holds Kalshi `open_markets.json`,
`series_sports.json`, per-series market pages and the four contract-terms PDFs
(with text extractions), Polymarket US `markets_open.json` (30,720 open markets,
63 pages of 500 under `pmus/open/`), the full-collection walk under `pmus/markets/`
and `pmus/tail/`, one raw L2 order book under `orderbook/`, and the docs pages
read for the auth and fee claims.

## Reproducing

With the raw data in place (Python 3.10+, standard library only):

```bash
python3 src/compare_pairs.py
```

prints the reconciliation (115 Kalshi events, 111 parsed, 4 dropped; 2,448
Polymarket US moneyline/drawable markets in 1,462 game keys; 74 pairs), the
window and source tables, and `SETTLEMENT-IDENTICAL PAIRS: 0 of 74`, and
rewrites `data/raw/gateA/pair_comparison.json`. Re-run 2026-08-28 against the
same raw data: the counts above, and a JSON byte-identical to the committed
copy. Log at `notes/compare_pairs.log`.

Rebuilding the raw data is a live pull and will not reproduce the same sample,
because both venues' open-market sets move daily:

```bash
pip install certifi                       # the only third-party dependency
python3 src/pull_pmus.py markets markets  # data/raw/gateA/pmus/markets/offset_*.json, markets_all.json
python3 src/pull_tail.py 542500           # resume from an offset, writes markets_tail.json
```

`compare_pairs.py` reads `data/raw/gateA/pmus/markets_open.json` (the
`closed=false` walk) and `data/raw/gateA/kalshi/open_markets.json` /
`series_sports.json` (Kalshi `GET /markets?series_ticker=…&status=open` and
the sports series listing). I ran those Kalshi pulls and the `closed=false` walk
inline while working, and there is no committed script for them.

## Notes

Not investment advice. No capital was deployed, no orders were placed, and no
position was taken at any point in this study.

Repository status, appended 2026-08-28. This repository had no remote when the
earlier commits were written, and the sentence introducing it above began
"Private working repository". It was pushed to `anaborne/cross-venue` and made
public on 2026-08-28. The same publication pass updated those two statements of
repository status in place, rewrote this file's prose for a reader outside the
project, and replaced my internal verification notes with `METHOD.md`. Every
finding, number and correction is as it was.
