# C5, cross-venue price dispersion. Study plan, 2026-08-28

Written when I picked C5 back up. I had shelved it for three reasons and two of
them do not survive contact.

---

## 0. A correction before anything else

I had been carrying the claim that Polymarket US charges 5% taker on sports, so
a gap would have to be enormous to clear it. It is wrong, and it was wrong when I
wrote it into a private planning note.

Polymarket's fee is the same quadratic shape as Kalshi's, `fee = C × rate × p × (1-p)`,
and the 0.05 is the rate inside that formula. Verified
against Polymarket's own fee documentation and a published side-by-side.

Taker cost per 100 contracts at a 50c price:

| Venue | Sports taker | Per contract |
|---|---|---|
| Kalshi (rate 0.07) | $1.75 | 1.75c |
| Polymarket US (rate 0.05) | $1.25 | 1.25c |
| Polymarket global (rate 0.03) | $0.75 | 0.75c, and inaccessible |

Polymarket US is cheaper than Kalshi on sports takers. I inherited the number
that helped shelve C5 without checking it, the same way I inherited the phantom
68-day ceiling recorded in `METHOD.md`.

The maker side is the larger fact. Polymarket charges makers zero and advertises
a maker rebate on sports. Kalshi's maker rate is 0.0175, which is 0.44c per
contract at 50c.

| Execution shape | Fee per matched pair at ~50c |
|---|---|
| taker on both legs | ~3.0c |
| maker on Polymarket, taker on Kalshi | ~1.75c |
| maker on both legs | ~0.44c |

A factor of seven between the best and worst execution of the identical trade.
Any C5 measurement that assumes taker-taker is measuring the worst version of the
strategy, and any measurement that assumes maker-maker is measuring one that may
be unfillable. Both must be reported, and neither may be chosen after the numbers
arrive.

The maker-rebate claim is the one number here not yet read from a binding venue
document. Confirm it against Polymarket US's own fee schedule before it is
load-bearing.

## Second correction: Robinhood is not a venue

Robinhood Event Contracts forwards orders to KalshiEx and they rest on Kalshi's
order book. Prices match to the cent, there is no Robinhood-internal market
making, and there is no public API. It is a front-end onto a book already in the
universe, so it offers no cross-venue gap and cannot be an arb counterparty.

This is the cheapest kill available and it must be run first against every
candidate venue. A "six venue" universe that is really three books with
front-ends attached is a different problem, and I never checked my own venue
count for this.

## Third correction: the slippage figures were never about Kalshi

I had been citing 0.05c slippage against 3.62c on a 50,000-contract order. That
is Polymarket global against Polymarket US, a comparison between two Polymarket
venues, one of which is inaccessible. It says Polymarket US's book is thin. It
says nothing about a Kalshi-to-Polymarket-US gap, which is the only pair actually
available.

---

## 1. What survives of the case for shelving C5

| Reason I shelved it | Status |
|---|---|
| "5% taker means the gap must be enormous" | Dissolved. The fee is roughly Kalshi's, and cheaper on sports. |
| "$50 a venue is not a position" | Dissolved as an objection to studying it. It is a deployment constraint. Measurement costs $0. |
| "It is the most obvious idea on the list, which is a reason for suspicion" | Stands, unchanged. |

The third reason is now the whole of the case against, and it is a prior.

---

## 2. Where the "capital does not change anything" argument fails

It holds for a forecast study. The daily-temperature calibration study and an
earlier sports study were forecast studies, their edge lived in a probability
estimate, and the size of the hypothetical position changed nothing about whether
the estimate was right.

C5's entire edge lives in execution, and every execution quantity is a function
of size. Slippage is a function of size. Fill probability on a resting leg is a
function of size. The number of price levels you consume is a function of size.
The figure quoted above, 0.05c against 3.62c, is a size-dependent number,
measured at 50,000 contracts.

So the study does not pick a capital number and test at it. It sweeps size and
emits an edge-versus-size curve, and the capital number falls out of where that
curve crosses zero. A single-size paper test would answer a question nobody
asked.

---

## 3. C5 cannot be backtested. It has to be recorded forward.

