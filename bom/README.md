# Complete BOMs with prices

One CSV per year range. Each has three sections:

1. **Daughterboard**: every part on the daughterboard (the same board in every file).
2. **Motherboard**: every part on that year's motherboard.
3. **Extra parts**: what it takes to put the board in a car: wideband oxygen sensor, sensor lead, MAP hose, USB cable, and the optional air-temperature, throttle-position and tuning-software items.

Every line gives the component, how many, the unit price, the total price, the manufacturer and part number, where to buy it, who fits it, whether it is required, stock, and where the price came from. The two board sections also carry the bare PCB and JLCPCB's assembly fees. Each section ends with a subtotal and the file ends with a total.

## Current design (Daughterboard rev 0.10)

| Years | Motherboard | Daughterboard parts | Daughterboard PCB and assembly | Motherboard parts | Motherboard PCB and assembly | Extra parts | Total |
|---|---|---|---|---|---|---|---|
| [1989-93](1989-93.csv) | 1989-95 rev 0.13 | $41.30 | $11.28 | $37.56 | $3.32 | $117.49 | **$210.94** |
| [1994-95](1994-95.csv) | 1989-95 rev 0.13 | $41.30 | $11.28 | $37.56 | $3.32 | $118.04 | **$211.49** |
| [1996-97](1996-97.csv) | 1996-97 rev 0.9 | $41.30 | $11.28 | $44.04 | $3.31 | $118.04 | **$217.97** |
| [1999-2000](1999-2000.csv) | 1999-2000 rev 0.9 | $41.30 | $11.28 | $44.18 | $3.42 | $117.32 | **$217.49** |
| [2001-05](2001-05.csv) | 2001-05 rev 0.9 | $41.30 | $11.28 | $40.29 | $3.42 | $117.32 | **$213.61** |

## Boards ordered in November 2026 (Daughterboard rev 0.9)

| Years | Motherboard | Daughterboard parts | Daughterboard PCB and assembly | Motherboard parts | Motherboard PCB and assembly | Extra parts | Total |
|---|---|---|---|---|---|---|---|
| [1989-93](ordered-2026-11/1989-93.csv) | 1989-93 rev 0.11 | $39.70 | $8.20 | $38.79 | $3.42 | $117.30 | **$207.40** |
| [1994-95](ordered-2026-11/1994-95.csv) | 1994-95 rev 0.9 | $39.70 | $8.20 | $38.30 | $3.30 | $117.85 | **$207.35** |
| [1996-97](ordered-2026-11/1996-97.csv) | 1996-97 rev 0.7 | $39.70 | $8.20 | $44.96 | $3.30 | $117.85 | **$214.01** |
| [1999-2000](ordered-2026-11/1999-2000.csv) | 1999-2000 rev 0.7 | $39.70 | $8.20 | $46.70 | $3.41 | $117.13 | **$215.13** |
| [2001-05](ordered-2026-11/2001-05.csv) | 2001-05 rev 0.7 | $39.70 | $8.20 | $41.21 | $3.41 | $117.13 | **$209.65** |

These boards are already bought, so the JLCPCB invoice has their real PCB and assembly figures. The lines here use the same batch-of-30 basis as the current design for comparison; the actual order was a handful of boards, where the per-order fees weigh far more on each board.

## How the prices work

- Prices are in USD for a **batch of 30 board sets**: each unit price is the quantity tier that applies when buying that part for 30 boards. JLCPCB and LCSC prices and stock were read on 2026-11-17.
- Each board section ends with five fabrication lines: the bare PCB, and JLCPCB's assembly fees (setup, stencil, the loading fee for each extended part, and placement per solder joint). The per-order fees are divided across the 30 boards, so they rise sharply for a smaller batch: the daughterboard's fixed fees are about $123 per order.
- The bare-PCB price is an **estimate, +-40 %**. JLCPCB publishes no price table, so it is scaled from one published anchor; use the quote on the order page. The assembly fees are computed from JLCPCB's published fee table.
- Within each section the lines are sorted by total price, highest first; lines with no price come last.
- Subtotals and totals count **required lines only**. Lines marked Optional, Alternative or Manual cars are listed with a price but not added in.
- Still left out: the 35 % US duty JLCPCB collects (about $19 per set on the cost model, if it also applies to the parts JLCPCB buys), freight from JLCPCB (a guess of about $2.50 per set), and the labour to hand-fit the through-hole parts. The cost model is in [`review/2026-11/REPORT.md`](../review/2026-11/REPORT.md), section S3.
- **Price type** says how far to trust a price: `live` was read from the seller; `computed` comes from a published fee table; `snapshot` is distributor data from an aggregator, not checked live; `estimate` is a guess; `not priced` means no price was found.
- A supplier part marked `(candidate)` is a hand-fitted part the design lists without a part number; the part named is a matching one found at LCSC, not a tested choice.
- The **Notes** column carries review remarks. R110 on the daughterboard is listed with the wrong part (0.62 ohm; it needs 62 ohm, C17971).

## Caveats

- Prices and stock move daily. Check them again on the day of an order.
- The MAP hose is priced as a Turbosmart 4 mm, 3 m pack ($17.99 at three US shops). A seller buying for a batch can cut it from a 30 m roll for about $7.41 per car (SFS Performance, listed as an alternative), but that ships from Lithuania and the shipping and duty are not included.
- Harness-header prices were converted from CAD and not checked live.
- No lead or hose length has been measured on a car, and the sensor thread fit to the stock bung has not been checked.
