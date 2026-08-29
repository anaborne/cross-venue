# Method

How I work in this repository, and the API behaviour I checked before relying on
it. Each item names the primary source I read and the date I read it. Where a
fact came out of an earlier study of mine against the same API, I say so.

## Conventions

Raw responses go to disk before anything parses them. Every pull prints a
reconciliation block (rows retrieved, rows parsed, rows dropped, and the reason
for each drop) and I read it before I read the result. A silent parser exclusion
looks exactly like data that does not exist, and it fails in the direction that
makes the scope look smaller and the analysis look tractable.

Bulk pulls run in a terminal on my own machine, with nothing between me and the
raw response. A number I did not read out of the raw bytes does not go into a
study.

Claims carry their evidence into the document. In `notes/gateA.md` every claim is
marked. [V] means I checked it against a primary source I name inline,
[I] means I inferred it, [U] means I have not checked it. Nothing goes
into a document at higher confidence than the evidence behind it, because the
document format strips the hedge that a working note would have carried.

Corrections are appended and dated. When something here turns out to be wrong,
the wrong sentence stays where it is and a dated section below it states what it
got wrong. `PLAN.md` and `notes/gateA.md` both carry such sections, and both
leave the superseded text standing. Redaction is handled the same way, by an
itemised dated note.

Before writing a sentence shaped like "there is no X", "this is a hard ceiling"
or "the only way is Z", I read the API's own endpoint index and run at least one
search. Confirming that one instance fails is not evidence about the space. That
habit comes from a specific failure. In an earlier study I queried one older
Kalshi event, got an empty array, and wrote "there is no paid tier that fixes this
and no archive to fall back on" into a pre-registration. It was false. Kalshi
serves a full unauthenticated `/historical/*` tier going back at least 19 months,
and the claim would have capped that study's sample at 68 summer days. The check I
skipped cost one web search.

The design of a check comes before the check. If no available result would
falsify the claim, there is no test. Querying one old ticker to confirm that old
data is unavailable is a ritual.

## What I verified about the Kalshi API

Unauthenticated reads. Verified 2026-08-27 unless another date is given. Items
attributed to an earlier study were measured by me against this same API in the
work published at <https://github.com/anaborne/kalshi-temperature-calibration>
and in an unpublished sports study.

### Tiers and archive

- `/markets` serves a live tier only. Anything settled before the timestamp at
  `GET /historical/cutoff` is served by `/historical/markets`,
  `/historical/markets/{ticker}` and `/historical/markets/{ticker}/candlesticks`.
  The historical candlesticks path takes no series segment, unlike the live one.
  Verified back to January 2025.
- The cutoff rolls. `market_settled_ts` read 2026-06-27 on 2026-08-27 and
  2026-06-28 the next day.
- The tier stamp orders the attempt and does not decide it. 84 markets settled
  roughly a week before the cutoff were returned by the live `/markets` listing,
  404 on the live candlestick path, and resolved on the historical one (earlier
  study, verified by reading both its results and its fetch code). Always attempt
  both tiers and let the timestamp choose only the order.
- Whether the boundary is inclusive on the live side is [I] inferred. No
  market settling exactly at the cutoff timestamp has been tested. Attempting
  both tiers contains it, so a wrong guess costs one wasted request.
- A 404 from the candlestick paths is not a stable answer. A 65,226-market pull
  ended with 113 markets recorded as HTTP 404 on both the historical and the live
  candlestick path, and a second pass minutes later fetched all 115 outstanding
  markets successfully. A retry is the only thing that distinguishes a transient
  404 from a real absence on this API.
- `/historical/markets/{t}/candlesticks` requires `start_ts`. With
  `period_interval` alone it returns 400 `"start_ts is required"`, which a client
  that does not default the window will report as a market with no data.
- Legacy series prefixes resolve for some dates and not others. `HIGHNY-25JAN15`
  returns empty, `HIGHNY-22JUL04` returns four settled markets. The archive does
  not stop at the KX rename. Walking `KX` series still suffices, because
  `/events?series_ticker=KX…` enumerates the legacy-prefixed event tickers anyway.
