# Gate A: venue independence, settlement identity, read path

Date: 2026-08-27/28. Author: Immanuel Anaborne. The criteria, the kill threshold
and the reconciliation check were set before the pull, and I re-derived every
number below from the committed run log before publishing. The sample minimum
was set before the pull as well, in my own notes only, and §2a states what that
does and does not establish. All work read-only, $0, no orders, no snapshots
recorded, no gap computed. Raw responses under `data/raw/gateA/`.

Every claim below is marked. [V] means I checked it against a primary source I
name inline, [I] means I inferred it, [U] means I have not checked it. Nothing is
stated at higher confidence than its evidence. The convention is described in
[`METHOD.md`](../METHOD.md).

---

## 0. Blocking gap in the inputs: PLAN.md does not exist

[V] The repository contains exactly two tracked files, my running verification
notes and `.gitignore`. `PLAN.md` is absent from the working tree, from
`git log --all` (one commit, the scaffold), and from every branch and stash, and
`find` over the home directory to depth 4 returns nothing. Verified 2026-08-27.

I ran Gate A anyway, against the three questions and the §6 kill threshold (30)
as I had written them down before the pull. Three things could not be checked
against the plan and are carried forward as open items:

- the plan's own definition of "the universe" and of a tradeable pair
- the exact wording of §6 beyond the threshold number
- what value the plan currently records for the Polymarket US sports maker
  rebate. The rebate is verified below, and I cannot diff it against the
  unconfirmed figure the plan flags, so I cannot say whether the plan is wrong or
  merely unsourced.

Everything downstream of this gate was reasoned out against a document that was
not in front of it.

---

## 1. Venue independence

### 1a. The premise, corrected

My plan states that Robinhood Event Contracts "forwards to KalshiEx and rests on
Kalshi's book". [V] That is true and incomplete. Robinhood's own support page
*Event contracts overview* states verbatim:

> "Event contracts are offered by Robinhood Derivatives, LLC through either
> KalshiEX LLC, ForecastEX, LLC or Rothera Exchange and Clearing LLC."

<https://robinhood.com/us/en/support/articles/robinhood-event-contracts/>

Three exchanges. The same page states Robinhood Derivatives is a registered FCM
and [V] "does not make markets in any futures or event contracts". The front-end
conclusion holds, Robinhood is not a venue, and a collector that assumes
"Robinhood ⇒ Kalshi book" will mis-attribute every contract Robinhood routes to
ForecastEX or Rothera. I had taken the single-destination framing along with the
fact and had not checked it.

### 1b. Independent books

