# What changed in each revision

Newest first. The boards' own change lists are in each board's README ([daughterboard](daughterboard/README.md),
[1989–95](motherboards/1989-95/README.md), [1996–97](motherboards/1996-97/README.md),
[1999–2000](motherboards/1999-2000/README.md), [2001–05](motherboards/2001-05/README.md)). The desk and simulation
checks behind each step are in [VERIFICATION.md](VERIFICATION.md).

Current boards: daughterboard rev 0.14; motherboards rev 0.19 (1989–95) and rev 0.15 (1996–97, 1999–2000, 2001–05).
No board has been built or tested yet.

**Rev 0.14 (2026-11-23; motherboards rev 0.19 / 0.15):** the ECU reads the car's own
air-temperature sensor by default (the firmware's curve is Mazda's), so no GM sensor is needed; on 1989–93 the airflow
meter stays plugged in and runs the fuel pump through the stock circuit opening relay, and JP6 ships on AFM
([INSTALL.md](INSTALL.md#7-air-temperature)). The 1996–2005 boards gain R37, a not-fitted tachometer pull-up to 12 V,
for a car whose wiring leaves the tach wire low ([1996–97 card](quickstart/1996-97.md#measure-before-you-remove-the-stock-ecu)).
No silkscreen is printed on a pad, a part, other silkscreen or the board edge on any board any more, and the
release check now fails a board where any is (`scripts/silk_clean.py`; the daughterboard had 404 such items); the
daughterboard's status lights are named RUN / COMM / WARN / ERR / PWR and its buttons BOOT / RESET, and the
motherboards' land rows read JD1 / JD2. **1989–95:** the year jumpers JP1–JP4 are gone. The pins that differ between
1989–93 and 1994–95 are on 0 Ω links R38–R42, each named on the board with its years, and JLCPCB fits them for the
car: the board is assembled in two versions, each with its own BOM and CPL (`fab/..._for-1989-93_` /
`_for-1994-95_`), from one PCB. JP5 (tach after a coil-on-plug conversion) and JP6 (airflow meter or BOOST) stay
jumpers. **MAP sensor screws:** M3 × 16 with nylon-insert nuts (the parts lists had M3 × 10, which is too short).
The MPX5700AP is one solid block about 8 mm thick with its holes through all of it (NXP case 867B-04), and our 3D
model had shown a thin flange. Same pinout, and a rev 0.13 daughterboard fits these motherboards; the copper changed
only round R37 (1996–2005) and the year links (1989–95).

**Rev 0.13 (2026-11-20; motherboards rev 0.16 / 0.12):** the daughterboard is a **castellated module**. Its long edges
run through the old header pin rows, so its J1 / J2 pins are 80 plated half-holes, and it is soldered flat onto
two rows of lands on the motherboard, by reflow or with an iron: no headers, sockets, standoffs or screws, and the
1×40 sockets that were the scarcest part are gone. Same parts, placement, routing and pinout on the daughterboard
(125 × 70.5 mm now); on the motherboards the parts that sat under it moved out and the copper to the lands was
joined again. An earlier daughterboard does not fit these motherboards, nor this one the earlier motherboards.
Soldering it down: [BUILD.md](BUILD.md#1-solder-the-daughterboard-to-the-motherboard). Motherboards rev 0.18 / 0.14
(the same day) name the add-on header J5's pins on the silkscreen on both sides of it, each name next to its own
row and readable with the ribbon plug fitted (R35 / R36 moved left of J5 to make room); each motherboard folder has a 3D render of that board with the daughterboard on it (`renders/assembly.jpg`).

**Rev 0.12 (2026-11-20; motherboards rev 0.15 / 0.11):** the processor is the STM32F405 (JLCPCB stocks it; the
F407 and F427 fit the same pads), the CAN transceivers are NXP TJA1042T/3, R21 / R22 are fitted so the A/C request
and clutch switches (which close to ground) are read, and the 1996–2005 harness headers have 1.3 mm holes. The
firmware adds rev limits for a cold engine, lambda protection, an overboost cut and a MAP-failure fallback; the
wideband controller has a watchdog on its heater loop.

**Rev 0.11 (2026-11-18; motherboards rev 0.14 / 0.10):** no via in or against any SMD pad on any board, so the
boards need no filled vias. The vias that sat in the driver tabs are now in the tab copper around them, the others
beside their pads; every board passes KiCad's DRC with nothing unconnected, and the release check now fails a board
with a via in a pad. Every unit ships with a GM air-temperature sensor for the car's own IAT wires, and the 1989–93
fuel pump runs from the airflow meter's old signal wire (JP6 on BOOST). *(Both were changed afterwards: the ECU now reads the car's own air-temperature sensor by default, and the 1989–93 fuel pump stays stock, with JP6 on AFM. See [INSTALL.md](INSTALL.md#7-air-temperature).)* R110 is the 62 Ω part. The change list:
[review/2026-11/NEXT-REV.md](review/2026-11/NEXT-REV.md).

**2026-11-15:** those choices are made. The processor stays the standard STM32F407VGT6, as on every other board
read. The 1989–95 motherboard gets no clamp parts of its own; 1990–93 cars used at sustained high rpm are converted
to one wire per injector instead ([INSTALL.md](INSTALL.md#one-wire-per-injector-on-a-199093-car-optional)). AEM's
wideband harness stays. The injector clamp TVS is now a part JLCPCB has: the 185 °C part first named was not in
its stock, and nothing rated above 150 °C in that package was
([what was found](VERIFICATION.md#clamp-tvs-what-jlcpcb-stocks-2026-11-15)). On a stock-wired 1989–93 car one
driver now works each injector wire, as on rusEFI's and Speeduino's boards for these cars: JP1 and JP2 carry no
shunt. The boards themselves are unchanged
([what it means](VERIFICATION.md#1989-93-one-driver-per-injector-wire-2026-11-15)).

**2026-11-14:** the motherboards' wideband connector was the wrong series (a guess); it is now the JST header
that AEM's instructions point to (motherboards rev 0.13 / 0.9, routed again). The full-firmware emulation was run
again with the rev 0.10 firmware, and the pictures and 3D viewer were redrawn from the current boards.
[What other Miata plug-in ECUs do](research/other_miata_pnp_boards.md) about the choices still open is written up.

**Rev 0.10 (2026-11-13):** the daughterboard is now six layers in the same outline, with a turn-off clamp per
injector, a microSD socket and flex-fuel and nitrous inputs; the motherboards take AEM's wideband harness and have a
20-pin add-on header with CAN, and 1989–93 and 1994–95 share one board set by jumpers. Before the layout every
figure the design rests on was read again from its maker's document. That found a series resistor the injector
drivers' inputs should always have had, and showed that the injector inductance behind every temperature estimate
was a guess. A model of the whole board's copper now gives those temperatures. See
[Rev 0.10](VERIFICATION.md#rev-010-six-layers-injector-clamps-card-socket-two-more-inputs-2026-11-13).

**1989–93 motherboard rev 0.11:** the manual cars' throttle position sensor conversion uses the stock throttle switch
plug, through three 0 Ω links. Pin 1N is no longer wired straight to the sensor 5 V, which the stock switch would have
shorted at every idle. See [Throttle position sensor (1989–93 manual cars)](README.md#throttle-position-sensor-198993-manual-cars).

**Rev 0.9:** layout only. J1 is back on the daughterboard's top edge with the driver strip below it, and the
daughterboard sits 16 mm lower, centred on each motherboard. Re-checked: same results as rev 0.8.

**Rev 0.8 (2026-11-03):** a larger daughterboard (125 × 76 mm) with DPAK injector drivers on drain copper and thermal
vias (estimated 110 °C at 90 % duty and 85 °C ambient, where rev 0.7 reached thermal shutdown), protected relay, lamp,
tach and ignition outputs, a separate protected 5 V for the harness sensors, LSU drive clamps, a +3V3 shunt clamp and
fault-tolerant CAN transceivers. Every harness cavity shorted to ground, 14.4 V and 24 V: 4 failures left (rev 0.7:
215), all the LSU drive resistors taking a battery short so the ICs don't. See
[Rev 0.8](VERIFICATION.md#rev-08-driver-temperature-and-protected-outputs).

**Full-firmware emulation (2026-11-02):** the unmodified rusEFI firmware runs on an emulated STM32F407 through every
model year with 0 failures (two firmware bugs found and fixed). It flashes a blank emulated wideband STM32F103, which
then reports lambda over CAN (`firmware/sim/`). The expanded circuit and fault checks found 13 new hardware items
(N1-N13). Daughterboard rev 0.7 and the motherboards' 3 A heater fuse fixed most of them; see
[Rev 0.7](VERIFICATION.md#rev-07-fixes-for-the-2026-11-02-findings).

**Verification (desk + simulation, 2026-10-30):** [VERIFICATION.md](VERIFICATION.md). Pinouts and firmware check out
for all five years (after fixing a firmware bug that would have cut fuel and spark on 1996-2002 cars). The hardware
changes it called for are in daughterboard rev 0.5 and motherboards rev 0.6 (1989-95) / 0.4 (1996-2005):
- 5 V drive for the low-side drivers, held off until the firmware runs;
- freewheel diodes on the idle and VVT valves;
- BOOT1 pull-down;
- no 2003-05 key-off back-feed;
- a fused, clamped logic supply and a fused AUX +12 V pin;
- clamped crank/cam inputs;
- two drivers per injector wire on 1989-93.

Every fix was re-simulated. Two wires still need checking on a car.

## Ordered boards, 2026-11

**The boards ordered in November 2026** are the set before the current one (daughterboard rev 0.9). Their files are kept in
[`ordered-boards/2026-11/`](ordered-boards/2026-11/), with [what to rework, check and set before first power](ordered-boards/2026-11/BRING-UP.md); what the rev 0.10 review means for them is in
[VERIFICATION.md](VERIFICATION.md#the-ordered-rev-09-boards).

### What the bring-up of the rev 0.9 boards should settle before more boards are ordered

These were the checks in the previous ORDERING.md ("Settle these on the received rev 0.9 boards first"). Each of
them can change a current board or how you fit it. The measurements are described in
[BRING-UP.md](ordered-boards/2026-11/BRING-UP.md).

| Check | What the answer changes |
|---|---|
| **A/C request and clutch** (1996-97 cavities 1K, 1L): switched to ground or to 12 V? | The boards fit R21 / R22 (4.7 kΩ to 12 V) because the stock ECU's voltage tables show switches to ground. If a car drives either wire to 12 V, leave that resistor off (delete its line from the JLC BOM and placement file) and set the input back to active high. |
| **Tachometer** (1996-97 4L; 1999-2000 2K; 2001-05 3O): about 0 V or 12 V with the stock ECU out? | At about 0 V the cluster needs a pull-up of about 1 kΩ to switched 12 V. The 1996-2005 motherboards have no footprint for it yet, so it would be wired by hand. |
| **Harness header fit.** The rev 0.9 motherboards have 1.1 mm holes; TE asks for 1.35 mm. | The motherboards drill 1.3 mm on 1996-97, 1999-2000 and 2001-05. If the pins went into 1.1 mm without force, 1.3 mm is comfortable. The 1989-95 board is still 1.1 mm, so test-fit a 174917-6 there before ordering 1989-95 boards. |
| **Case fit, 1996-2005.** These motherboards use the NA outline and mounting holes as a placeholder. | Measure a stock 1996-97 / NB case and fit a rev 0.9 motherboard in it. The 76-position header is 130 mm wide. Do not order 1996-2005 motherboards in quantity until a board has fitted a real case. |
| **Injector inductance** (LCR meter, injector unplugged) | Every clamp and temperature figure assumes 20 mH. Near 8 mH there is margin to spare; near 20 mH on a 1989-93 car read the high-rpm note in the README. No board change either way. |
| **Wideband heater current in a hot cabin** | Fuse F1 (2920L300, 3 A hold at 25 °C) holds 1.99 A at 60 °C, against a cold-heater peak of about 2.25 A. If it trips, fit the 2920L400/30GR (C19078761, same pads) instead; it can be swapped in the JLC BOM. |
| **Part orientation** on the received boards (BRING-UP item 3) | The rev 0.9 placement file was made with the same rotation rules (`JLC_ROT`, 2026-10-31) as the current one. A part that came out wrong there will come out wrong again: fix its rule ([ORDERING.md, check the placement preview](ORDERING.md#3-check-the-placement-preview)) before ordering. |