- Kalshi serves no historical orderbook, at any tier or price. The historical
  candlestick payload's complete field set, enumerated recursively, is `ticker`,
  `end_period_ts`, `volume`, `open_interest`, `price.{open,high,low,close,mean,previous}`,
  `yes_bid.{open,high,low,close}` and `yes_ask.{open,high,low,close}`, with no
  size, depth, quantity or resting-liquidity field. The `historical` section of
  `docs.kalshi.com/llms.txt` is cutoff, market candlesticks, fills, orders,
  positions, trades, markets, market. `GET /markets/{ticker}/orderbook` takes no
  timestamp and serves current state only, and
  `/historical/markets/{t}/orderbook`, `/historical/markets/{t}/orderbook_snapshots`
  and `/historical/depth` all 404. Displayed size is recoverable going forward by
  polling `/markets/{t}/orderbook`, and not backward.
- `GET /historical/trades` is unauthenticated, cursor-paginated and covers the
  full archive. It carries `count_fp` (contracts), `created_time` (microsecond),
  `yes_price_dollars`, `no_price_dollars`, `taker_book_side`,
  `taker_outcome_side`, `is_block_trade` and `trade_id`. Verified back to the
  first market in each series tested, 2025-09-05 for NFL and 2025-11-19 for NBA.
  This is realized size, and it is the only free size-like quantity that survives
  into history.

### Rate

- A run at 8 workers and 6 rps logged 8 lines of `GET failed after 6 tries :: 429`
  against a client that retries six times with exponential backoff, so each of
  those is a request the API refused for over a minute. It cost 44 markets,
  recovered on a re-run. A run at 6 workers and 4 rps logged zero failures. A
  later 65,226-market pull sustained 3.73 rps for 291 minutes with no 429 at any
  point. I run at 4 rps. No ceiling has been established, and no run at a higher
  rate is recorded anywhere in my work.

### Schema

- Live market records carry `volume_fp`, `open_interest_fp`, `yes_bid_dollars`,
  `yes_ask_dollars`, `yes_bid_size_fp`, `last_price_dollars` and
  `settlement_value_dollars`. The bare `volume`, `open_interest`, `yes_bid`,
  `yes_ask` and `last_price` keys are absent, and `dict.get` on them returns
  `None`. Verified by reading raw response keys on
  `GET /markets?series_ticker=KXNFLGAME`. A parser written against the old names
  reports zeros, and zero volume with no two-sided quotes reads as an illiquid
  market. It bit me once, on twelve NFL and NBA series at the same time.
- Candle prices and sizes are decimal-dollar strings. `yes_bid.close` reads
  `'0.3900'` and `volume` reads `'0.00'`. Read as integers they come back zero,
  and a zero mid-quote reads as a market priced at nothing.
- A settled market's orderbook returns 200 with empty arrays.
  `GET /markets/{settled_ticker}/orderbook` gives
  `{"orderbook_fp":{"no_dollars":[],"yes_dollars":[]}}`. A parser reading that as
  zero displayed size records a fabricated zero.
- `expiration_value` gives the exact settled value on recent weather markets and
  is absent on older ones. It does not generalise to sports. On settled
  `KXNFLPASSYDS` rows it reads the literal string `passing_td`, a category label,
  on markets whose subject is passing yards. Verified on
  `KXNFLPASSYDS-26FEB08SEANE-SEASDARNOLD14-350` and four ladder siblings. Use
  `result` plus the strike from `yes_sub_title` or `floor_strike`.
- The hourly candlestick `volume` field and `GET /historical/trades` do not
  agree. Across 1,082 market-hours on 38 markets, 1,065 agree and 17 do not,
  98.43%. Some hours report 0 on the candle against 141, 255, 281, 309 and 350
  contracts on the trades; others agree in total and split contracts differently
  across an hour boundary, which puts the candle period at
  `[end_period_ts - 3600, end_period_ts)`. Anything conditioning on realised size
  should read `/historical/trades`.

### Settlement authority

- On weather series, settlement authority is whatever the market's own
  `rules_primary` names. The help centre is stale and is not binding.
- Daily temperature markets switched settlement authority around 2026-08-13,
  from the NWS Climatological Report (Daily) to The Weather Company, across 20 of
  21 city series. Both regimes appear in any sample spanning that date.
