# Complete BOM with prices

Two files, generated on 2026-11-17:

| File | What it holds |
|---|---|
| `complete_bom.csv` | 442 lines: every part on every board (current design and the boards ordered in November 2026), the fabrication and import lines, and every part needed to put a board in a car, each with a price at batches of 5, 30 and 100 |
| `complete_bom_summary.csv` | The same rolled up per year range: parts, fabrication and import, in-car parts, total |

## Cost per car, current design

Daughterboard rev 0.10 plus the year's motherboard. Columns 2 to 6 are at a batch of 30.

| Years | Parts placed by JLCPCB | Hand-fitted parts | Board set made and delivered | Required in-car parts | Total | Total at batch 5 | Total at batch 100 |
|---|---|---|---|---|---|---|---|
| 1989-93 | $42.27 | $36.59 | $115.86 | $127.17 | **$243.03** | $302.33 | $226.26 |
| 1994-95 | $42.27 | $36.59 | $115.86 | $127.72 | **$243.58** | $302.88 | $226.81 |
| 1996-97 | $42.23 | $43.11 | $122.33 | $127.72 | **$250.05** | $309.95 | $231.82 |
| 1999-2000 | $42.36 | $43.11 | $122.51 | $127.00 | **$249.51** | $308.95 | $231.25 |
| 2001-05 | $42.48 | $39.11 | $118.67 | $127.00 | **$245.67** | $304.28 | $228.50 |

- "Made and delivered" adds bare PCBs, assembly and extended-part fees, inbound freight and the 35 % US duty JLCPCB collects. Those four lines are estimates from the cost model in `review/2026-11/REPORT.md` (section S3), not quotes.
- Required in-car parts: Bosch LSU 4.9 sensor, a made-up sensor lead, 3 m of MAP hose (with a tee where the car needs one), a 3 m USB cable, case washers and ties. The car's own ECU case is reused.
- Not in the totals: labour, packaging, outbound postage, payment fees, and the optional items (IAT sensor and adapter, TPS conversion for 1989-93, weld bungs, TunerStudio registration, microSD card). They are listed in `complete_bom.csv` with prices where one was found.

## Parts only, ordered boards (batch 30)

Daughterboard rev 0.9 plus each ordered motherboard. PCB, assembly, duty and freight for these are on the JLCPCB invoice and are not estimated here.

| Years | Parts placed by JLCPCB | Hand-fitted parts | Board set, parts only |
|---|---|---|---|
| 1989-93 | $41.10 | $37.39 | $78.49 |
| 1994-95 | $40.61 | $37.39 | $78.00 |
| 1996-97 | $40.58 | $44.09 | $84.66 |
| 1999-2000 | $40.71 | $45.69 | $86.40 |
| 2001-05 | $40.83 | $40.09 | $80.91 |

## Reading `complete_bom.csv`

- **Section** is Daughterboard, Motherboard, Fabrication and import, or In-car parts. **Design** is `current` or `ordered 2026-11`.
- **Unit USD (batch N)** is the price tier that applies when buying for N boards (quantity per board times N). For in-car parts the batch 5 column is the one-off retail price.
- **In total** says whether the line is counted in the summary. Optional and alternative lines are `no`.
- **Price confidence**: `live` was read from the seller on the date in the source column; `snapshot` is distributor data from an aggregator; `estimate` is a guess or a figure scaled from one data point; `not priced` means no price was found. This file has 8 snapshot, 36 estimate and 7 unpriced lines.
- **Notes** carries review remarks: R110 is listed with the wrong part (0.62 ohm instead of 62 ohm), and low-stock parts name their replacement.
- Lines marked `(candidate)` are hand-fitted parts the self-order BOM lists without a part number; the part named is a matching one found at LCSC, not a tested choice.

## Caveats

- Prices and stock move daily. Check them again on the day of an order.
- The MAP hose price is a premium brand ($70.30 per 25 ft roll), the only one that could be verified; a generic hose should cost much less.
- Harness-header prices were converted from CAD and not checked live.
- No lead or hose length has been measured on a car, and the sensor thread fit to the stock bung has not been checked.
- JLCPCB part prices carry no allowance for attrition.
