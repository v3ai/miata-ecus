# Miata ECU motherboard 1999-2000 (NB1), rev 0.9

The motherboard replaces the stock Mazda ECU board inside the **stock ECU case**. It carries:

- the stock harness header;
- the year-independent I/O: the wideband sensor connector (AEM X-Series harness), USB-C, the MAP sensor and the add-on header (flex fuel, nitrous, CAN, boost);
- the sockets for the universal daughterboard, which does all the engine control (including the wideband controller).

## Changes in this revision
- Rev 0.9: the wideband sensor connector J2 is now a JST PUD side-entry header (S08B-PUDSS-1, two rows of four at 2.0 mm) instead of rev 0.8's Molex Micro-Fit 2x4. AEM's instructions for the X-Series gauge name the harness's replacement terminal, JST SPUD-001T-P0.5, which is the contact of JST's PUD series (plug housing PUDP-08V-S): a Micro-Fit header would not have taken the plug. The wire colour of each pin is printed beside the connector, to check a harness against by eye. The board is routed again; nothing else changed.
- Rev 0.8, for daughterboard rev 0.10 (a rev 0.9 daughterboard fits too, without the new functions). The wideband sensor connector J2 is a Molex Micro-Fit 2x4 for the off-the-shelf AEM X-Series sensor harness (30-3427) instead of the 2x3 for a hand-made lead; that plug family was a guess, and wrong: corrected in rev 0.9. The separate air-temperature connector J3 and its jumper are gone: the stock sensor's harness wire goes straight to the air-temperature input. The add-on header J5 is a 2x10 box header for a ribbon cable and gains the flex-fuel input (4.7k pull-up to 5 V, R35), the nitrous arming input (10k pull-down, R36) and the CAN bus; a boost valve on it has its own freewheel diode (D5), and its +12 V fuse F4 holds 1.1 A instead of 0.5 A. The harness header is now TE 178780-1 (76 positions, in stock at distributors) with this car's four plugs on it, instead of TE 176122-6.
- Rev 0.7, for daughterboard rev 0.9: the daughterboard sits 16 mm lower, centred on the board (42 mm from the top, as up to rev 0.7), with its J1 on its top edge again: JD1 and the upper standoffs HD1/HD2 are back at their rev 0.7 places, JD2, the lower standoffs HD3/HD4, the AUX header J5 (with F4 beside it) and the parts placed against JD2 (CAN termination R1/R6, pull-up options) are 16 mm lower, and the board is routed again. Not compatible with a rev 0.8 daughterboard.
- Rev 0.6, for daughterboard rev 0.8: the harness's sensor 5 V (2I) and the AUX header pin J5-14 now come from the daughterboard's protected 5 V (V5_EXT, JD1 pin 13, which was a ground pin): a sensor 5 V wire shorted to the battery no longer back-feeds the MAP sensor and the ECU's own 5 V. The MAP sensor keeps its own supply (V5_SENS). The daughterboard outline on the silkscreen is 16 mm taller (125 x 76 mm): its new strip of output drivers overhangs the free area above JD1.
- Rev 0.5: LSU heater fuse F1 is a 3 A hold PTC (LUTE 2920L300/30GR, 30 V, 2920 size) instead of the 2 A 1812 part. A cold LSU 4.9 heater draws 1.6-2.3 A rms at the start of the wideband's warm-up, more than the old fuse holds once warm, so it could trip and the controller time out. No 1812 PTC holds 3 A above 8 V.
- Rev 0.4: freewheel diode D1 on the idle valve to its +12 V feed (the PWM turn-off energy no longer goes into the daughterboard driver); F4 resettable fuse on the AUX +12 V pin J5-15; not-fitted 12 V pull-up options R20-R22 for the VSS / A/C / clutch inputs.
- Rev 0.3: IAT source is now a removable jumper (JP1, 1x3 2.54 mm header + shunt) instead of the R4 / R5 0R links: shunt on EXT (default) reads the IAT connector J3, on STOCK the stock harness sensor; labelled on the silkscreen.
- Rev 0.2: MAP sensor is now the MPX5700AP (absolute, case 867B, one barb; LCSC C90152) instead of the MPX5700DP: new footprint with the real lozenge body and offset barb, holes on the NXP 23.11 mm spacing with 3.3 mm M3 clearance drills.
- Rev 0.1: first release (design complete, case geometry provisional).