- Kalshi station identifiers are quoted in the rules text and are not always the
  obvious airport. Chicago is `CLIMDW` (Midway, not O'Hare) and Houston is
  `CLIHOU` (Hobby, not Bush).
- The `rules_primary` rule does not generalise to sports. On
  `KXNFLANYTD-26FEB08SEANE-SEAGHOLANI36`, `rules_primary` and `rules_secondary`
  name no source at all, and the series record is the only statement of authority
  that exists.
- `settlement_sources` is a list of objects carrying `name` and `url`, and the
  URL is the informative half. `KXNFLANYTD` reads
  `[{"name":"ESPN","url":"https://www.espn.com"},{"name":"Kalshi using information originating from the NCAA","url":"https://www.ncaa.com/sports/football/fbs"}]`,
  a college-football URL on a pro-football series.
- The API's `settlement_sources` and the binding contract-terms PDF at
  `assets.kalshi.com/contract_terms/` can name different authorities. For
  `KXNFLGAME` the API returns one source and `NFLGAME.pdf` names eight in
  hierarchical order. Reading `settlement_sources` from the API and treating it
  as the settlement authority is wrong for that series. Verified 2026-08-28, with
  two further instances in `notes/gateA.md` §2e.

### Fees

- Schedule effective 2026-07-07. Taker `roundup(M × 0.07 × C × P × (1−P))` with
  M defaulting to 1, maker `roundup(M × 0.0175 × C × P × (1−P))` with M
  defaulting to 0, and no settlement fee.
- `fee_type` is per-series and differs within a sport. `KXNFLGAME`,
  `KXNFLSPREAD`, `KXNFLTOTAL`, `KXNFL2TD`, `KXNBAGAME` and `KXNBATOTAL` are
  `quadratic_with_maker_fees`, while the player props `KXNFLPASSYDS`, `KXNBAAST`
  and `KXNBAPTS` are plain `quadratic` with no maker fee.
- `fee_type` is not constant over a series' archive.
  `GET /series/fee_changes?show_historical=true` returns, for `KXNBATOTAL`, a
  change to `quadratic_with_maker_fees` multiplier 1 scheduled
  `2025-11-15T08:00:00Z`. That series' archive starts 2025-10-22, so 2,035 of its
  14,787 settled markets (13.8%) predate the change, and the endpoint records only
  what the fee type became. The other five series tested return zero changes and
  all six read `fee_multiplier = 1` today. There is an override layer above the
  series record at `GET /events/fee_changes`, serving per-event
  `fee_type_override` and `fee_multiplier_override`. Sampled on 3 events per
  series out of 4,243, zero overrides found.
- `KXMLBGAME` carries `fee_multiplier: 0.5` and `exchange_index: 3` where the
  NFL, NBA and NHL game series carry 1 and 0. Verified 2026-08-28.

### Quote quality

- `(yes_bid.close + yes_ask.close) / 2` is not a market price on a sixth of
  Kalshi's sports prop quotes. Across 87,053 scored prop observations, 17.3% sit
  on a one-sided book, with `yes_bid` at 0.00 or `yes_ask` at 1.00, both non-null
  and both surviving any null-side filter. The mean bid-ask spread in the
  0.40 to 0.50 mid band is 25.9 cents against a median of 5. A forecast scored
  against that midpoint is not scored against a price anyone could trade.

### Catalogue

- `GET /series?category=Sports` returns 3,580 series in one unpaginated response
  and `GET /series` returns 13,558. 286 match `^KXNFL` and 204 match `^KXNBA`.

## What I verified about the Polymarket US API

Unauthenticated reads unless stated. Verified 2026-08-27/28. Raw responses under
`data/raw/gateA/`.

### The public gateway

- `gateway.polymarket.us` requires no authentication at all.
- `GET /v1/markets?limit=&offset=` is offset-paginated, and a short page is not
  the end of the collection. `/v1/markets?limit=500&offset=2000` returns 499 rows
  because id 2451 is absent. A first pull of mine terminated there and reported
  2,499 markets. A binary probe puts the true collection size between offsets
  542,577 and 542,968, so the reported figure was low by a factor of about 217.
  `src/pull_pmus.py` now terminates only on an empty page.
- The `closed=false` walk returned 30,720 open markets over 63 pages of 500, with
  0 duplicates and 0 null ids.
- `GET gateway.polymarket.us/v1/markets/{slug}/book` is declared `security: []`
  in the venue's own OpenAPI spec and is fully unauthenticated. It returns `bids`
  and `offers` alongside `state`, `stats` and `transactTime`. It ignores a
  `depth` parameter entirely (`depth` 1, 3, 5, 50, 1000 and no parameter all
  return an identical book) and serves the whole book, 3 to 14 levels per side
  across 25 live markets. That is deeper than the institutional endpoint's
  documented cap.
- One-sided books occur here as well. Several NFL prop markets returned `bids=0`
  or `offers=0` with the other side populated.

### Three auth surfaces

| surface | host | auth | gate |
|---|---|---|---|
| Institutional / Exchange | `api.prod.polymarketexchange.com` | Auth0 Private Key JWT (RSA, `client_credentials`) | entity registration, a signed Entity Participant and Clearing Member Agreement, then manual Client ID issuance by Polymarket |
| Retail | `api.polymarket.us` | `X-PM-Access-Key` / `X-PM-Timestamp` / `X-PM-Signature`, Ed25519 | app account plus identity verification |
| Public gateway | `gateway.polymarket.us` | none | none |

Probed and saved. `api.polymarket.us/v1/orderbook/TEST` returns
`401 "Missing required API key headers"`, and
`api.prod.polymarketexchange.com/v1/orderbook/TEST` returns
`401 {"message":"Unauthorized"}`.

The Order Book API Overview states verbatim that the institutional book
endpoints "only require Auth0 JWT authentication with `read:marketdata` scope"
and that "You do not need to provide the `x-participant-id` header or complete
KYC onboarding to access order book data." That is accurate about KYC. The JWT
behind it still requires a countersigned entity agreement and manual credential
issuance, so the path is not obtainable at $0. I did not obtain one and make no
claim that it works end to end.

### Institutional book endpoint

- `GET /v1/orderbook/{symbol}` exists and returns L2 depth. From the OpenAPI
  schema served inside
  `docs.polymarket.us/api-reference/order-book/get-order-book.md`, the response
  carries `bids` and `offers`, each an array of `BookEntry {px, qty}`, plus
  `state`, `stats` and `transactTime`.
- Maximum depth parameter 10, default 3. Stated twice in the venue's own docs,
  in the OpenAPI parameter block and in the Order Book API Overview's
  request-parameter table.
- The two book endpoints have incompatible schemas and the difference is silent.
  Institutional `px` is a flat string (`"px": "0.78"`). The public gateway's `px`
  is a nested object (`"px": {"value": "0.7800", "currency": "USD"}`), and the
  book sits under a `marketData` wrapper. A parser written against the OpenAPI
  spec and pointed at the free endpoint reads `px` as a dict.

### Fees

- From the venue's own binding schedule at `https://docs.polymarket.us/fees.md`,
  saved at `data/raw/gateA/pmus_fees.md`, effective exchange-wide from 12 AM ET,
  Wednesday July 1, 2026. Maker rebate θ = −0.0125 in `Fee = Θ × C × p × (1−p)`,
  maximum −$0.31 per 100 contracts at p = $0.50, applied at the point of trade,
  credited to balance at fill, computed per fill independently of the taker-side
  rounding adjustment, banker's rounding to the cent. Taker θ = 0.06, maximum
  $1.50 per 100.
- There is no sports-specific maker rebate. The schedule's own banner says
  exchange-wide, the complete 350-line docs index carries exactly two
  fee-schedule entries both pointing at the same `/fees.md`, the Sports FAQs page
  has no fee or rebate section, and all 30,720 of 30,720 open markets carry
  `feeCoefficient: 0.06` with zero leagues carrying any other value.

### Resolution

- The Sports FAQs page (`docs.polymarket.us/faqs/sports-faqs.md`) states a
  hierarchy. Primary is the governing body. Secondary is official scorecards,
  referee and umpire reports, press releases and governing-body results
  databases. Tertiary is AP, Reuters, ESPN, BBC Sport, official team and league
  sites, and wire services.
- Market descriptions name a single authority in the form "Outcome sourced from
  X." and state the postponement window as "within two weeks of the originally
  scheduled date". Present on 74 of 74 pairs in the Gate A sample.
- Last fair market price is defined precisely as the price at the moment of the
  official announcement, explicitly not the last traded price at close.
