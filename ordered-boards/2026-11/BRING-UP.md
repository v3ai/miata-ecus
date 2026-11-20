# Bringing up the boards ordered in November 2026

These are daughterboard rev 0.9 with the motherboards of that order (1989-93 rev 0.11, 1994-95, 1996-97, 1999-2000
and 2001-05). The full checklist, with the reason for each item, is
[REPORT.md Part 1](../../review/2026-11/REPORT.md#part-1-rework-and-checks-before-first-power-up-of-the-ordered-boards);
the staged bench sequence is its section 1B. This page is the short version, plus what changed in the firmware since
the review.

## Before first power

1. **Replace R110 on every daughterboard** with a 62 Ω 1 % 1206 resistor (LCSC C17971). The fitted part is 0.62 Ω;
   the wideband reads about lambda 1.0 whatever the mixture until it is changed. The sensor is not harmed.
2. **Check the JLCPCB order record for "epoxy filled and capped" vias.** If the vias were not filled, look at the
   Q1-Q8 tab joints and the processor's pins under a loupe for solder that ran down a via.
3. **Check the orientation** of the SOT-23 diodes (D15-D18, D35-D37), each motherboard's USB protection part U4 and
   D6, D7, D12 against the assembly drawing.
4. **1996-97 and 1999-2000: test-fit the harness header** before soldering it (1.1 mm holes, TE asks for 1.35 mm).
5. **The IAT jumper JP1** on each motherboard: shunt on **1-2 (STOCK)** to read the car's own sensor through the
   harness, or on **2-3 (EXT)** to read a sensor plugged into J3. See "Firmware settings" below: the firmware has to
   be told which sensor it is.
6. **Fit R21 and R22 on each motherboard** (4.7 kΩ 0603, LCSC C23162; the pads are there, marked not fitted): the
   12 V pull-ups of the A/C request and clutch inputs. Those switches close to ground, so without the pull-ups the
   inputs never change. The current firmware reads both inputs active low, which on a board without R21 / R22 means
   "A/C requested" and "clutch pressed" all the time. If you don't fit them, set the A/C switch and clutch pins to
   none in TunerStudio.

7. **1996-2005: the outline and mounting holes are a stand-in** (the 1990-95 case's), not measured from a real case;
   1996-97 and 1999-2000 have four M4 holes, not six. Check the board against your case before cutting or drilling
   anything, and mount it loose until the holes are known.

## Firmware settings for these boards

Flash the current firmware: one firmware serves every daughterboard from rev 0.9 on. It now assumes the current
motherboards, which differ from these in two places. In TunerStudio, after choosing the engine preset:

- **Air temperature sensor.** The firmware loads the GM sensor's curve that ships with the current kit
  (-20 °C 28146 Ω, 40 °C 1443 Ω, 100 °C 175.3 Ω).
  - JP1 on **EXT** with the GM sensor wired to J3: leave it.
  - JP1 on **STOCK**, reading the car's own Mazda sensor: enter the Mazda curve under Sensors > Intake air
    temperature. 1989-97: -20 °C 16150 Ω, 40 °C 1150 Ω, 80 °C 330 Ω (rusEFI's NA values). 1999-2005: -20 °C
    18000 Ω, 23.9 °C 2100 Ω, 120 °C 100 Ω (the values rusEFI's NB presets load). Left on the GM curve, an NA sensor
    reads about 10 °C high at -20 °C, 8 °C at 20 °C and 6 °C at 40 °C, so the engine runs lean when cold.
  - Leave the bias resistor and supply as loaded (2301.6 Ω, 4.262 V): they are the board's divider, not the pull-up.
- **1989-93 fuel pump.** The firmware switches the pump relay on the boost output, because the current 1989-95
  motherboard sends that output to the airflow meter's wire 2O (jumper JP6). The 1989-93 motherboard of this order has
  no JP6: on these cars keep the airflow meter plugged in, so its contact runs the pump as from the factory, and set
  Fuel pump pin to "none" and Boost control pin back to the boost output if a boost valve is wired to J5.
- **A/C request and clutch switch:** active low (fit R21 / R22 first, item 6 above).
- **Tach output** is already off on 1989-95 in the current firmware (the ordered motherboards wire it straight to 2I).
- **Protections** (firmware from rev 0.12 on): a cold-engine rev limit, an overboost cut at 170 kPa, a MAP-failure
  fallback and lambda protection. Lambda protection cuts fuel when the wideband reads lean under load, so on a
  daughterboard that still has the 0.62 Ω R110 it would act on a false reading: replace R110 first (item 1), or turn
  lambda protection off until it is replaced.
- **Base timing:** lock the timing at 10° in TunerStudio, check it with a timing light and correct the trigger angle
  before driving.
- **Keep a copy** of the firmware and the TunerStudio `.ini` you flash: GitHub keeps the Actions build artifacts for
  a limited time only.
- **Wideband firmware:** the pinned version already refuses to heat on a low or unmeasured supply (upstream 6d27ef2 and
  7670779); upstream 9295698 is not in it and is not needed for that. Still, bench-test the wideband from 12 V, not
  from USB alone.

## Measurements on the car

With the stock ECU unplugged and the key on, measure these cavities to ground. 1996-97 names; the other years are in
[REPORT.md Part 6](../../review/2026-11/REPORT.md#part-6-needs-a-measurement).

| What | 1996-97 cavity | Reading and what it decides |
|---|---|---|
| A/C request, clutch | 1K, 1L | Switch operated: near 0 Ω to ground; released: open. That is the ground-switched input R21 / R22 and the active-low firmware expect. If either is driven to 12 V instead, remove its resistor and set that input back to active high |
| Tachometer | 4L | About 0 V: the cluster needs a pull-up, so add about 1 kΩ from 4L to switched 12 V or the tach stays dead. About 12 V: nothing to do |
| Fan 2 output | 1B | The firmware drives 1B as the second fan (condenser fan relay on the 1996 diagrams; one aftermarket table calls it the A/C relay). Confirm what the wire switches before letting it run |
| 4I | 4I | Possibly a constant battery feed: the board leaves it open. Never drive it |

## Measurements to take while the boards are on the bench

These decide open design questions for the next order; the list with what each one decides is in
[NEXT-BATCH.md step 2](../../review/2026-11/NEXT-BATCH.md#step-2-take-the-measurements-that-decide-open-design-questions).
The most useful first: the inductance of one stock injector (LCR meter), supply current at 6 / 8 / 13.8 V, the
drivers' temperature under load in a closed case, and the wideband against a commercial unit.

For the dwell table (the firmware still has rusEFI's flat 4 ms with no battery-voltage correction): one stock coil's
primary resistance, and its primary current against time at 14 V and at 10 V (a 0.1 Ω shunt in the coil's ground
lead and a scope, the coil driven from the bench supply through the board's ignition output). The time to reach
about 6-7 A at each voltage gives the dwell and its voltage correction.

## Corrections to the frozen documents (2026-11-20)

The files in this folder are kept as ordered; these statements in them are wrong:

- `INSTALL.md` section 3, step 4: "six M4 holes". The 1996-97 and 1999-2000 boards have four (H3-H6).
- `INSTALL.md` section 7: "The year buttons are set for the stock Mazda sensor." True of the firmware as ordered;
  the current firmware loads the GM curve (see "Firmware settings" above).
- `VERIFICATION.md` N5: the heater fuse F1 (LUTE 2920L300/30GR) holds 1.99 A at 60 °C and 1.34 A at 85 °C (LUTE
  datasheet), not about 2.4 A. A cold heater draws up to 2.25 A rms for the first seconds, so in a hot cabin F1 can
  trip during warm-up: if the wideband times out on a hot day, that is the first suspect. The 2920L400/30GR
  (C19078761) fits the same pads.
- The motherboard READMEs: the 76-position header 178780-1 is sold new (LCSC C5166246, a few in stock on 2026-11-20),
  not only salvaged.