## Files
| Path | What |
|---|---|
| `miata_mb_9900.kicad_pro / .kicad_sch / .kicad_pcb` | KiCad 7 project. Root schematic plus three sheets: harness, daughterboard, I/O |
| `miata_mb_9900_schematic.pdf` | Schematic PDF |
| `fab/miata-ecu-motherboard-1999-2000-rev0.9_jlcpcb_gerbers.zip`, `fab/miata-ecu-motherboard-1999-2000-rev0.9_jlcpcb_bom.csv`, `fab/miata-ecu-motherboard-1999-2000-rev0.9_jlcpcb_cpl.csv` | JLC fabrication and assembly files (2 layers, 1.6 mm). The JLC BOM is the SMD parts and USB-C only |
| `fab/miata-ecu-motherboard-1999-2000-rev0.9_self_order_bom.csv` | Everything you order and fit yourself: harness header, through-hole connectors, MAP sensor, shunt, standoffs and screws, plus the not-fitted options. Its columns load into LCSC's BOM tool |
| `fab/miata-ecu-motherboard-1999-2000-rev0.9_parts_list.csv` | Every part, including the hand-fitted and not-fitted ones |
| `fab/drc_report.txt` | KiCad DRC |
| `ecu_mb.pretty/`, `fp-lib-table` | Project footprints (harness header, MAP sensor lying flat, USB-C, M4 case hole) |
| `renders/` | Top and bottom copper |
| `scripts/` | The design source; `mb_make.sh` rebuilds the whole board |

## Case fit
**PROVISIONAL.** No source gives this case's board outline and mounting holes yet (the open-source boards for these years either use their own enclosure or a different Mazda case). Until a stock board or case is measured, this board uses the NA case outline and holes as a stand-in, with the header centred on the top edge. Moving to the real outline is a change of OUTLINE / CASE_HOLES / HDR_1A in the year module plus an automatic reroute. **Do not order this board before the case is measured.**

Board: **154.0 × 161.5 mm**, 1.6 mm. The origin is the top-left corner and y points down, toward the bottom edge.

| Hole | x, y (mm) |
|---|---|
| H3 | 4.0, 84.0 |
| H4 | 150.0, 84.0 |
| H5 | 4.0, 143.0 |
| H6 | 150.0, 143.0 |

All holes are 4.5 mm plated with a 7 mm pad, tied to GND, for M4 screws. Harness header terminal 1A sits at (16.00, 18.13) mm (lower pin row).

