# Ordering the boards

How to order the current boards: **daughterboard rev 0.14** (the castellated module) and **motherboards rev 0.19
(1989-95) and 0.15 (1996-97, 1999-2000, 2001-05)**, which have its lands. These go together only: an earlier,
socketed board fits neither. Read it with [Things to know before ordering](README.md#things-to-know-before-ordering)
and the board READMEs. Stock figures are JLCPCB's and LCSC's as read on the dates given; check them again on the day.

**The supported path is an assembled unit until a first board has been built.** No person has reviewed the
schematics, and neither the castellated module (rev 0.13 on) nor any board of this series has been built. If you order the boards
yourself, you are the first, and [BUILD.md](BUILD.md) is unchecked.

## 1. Before you order

1. **Read what a build involves:** [BUILD.md](BUILD.md). You solder the daughterboard onto the motherboard yourself,
   fit the through-hole parts, flash it over USB and check it before the car.
2. **Buy the harness header first.** It is the part most likely to hold you up, and it is not in the JLCPCB
   assembly:
   - **1996-97 and 1999-2000:** TE 178780-1. **2001-05:** TE 353830-5. Both were out of stock at LCSC on 2026-11-21 and
     distributors quoted long lead times.
   - **1989-95:** TE 174917-6, LCSC C592838: 32 in stock on 2026-11-21, about $12.4 each. Distributors describe
     174917-6 with two different pitches, so check any listing against the board footprint before buying.
   - **Fallback:** salvage the header from a stock ECU.
   - Buy 12-15 per year at a time, if you are buying for several boards.
3. **What you buy elsewhere and fit by hand** (JLCPCB does not place these): the harness header, the MAP sensor
   (MPX5700AP) with its two M3 screws and nuts, the wideband sensor header J2, the add-on header J5 (optional), and
   the two option-jumper headers and their shunts on the 1989-95 board. The full list for each board is its
   `fab/*_self_order_bom.csv`; the whole shopping list, with quantities and tick boxes, is
   [`additional-parts/shopping_list.html`](additional-parts/shopping_list.html)
   ([`additional-parts/order_all_boards.csv`](additional-parts/order_all_boards.csv) is the same as a spreadsheet).
   In-car parts (wideband sensor and harness, vacuum hose and tee) are on the same page.
4. **Which years to order now.** 1989-95 is the board whose case outline is the stock one. The 1996-2005 boards still
   have the 1990-95 outline and mounting holes as a stand-in: the owner's own pilot of two 1996-97 sets is how the
   1996-97 case gets measured, and other 1996-2005 buyers should wait for that result before ordering.
5. **Rev 0.9 boards ordered in November 2026:** their files and bring-up are in
   [ordered-boards/2026-11/](ordered-boards/2026-11/) and [CHANGES.md](CHANGES.md#ordered-boards-2026-11).

## 2. Files and board settings

Each board's files are in its `fab/` folder.

| Board | Upload to JLCPCB | Order separately and fit by hand |
|---|---|---|
| Daughterboard | `miata-ecu-daughterboard-rev0.14_jlcpcb_gerbers.zip`, `..._jlcpcb_bom.csv`, `..._jlcpcb_cpl.csv` | Nothing: J1 / J2 are castellated edges |
| Motherboard, each year | `miata-ecu-motherboard-<years>-rev0.1x_jlcpcb_gerbers.zip`, `..._jlcpcb_bom.csv`, `..._jlcpcb_cpl.csv` | `..._self_order_bom.csv`: harness header, MAP sensor and its screws, wideband and add-on headers, and the optional R20 |
| Motherboard 1989-95 | the same gerbers, and the BOM and CPL of **your car's version**: `..._for-1989-93_jlcpcb_bom.csv` / `..._cpl.csv` or `..._for-1994-95_...` (they differ only in the year links JLCPCB fits). For both, place two orders, or one order per version | the version's `..._self_order_bom.csv`, as above, plus the JP5 / JP6 headers and shunts |

**Daughterboard:** 6 layers, 1.6 mm, JLCPCB's standard six-layer stack (1 oz outer, 0.5 oz inner copper; the
track-current check assumes that). No via sits in or against an SMD pad, so plain tented vias are fine: no via
filling or capping is needed. Assembly on the top side only.
- **Surface finish:** the repo files do not name one. Take JLCPCB's default for the stack, and check in the preview that it is offered with castellated holes.
- **Castellated holes: Yes** (an extra charge). The 80 half-holes on the long edges are the module's pins; without the
  option the edges may be routed plain. The design meets JLCPCB's castellation rules (1.0 mm holes, 1.54 mm apart, the
  pads reach 0.85-1.3 mm in from the edge). Check in the preview that the half-holes show plated, and that the option
  is offered for six layers on the day.