Kalshi has a historical tier. Polymarket US's order book API serves snapshots
only, with no historical endpoint. And even with two archives, an arb needs
simultaneous quotes on both venues, which hourly candlesticks on two independent
clocks cannot establish.

This inverts the shape of the work from the last two studies. Cheap in money,
expensive in calendar. It is a collection job that runs unattended for weeks,
then a one-day analysis.

The Polymarket US read path is available. `GET /v1/orderbook/{symbol}` returns L2
depth up to 10 price levels, `GET /v1/orderbook/{symbol}/bbo` returns top of
book, a gRPC market-data stream exists for continuous use, and read-only market
data needs only a JWT with `read:marketdata` scope, with no KYC. Kalshi's live
book is already reachable from the client in my sibling repository,
<https://github.com/anaborne/kalshi-temperature-calibration>.

---

## 4. The staged test

Same funnel discipline as the two studies before it. Each gate is pre-registered
before the data behind it exists.

### Gate A: settlement identity. $0, one day, and it is the likeliest kill.

Two venues listing "the same" event is not the same contract. Settlement source,
timing and definition are where they differ, and I have already logged three
instances of a Kalshi series whose named authority was wrong, changed mid-sample,
or absent entirely.

Read `rules_primary` on Kalshi and the equivalent resolution text on Polymarket
US for a sample of matched markets. Record, per pair, whether the settlement
source, the settlement time, and the edge-case definitions are identical.

A pair whose resolution criteria differ is an unhedged bet on the discrepancy. It
must be excluded from the universe. If the identical-settlement universe is
small, C5 shrinks to that universe or dies there.

Also settled at Gate A, both $0. Whether Polymarket US serves New York, and which
of the candidate venues are independent books (the Robinhood finding above).

### Gate B: does a fee-clearing gap exist, and at what size. Free, two to three weeks unattended.

A scheduled collector on a single always-on host writes synchronized snapshots of
both books at a fixed cadence, 15 seconds or faster, capturing full available
depth on both sides, with local timestamps and a recorded clock offset between
the two captures.

Depth is the whole point. Top of book answers "is there a gap" and the question
is "how much of one".

From that series, compute the gross gap and then the net gap under all three
execution shapes from §0, at each of a pre-registered ladder of sizes. Report the
edge-versus-size curve per venue pair and per month, with no pooled figure.

### Gate C: leg risk, from the same recording, no extra collection.

A gap you cannot fill both sides of is not an edge. From the snapshot series,
measure how long a fee-clearing gap survives before it closes, and how often it
closes against you.

This is the number that decides whether the maker-maker execution in §0 is
reachable or fictional, and it is measurable for free from data already being
collected for Gate B.

### Gate D: real fills. The first place money appears.

Snapshots do not prove fills. Place minimum-size real orders on both venues
against gaps the recording flags live, and compare the achieved fill against the
snapshot-implied price. Twenty to thirty round trips is enough to see whether the
recorded book is the book you actually trade against.

An earlier study of mine could never take this step, because its size data did
not exist at any price. C5 can take it, which is the strongest structural
argument for preferring it.

---

## 5. Money

| Stage | Cost |
|---|---|
| Gates A, B, C | $0. Both read paths are free and unauthenticated or JWT-only. |
| Gate D | Low three figures, funding minimum-size orders on both venues. |
| Deployment | Emitted by Gate B's curve. Not chosen in advance. |

The capacity arithmetic, so the ceiling is known before any capital moves. A
matched pair ties up roughly $0.95 of collateral, split across two venues that
cannot share it. Per $1,000 of pre-positioned capital that is on the order of
1,000 pairs at full deployment. At a 5c gross gap and taker-taker fees of 3.0c,
about $20 net per fully-deployed opportunity; at maker-maker fees of 0.44c, about
$45.

Any first deployment, if Gates A through D clear, is therefore sized by
pre-positioning, because collateral cannot move between
venues fast enough to chase a gap. Size is an output of the Gate B curve and is
not declared here.

Stated before the study runs, so the capacity cannot be discovered as a
disappointment afterwards. At those numbers C5's annual capacity at retail size
is four figures unless the measured gaps are far wider or far more frequent than
the arithmetic above assumes, and it does not scale into a strategy of
consequence at any capital level a retail participant can pre-position across two
venues. It is worth running because the measurement is free and the answer is not
known, and it is worth running now because the same collection infrastructure
serves any future cross-venue question.