Registration status is [V] from the CFTC's own DCM register
(<https://www.cftc.gov/IndustryOversight/IndustryFilings/TradingOrganizations>),
read 2026-08-27.

| Entity | CFTC status | Own book? | Basis |
|---|---|---|---|
| Kalshi (KalshiEX LLC) | Designated | Yes | [V] own API serves `GET /markets/{ticker}/orderbook`; depth and quote behaviour measured directly and recorded in `METHOD.md` |
| QCX LLC d/b/a Polymarket US | Designated | Yes | [V] pulled a live L2 book here, see §3 |
| ForecastEx LLC | Designated | [I] Yes | CFTC register + Robinhood names it as a routing destination alongside Kalshi |
| Railbird Exchange, LLC | Designated | [I] Yes | CFTC register; DraftKings-acquired |
| Crypto.com Exchange LLC (CDNA) | Designated | [I] Yes | CFTC register |
| CME Group DCMs | Designated | [I] Yes | CFTC register; FanDuel Predicts is the front-end |
| Rothera Exchange and Clearing LLC | Designated | [I] Yes | CFTC register + named by Robinhood |
| Coinbase Derivatives, LLC | Designated | [I] Yes | CFTC register |
| Aristotle Exchange DCM, Inc. | Designated | [U] | CFTC register only |
| Gemini Titan, LLC | Designated | [U] | CFTC register only |
| Bitnomial Exchange, LLC | Designated | [U] | CFTC register only |

Only the first two rows are verified as operating books, by reading a book. The
rest are registration facts and not liquidity facts. A DCM designation says an
entity may operate a market, and says nothing about whether it currently runs one
with resting orders.

### 1c. Front-ends (not venues)

| Front-end | Rests on | Basis |
|---|---|---|
| Robinhood Event Contracts | KalshiEX + ForecastEX + Rothera | [V] Robinhood's own support page, quoted above |
| Webull | Kalshi | [I] Kalshi names Webull Financial LLC as a broker partner; Webull's own prediction-markets page is silent on the exchange, checked, it does not name Kalshi |
| Coinbase (retail app) | Kalshi | [U] press reporting only. Complicated by Coinbase owning its own DCM (Coinbase Derivatives), so do not assume one implies the other |
| DraftKings Predictions | CME + Crypto.com, migrating to Railbird | [U] trade press only |
| FanDuel Predicts | CME Group | [U] trade press only |
| IBKR ForecastTrader | ForecastEx | [U] not checked against IBKR's own docs |
| Truth Social | Crypto.com (own build cancelled) | [U] press only |

### 1d. What this section does NOT establish

I am not writing that the table above is the complete set of US-available venues.
The CFTC register carries a further ~15 entities in *Pending* status, and some may
be live by the time a collector runs. PredictIt and the Iowa Electronic Markets
operate under no-action letters and appear on no DCM list at all, and [U] I
checked neither. The correct operational statement is: these are the DCMs on the
CFTC register as of 2026-08-27, and only Kalshi and Polymarket US have been
verified to serve a book.

---

## 2. Settlement identity, the gate itself

### 2a. Sample construction

Live-tier only, both venues, 2026-08-27/28.

- Kalshi: full cursor walk of `GET /markets?series_ticker={S}&status=open` for
  `KXMLBGAME`, `KXNFLGAME`, `KXEPLGAME`, `KXNBAGAME`, giving 250 markets across
  115 events.
- Polymarket US: full offset walk of `GET gateway.polymarket.us/v1/markets?closed=false`,
  giving 30,720 markets, 63 pages, 0 duplicates, 0 null ids. 2,448 of them carry
  `marketType ∈ {moneyline, drawable_outcome}` across 1,462 game keys.
- Join key `(league, date, away+home)`, built from the Polymarket US slug and
  matched against the Kalshi event ticker.

Reconciliation, pair construction

| | count |
|---|---|
| Kalshi open game events | 115 |
| parsed into join keys | 111 |
| dropped, ticker unparsed | 4 |
| drop reason | doubleheader `G1`/`G2` suffix: `KXMLBGAME-26AUG292205AZSFG2`, `-26AUG291915BOSNYYG2`, `-26AUG291605AZSFG1`, `-26AUG291305BOSNYYG1` |
| Polymarket US game keys | 1,462 |
| pairs matched | 74 |
| pairs evaluated | 74 (0 dropped in evaluation) |

74 clears the 40-pair minimum I had set for myself. That minimum is not written
into `PLAN.md` §6 and cannot be checked against the pre-registration file; it is
asserted here only. The 4 doubleheaders are excluded from the
denominator and are an open item.

### 2b. Result

[V] 0 of 74 pairs are settlement-identical.

| dimension | pairs identical |
|---|---|
| settlement SOURCE | 0 / 74 |
| settlement TIME | 0 / 74 |
| edge-case definitions (cancellation fallback) | 74 / 74 |
| all three | 0 / 74 |

The source and edge-case rows are the corrected ones. The run log at
`notes/compare_pairs.log` carries the figures the scorer printed on the day,
27 / 74 and 0 / 74. The correction at the foot of this file states what was
wrong with each.

### 2c. What drives it: the postponement window

One clause differs on every pair in the sample, in the same direction, verbatim.

- Kalshi MLB (43 pairs): *"the market will remain open and close after the
  rescheduled game has finished (within two days). If the game is cancelled or
  rescheduled to over two days away, the market will resolve to a fair price"*
- Kalshi NFL (27 pairs): *"If the game is postponed but begins within 48 hours
  … If the game is not started within 48 hours, the market will resolve to a fair
  price"*
- Kalshi EPL (4 pairs): *"If the game is cancelled or rescheduled to over 48
  hours away, the market will resolve to a fair price"*
- Polymarket US (74 pairs): *"If the game is delayed, postponed, or suspended and
  not rescheduled to a date within two weeks of the originally scheduled date,
  the market will settle to the last fair market price."*

Phrase census over the 74 pairs, designed so that a match would have shown up
here if one existed:

| side | phrase | count |
|---|---|---|
| Kalshi | "(within two days)" | 43 |
| Kalshi | "begins within 48 hours" | 27 |
| Kalshi | "not started within 48 hours" | 27 |
| Kalshi | "rescheduled to over 48 hours away" | 4 |
| Polymarket US | "within two weeks of the originally scheduled date" | 74 |

48 hours against 336 hours, 74 of 74, no exceptions. The census was computed
inline over the same rules text and the script for it is not committed, so it is
not reproducible from this repository.

The economic content: a game postponed and replayed 3 to 13 days later settles at
last fair market price on Kalshi and on the actual game result on Polymarket US.
A position held across both legs is unhedged in that window. It is a bet on
whether the makeup game lands inside 48 hours, which is the exclusion criterion
the plan's §4 defines Gate A to catch.

Corroborating the market text, the binding contract-terms PDFs
(`assets.kalshi.com/contract_terms/`) carry the same 48-hour figure for
`NFLGAME`, `NBAGAME` and `MLBGAME`, so this is the contract.

### 2d. Settlement time also differs, independently

[V] (computed inline, script not committed) `expiration_time == endDate`: 0 / 74.
[V] (same) `expected_expiration_time == endDate`: 0 / 74. Neither is reproducible
from this repository; `compare_pairs.py` does not compute them.

Representative (MLB, `KXMLBGAME-26AUG272145AZSF` against
`aec-mlb-az-sf-2026-08-27`): Kalshi `expiration_time` `2026-08-31T01:45:00Z`,
`expected_expiration_time` `2026-08-28T04:45:00Z`, Polymarket US `endDate`
`2026-09-11T01:45:00Z`, a ~11-day separation consistent with the window
difference above.

Separately, [V] the `NFLGAME` contract terms fix *"Expiration time … 10:00 AM
ET"*, which matches neither the API's `expiration_time` nor `close_time` on any
market checked. Kalshi's own two statements of settlement time do not agree.
Flagged and unresolved.

### 2e. Settlement source: three new instances of a pattern the plan flagged

The plan records three Kalshi series whose named authority was wrong, changed
mid-sample, or absent. This pull found three more.

(i) [V] Kalshi's EPL series does not name the Premier League as a settlement
source. `KXEPLGAME.settlement_sources` is `ESPN`, `Fox Sports`. The governing
body is absent. Polymarket US says *"Outcome sourced from Premier League."*
4 pairs.

(ii) [V] Kalshi's `KXNHLGAME` contract-terms URL serves the wrong contract.
`settlement_sources` reads `NHL <https://www.nhl.com>`, and `contract_terms_url`
points to `assets.kalshi.com/contract_terms/NHLGAME.pdf`. That PDF is titled
`ACHIEVEMENTS`, governs `<achievement>` (its worked example is "The 2025 winner
of the French Open Men's Singles Championship"), and contains zero occurrences of
"hockey", "NHL", "puck" or "goal", grep-verified. Its postponement rule is two
weeks where NFL/NBA/MLB's is 48 hours, and its Source Agency clause is not
hierarchical where theirs are. The binding terms document for Kalshi's NHL game
series is a different contract. No NHL pairs entered the sample: `KXNHLGAME` is
not one of the four series this pull walked, so this does not affect the count.
It would have, in season. Whether the series had open events at the time was not
checked.

(iii) [V] Kalshi's API and its own binding contract terms name different sources.
For `KXNFLGAME` the API returns one source, `the Governing League <nfl.com>`.
`NFLGAME.pdf` states:

> "The Source Agencies are, in hierarchical order, the governing league or
> association of \<football game\> (e.g., the National Football League, NCAA,
> UFL), ESPN, CBS Sports, Fox Sports, NBC Sports, the Associated Press, The Wall
> Street Journal, and the official broadcaster of \<football game\>."

One name in the API, eight in the contract. Reading `settlement_sources` from the
API and treating it as the settlement authority is wrong for this series.

Source comparison across the sample

| league | pairs | Kalshi `settlement_sources` | Polymarket US market text | src match |
|---|---|---|---|---|
| nfl | 27 | the Governing League \<nfl.com\> | "Outcome sourced from NFL." | no, the two names differ |
| mlb | 43 | ESPN; Fox Sports; the Governing League \<mlb.com\> | "Outcome sourced from MLB." | no, 3 against 1 |
| epl | 4 | ESPN; Fox Sports | "Outcome sourced from Premier League." | no, governing body absent on Kalshi |

The NFL row read "yes" until 2026-09-03. Kalshi's API names *the Governing
League* and Polymarket US names *NFL*, and the scorer counted the 27 as matches
because it searched the whole `settlement_sources` entry, URL included, and
`https://www.nfl.com/` contains the token. On the names alone the two venues
name different things, and the source dimension is 0 of 74. The correction at
the foot of this file has the detail. The API field is separately contradicted
by the contract terms per (iii).

[V] Polymarket US's own hierarchy (Sports FAQs, `docs.polymarket.us/faqs/sports-faqs.md`)
is primary the governing body, secondary official scorecards, referee and umpire
reports, press releases and governing-body results databases, tertiary AP,
Reuters, ESPN, BBC Sport, official team and league sites and wire services.
Compared to Kalshi's NFL chain, only the first rung agrees. Kalshi lists CBS,
NBC, the WSJ and the broadcaster; Polymarket US lists Reuters and BBC. No pair in
the sample has an identical source cascade.

### 2f. What does match

For completeness, the parts that are identical and are not enough:

- [V] Tie handling, NFL. Both settle $0.50 per side. Kalshi's contract terms
  generalise to `$1/n` rounded down, and Polymarket US's FAQ says the same for
  co-winners.
- [V] EPL scope. Both are "90 minutes plus stoppage time", excluding extra time
  and penalties.
- [V] Cancellation in kind. Both fall back to a last-fair-price construct (Kalshi
  "a fair price in accordance with the rules", Polymarket US "last fair market
  price"). Whether those two constructs compute the same number is [U].
  Polymarket US defines LFMP precisely, as the price at the moment of the
  official announcement and explicitly not the last traded price at close, while
  Kalshi's "fair price in accordance with the rules" is not defined in the market
  text. A pair could differ here even where the phrasing looks parallel.

### 2g. A checked-and-discarded discrepancy

Market id 1 (`aec-nfl-lac-ten-2025-11-02`, closed) carries older language, *"If
the game is postponed, this market will remain open until the game has been
completed"* and *"will resolve 50-50"*, which contradicts both the current
template and the Sports FAQ. [V] Neither string appears in any of the 30,720
currently-open Polymarket US markets (0 and 0). It is superseded legacy text and
not a live inconsistency. Recorded because a sample drawn from settled markets
would have hit it, and it would have looked like a live contradiction.

---

## 3. Read-path confirmation

### 3a. The plan's endpoint is real, and is not the cheapest path

[V] `GET /v1/orderbook/{symbol}` exists and returns L2 depth. From Polymarket
US's own OpenAPI schema, served inside
`docs.polymarket.us/api-reference/order-book/get-order-book.md`, the response
carries `bids` and `offers`, each an array of `BookEntry {px, qty}`, plus
`state`, `stats` and `transactTime`. Aggregated price levels, so L2. Confirmed.

[V] Maximum depth parameter 10, default 3. Stated twice in the venue's own docs
and consistent. The OpenAPI parameter block reads *"Number of price levels to
return (default 3, max 10)"*, and the Order Book API Overview's
request-parameter table reads *"default: 3, max: 10"*.

### 3b. The JWT / no-KYC claim: partly confirmed, and the framing is wrong

[V] The scope is real. `read:marketdata` appears 7 times across the docs corpus.
The Order Book API Overview states verbatim:

> "These endpoints only require Auth0 JWT authentication with `read:marketdata`
> scope. You do not need to provide the `x-participant-id` header or complete KYC
> onboarding to access order book data."

[V] "No KYC" is not "no gating", and the plan conflates two different APIs with
two different auth schemes. There are three surfaces.

| surface | host | auth | gate |
|---|---|---|---|
| Institutional/Exchange | `api.prod.polymarketexchange.com` | Auth0 Private Key JWT (RSA, `client_credentials`) | entity registration at `institutional.polymarketexchange.com/register`, a signed Entity Participant and Clearing Member Agreement, then *"The Polymarket team will review your submission and provide your Client ID"*, so manual issuance |
| Retail | `api.polymarket.us` | `X-PM-Access-Key` / `X-PM-Timestamp` / `X-PM-Signature`, Ed25519 | app account plus *"Complete identity verification"* before API access |
| Public gateway | `gateway.polymarket.us` | none | none |

Probed, saved under `data/raw/gateA/`.
`api.polymarket.us/v1/orderbook/TEST` returns `401 "Missing required API key headers"`.
`api.prod.polymarketexchange.com/v1/orderbook/TEST` returns `401 {"message":"Unauthorized"}`.

So the orderbook endpoint does not require KYC in the retail sense, and the docs'
claim is accurate on its own terms. It is still not obtainable at $0 here,
because the JWT requires a countersigned entity agreement and manual credential
issuance. I did not obtain one and make no claim that the path works end to end.
Marked [U].

### 3c. A sibling endpoint serves the same data free, and deeper

Rather than conclude that the book costs an entity onboarding, I checked the docs
index. [V] `GET gateway.polymarket.us/v1/markets/{slug}/book` is declared
`security: []` in the same OpenAPI spec and is fully unauthenticated.

Raw response saved to disk before parsing, as with every pull here:
`data/raw/gateA/orderbook/aec-valorant-nrg-loud-2026-08-28_book_raw.json`
(2,444 bytes, `HTTP/2 200`, headers in `..._headers.txt`).

Reconciliation of that raw response

| | |
|---|---|
| HTTP status | 200 |
| bytes retrieved | 2,444 |
| bid levels retrieved | 12 |
| bid levels parsed | 12 |
| offer levels retrieved | 10 |
| offer levels parsed | 10 |
| levels dropped | 0 |
| best bid / best offer | 0.7800 / 0.7900 |
| `state` | `MARKET_STATE_OPEN` |
| `transactTime` | 2026-08-28T03:55:58.653583739Z |

[V] It ignores `depth` entirely and returns the full book. `depth=1`, `3`, `5`,
`50`, `1000` and no-param all return the identical 12/10. Across 25 live markets
the level count varies with the market, 3 to 14 per side on two-sided books and 0
on the thin side of several one-sided NFL prop books, so it is not truncating at
a constant. The free endpoint is deeper than the institutional one's max of 10.

[V] The two endpoints have incompatible schemas, and the difference is silent.
Institutional: `px` is a flat string (`"px": "0.78"`). Public gateway: `px` is a
nested object (`"px": {"value": "0.7800", "currency": "USD"}`), and the book sits
under a `marketData` wrapper. A parser written against the OpenAPI spec in the
plan and pointed at the free endpoint reads `px` as a dict, the same failure
shape as the `*_dollars` rename already recorded in `METHOD.md`.

[V] One-sided books are present here too. Several NFL prop markets returned
`bids=0` or `offers=0` with the other side populated, matching the 17.3%
one-sided finding on Kalshi in `METHOD.md`. A midpoint computed without a
two-sided check is not a price on this venue either.

Implication for the plan: if the read path exists only to sample displayed depth,
the entity onboarding is not required, the cost is $0, and the data is better.
That should be resolved before anyone signs an Entity Participant Agreement.

---

## 4. The flagged number: Polymarket US sports maker rebate

Read from the venue's own binding fee schedule, `https://docs.polymarket.us/fees.md`,
saved at `data/raw/gateA/pmus_fees.md`. Not a third-party summary.

[V] Maker rebate θ = −0.0125, in `Fee = Θ × C × p × (1−p)`, where `C` is
contracts and `p` the decimal price. Maximum −$0.31 per 100 contracts at
p = $0.50. Applied at the point of trade, credited to balance at fill, computed
per fill independently of the taker-side rounding adjustment. Banker's rounding
to the cent. Taker θ = 0.06 (max $1.50/100).

Schedule header: "Effective exchange-wide from 12 AM ET, Wednesday July 1, 2026."

[V] There is no sports-specific maker rebate. A negative claim gets the full
check described in `METHOD.md`.

- The fee schedule's own banner says exchange-wide.
- The complete docs index `llms.txt` (350 lines, saved) contains exactly two
  fee-schedule entries, both pointing at the same `/fees.md`. There is no second,
  sport-scoped schedule.
- The Sports FAQs page contains no fee or rebate section.

[V] Cross-checked exhaustively against live data. All 30,720 / 30,720 open
Polymarket US markets carry `feeCoefficient: 0.06`, matching the exchange-wide
taker θ. Grouped by league slug, zero leagues carry any other value. The
schedule is flat across the venue as claimed.

Contrast worth carrying forward. `METHOD.md` records that Kalshi's `fee_type` is
per-series and varies within a sport (game series are
`quadratic_with_maker_fees`, player props are plain `quadratic` with no maker
fee) and that `fee_type` is not even constant over a series' archive. This pull
adds [V] that `KXMLBGAME` carries `fee_multiplier: 0.5` and `exchange_index: 3`
where NFL/NBA/NHL game series carry `1` and `0`. Polymarket US is flat and Kalshi
is not, so any cross-venue net-of-fee figure must read Kalshi's fee per series
(and per era) and may use a constant only on the Polymarket US leg.

---

## 5. A truncation this pull produced and caught

The first Polymarket US pull terminated on a short page and reported 2,499
markets. It was wrong. `/v1/markets?limit=500&offset=2000` returns 499 rows
because id 2451 is simply absent from the collection, and not because the
collection ends. A binary probe puts the true size between offsets 542,577 and
542,968. The first number was low by a factor of ~217.

`src/pull_pmus.py` now terminates only on an empty page, with the reason in a
comment at the break. Logged because it is the recurring shape in `METHOD.md`, a
plausible-looking count that makes the scope look smaller than it is, and because
it fired inside the pull that was written to guard against it.

Appended 2026-09-03. It fired a third time, in the same script. `walk()` carried
a `cap=400000` in its loop condition, so a full-collection walk would have
stopped at offset 399,500 holding 400,000 rows of a collection the probe above
sizes between 542,577 and 542,968, and the reconciliation block would have
reported that as a complete run. The cap no longer stops the walk. It raises on
a non-empty page, and its default is above the probed size. The Gate A count is
unaffected, which came from the 63-page `closed=false` walk and never reached
the cap.

---

## 6. Count, and the §6 test

Settlement-identical pairs: 0 of 74 evaluated.

PLAN.md §6 kills C5 below 30. 0 < 30.

The sample was not adjusted to reach the threshold and is not adjusted now. It
was drawn before the criteria were applied, at 74 pairs, 85% above the 40-pair
minimum recorded in §2a, and every one of the 74 fails on the same clause, in
the same direction, with no borderline cases. 48 hours against two weeks,
verbatim, 74/74.

Reporting and stopping here, as §6 requires.

### What would change this number, for whoever reads it next

Stated so the result is not over-read. The finding is that Kalshi and Polymarket
US game moneylines are not the same contract. It is not a finding that no
tradeable pair exists anywhere.

1. Untested contract families. Only game moneyline and drawable outcome was
   joined. Spreads, totals, player props and futures were not compared and may
   carry different postponement language. [U]
2. The 4 dropped doubleheaders were never evaluated. [U]
3. Untested venue pairs. Kalshi against Polymarket US only. Kalshi against
   Railbird, Kalshi against CME and Polymarket US against CME were not examined.
   [U]
4. The window could be a policy and not a contract. Both figures are current
   live-tier text. Whether either venue has changed its window historically is
   [U], and `METHOD.md` already records Kalshi changing a settlement authority
   mid-sample, so this is a live possibility.
5. If the 48h / two-week gap ever closes, the remaining blockers are the source
   cascades (§2e) and the undefined relationship between Kalshi's "fair price in
   accordance with the rules" and Polymarket US's precisely-defined LFMP (§2f).
   Neither is resolved by the window matching.

---

## Correction, appended 2026-08-29: PLAN.md now exists in the repository

§0 above was true when written. `PLAN.md` was committed on 2026-08-29, after this
gate ran, from the plan text Gate A was run against. Its §6 reads "Gate A finds
fewer than 30 settlement-identical market pairs → C5 dies", which is the
threshold this gate applied. The three open items in §0 (the universe and pair
definitions, the exact §6 wording, the maker-rebate figure) can now be checked
against the file, and the maker-rebate figure was already resolved in §4 above
from the venue's own schedule. Everything above this line is left as written.

The full §6 line reads "Gate A finds fewer than 30 settlement-identical market
pairs → C5 dies, or shrinks to the identical subset and is re-scoped." The
paragraph above quotes only the first branch. The kill is unaffected, because the
identical subset measured 0 pairs and the re-scope branch has nothing to re-scope
onto. Recorded here, and the paragraph above stands as written.

---

## Correction, appended 2026-09-03: two of the three scored dimensions were wrong

An audit of the scoring code found two errors in `src/compare_pairs.py`. Both are
fixed in the committed script. The headline is unchanged: 0 of 74 pairs are
settlement-identical, and every pair still fails on the postponement window.

Settlement source, 27 / 74 to 0 / 74. The test was
`psrc.lower() in ksrc[0].lower()`, and `ksrc[0]` is the Kalshi source name
followed by its URL. On the 27 NFL pairs the Kalshi entry is
`the Governing League <https://www.nfl.com/>` and the Polymarket US source is
`NFL`. The token `nfl` appears in the URL and nowhere in the name, so all 27
matches came from the hostname. The test now reads the name half only, and no
pair in the sample matches on source.

Edge cases, 0 / 74 to 74 / 74. The line read
`edge_ok = (kcancel==pcancel) and time_ok`. The `and time_ok` conjunction forced
the edge-case column to False on every pair whose window differed, which is all
74, so the column reported the time column and measured nothing of its own. On
the edge-case term alone both venues fall back to a last-fair-price construct on
all 74, which is what §2f already said in prose. `identical` ANDs the three
columns separately and is unaffected. Whether the two fallback constructs compute
the same number is still [U], per §2f.

Four further changes to the same script do not move a published number. The
Kalshi postponement window is now read from `rules_primary` and
`rules_secondary` together, where it was read from `rules_secondary` alone while
the cancellation test already read both. `window_hours` now reads only sentences
that mention a postponement, reschedule, delay or suspension, where it used to
return the first time phrase anywhere in the blob and ranked days ahead of hours
regardless of position. A series outside the four-entry league map used to raise
`KeyError`, and is now recorded as a drop. The reconciliation block now prints the
Kalshi join keys with no Polymarket US counterpart (37 on this run, previously
unreported), the count of Polymarket US markets of the right type against the
count whose slug parsed, and any pair where a window could not be read.

The two window changes were exercised against the rules text quoted verbatim in
§2c, and reproduce the 48 / 336 split on all three leagues. They could not be
re-checked against the raw pull, which is not committed, so a window figure
moving under the wider read is [U].

`notes/compare_pairs.log` and `data/raw/gateA/pair_comparison.json` are the
outputs of the 2026-08-29 run and are left as they were printed. They carry the
27 / 74 and 0 / 74 figures. Neither can be regenerated here, because the three
files `compare_pairs.py` reads are not committed. The corrected figures above
were derived from the committed `pair_comparison.json`, which records each pair's
Kalshi source list and Polymarket US source string, and from the rules text
quoted verbatim in §2c and §2f.