- **Assembly type: Standard, not Economic.** JLCPCB's capabilities page (read 2026-11-21) lists "Gold Fingers /
  Castellated Holes / Edge Plating" as **not supported** by Economic PCBA and **supported** by Standard PCBA. Standard
  also needs edge rails and fiducials ("Necessary" on that page); check on the order page what it adds to the board.
- **Cost of Standard assembly:** JLCPCB does not quote it in advance. The repo's own fee model
  ([review/2026-11/kb/research/R21-jlcpcb-cost-model.md](review/2026-11/kb/research/R21-jlcpcb-cost-model.md)) puts it at
  roughly **+$14 per board at 5 boards and +$3 at 30**: setup $25.56 against $8.18, stencil $8.21 against $1.53, and a
  fee for every unique line including basic parts. **That is an estimate; the real figure is on the JLCPCB order page.**

**Motherboards:** 2 layers, 1.6 mm. No castellation, so **Economic assembly is fine** (the repo's fee notes put Economic at 2-50 boards per order; check on the day). Assembly on the top side only;
the JLC BOM is the SMD parts and the USB-C socket. The USB-C socket has through-hole shell pegs: check in JLC's quote
whether that needs Standard. The lands JD1 / JD2 are in the paste stencil, so an assembled board arrives with them
tinned.

**Soldering the module down** is yours to do: JLCPCB's assembly does not take one of your own boards as a part on
another (check their "consigned parts" option on the day if you want them to). On a hot plate, in an oven or with an
iron: [BUILD.md](BUILD.md#1-solder-the-daughterboard-to-the-motherboard).

## 3. Check the placement preview

JLCPCB's part models do not all share KiCad's zero rotation. `scripts/order_bom.py` corrects the placement file with
the offsets seen in JLC's preview of the rev 0.5 daughterboard (`JLC_ROT`) and moves the USB-C socket 1.14 mm to its
pad centre (`JLC_OFFSET`). These parts have **not** been seen in a preview with those corrections. Check each one
in JLC's placement preview, pin 1 or the cathode band against the board's marking. Where the last column says yes, the
received rev 0.9 boards were placed with the same rule, so a look at them answers it too:

| Board | Parts | Package | Rotation the file gives | Also on the rev 0.9 boards? |
|---|---|---|---|---|
| Daughterboard | U3, U14 (TLS115B0EJ, 5 V sensor supplies) | Infineon PG-DSO-8 | SOIC offset, 270° | Yes |
| Daughterboard | J4 (microSD socket) | Molex 47219-2001 | no offset | No: new in rev 0.10 |
| Daughterboard | D46-D49 (1.5SMC16A injector clamps), D6 | SMC | no offset | D6 yes; D46-D49 no, new in rev 0.10 |
| Daughterboard | D8, D10, D31-D34, D40, D41 (B5819W) | SOD-123 | no offset | Yes |
| Daughterboard | D13, D14, D19-D30, D38, D39 (1N4148WS, BAT54WS) | SOD-323 | no offset | Yes |
| Daughterboard | U1 (STM32F405), U102 (STM32F103) | LQFP-100, LQFP-48 | 270° (seen on LQFP-32 only) | Yes: same footprints as rev 0.9's U1 and U102 |
| Each motherboard | U4 (USBLC6-2SC6) | SOT-23-6 | 180° (seen on SOT-23 and SOT-23-5) | Yes |
| Each motherboard | J4 (USB-C) | GCT USB4105 | moved 1.14 mm to the pad centre | Yes, before the move |

The rest (chip resistors, capacitors and inductors, SMA diodes, LEDs, crystals, buttons, SOT-23, SOT-223, TO-252,
SOIC, TSSOP and the resistor arrays) match a correction already seen in a preview.

If a part is wrong, correct it in the preview for this order, then fix its rule in `JLC_ROT` or `JLC_OFFSET` and
regenerate the files (`scripts/reexport.sh`) so the next order is right. Polarised parts that are wrong are easy to
miss: compare every diode's band with the silkscreen.

## 4. Check stock on the day

The parts with the least stock, against one board set each:

| Part | LCSC | Per board | Stock | Enough for |
|---|---|---|---|---|
| microSD socket J4 (daughterboard) | C164170 | 1 | 110 (2026-11-17) | 110 |
| MPX5700AP MAP sensor (motherboard, by hand) | C90152 | 1 | 155 (2026-11-17) | 155 |
| TLS115B0EJ, U3 / U14 | C3743696 | 2 | 554 (2026-11-17) | 277 |
| STM32F405VGT6, U1 | C56621 | 1 | 1,035 (2026-11-17) | 1,035 |
| 1.5SMC16A injector clamps | C1973780 | 4 | 1,699 (2026-11-17) | 424 |
| VND7NV04TR-E injector and coil drivers, Q1-Q8 | C155605 | 8 | 2,386 (2026-11-23; 0 on 2026-11-21) | 298 |

**Drivers Q1-Q8:** C155605's stock dipped to 0 on 2026-11-21 and was back to 2,386 on 2026-11-23. If it is out of
stock when you order, use **VND14NV04TR-E (C2649436)** for Q1-Q8. It is a drop-in alternate: the same DPAK footprint
and pinout, and already on the board for the wideband heater (Q101).

If the injector clamp runs out, any SMCJ14A or SMDJ14A fits the same pads
([daughterboard README](daughterboard/README.md#before-ordering)).

Harness headers: see [section 1](#1-before-you-order).

## 5. Order in this sequence

1. **A pilot:** 5 daughterboards and a motherboard for each year you can test. The owner's own pilot is two 1996-97 sets
   for two 1996-97 cars (two 1996-97 motherboards), and it is how the 1996-97 case gets measured. Rev 0.13 is the first
   castellated module, soldered flat; rev 0.12 brought a new processor part number and a new CAN transceiver, and rev
   0.11 / 0.10 the via rule and every rev 0.10 change. None has been built. Solder one module down first and check its
   joints and its temperature at load before ordering more.
2. Bring the pilot up on the bench and in a car. Then one daughterboard lot for every year at once, on Standard
   assembly.
3. Motherboards per year, 8-10 at a time, once that year has run in a car.
4. Other 1996-2005 buyers: wait for the 1996-97 case measurement (section 1, item 4).

## 6. Not in this release

These need the board re-routed. None stops a rev 0.14 board from working; they are in
[NEXT-REV.md](review/2026-11/NEXT-REV.md).

| Item | What it means for a board ordered now |
|---|---|
| 1989-95 header holes still 1.1 mm (pads must grow first) | Test-fit the 174917-6; ream a hole by hand if a pin binds |
| 1989-95: pin 1B's current runs through 46 mm of 0.6 mm track | About 20 °C rise at the heater's cold peak: adequate |
| C12 on the processor's VDDA pin side, ferrite FB1 before it | Analog supply filtering not ideal; the readings work |
| More copper (vias around the tab) at the 3.3 V regulator U4 | 0-1 °C warmer |
| No pull-up footprint on the alternator control wire (1999-2000 1O, 2001-05 3M) | Wire one by hand if the car needs it |
| No tach pull-up footprint on 1996-2005 | Wire one by hand if the car measures about 0 V on the tach wire ([how to measure it](quickstart/1996-97.md#measure-before-you-remove-the-stock-ecu)) |

## 7. Cost

Parts per board, as priced on 2026-11-17 in each board's `*_costed_bom.csv`; the board itself and assembly fees are
not included (for the daughterboard's Standard assembly, see section 2). Complete sets per year, with the in-car parts,
are in [bom/README.md](bom/README.md).

| Board | Batch 5 | Batch 30 | Batch 100 |
|---|---|---|---|
| Daughterboard rev 0.14 | $49.67 | $42.33 | $38.02 |
| 1989-95 motherboard rev 0.19, 1989-93 version | $44.34 | $41.87 | $41.33 |
| 1989-95 motherboard rev 0.19, 1994-95 version | $44.36 | $41.88 | $41.34 |
| 1996-97 motherboard rev 0.15 | $46.44 | $42.85 | $40.09 |
| 1999-2000 motherboard rev 0.15 | $46.55 | $42.96 | $40.18 |
| 2001-05 motherboard rev 0.15 | $41.80 | $39.06 | $37.37 |
