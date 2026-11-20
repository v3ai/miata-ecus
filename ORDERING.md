# Ordering the rev 0.13 boards

A checklist for ordering the current boards: **daughterboard rev 0.13** (the castellated module) and **motherboards
rev 0.16 (1989-95) and 0.12 (1996-97, 1999-2000, 2001-05)**, which have its lands. These go together only: an earlier,
socketed board fits neither. Read it with [Things to know before ordering](README.md#things-to-know-before-ordering)
and the board READMEs. Stock figures are JLCPCB's as read on 2026-11-17 (`*_costed_bom.csv`); check them again on the day.

No person has reviewed the schematics, and neither rev 0.12 nor the castellated rev 0.13 has been built. The boards received in November 2026
(daughterboard rev 0.9, [ordered-boards/2026-11/](ordered-boards/2026-11/)) are the nearest thing to a test of it.
Section 1 lists what their bring-up should settle first.

## 1. Settle these on the received rev 0.9 boards first

Each of these can change a rev 0.13 board or how you fit it. The measurements are described in
[BRING-UP.md](ordered-boards/2026-11/BRING-UP.md).

| Check | What the answer changes |
|---|---|
| **A/C request and clutch** (1996-97 cavities 1K, 1L): switched to ground or to 12 V? | The boards fit R21 / R22 (4.7 kΩ to 12 V) because the stock ECU's voltage tables show switches to ground. If a car drives either wire to 12 V, leave that resistor off (delete its line from the JLC BOM and placement file) and set the input back to active high. |
| **Tachometer** (1996-97 4L; 1999-2000 2K; 2001-05 3O): about 0 V or 12 V with the stock ECU out? | At about 0 V the cluster needs a pull-up of about 1 kΩ to switched 12 V. The 1996-2005 motherboards have no footprint for it yet, so it would be wired by hand. |
| **Harness header fit.** The rev 0.9 motherboards have 1.1 mm holes; TE asks for 1.35 mm. | The motherboards drill 1.3 mm on 1996-97, 1999-2000 and 2001-05. If the pins went into 1.1 mm without force, 1.3 mm is comfortable. The 1989-95 board is still 1.1 mm, so test-fit a 174917-6 there before ordering 1989-95 boards. |
| **Case fit, 1996-2005.** These motherboards use the NA outline and mounting holes as a placeholder. | Measure a stock 1996-97 / NB case and fit a rev 0.9 motherboard in it. The 76-position header is 130 mm wide. Do not order 1996-2005 motherboards in quantity until a board has fitted a real case. |
| **Injector inductance** (LCR meter, injector unplugged) | Every clamp and temperature figure assumes 20 mH. Near 8 mH there is margin to spare; near 20 mH on a 1989-93 car read the high-rpm note in the README. No board change either way. |
| **Wideband heater current in a hot cabin** | Fuse F1 (2920L300, 3 A hold at 25 °C) holds 1.99 A at 60 °C, against a cold-heater peak of about 2.25 A. If it trips, fit the 2920L400/30GR (C19078761, same pads) instead; it can be swapped in the JLC BOM. |
| **Part orientation** on the received boards (BRING-UP item 3) | The rev 0.9 placement file was made with the same rotation rules (`JLC_ROT`, 2026-10-31) as rev 0.13. A part that came out wrong there will come out wrong again: fix its rule (section 3) before ordering. |

## 2. Files and board settings

Each board's files are in its `fab/` folder.

| Board | Upload to JLCPCB | Order separately and fit by hand |
|---|---|---|
| Daughterboard | `miata-ecu-daughterboard-rev0.13_jlcpcb_gerbers.zip`, `…_jlcpcb_bom.csv`, `…_jlcpcb_cpl.csv` | Nothing: J1 / J2 are castellated edges |
| Motherboard, each year | `miata-ecu-motherboard-<years>-rev0.1x_jlcpcb_gerbers.zip`, `…_jlcpcb_bom.csv`, `…_jlcpcb_cpl.csv` | `…_self_order_bom.csv`: harness header, MAP sensor and its screws, wideband and add-on headers, and the optional R20 |

[`additional-parts/order_all_boards.csv`](additional-parts/order_all_boards.csv) adds up every hand-fitted part for
one motherboard of each year with a daughterboard each, plus the in-car parts.

**Daughterboard:** 6 layers, 1.6 mm, JLCPCB's standard six-layer stack (1 oz outer, 0.5 oz inner copper; the
track-current check assumes that). No via sits in or against an SMD pad, so plain tented vias are fine: no via
filling or capping is needed. Assembly on the top side only. **Choose castellated holes** ("Castellated Holes: Yes",
an extra charge): the 80 half-holes on the long edges are the module's pins, and without the option the edges may be
routed plain. The design meets JLCPCB's castellation rules (1.0 mm holes, 1.54 mm apart, the pads reach 0.85-1.3 mm
in from the edge); check in the preview that the half-holes show plated, and that the option is offered for six layers
on the day.

