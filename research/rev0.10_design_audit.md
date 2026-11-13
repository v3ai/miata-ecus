# Daughterboard rev 0.10: design audit

Started 2026-11-13, before the new six-layer layout. The aim: list what the board relies on, check each item against
a primary source (the maker's datasheet or data files), and say plainly what could not be checked. "Read" means the
document was fetched and read on that date; "recalled" means it comes from memory or an earlier revision's notes and
was not re-read.

No board has been built. Nothing here is a bench measurement.

## Findings that change the design

| # | Finding | Source | Effect | Action in rev 0.10 |
|---|---|---|---|---|
| A1 | **The eight low-side drivers (Q1-Q8, VND7NV04) need at least 150 Ω in series with their input; the board has none.** ST lists "RIN MIN, minimum input series impedance, 150 Ω" in the absolute maximum ratings, and its switching figures are measured with "Rgen = RIN MIN = 150 Ω". U11 (SN74LVC4245A) drives the inputs directly; its output is about 20 Ω (0.55 V at 24 mA). The wideband heater driver (same family, VND14NV04) has FOME's 1 kΩ, so only Q1-Q8 are affected. | ST VNx7NV04 datasheet, Doc ID 7383 rev 4, table 2 and table 4 (read) | **Applies to the ordered rev 0.9 boards too.** ST does not say what happens below 150 Ω. The input pin is the MOSFET gate ("electrically connected to the gate"), so the likely cost is current in the input structure when the internal clamp or a protection acts against a stiff driver. In normal switching nothing visible would happen; the risk is in the clamp and fault cases, and it is not quantified | R152-R159, 220 Ω, between U11 and each driver input (the 10 kΩ pull-downs stay on the driver side). On the ordered boards: see "Ordered boards" below |
| A2 | **The drivers' clamp starts to conduct at 36 V, not 40 V.** VCLAMP is 40 / 45 / 55 V at 3.5 A, but VCLTH (the threshold) is 36 V at 2 mA. Rev 0.8's check "the 30 V TVS always clamps first, 0 mW in the drivers" used 40 V | Same datasheet, table 4 (read) | An external clamp has to hold the drain under about 36 V to keep the turn-off energy out of a minimum-clamp driver | The new injector clamp is sized against 36 V (A4) |
| A3 | **Injector inductance is not known, and 8 mH may be low.** Every energy and temperature figure up to rev 0.9 assumes 8 mH. A published fit for a 14.8 Ω port injector gives 20.3 mH. Mazda specifies resistance (12-16 Ω) only | Sensors 2020, 20, 4151 (read, one injector, not a Miata part); Mazda value recalled | Clamp energy scales with inductance: 2.5 times the documented figures at 20 mH. On the ordered boards a driver would take 0.9 W instead of 0.4 W at 7200 rpm sequential, and the 1989-93 motherboard's D3/D4 about 3.9 W each instead of 1.55 W | Everything is now sized for 20 mH. Measuring one Miata injector with an LCR meter would settle it |
| A4 | **Injector clamp: per injector, a fast diode to a 14 V TVS that returns to the battery input**, not one shared TVS to ground. A TVS to ground under 36 V conducts whenever the supply is above it: continuously in a 40-45 V load dump, through the injectors, and a TVS that fails short there holds its injectors open. Returned to the battery input the clamp has no DC path at any supply voltage, and it puts 40 % less heat into the ECU, because the supply adds no energy during the decay | `firmware/tools/sim_inj_clamp.py` (ngspice) | 20 mH, 14.4 V: 8.8 mJ per shot in the TVS and diode against 15.3 mJ in a driver today; peak 32 V; current falls to 35 % in 0.56 ms against 0.41 ms, so **the injector dead time grows by roughly 0.05-0.15 ms** and the tune's dead-time table needs checking on the car. SMCJ14A is the highest part that keeps a minimum-clamp driver out of it at 15.5 V with the TVS hot (16A: the driver takes all of it in that corner) | D42-D45 ES1D, D46-D49 SMCJ14A. The 1989-95 motherboard's D3/D4 take nothing once this is fitted (simulated) and can come off |
| A5 | **The microSD socket named in the WIP design was push-pull, not push-push.** Molex 104031-0811 holds the card by friction only | KiCad library description of the Molex drawing; element14 listing (read) | A card can walk out under vibration | Molex 47219-2001, hinged lid (LCSC C164170), the socket rusEFI's boards use |
| A6 | **SD cards want pull-ups on every data line, also in SPI mode.** DAT1 and DAT2 were left open | Espressif's summary of the SD specification (read); the specification itself was not read | A floating input on the card: extra supply current, in the worst case erratic behaviour | 47 kΩ on CS, DI, DO, DAT1 and DAT2 |
| A7 | **Logic supply fuse and filter (F1 0.5 A, L1 0.5 A) are too small**, as the external review said; the card adds up to 0.1 A at 3.3 V | Review note in VERIFICATION.md; SD current recalled (100 mA default speed) | A hot ECU with a weak crank could trip F1 | F1 1.1 A hold, 33 V, 1812; L1 to match |

## Checked and found correct

| Item | Checked against | Result |
|---|---|---|
| Processor pin numbers, supply pins, and the peripheral each net needs (CAN2, USB, SPI2 for the card, USART3, SWD, ADC channels), one EXTI line per interrupt input | ST's pin data file for the STM32F407VGT6 in LQFP100 (`research/st/`, from ST's STM32_open_pin_data), by `firmware/tools/check_mcu_pins.py` | All 79 connected pads match. The hand-made pin table the other tools use agrees with ST on all 100 pins. Flex on PC6 has EXTI line 6 to itself |
| Wideband processor (STM32F103C8T6) pins: CAN on PA11/PA12, USART1 on PA9/PA10 to the main processor's USART3, heater PWM on TIM2_CH3, ADC inputs | ST's pin data file for the F103C8 in LQFP48 | Match |
| VND7NV04: 60 mΩ at 25 °C / 120 mΩ over temperature, 6 A minimum limit, 200 mJ single pulse, 2.1 °C/W junction to case, shutdown 150 °C minimum, input threshold 0.5-2.5 V, 150 µA input current | ST datasheet (read) | As used in the design and the simulations |
| ZXMS6004FF: 60-70 V clamp, 500 mΩ at 5 V and 600 mΩ at 3 V, limit 1 A minimum, input current 220 µA maximum in shutdown, no series resistor asked for | Diodes datasheet (read; the pin drawing did not extract, so pins 1 IN / 2 S / 3 D rest on the earlier revision's reading) | As used. It switches fully from 3 V, which the CEL change below relies on |
| TLS115B0EJ pins (1 OUT, 3 GND, 5 ADJ, 7 EN, 8 IN, pad GND), 150 mA, output may be shorted to battery, tracks only while IN is 1 V above ADJ | Infineon datasheet v1.11 (read) | Pinout matches. EN tied to the 12 V rail is inside its 45 V rating |
| LMR14020 pins, 0.75 V reference (68k / 12k gives 5.0 V), 10 kΩ on RT is about 2.2-2.3 MHz inside the 2.5 MHz limit, EN may be tied to VIN, 0.1 µF boot capacitor | TI datasheet SNVSAA5B (read) | Matches |
| SN74LVC4245A pins, A port is the 5 V side, DIR low sends B to A, DIR and OE referenced to the 5 V supply, either supply may come up first | TI datasheet SCAS375 (read) | Matches the wiring of U11 and U12 |
| Flex-fuel sensor: 12 V supply, the ECU pulls the signal up to 5 V, the sensor pulls it low, 50-150 Hz, 1-5 ms pulses | A reproduction of GM's workshop manual (read; not GM's own site) | Matches the 4.7 kΩ pull-up to the sensor 5 V on the motherboards and the 12 V pin on the add-on header |
| JLCPCB six-layer limits: 0.09 mm track and gap, 0.15 mm hole / 0.25 mm via minimum (0.2 mm hole preferred), 0.2 mm hole to track, via-in-pad filled and capped by default | JLCPCB capabilities page (read) | The design rules in use (0.15-0.2 mm tracks, 0.6 / 0.3 mm vias) are well inside them |

