# Complete BOMs with prices

One CSV per year range. Each has three sections:

1. **Daughterboard**: every part on the daughterboard (the same board in every file).
2. **Motherboard**: every part on that year's motherboard.
3. **Extra parts**: what it takes to put the board in a car: wideband oxygen sensor, sensor lead, MAP hose, USB cable, and the optional air-temperature, throttle-position and tuning-software items.

Every line gives the component, how many, the unit price, the total price, the manufacturer and part number, where to buy it, who fits it, whether it is required, stock, and where the price came from. Each section ends with a subtotal and the file ends with a total.

## Current design (Daughterboard rev 0.10)

| Years | Motherboard | Daughterboard parts | Motherboard parts | Extra parts | Total |
|---|---|---|---|---|---|
| [1989-93](1989-93.csv) | 1989-95 rev 0.13 | $41.30 | $37.56 | $127.17 | **$206.03** |
| [1994-95](1994-95.csv) | 1989-95 rev 0.13 | $41.30 | $37.56 | $127.72 | **$206.58** |
| [1996-97](1996-97.csv) | 1996-97 rev 0.9 | $41.30 | $44.04 | $127.72 | **$213.06** |
| [1999-2000](1999-2000.csv) | 1999-2000 rev 0.9 | $41.30 | $44.18 | $127.00 | **$212.48** |
| [2001-05](2001-05.csv) | 2001-05 rev 0.9 | $41.30 | $40.29 | $127.00 | **$208.59** |

## Boards ordered in November 2026 (Daughterboard rev 0.9)

| Years | Motherboard | Daughterboard parts | Motherboard parts | Extra parts | Total |
|---|---|---|---|---|---|
| [1989-93](ordered-2026-11/1989-93.csv) | 1989-93 rev 0.11 | $39.70 | $38.79 | $126.98 | **$205.46** |
| [1994-95](ordered-2026-11/1994-95.csv) | 1994-95 rev 0.9 | $39.70 | $38.30 | $127.53 | **$205.52** |
| [1996-97](ordered-2026-11/1996-97.csv) | 1996-97 rev 0.7 | $39.70 | $44.96 | $127.53 | **$212.19** |
| [1999-2000](ordered-2026-11/1999-2000.csv) | 1999-2000 rev 0.7 | $39.70 | $46.70 | $126.81 | **$213.20** |
| [2001-05](ordered-2026-11/2001-05.csv) | 2001-05 rev 0.7 | $39.70 | $41.21 | $126.81 | **$207.72** |

## How the prices work

- Prices are in USD for a **batch of 30 board sets**: each unit price is the quantity tier that applies when buying that part for 30 boards. JLCPCB and LCSC prices and stock were read on 2026-11-17.
- Subtotals and totals count **required parts only**. Lines marked Optional, Alternative or Manual cars are listed with a price but not added in.
- The totals are parts only. They leave out the bare PCBs, JLCPCB assembly and extended-part fees, import duty and freight. The cost model in [`review/2026-11/REPORT.md`](../review/2026-11/REPORT.md) (section S3) estimates those at about $37 per set at a batch of 30.
- **Price type** says how far to trust a price: `live` was read from the seller; `snapshot` is distributor data from an aggregator, not checked live; `estimate` is a guess; `not priced` means no price was found.
- A supplier part marked `(candidate)` is a hand-fitted part the design lists without a part number; the part named is a matching one found at LCSC, not a tested choice.
- The **Notes** column carries review remarks. R110 on the daughterboard is listed with the wrong part (0.62 ohm; it needs 62 ohm, C17971).

## Caveats

- Prices and stock move daily. Check them again on the day of an order.
- The MAP hose is a premium brand ($70.30 per 25 ft roll, so $27.67 for 3 m), the only price that could be verified. A generic hose should cost much less.
- Harness-header prices were converted from CAD and not checked live.
- No lead or hose length has been measured on a car, and the sensor thread fit to the stock bung has not been checked.