---

## 6. Kill criteria, committed now

- Gate A finds fewer than 30 settlement-identical market pairs → C5 dies, or
  shrinks to the identical subset and is re-scoped.
- Polymarket US does not serve New York → C5 dies on access, with no workaround
  sought.
- Gate B's edge-versus-size curve is below zero at every size under taker-taker
  execution and maker-maker execution is shown unreachable at Gate C → C5 dies.
- Gate D's achieved fills diverge from snapshot-implied prices by more than the
  measured edge → C5 dies, and that is the earlier study's size problem arriving
  through a different door.
- Any change to a pre-registered element after a number from that gate is seen →
  C5 dies. Same clause, same reason, third study.

## 7. Standing constraints, unchanged

New York jurisdiction risk applies to Kalshi and now to a second venue as well,
and pre-positioned collateral on two venues is exactly the shape of exposure a
geofence event would strand. Collateral committed to an open arb is working
capital, but a fence lands on both legs at once and the
hedge does not protect against the venue itself becoming unreachable.

Polymarket global remains out of scope. Access from New York would mean
misrepresenting residency, and no workaround is to be found.

---

# Provenance of this file

Recorded 2026-08-28, appended when the file was first committed to this
repository.

Everything above the "Provenance" heading was written on 2026-08-28, before Gate
A ran and before any Gate A data existed. The version first committed here was
reproduced byte-for-byte as authored, and nothing above had been edited,
reordered or softened at that point. Two later passes changed the text of this
file, and both are recorded below the Provenance section. No figure, threshold,
gate definition, kill criterion or measured result was changed by either.

It reached the repository late for a mundane reason. The `cp` that was supposed
to place it here pointed at a path the file was not at, failed without stopping
the rest of the sequence, and I did not notice until after Gate A had reported.
Gate A therefore ran against §6's kill threshold as I had written it down
beforehand, and `notes/gateA.md` §0 records that the file itself was not
available at the time.

Two facts support the ordering.

1. The document carries a creation timestamp dated before the Gate A run, in the
   notes it was authored in. Only I can check that one.
2. §6's threshold ("PLAN.md section 6 kills C5 below 30") was written down and
   quoted before the pull, and `notes/gateA.md` records that the file itself was
   never available while the gate ran. A threshold fixed before the data existed
   is what pre-registration turns on.

A plan committed after its own result should be read with suspicion. What
supports it is the threshold having been written down first, and not this note's
assurance.

---

# Correction 1: three figures in §0 were wrong, and the kill fired

Recorded 2026-08-28, after Gate A, and appended below. The sections it corrects
stand as written.

## The gate result

0 of 74 sampled Kalshi and Polymarket US event pairs are settlement-identical.
§6 kills C5 below 30. The criterion fired.

One clause carries it, and it is not interpretive. Kalshi settles a postponed
game at last fair price within 48 hours (43 MLB, 27 NFL, 4 EPL). Polymarket US
honours the actual result "within two weeks of the originally scheduled date" (74
of 74). A game replayed 3 to 13 days late therefore cashes out one leg at a price
while the other pays on the outcome, which is the unhedged bet on the discrepancy
that §4's Gate A exists to detect. `expiration_time == endDate` on 0 of 74 as
well. The 48-hour figure is corroborated in Kalshi's binding contract-terms PDFs,
so it is the contract.

The sample was drawn at 74, 85% above the 40 I had set as the minimum, before the
criteria were applied. Every pair fails on the same clause in the same direction
with no borderline cases.

## §0's fee arithmetic was wrong in three places

Each of these came from a third-party comparison page or a single documentation
page. None came from the venue's own binding schedule. The direction of §0's
conclusion survives and its numbers do not.