## Not verified

- **Injector inductance** (A3) and the injector's real closing time against clamp voltage. Simulated current decay is
  a stand-in for closing time.
- **What happens to a VND7NV04 driven without the 150 Ω** (A1). The rule is ST's; the consequence is my reading.
- **The TVS temperature coefficient**: Littelfuse gives the formula without the number; 0.1 %/°C is assumed.
- **Load dump level.** The design assumes a suppressed dump of about 35 V. Above 36-40 V the drivers' own clamps conduct
  through their loads for as long as the dump lasts (0.5-0.7 A and about 25 W per injector driver at 45 V, simulated).
  Whether a Miata alternator limits the dump is not known. This is unchanged from rev 0.9.
- **Stock at JLCPCB/LCSC** for the new parts. Numbers were found by search on 2026-11-13; stock was not checked.
- **Thermal figures** are copper-area estimates, as before, until the layout exists; then they are estimates from the
  real copper. Eight drivers in a row heat each other.
- **The SD specification's own text** on pull-ups, and the GM flex-sensor document from GM itself.
- **ZXMS6004FF pin drawing and the SOT23F land pattern** against the SOT-23 footprint in use (geometry worked out from
  recalled package dimensions: the flat leads land fully on the pads).

## Ordered boards (rev 0.9)

A1 applies to them. The boards will switch injectors as designed; what is not guaranteed is the drivers' behaviour
when they clamp or protect themselves. Two ways to bring them inside ST's rating, both by hand:

- lift pin 1 (the input, left lead) of each of Q1-Q8 and bridge it to its pad with a 220 Ω 0603; or
- cut each track between U11 and the driver input and bridge the cut with a 220 Ω 0402.

A3 also applies: with 20 mH injectors the drivers and, on the 1989-93 motherboard, D3/D4 run hotter than documented at
sustained high rpm. Measure an injector before trusting the published temperatures.

## Changes folded in from the external review (2026-11-12)

CEL no longer behind the shared driver enable (gate driven from the processor pin directly: the ZXMS6004FF switches
from 3 V); battery sense taken from the battery input itself; 100 nF at the buck converter's input pins; the wideband
battery-sense resistor next to J1; RC filters on the flex and nitrous inputs (10 µs and 100 µs). Not changed: the
analog clamp diodes (a lower-leakage Schottky clamps 0.1-0.15 V higher, above the 3.6 V the analog pins allow; the
hot-leakage error stays a documented limit).
