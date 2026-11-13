# Miata ECU motherboard 1989-1995 (NA6 / NA8), rev 0.12

The motherboard replaces the stock Mazda ECU board inside the **stock ECU case**. It carries:

- the stock harness header;
- the year-independent I/O: the wideband sensor connector (AEM X-Series harness), USB-C, the MAP sensor and the add-on header (flex fuel, nitrous, CAN, boost);
- the sockets for the universal daughterboard, which does all the engine control (including the wideband controller).

## Changes in this revision
- Rev 0.12: one board for 1989-93 and 1994-95 (same case and header); the pins that differ are on jumpers JP1-JP6, set for the car (table below). Rev 0.12 is for daughterboard rev 0.10 (a rev 0.9 daughterboard fits too, without the new functions). The wideband sensor connector J2 is a Molex Micro-Fit 2x4 for the off-the-shelf AEM X-Series sensor harness (30-3427) instead of the 2x3 for a hand-made lead; the plug family is assumed, check it against the harness. The separate air-temperature connector J3 and its jumper are gone: the stock sensor's harness wire goes straight to the air-temperature input. The add-on header J5 is a 2x10 box header for a ribbon cable and gains the flex-fuel input (4.7k pull-up to 5 V, R35), the nitrous arming input (10k pull-down, R36) and the CAN bus; a boost valve on it has its own freewheel diode (D5), and its +12 V fuse F4 holds 1.1 A instead of 0.5 A. The tach output only reaches cavity 2I through JP5, left open: 2I is the igniter's signal into the ECU. D3/D4 are not fitted with a rev 0.10 daughterboard, which clamps each injector driver itself. Sequential injection on 1989-93 is now two jumpers (JP1/JP2 to SEQ), not solder links.
- Rev 0.11, for daughterboard rev 0.9: the throttle position sensor conversion uses the stock throttle switch plug, as rusEFI's Hellen NA6 and MRE boards do, instead of rev 0.10's separate lead: J6 is gone. Harness pin 1N (the manual cars' idle contact) is no longer wired straight to the sensor 5 V: it goes through R28 (0R, not fitted), so a car with the stock switch no longer shorts the 5 V to ground at every idle (rev 0.10 and earlier did, if 1N is the idle contact as the rusEFI sources say). Pin 2L goes through R29 (0R, fitted) to the spare analog AUX1 as before, or through R30 (0R, not fitted) to the TPS input. For a sensor on the stock plug: fit R28, move R29 to R30. The links are hand-routed into the rev 0.9 copper; nothing else moved.
- Rev 0.10 (replaced by 0.11): J6, a 4-pin connector for a separate TPS lead.
- Rev 0.9, for daughterboard rev 0.9: the daughterboard sits 16 mm lower, centred on the board (42 mm from the top, as up to rev 0.7), with its J1 on its top edge again: JD1 and the upper standoffs HD1/HD2 are back at their rev 0.7 places, JD2, the lower standoffs HD3/HD4, the AUX header J5 (with F4 beside it) and the parts placed against JD2 (CAN termination R1/R6, pull-up options) are 16 mm lower, and the board is routed again. Not compatible with a rev 0.8 daughterboard.
- Rev 0.8, for daughterboard rev 0.8: the harness's sensor 5 V (1N, 2K) and the AUX header pin J5-14 now come from the daughterboard's protected 5 V (V5_EXT, JD1 pin 13, which was a ground pin): a sensor 5 V wire shorted to the battery no longer back-feeds the MAP sensor and the ECU's own 5 V. The MAP sensor keeps its own supply (V5_SENS). The daughterboard outline on the silkscreen is 16 mm taller (125 x 76 mm): its new strip of output drivers overhangs the free area above JD1. D3/D4 (the batch injector clamps) are now SMCJ30A (33.3-36.8 V breakdown) instead of SMCJ40A: the new daughterboard drivers clamp at 40 V minimum, so a 40 V TVS could leave the turn-off energy in a driver; at 30 V the TVS always clamps first. Not-fitted option R27: 4.7k pull-up from the protected 5 V for the manual cars' TPS idle switch on 2L.
- Rev 0.7: LSU heater fuse F1 is a 3 A hold PTC (LUTE 2920L300/30GR, 30 V, 2920 size) instead of the 2 A 1812 part. A cold LSU 4.9 heater draws 1.6-2.3 A rms at the start of the wideband's warm-up, more than the old fuse holds once warm, so it could trip and the controller time out. No 1812 PTC holds 3 A above 8 V.
- Rev 0.6: freewheel diode D1 on the idle valve and D2 on the purge solenoid (2X) to its +12 V feed (the PWM turn-off energy no longer goes into the daughterboard driver); F4 resettable fuse on the AUX +12 V pin J5-15; not-fitted 12 V pull-up options R20-R22 for the VSS / A/C / clutch inputs. INJ1+INJ4 drive 2U and INJ2+INJ3 drive 2V in parallel (R23/R24), with an SMCJ40A clamp per wire (D3/D4), so no driver carries two injectors; 2Y/2Z are only reached through the not-fitted sequential-conversion links R25/R26.
- Rev 0.5: IAT source is now a removable jumper (JP1, 1x3 2.54 mm header + shunt) instead of the R4 / R5 0R links: shunt on EXT (default) reads the IAT connector J3, on STOCK the stock harness sensor; labelled on the silkscreen.
- Rev 0.4: MAP sensor is now the MPX5700AP (absolute, case 867B, one barb; LCSC C90152) instead of the MPX5700DP: new footprint with the real lozenge body and offset barb, holes on the NXP 23.11 mm spacing with 3.3 mm M3 clearance drills.
- Rev 0.3: sensor 5 V now on both 1N (NA6, per the Hellen NA6 map) and 2K; spare low side on 1R (the early cars' BLK/GRN fan-relay wire); 2S left open (it is only used on 94-95).
- Rev 0.2: wideband controller moved to the daughterboard; J5 centred; MAP sensor rotated 90 deg clockwise; LSU connector 6 mm right; SWD header removed; heater fuse now 30 V rated.

## Files
| Path | What |
|---|---|
| `miata_mb_8995.kicad_pro / .kicad_sch / .kicad_pcb` | KiCad 7 project. Root schematic plus three sheets: harness, daughterboard, I/O |
| `miata_mb_8995_schematic.pdf` | Schematic PDF |
| `fab/miata-ecu-motherboard-1989-95-rev0.12_jlcpcb_gerbers.zip`, `fab/miata-ecu-motherboard-1989-95-rev0.12_jlcpcb_bom.csv`, `fab/miata-ecu-motherboard-1989-95-rev0.12_jlcpcb_cpl.csv` | JLC fabrication and assembly files (2 layers, 1.6 mm). The JLC BOM is the SMD parts and USB-C only |
| `fab/miata-ecu-motherboard-1989-95-rev0.12_self_order_bom.csv` | Everything you order and fit yourself: harness header, through-hole connectors, MAP sensor, shunt, standoffs and screws, plus the not-fitted options. Its columns load into LCSC's BOM tool |
| `fab/miata-ecu-motherboard-1989-95-rev0.12_parts_list.csv` | Every part, including the hand-fitted and not-fitted ones |
| `fab/drc_report.txt` | KiCad DRC |
| `ecu_mb.pretty/`, `fp-lib-table` | Project footprints (harness header, MAP sensor lying flat, USB-C, M4 case hole) |
| `renders/` | Top and bottom copper |
| `scripts/` | The design source; `mb_make.sh` rebuilds the whole board |

## Case fit
Stock NA case (same for 1990-95). Outline and holes come from the rusEFI microRusEFI NA plug-and-play board, which fits this case, measured against its known 48-pin header footprint, and from the early Hellen NA6 KiCad board (rev a/b), which uses the same Mazda case outline. H1 is a recessed boss: stack 3 M4 washers under the board.

Board: **154.0 × 161.5 mm**, 1.6 mm. The origin is the top-left corner and y points down, toward the bottom edge.

| Hole | x, y (mm) |
|---|---|
| H1 | 17.0, 7.3 |
| H2 | 137.0, 7.3 |
| H3 | 4.0, 84.0 |
| H4 | 150.0, 84.0 |
| H5 | 4.0, 143.0 |
| H6 | 150.0, 143.0 |

All holes are 4.5 mm plated with a 7 mm pad, tied to GND, for M4 screws. Harness header terminal 1A sits at (39.70, 18.13) mm (lower pin row).

## Harness header
TE **174917-6**, 48 pins: plug 1 = 1A-1V (22 pins), plug 2 = 2A-2Z (26 pins); rusEFI's 1990 page calls the second plug 3A-3Z. TE lists it as not currently available: desolder one from a stock ECU or use a clone. Fitted by hand.

| Pin | Net | Use | Stock function / note |
|---|---|---|---|
| 1B | `VBAT_IN` | ECU power (main relay) | main relay output: ECU power |
| 1C | `VIGN_IN` | switched 12 V sense (wakes the logic supply) | starter (START) signal: battery only while cranking. Not ignition-on: the firmware doesn't use it as ignition sense |
| 1E | `OUT_CEL` | check engine lamp |  |
| 1G | `OUT_IGN1` | ignition 1 (5 V logic) | igniter 1&4 (wasted spark) / COP 1 |
| 1H | `OUT_IGN2` | ignition 2 (5 V logic) | igniter 2&3 (wasted spark) / COP 2 |
| 1J | `OUT_AC` | A/C relay | A/C relay |
| 1L | `OUT_FAN` | fan relay | radiator fan relay |
| 1M | `IN_SW1` | 12 V switch input 1 | vehicle speed sensor |
| 1N | `HARN_1N` | option links R28 | manual cars: the stock throttle switch's idle contact (closes to ground at idle). 5 V only through R28 (not fitted), for a 0-5 V sensor on the stock plug |
| 1Q | `IN_SW2` | 12 V switch input 2 | A/C switch |
| 1R | `HARN_1R` | jumper JP3 | A/C extra cooling fan relay (BLK/GRN) on 1990-91: second fan output through JP3 (position 90-93) |
| 1V | `IN_SW3` | 12 V switch input 3 | clutch switch |
| 2A | `GND` | ground |  |
| 2B | `GND` | ground | power ground |
| 2C | `GND` | ground |  |
| 2D | `GND` | ground | signal ground |
| 2E | `IN_HALL1` | hall input 1 (crank) | CAS crank (SGT, open collector) |
| 2F | `GND` | ground | AFM ground |
| 2G | `IN_HALL2` | hall input 2 (cam) | CAS cam (SGC) |
| 2I | `HARN_2I` | jumper JP5 | stock: the igniter's signal INTO the ECU (the igniter drives the tachometer itself). JP5 open. |
| 2K | `V5_EXT` | sensor 5 V reference (out; protected, short-to-battery proof) | 5 V sensor reference (protected harness 5 V) |
| 2L | `HARN_2L` | option links R29 / R30 | manual cars: the throttle switch's other contact. R29 (fitted) to the spare analog AUX1, or R30 (not fitted) to the TPS input after a sensor conversion |
| 2M | `IN_TPS` | TPS | automatics' TPS signal (a manual car's converted sensor comes in on 2L through R30) |
| 2N | `IN_AUX2` | spare analog 2 | stock narrowband O2 |
| 2O | `HARN_2O` | jumper JP6 | airflow meter signal. JP6: to the spare analog input (AFM), or the boost valve output on this wire once the meter is gone |
| 2P | `IN_IAT` | air temperature (stock sensor) | air temperature sensor in the airflow meter |
| 2Q | `IN_CLT` | coolant temp |  |
| 2R | `HARN_2R` | jumper JP4 | 1994-95: pressure regulator control solenoid, through JP4. Not connected on 1989-93 |
| 2S | `HARN_2S` | jumper JP3 | 1994-95: condenser fan relay, second fan output through JP3 (position 94-95) |
| 2T | `OUT_FP` | fuel pump relay | fuel pump relay |
| 2U | `OUT_INJ1` | injector 1 | 1989-93: two injectors on this wire (JP2 on PAIR adds the INJ4 driver). 1994-95: injector 1 |
| 2V | `OUT_INJ2` | injector 2 | 1989-93: the other two injectors (JP1 on PAIR adds the INJ3 driver). 1994-95: injector 2 |
| 2W | `OUT_IACV` | idle air valve |  |
| 2X | `OUT_VVT` | PWM low side (VVT driver) | purge solenoid (VVT driver reused, set as purge / generic PWM) |
| 2Y | `HARN_2Y` | jumper JP1 | 1994-95: injector 3 (JP1 on SEQ). 1989-93: empty until a sequential conversion |
| 2Z | `HARN_2Z` | jumper JP2 | 1994-95: injector 4 (JP2 on SEQ). 1989-93: A/T control unit on automatics, never JP2 on SEQ there |

Not connected: 1A, 1D, 1F, 1I, 1K, 1O, 1P, 1S, 1T, 1U, 2H, 2J.

## Bottom edge, left to right
| Ref | What | Notes |
|---|---|---|
| J2 | Wideband sensor (Molex Micro-Fit 3.0, 2×4, right angle) | For the **AEM X-Series sensor harness 30-3427** and a Bosch LSU 4.9. Pin 1 trim (LSU RT), 2 heater −, 3 common (VM), 5 pump current (IP), 6 sense (UN), 8 heater +; 4 and 7 empty. The pin functions are from AEM's manual; **that the harness plug is a Micro-Fit 2×4 is an assumption: check it against the harness before ordering.** Heater fed from the main relay through F1 (3 A hold, 30 V, 2920). The controller is on the daughterboard |
| J4 | USB-C | USB 2.0 device: tuning, logging, DFU |
| U2 | MPX5700AP | Absolute MAP sensor (15-700 kPa, case 867B). Lies flat on 2 × M3, marking side up, leads bent 90° down, the single barb toward the board centre |

**Air temperature:** the stock sensor's harness wire goes straight to the air temperature input (inside the airflow meter on 1989-97, in the air filter box on 1999-2005). The separate IAT connector and its jumper are gone. The pull-up is 2.7 kΩ.

**CAN:** R1 + R6 terminate the bus at the ECU end; remove R6 if the bus is terminated elsewhere. The bus is on the add-on header (J5-19 CAN H, J5-20 CAN L) for a dash or gauges; it is the bus the on-board wideband controller reports on, at 500 kbit/s.

**Add-on header (J5, 2×10 box header, 2.54 mm; a 20-way ribbon cable fits):** what the stock harness has no pins for.

| Pin | Net | Use |
|---|---|---|
| 1 | `OUT_IGN3` | ignition 3 (5 V logic), coil-on-plug |
| 2 | `OUT_IGN4` | ignition 4 (5 V logic), coil-on-plug |
| 3 | `OUT_BOOST` | boost valve, low side (freewheel diode D5 to pin 15 on the board) |
| 4 | `OUT_ALT` | alternator driver, low side |
| 5 | `OUT_MAINRLY` | main relay driver, low side |
| 6 | `IN_KNOCK` | knock sensor |
| 7 | `VR1_P` | VR input 1 + |
| 8 | `VR1_N` | VR input 1 − |
| 9 | `VR2_P` | VR input 2 + |
| 10 | `VR2_N` | VR input 2 − |
| 11 | `IN_AFR` | external 0-5 V wideband |
| 12 | `IN_FLEX` | flex-fuel sensor signal (4.7 kΩ pull-up to 5 V on the board, R35) |
| 13 | `IN_N2O` | nitrous arming switch: 12 V = armed (10 kΩ pull-down on the board, R36) |
| 14 | `V5_EXT` | sensor 5 V (protected) |
| 15 | `AUX_VBAT` | +12 V from the main relay through F4 (1.1 A hold) |
| 16 | `GND` | ground |
| 17 | `GND` | ground |
| 18 | `GND` | ground |
| 19 | `CAN_H` | CAN high |
| 20 | `CAN_L` | CAN low |

**Flex fuel** (GM / Continental type sensor): signal to J5-12, sensor +12 V from J5-15, ground to J5-16. In TunerStudio set the flex sensor input to "Flex input (J2-24)". **Nitrous:** arming switch from +12 V to J5-13; in TunerStudio enable nitrous control, set the trigger to "Nitrous arm (J2-25)" and pick a spare output (boost on J5-3, or the second fan output) for the solenoid relay. **Boost valve:** between J5-15 (+12 V) and J5-3. All of these need a rev 0.10 daughterboard.

**Jumpers (2.54 mm headers with shunts, in the margins beside the daughterboard):** this one board covers 1989-93 and 1994-95; the pins that differ are on jumpers. Set them for the car before the first start.

| Jumper | Marked | 1989-93 | 1994-95 | What it does |
|---|---|---|---|---|
| JP1 | INJ3 | PAIR | SEQ | Injector 3 driver: PAIR = in parallel with INJ2 on 2V (1989-93 stock harness, two injectors per wire); SEQ = its own wire 2Y (1994-95, or a 1989-93 sequential conversion) |
| JP2 | INJ4 | PAIR | SEQ | Injector 4 driver: PAIR = in parallel with INJ1 on 2U (1989-93 stock); SEQ = its own wire 2Z (1994-95, or a 1989-93 sequential conversion). NEVER SEQ on a 1989-93 automatic: 2Z is the A/T control unit |
| JP3 | FAN2 | 90-93 | 94-95 | Second fan relay output: 1R on 1990-93 (the 1990-91 A/C fan), 2S on 1994-95 (condenser fan) |
| JP4 | 94-95 2R | open | fitted | Fit on 1994-95: the pressure regulator control solenoid on 2R. Leave open on 1989-93 |
| JP5 | TACH COP | open | open | Leave OPEN with the stock igniter: it drives the tachometer and sends its signal to the ECU on 2I. Fit only after a coil-on-plug conversion with the igniter removed: the ECU then drives the tachometer through 2I (R37 is its 12 V pull-up; join the two tach wires at the old igniter plug) |
| JP6 | 2O | AFM | AFM | Airflow meter signal wire 2O: AFM = to the spare analog input (stock); BOOST = boost valve output on that wire once the meter is removed (valve between the old meter plug's signal pin and 12 V) |

**Protection:** D1 (and D2 where the VVT driver runs a coil) freewheel the PWM valve coils into their own +12 V feed, and D5 does the same for a boost valve on the add-on header, so the drivers don't absorb the turn-off energy. F4 fuses the add-on header's +12 V pin (1.1 A hold: a boost valve draws about 0.5 A).

**Switch inputs (R20-R22, not fitted):** the VSS, A/C and clutch inputs read signals that are driven to 12 V. If your car's signal only switches to ground (or is open collector), fit the 4.7 kΩ pull-up for that input. Never fit it for a switch that drives 12 V: the input would always read on.

**Throttle position sensor (manual cars):** the 1989-93 manual cars have no throttle position sensor, only a two-contact switch. The ECU calculates fuel from the MAP sensor, so the car runs without one, but rusEFI then flags the throttle sensor as failed and drops closed-loop idle, throttle-based acceleration fuel and overrun fuel cut. A 0-5 V sensor fits on the stock wiring, as on rusEFI's Hellen NA6 and MRE boards: the switch plug has three wires, the idle contact (1N), ground (2D) and the full-throttle contact (2L), and a sensor needs 5 V, ground and a signal. **Board links:** fit R28 (0R 0805) to put the protected 5 V on 1N, and move the 0R from R29 to R30 so that 2L goes to the TPS input instead of AUX1. Until R28 is fitted, 1N is open: with the stock switch fitted, 5 V on 1N would be shorted to ground at every idle. **Sensor:** a Kia sensor with the same 3-pin Mazda plug (0K01118911 and the others in the self-order BOM) plugs into the stock plug, on a printed mount (Thingiverse 3414132, print in ASA); or Flyin' Miata's TPS upgrade kit. **Before fitting R28,** unplug the switch and check on your car which plug wire reaches 1N, 2L and 2D, and on the sensor which pins are the ends of its track (constant resistance between them at any throttle): those must meet 1N and 2D, and the third (the wiper) 2L. In TunerStudio, calibrate the throttle closed and wide open (a reversed sensor calibrates the same way). **Automatics** already have a sensor on 2M (with its 5 V on 2K): leave R28 and R30 off. Every part is in the self-order BOM.

**Throttle switch contact (R27, not fitted):** on the manual cars 2L is one of the throttle switch's contacts, which closes to ground. Fit the 4.7 kΩ pull-up to the protected 5 V only if you keep the stock switch and want the ECU to read it (on AUX1, through R29); never with a sensor on 2L.

**Sensor 5 V:** the harness's 5 V reference and the AUX header pin J5-14 come from the daughterboard's protected 5 V regulator (V5_EXT; it survives a short to the battery or to ground). The MAP sensor has its own supply (V5_SENS), so a damaged sensor wire doesn't take the MAP reading with it.

**Injectors (1989-93):** the stock harness has two injectors on each of 2U and 2V (about 1.8 A per wire). With JP1 and JP2 on PAIR two daughterboard drivers share each wire (INJ1 + INJ4 on 2U, INJ2 + INJ3 on 2V) and rusEFI's batch mode fires each pair together. A rev 0.10 daughterboard clamps each driver itself, so D3/D4 are not fitted; **fit them (SMCJ30A) only to run this board with a rev 0.9 daughterboard on a 1989-93 car.** For a sequential conversion (new wires to 2Y/2Z) move JP1 and JP2 to SEQ and switch the firmware to sequential. **Never put JP2 on SEQ on a 1989-93 automatic: 2Z goes to the A/T control unit.**

**Tachometer (1989-95):** cavity 2I is the igniter's signal into the ECU; the igniter drives the tachometer itself. JP5 is left open and the firmware has no tach output on these years. Only after a coil-on-plug conversion with the igniter removed: fit JP5, set the tach output in TunerStudio, and join the two tach wires at the old igniter plug (R37 is the 12 V pull-up the tachometer then needs).

## Assembly
- The daughterboard plugs into JD1/JD2 (8.5 mm sockets) on four M3 × 11 mm standoffs.
- Fitted by hand (all in `fab/miata-ecu-motherboard-1989-95-rev0.12_self_order_bom.csv`): the harness header (salvage from a stock ECU or use a clone), the daughterboard sockets JD1/JD2, the wideband sensor connector, the add-on header, any jumper headers and their shunts, the MAP sensor, the standoffs, and any not-fitted option links. JLCPCB fits only the SMD parts and USB-C. USB-C has through-hole shell pegs: check in JLC's quote whether that needs Standard PCBA.
- The case needs cut-outs in its bottom edge for the wideband connector, USB-C and the MAP hose, and a way out for the add-on ribbon cable.

## Still to verify
- The case geometry: hole centres and header 1A position, with calipers on a stock case.
- Your car's fan wiring: early cars switch the fan relay on 1R, later ones on 1L; both are driven (fan and spare outputs).
- LCSC stock for the extended parts (C124412, C127367, C277684, C587650, C3020560, C410772, C46641168, C3406).
- Harness pins 1N and 2L on a 1989-93 car: with the throttle switch unplugged, which plug wire reaches each (the rusEFI sources give 1N = idle contact, 2D = ground, 2L = full-throttle contact). Do this before fitting R28.
- The TPS conversion on a manual car: the sensor and mount against your throttle body, and the sensor's output across the throttle travel (calibrate closed and wide open in TunerStudio).