## Harness header
TE **178780-1**, 76 positions, the same header as the 1996-97 board (rev 0.8; the car's own header is the 64-position 176122-6, whose three plugs are the same housings): plug 1 = 1A-1V (22), plug 2 = 2A-2P (16), plug 3 = 3A-3Z (26). The 12-position bay between plugs 1 and 2 has no harness plug and is not connected. Fitted by hand.

| Pin | Net | Use | Stock function / note |
|---|---|---|---|
| 1B | `VBAT_IN` | ECU power (main relay) | ECU +12 V from the main relay |
| 1E | `OUT_CEL` | check engine lamp | MIL |
| 1I | `OUT_LS7` | spare low side | A/C (condenser) fan relay |
| 1O | `OUT_ALT` | PWM low side (alternator driver) | alternator field coil control (PWM) |
| 1P | `IN_SW2` | 12 V switch input 2 | A/C switch |
| 1R | `OUT_FAN` | fan relay | radiator cooling fan relay |
| 1S | `OUT_AC` | A/C relay | A/C compressor relay |
| 1U | `OUT_VVT` | PWM low side (VVT driver) | front HO2S heater (PWM low side; no VVT on NB1) |
| 2B | `IN_IAT` | air temperature (stock sensor) | intake air temperature sensor (in the air filter box) |
| 2C | `IN_AUX2` | spare analog 2 | front HO2S |
| 2D | `IN_SW1` | 12 V switch input 1 | vehicle speed sensor |
| 2E | `IN_CLT` | coolant temp | coolant temperature |
| 2F | `IN_KNOCK` |  | knock sensor |
| 2H | `IN_HALL2` | hall input 2 (cam) | cam position sensor (hall, 3-wire) |
| 2I | `V5_EXT` | sensor 5 V reference (out; protected, short-to-battery proof) | +5 V sensor reference |
| 2J | `IN_HALL1` | hall input 1 (crank) | crank position sensor (hall, 3-wire) |
| 2K | `OUT_TACH` | tach out | tachometer |
| 2L | `IN_AUX3` | spare analog 3 | MAF signal |
| 3A | `GND` | ground |  |
| 3B | `GND` | ground |  |
| 3C | `GND` | ground | power grounds |
| 3E | `IN_TPS` | TPS | throttle position sensor |
| 3F | `GND` | ground | sensor ground |
| 3G | `OUT_IGN1` | ignition 1 (5 V logic) | igniter cylinders 1 & 4 |
| 3H | `OUT_IGN2` | ignition 2 (5 V logic) | igniter cylinders 2 & 3 |
| 3I | `IN_SW3` | 12 V switch input 3 | clutch switch |
| 3J | `IN_AUX1` | spare analog 1 | rear HO2S |
| 3M | `OUT_IACV` | idle air valve | idle air control valve (low side) |
| 3N | `OUT_FP` | fuel pump relay | fuel pump relay |
| 3O | `IAC_12V` |  | idle valve +12 V supply (fused, F2) |
| 3Q | `OUT_MAINRLY` | main relay control | VICS solenoid (spare relay-driver channel) |
| 3W | `OUT_INJ1` | injector 1 |  |
| 3X | `OUT_INJ2` | injector 2 |  |
| 3Y | `OUT_INJ3` | injector 3 |  |
| 3Z | `OUT_INJ4` | injector 4 |  |

Not connected: 1A, 1C, 1D, 1F, 1G, 1H, 1J, 1K, 1L, 1M, 1N, 1Q, 1T, 1V, 2A, 2G, 2M, 2N, 2O, 2P, 3D, 3K, 3L, 3P, 3R, 3S, 3T, 3U, 3V.

## Bottom edge, left to right
| Ref | What | Notes |
|---|---|---|
| J2 | Wideband sensor (JST PUD side-entry header S08B-PUDSS-1, 2×4, 2.0 mm) | For the **AEM X-Series sensor harness 30-3427** and a Bosch LSU 4.9. Pin 1 trim (LSU RT, green wire), 2 heater − (white), 3 common (VM, orange), 5 pump current (IP, red), 6 sense (UN, black), 8 heater + (brown); 4 and 7 empty. Pins 1/2 are the first column, odd pins in the row away from the board edge; the colours are printed beside the connector. The pin functions and the terminal (JST SPUD-001T-P0.5, the PUD series' contact) are from AEM's instructions for the gauge; **nobody has plugged a harness into this board yet: compare the wire colours with the print before the first use.** Heater fed from the main relay through F1 (3 A hold, 30 V, 2920). The controller is on the daughterboard |
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

**Protection:** D1 (and D2 where the VVT driver runs a coil) freewheel the PWM valve coils into their own +12 V feed, and D5 does the same for a boost valve on the add-on header, so the drivers don't absorb the turn-off energy. F4 fuses the add-on header's +12 V pin (1.1 A hold: a boost valve draws about 0.5 A).

**Switch inputs (R20-R22, not fitted):** the VSS, A/C and clutch inputs read signals that are driven to 12 V. If your car's signal only switches to ground (or is open collector), fit the 4.7 kΩ pull-up for that input. Never fit it for a switch that drives 12 V: the input would always read on.

**Sensor 5 V:** the harness's 5 V reference and the AUX header pin J5-14 come from the daughterboard's protected 5 V regulator (V5_EXT; it survives a short to the battery or to ground). The MAP sensor has its own supply (V5_SENS), so a damaged sensor wire doesn't take the MAP reading with it.

## Assembly
- The daughterboard plugs into JD1/JD2 (8.5 mm sockets) on four M3 × 11 mm standoffs.
- Fitted by hand (all in `fab/miata-ecu-motherboard-1999-2000-rev0.9_self_order_bom.csv`): the harness header (salvage from a stock ECU or use a clone), the daughterboard sockets JD1/JD2, the wideband sensor connector, the add-on header, any jumper headers and their shunts, the MAP sensor, the standoffs, and any not-fitted option links. JLCPCB fits only the SMD parts and USB-C. USB-C has through-hole shell pegs: check in JLC's quote whether that needs Standard PCBA.
- The case needs cut-outs in its bottom edge for the wideband connector, USB-C and the MAP hose, and a way out for the add-on ribbon cable.

## Still to verify
- **The case outline, mounting holes and header position (provisional here).**
- 2K: tach output per three sources, "unused" per one; check on the harness.
- 3O feeds +12 V to the idle valve through F2 (2 A resettable).
- 3Q (VICS solenoid) is driven by the spare relay-driver channel (OUT_MAINRLY net, a ZXMS6004FF since daughterboard rev 0.8): the main relay itself is key-switched on NB1.
- 1U (front O2 heater) uses the PWM low side normally used for VVT (NB1 has no VVT).
- Left open: 1A (battery backup), 1D/1L (diagnostic link), 1K/1N (A/T), 1T (alternator sense), 1H, 3K, 3P (EU fuel pump), the EGR stepper (2M-2P), purge (3L), CDCV (3U), rear O2 heater (3V), brake / power-steering / neutral switches.
