# Design review, November 2026

A desk review of this repository at commit `6e346af` (2026-11-15), done between 2026-11-15 and 2026-11-17. It covers two design states: the **ordered** boards (daughterboard rev 0.9 and five motherboards, frozen in `ordered-boards/2026-11/`) and the **current** design (daughterboard rev 0.10; motherboards rev 0.13 and rev 0.9).

No board had been built when this was written. Everything here comes from the design files, datasheets and outside documents; nothing was measured.

## Start here

| File | What it is |
|---|---|
| [NEXT-BATCH.md](NEXT-BATCH.md) | The findings that shape the next batch, the next steps in order, the open decisions, and a register of the verified claims |
| [NEXT-REV.md](NEXT-REV.md) | The change list for the next board revision (rev 0.11): no via in any SMD pad, a GM air-temperature sensor on every year, part fixes, firmware, and the state of the work |
| [REPORT.md](REPORT.md) | The full report: errors and bring-up (S1), removals and cheaper parts (S2), cost model (S3), customer experience (S4), packaging and shipping (S5), background research (S6) |

The headline finding: **R110 on the daughterboard is fitted as 0.62 Ω (LCSC C25341) where the wideband circuit needs 62 Ω (C17971)**, in rev 0.9 and rev 0.10.

## Working notes (`kb/`)

| Path | Contents |
|---|---|
| `kb/parts/` | One note per part group: datasheet read, pin by pin against the PCB netlist |
| `kb/boards/` | Board and fabrication reviews (ERC / DRC parity, layout, thermal, bring-up plan, verification-claims audit) |
| `kb/pinouts/` | Two pinout audits per year range: from the design outward and from the factory documents inward |
| `kb/firmware/` | Firmware reviews: board definition, year presets, wideband firmware, build and update path |
| `kb/research/` | Outside research: other ECU designs, stock Miata ECUs by year, tuning practice, cost, manufacturing, packaging, shipping |
| `kb/followup/` | Four follow-up questions: IAT harness, a better-stocked processor, avoiding filled vias, complete-kit cost |
| `kb/findings/all_findings.jsonl` | Every first-pass finding, one JSON object per line |
| `kb/findings/clusters.json` | The findings rated medium or above, plus every removal, alternate-part and cost idea, merged into unique claims |
| `kb/verify/` | The verification notes behind each claim (`<claim>-<lens>.md`) and the verdicts (`verdicts.jsonl`) |
| `kb/parts_manifest.md`, `kb/parts_manifest.json` | Every BOM line on every board with its LCSC identity, price tiers and stock on 2026-11-15 |
| `kb/interconnect.md` | The daughterboard-to-motherboard pin table for every board |

## Priced BOMs

Each current board now has a `*_costed_bom.csv` beside its JLCPCB and self-order BOMs. It joins both BOMs with JLCPCB and LCSC prices and stock read on 2026-11-17, at batches of 5, 30 and 100 boards. The table is for the castellated rev 0.13 / 0.17 / 0.13 boards, with R110 and the 2 A fuse changed as the review asked (prices as read on 2026-11-17). The JLCPCB upload files are unchanged.

| File | Lines | Extended lines | Parts per board, batch 5 | Batch 30 | Batch 100 |
|---|---|---|---|---|---|
| `daughterboard/fab/miata-ecu-daughterboard-rev0.13_costed_bom.csv` | 92 | 37 | $49.67 | $42.33 | $38.02 |
| `motherboards/1989-95/fab/miata-ecu-motherboard-1989-95-rev0.18_costed_bom.csv` | 30 | 4 | $38.82 | $35.88 | $34.65 |
| `motherboards/1996-97/fab/miata-ecu-motherboard-1996-97-rev0.14_costed_bom.csv` | 20 | 4 | $45.90 | $42.37 | $39.67 |
| `motherboards/1999-2000/fab/miata-ecu-motherboard-1999-2000-rev0.14_costed_bom.csv` | 21 | 5 | $46.01 | $42.48 | $39.76 |
| `motherboards/2001-05/fab/miata-ecu-motherboard-2001-05-rev0.14_costed_bom.csv` | 21 | 5 | $41.25 | $38.58 | $36.96 |

- Totals are parts only. They leave out the bare PCB, assembly and extended-part fees, duty, freight, and the items listed as unpriced in each file's last row. The full cost model is REPORT.md section S3.
- Harness-header prices are distributor snapshots from an aggregator, converted from CAD, and were not checked live.
- The `Notes` column carries the review's remarks on a part (wrong value, low stock, a drop-in alternative).
- Prices and stock move daily. Check them again on the day of an order.

## Reading the paths in these files

- `repo/...` means this repository at the reviewed commit.
- `kb/...` means this folder.
- `evidence/`, `datasheets/`, `ext/`, `work/`, `tools/` and `kb/research/files/` were working material: netlist extracts, datasheet PDFs, third-party manuals and web pages, and scratch scripts. They are not published here, so those references cannot be followed.

## What is not here

- Notes and claims on legal, sales-policy, pricing and storefront topics are left out. That is 13 of the 162 verified claims and four research notes (R13, R27, R28, R32). Counts quoted in the report refer to the full set.
- The 570 low and informational findings in `all_findings.jsonl` were not verified.
