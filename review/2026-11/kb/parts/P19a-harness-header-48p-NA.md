# P19a Harness header TE 174917-6 (48 pin), J1 on 1989-95 / ord 1989-93 / ord 1994-95 motherboards

## Summary
1. VERIFIED: footprint `TE_174917-6_48P.kicad_mod` (identical md5 in repo/mb, motherboards/1989-95, ordered 1989-93 and 1994-95) matches the TE customer drawing 174917 rev M9 (24 Nov 2022; datasheets/extra/174917-6_lcsc-TE-drawing.pdf): 48 x dia 1.1 holes, row offset 4.5, along-row positions 0,3.5,6.6,9.6,...,30.7 | 36.9,40.4,43.5,...,67.6,71.1,74.6, 3 pegs dia 3.5 at -5.05 / 33.8 / 79.65 along the row, 10.2 from the A row (4.5 + 5.7 on the drawing). Max deviation 0.003 mm.
2. VERIFIED: pad names/chirality agree pad by pad (48/48, tol 0.1 mm, proper rotation, no mirror) with Speeduino NA6 PNP v1.3 footprint+symbol (pins 1-11 = 1A,1C..1U; 12-24 = 2A..2Y; 25-35 = 1B..1V; 36-48 = 2B..2Z; pegs on the B-row side). Letters 1A-1V and 2A-2Z, no letter skipped. Lower row (nearest board centre) = A,C,E..., upper row (toward pegs/edge) = B,D,F...
3. VERIFIED functional cross-check vs Hellen NA6-94 nets (plug "3" there = our "2"): 3A/3C/3B/3D GND = our 2A/2C/2B/2D GND; 3E crank = 2E IN_HALL1; 3G cam = 2G IN_HALL2; 3K 5V = 2K V5_EXT; 3P IAT = 2P; 3Q CLT = 2Q; 3U INJ1 = 2U; 3V INJ2 = 2V; 3W idle = 2W IACV; 3I tach = 2I. No mirror / shift found.
4. All three boards place J1 identically: origin 1A (139.70,68.13) evidence frame (board-relative 39.7,18.13), rot 0, top side; pegs NPTH 3.5; pad 1.5062 round, drill 1.0998 (ring 0.2 mm).
5. Hellen NA6-94 itself uses a 76-position 178780-1 (22|12|16|26, 122 mm wide) not this header: geometry not comparable (see finding), only the names/functions.
6. Sourcing: TE site says "not currently available" (VERIFIED, te.com page), but distributors list it: LCSC/JLC C592838 (extended, 32 pcs, $12.92/12.74/12.43/12.16 at 1/10/30/100), DigiKey (WEE marketplace) 2150 pcs EUR 5.34 at 30, 3 days; Newark ~$6 (489); RS 15+ $7.12 (UNVERIFIED aggregator via search). The repo says "salvage or clone only": too pessimistic.

## Mazda cavity naming
- Plug 1 (22): 1A-1V; plug 2 (26): 2A-2Z (rusEFI 1990 page: 3A-3Z; 1994 page: 2A-2Z). Letters run consecutively, I and O used. Mating plugs per TE drawing note 2: 174515 (22), 174516 (26), 917989, 917992; rusEFI wiki adds 22p 174515-6/175110-6, 26p 174516-6/175111-6 (UNVERIFIED secondary).
- TE drawing numbers contacts 1-48 (1-16 power, 17-48 signal) and does not give Mazda letters; the letter-to-row assignment rests on Speeduino symbol + rusEFI/Hellen net names (secondary, but three sources agree). Physical proof on a stock ECU not done.

## Comparison table (pad coordinates, along-row x, mm, A row y=0, B row y=-4.5; all within 0.003)
repo = TE drawing = rusEFI Breakout_48pin_174917 = Speeduino 1749171 (rotated). Hellen 178780-1 plug sections have the same 3.5,3.1,3.0.. pattern and 4.5 row spacing, drill 1.1, pegs 3.5.
rusEFI readme for its 174917 breakout: "NEVER populated" (Mar 2020): not proof by itself; Speeduino boards used real connectors (field use UNVERIFIED by me).

## Sources actually read
TE drawing M9 (LCSC copy, page image); te.com product page via page fetch; rusEFI wiki OEM-connectors; speeduino ECU_Connectors; ext/speeduino-hardware NA6 v1.3 pcb + lib + connector.sch; ext/hellen-miata-NA6 pcb + png; repo scripts mk_hdr_fp.py, mb_na6.py; evidence pcb_pads/footprints; tools/lcsc.py C592838 C5166285; DigiKey.de WEE page; web search results (Octopart/Newark/RS summaries).

## Not checked
Physical position of header vs stock case (1A at 39.7 mm, overhang ~7.4 mm: silk body to -25.5 mm); 3D/overhang vs case; JLC THT assembly of C592838; clone quality; price of mating plugs; DigiKey row-spacing 5.2 listing (drawing shows 4.5 and 5.2 = cavity pitch).