| §0 claimed | Gate A measured |
|---|---|
| Polymarket US sports taker rate 0.05, $1.25 per 100 at 50c | `feeCoefficient` 0.06 across 30,720 of 30,720 open markets, no league variation. $1.50 per 100 at 50c. |
| A maker rebate specific to sports | θ = −0.0125 exchange-wide from 2026-07-01, max −$0.31 per 100 at p=0.50. No sports-specific rebate. |
| Robinhood forwards to KalshiEX | Robinhood Derivatives forwards to KalshiEX, ForecastEX or Rothera. The front-end conclusion holds; the single-destination framing was wrong. |

Corrected execution arithmetic per matched pair at a 50c price. Taker on both
legs 3.25c (Kalshi 1.75 plus Polymarket US 1.50). Maker on both legs 0.13c
(Kalshi 0.44 plus Polymarket US −0.31). The spread between best and worst
execution is a factor of roughly 25, against the 7 stated in §0, and
Polymarket US remains the cheaper venue on takers, which was §0's point.

None of it changes the Gate A outcome, because settlement identity gates
everything downstream of it.

## Two further corrections to §3 and §4

A cheaper read path exists than §3 specified.
`gateway.polymarket.us/v1/markets/{slug}/book` carries `security: []`, requires
no authentication, ignores the depth parameter, and returns the full book up to
14 levels per side, deeper than the institutional endpoint's documented cap of
10.

§3's authentication claim conflated three surfaces. "Read-only market data needs
only a JWT with `read:marketdata` scope and no KYC" is accurate on its own terms,
and the JWT itself still requires a signed Entity Participant Agreement and
manual credential issuance. No end-to-end claim about that path was established.

## What Gate A returned that outlives C5

Three further instances of the resolution-authority pattern I track as a standing
habit. `KXEPLGAME` names no league in its settlement terms, listing only ESPN and
Fox Sports. `KXNHLGAME`'s contract-terms URL serves a PDF titled ACHIEVEMENTS
containing no mention of hockey. `KXNFLGAME` names one source in the API against
eight in its own contract terms, which means reading `settlement_sources` from
the Kalshi API is not a statement of what governs a series.

One reconciliation catch on my own work. The first Polymarket US market pull
terminated on a short page and reported 2,499 markets against a true count near
542,800, low by 217×, because id 2451 is absent. Caught by the reconciliation,
fixed and logged.

## Status

C5 is dead at Gate A, at a cost of $0 and one day. Gates B, C and D were never
built and no snapshot was ever recorded. The paths correctly listed as untested
are spreads, totals and props, which are unlikely to survive the same clause
because postponement is a property of the event, and other venue pairs, for
which no second independent book was verified to exist.

---

# Redaction note, 2026-08-28, at publication

Six passages above this line were edited in place, as itemised below. No figure,
threshold, criterion or measured result bearing on the study was changed. My
convention forbids silent revision, and this note is what makes the redaction
non-silent.

This repository was made public on 2026-08-28. Those six passages carried my
personal financial position and working setup, and were replaced with statements
of the same operational content:

1. §5's Gate D row named a specific dollar amount and recorded that I already
   held it. It now states the order of magnitude the gate requires.
2. §5's capacity paragraph read as a statement about capital on hand. It now
   states the same arithmetic per unit of pre-positioned capital.
3. §5 named a first-deployment range. Deployment size is an output of the Gate B
   curve, so the file now says that and declares no figure.
4. §5 measured C5 against my personal income target. It now states the strategy's
   capacity ceiling at retail size, which is what the paragraph was for.
5. §7 quoted a personal account-balance rule. The jurisdiction and collateral
   reasoning around it is unchanged.
6. §4's Gate B described the collection host as a specific personal machine. It
   now describes the requirement, which is a single always-on host.

The same publication pass edited the prose of this file throughout, for a reader
outside the project. That pass cut references to private planning documents and
to the internal shorthand this study was tracked under, and it is why the
Provenance section above no longer claims the file stands byte-for-byte as
authored. Every figure, threshold, gate definition, kill criterion, correction
and measured number is as authored.

The git history was rewritten on 2026-08-28 to remove the pre-redaction text from
every commit, and the GitHub repository was deleted and recreated so that the
superseded objects are not retrievable by SHA. Commit messages, authorship and
author dates are preserved, so the ordering this file's Provenance section asks a
reader to check is intact. The commit SHAs are not the ones a reader who cloned
this repository before 2026-08-28 evening would have seen.