**Motherboards:** 2 layers, 1.6 mm. Assembly on the top side only; the JLC BOM is the SMD parts and the USB-C socket.
The lands JD1 / JD2 are in the paste stencil, so an assembled board arrives with them tinned.

**Soldering the module down** is yours to do: JLCPCB's assembly does not take one of your own boards as a part on
another (check their "consigned parts" option on the day if you want them to). On a hot plate, in an oven or with an
iron: [INSTALL.md](INSTALL.md#soldering-the-daughterboard-to-the-motherboard).

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

| Part | LCSC | Per board | Stock 2026-11-17 | Enough for |
|---|---|---|---|---|
| microSD socket J4 (daughterboard) | C164170 | 1 | 110 | 110 |
| MPX5700AP MAP sensor (motherboard, by hand) | C90152 | 1 | 155 | 155 |
| TLS115B0EJ, U3 / U14 | C3743696 | 2 | 554 | 277 |
| STM32F405VGT6, U1 | C56621 | 1 | 1,035 | 1,035 |
| 1.5SMC16A injector clamps | C1973780 | 4 | 1,699 | 424 |
| VND7NV04 injector and coil drivers | C155605 | 8 | 2,391 | 298 |

If the injector clamp runs out, any SMCJ14A or SMDJ14A fits the same pads
([daughterboard README](daughterboard/README.md#before-ordering)).

**Harness headers** are hand-fitted and not in the JLC BOM. TE 178780-1 (1996-97 and 1999-2000, LCSC C5166246) had
no JLCPCB stock on 2026-11-17 and few at LCSC; salvaging one from a stock ECU is the fallback. Distributors describe 174917-6 (1989-95) with
two different pitches, so check any listing against the board footprint before buying. Buy 12-15 per year at a time.

## 5. Order in this sequence

1. A pilot of 5 daughterboards and a motherboard for each year you can test (for the two 1996-97 cars: two 1996-97
   motherboards). Rev 0.13 is the first castellated module, soldered flat; rev 0.12 brought a new processor part
   number and a new CAN transceiver, and rev 0.11 / 0.10 the via rule and every rev 0.10 change. None has been built.
   Solder one module down first and check its joints and its temperature at load before ordering more.
2. Bring the pilot up on the bench and in a car. Then one daughterboard lot for every year at once (JLCPCB's Economic
   assembly takes up to 50 boards).
3. Motherboards per year, 8-10 at a time, once that year has run in a car.

## 6. Not in this release

These need the board re-routed. None stops a rev 0.13 board from working; they are in
[NEXT-REV.md](review/2026-11/NEXT-REV.md).

| Item | What it means for a board ordered now |
|---|---|
| 1989-95 header holes still 1.1 mm (pads must grow first) | Test-fit the 174917-6; ream a hole by hand if a pin binds |
| 1989-95: pin 1B's current runs through 46 mm of 0.6 mm track | About 20 °C rise at the heater's cold peak: adequate |
| C12 on the processor's VDDA pin side, ferrite FB1 before it | Analog supply filtering not ideal; the readings work |
| More copper (vias around the tab) at the 3.3 V regulator U4 | 0-1 °C warmer |
| No pull-up footprint on the alternator control wire (1999-2000 1O, 2001-05 3M) | Wire one by hand if the car needs it |
| No tach pull-up footprint on 1996-2005 | Wire one by hand if the car measures about 0 V on the tach wire (section 1) |

## 7. Cost

Parts per board, as priced on 2026-11-17 in each board's `*_costed_bom.csv`; the board itself and assembly fees are
not included. Complete sets per year, with the in-car parts, are in [bom/README.md](bom/README.md).

| Board | Batch 5 | Batch 30 | Batch 100 |
|---|---|---|---|
| Daughterboard rev 0.13 | $49.67 | $42.33 | $38.02 |
| 1989-95 motherboard rev 0.16 | $38.82 | $35.88 | $34.65 |
| 1996-97 motherboard rev 0.12 | $45.90 | $42.37 | $39.67 |
| 1999-2000 motherboard rev 0.12 | $46.01 | $42.48 | $39.76 |
| 2001-05 motherboard rev 0.12 | $41.25 | $38.58 | $36.96 |
