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
- **Tach output** is already off on 1989-95 in the current firmware (the ordered motherboards wire it straight to 2I).

## Measurements to take while the boards are on the bench

These decide open design questions for the next order; the list with what each one decides is in
[NEXT-BATCH.md step 2](../../review/2026-11/NEXT-BATCH.md#step-2-take-the-measurements-that-decide-open-design-questions).
The most useful first: the inductance of one stock injector (LCR meter), supply current at 6 / 8 / 13.8 V, the
drivers' temperature under load in a closed case, and the wideband against a commercial unit.
