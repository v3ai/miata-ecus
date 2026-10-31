# Miata ECU motherboard 1999-2000 (NB1), rev 0.4

The motherboard replaces the stock Mazda ECU board inside the **stock ECU case**. It carries:

- the stock harness header;
- the year-independent I/O: the LSU 4.9 wideband sensor connector, IAT, USB-C and the MAP sensor;
- the sockets for the universal daughterboard, which does all the engine control (including the wideband controller).

## Changes in this revision
- Rev 0.4: freewheel diode D1 on the idle valve to its +12 V feed (the PWM turn-off energy no longer goes into the daughterboard driver); F4 resettable fuse on the AUX +12 V pin J5-15; not-fitted 12 V pull-up options R20-R22 for the VSS / A/C / clutch inputs.
- Rev 0.3: IAT source is now a removable jumper (JP1, 1x3 2.54 mm header + shunt) instead of the R4 / R5 0R links: shunt on EXT (default) reads the IAT connector J3, on STOCK the stock harness sensor; labelled on the silkscreen.
- Rev 0.2: MAP sensor is now the MPX5700AP (absolute, case 867B, one barb; LCSC C90152) instead of the MPX5700DP: new footprint with the real lozenge body and offset barb, holes on the NXP 23.11 mm spacing with 3.3 mm M3 clearance drills.
- Rev 0.1: first release (design complete, case geometry provisional).

## Files
| Path | What |
|---|---|
| `miata_mb_9900.kicad_pro / .kicad_sch / .kicad_pcb` | KiCad 7 project. Root schematic plus three sheets: harness, daughterboard, I/O |
| `miata_mb_9900_schematic.pdf` | Schematic PDF |
| `fab/jlcpcb_gerbers.zip`, `fab/jlcpcb_bom.csv`, `fab/jlcpcb_cpl.csv` | JLC fabrication and assembly files (2 layers, 1.6 mm). The JLC BOM is the SMD parts and USB-C only |
| `fab/self_order_bom.csv` | Everything you order and fit yourself: harness header, through-hole connectors, MAP sensor, shunt, standoffs and screws, plus the not-fitted options. Its columns load into LCSC's BOM tool |
| `fab/parts_list.csv` | Every part, including the hand-fitted and not-fitted ones |
| `fab/drc_report.txt` | KiCad DRC |
| `ecu_mb.pretty/`, `fp-lib-table` | Project footprints (harness header, MAP sensor lying flat, USB-C, M4 case hole) |
| `renders/` | Top and bottom copper |
| `../../scripts/` (repo top level) | The design source; `mb_make.sh` rebuilds the whole board |

## Case fit
**PROVISIONAL.** No source gives this case's board outline and mounting holes yet (the open-source boards for these years either use their own enclosure or a different Mazda case). Until a stock board or case is measured, this board uses the NA case outline and holes as a stand-in, with the header centred on the top edge. Moving to the real outline is a change of OUTLINE / CASE_HOLES / HDR_1A in the year module plus an automatic reroute. **Do not order this board before the case is measured.**

Board: **154.0 × 161.5 mm**, 1.6 mm. The origin is the top-left corner and y points down, toward the bottom edge.

| Hole | x, y (mm) |
|---|---|
| H3 | 4.0, 84.0 |
| H4 | 150.0, 84.0 |
| H5 | 4.0, 143.0 |
| H6 | 150.0, 143.0 |

All holes are 4.5 mm plated with a 7 mm pad, tied to GND, for M4 screws. Harness header terminal 1A sits at (26.35, 18.13) mm (lower pin row).

## Harness header
TE **176122-6** (4-174518-7), 64 positions: plug 1 = 1A-1V (22), plug 2 = 2A-2P (16), plug 3 = 3A-3Z (26). Fitted by hand.

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
| 2B | `HARN_IAT` | stock air-temp sensor (JP1 on STOCK) | intake air temperature (IAT jumper JP1 on STOCK to use it) |
| 2C | `IN_AUX2` | spare analog 2 | front HO2S |
| 2D | `IN_SW1` | 12 V switch input 1 | vehicle speed sensor |
| 2E | `IN_CLT` | coolant temp | coolant temperature |
| 2F | `IN_KNOCK` |  | knock sensor |
| 2H | `IN_HALL2` | hall input 2 (cam) | cam position sensor (hall, 3-wire) |
| 2I | `V5_SENS` | sensor 5 V reference (out) | +5 V sensor reference |
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
| 3Q | `OUT_MAINRLY` | main relay control | VICS solenoid (spare ULN2003 channel) |
| 3W | `OUT_INJ1` | injector 1 |  |
| 3X | `OUT_INJ2` | injector 2 |  |
| 3Y | `OUT_INJ3` | injector 3 |  |
| 3Z | `OUT_INJ4` | injector 4 |  |

Not connected: 1A, 1C, 1D, 1F, 1G, 1H, 1J, 1K, 1L, 1M, 1N, 1Q, 1T, 1V, 2A, 2G, 2M, 2N, 2O, 2P, 3D, 3K, 3L, 3P, 3R, 3S, 3T, 3U, 3V.

## Bottom edge, left to right
| Ref | What | Notes |
|---|---|---|
| J2 | LSU 4.9 (Molex Micro-Fit 2×3, right angle) | Pin n = LSU pin n: 1 IP, 2 VM, 3 H−, 4 H+, 5 RT, 6 UN. Heater fed from the main relay through F1 (2 A hold, 30 V). The controller is on the daughterboard |
| J3 | IAT (Micro-Fit 1×2) | M12×1.5 open-element thermistor, used when the IAT jumper JP1 is on EXT |
| JP1 | IAT source jumper (1×3, 2.54 mm) | Shunt on **2-3 (EXT, default)**: the IAT connector J3. Shunt on **1-2 (STOCK)**: the stock air-temp sensor through the harness (inside the AFM on 1989-97, the MAF on 1999-2005). Set the matching sensor curve in TunerStudio; the pull-up is 2.7 kΩ |
| J4 | USB-C | USB 2.0 device: tuning, logging, DFU |
| U2 | MPX5700AP | Absolute MAP sensor (15-700 kPa, case 867B). Lies flat on 2 × M3, marking side up, leads bent 90° down, the single barb toward the board centre |

**CAN:** R1 + R6 terminate the bus at the ECU end; remove R6 if the bus is terminated elsewhere.

**AUX (J5, 2×8 box header):** what the stock harness has no pins for: COP 3/4, boost, alternator and main-relay outputs, knock input, VR crank/cam inputs, external AFR input, UART, 5 V sensor supply, +12 V and GND.

**Protection (motherboard rev 0.4 / 0.6):** D1 (and D2 where the VVT driver runs a coil) freewheel the PWM valve coils into their own +12 V feed, so the drivers don't absorb the turn-off energy. F4 fuses the AUX +12 V pin (0.5 A hold).

**Switch inputs (R20-R22, not fitted):** the VSS, A/C and clutch inputs read signals that are driven to 12 V. If your car's signal only switches to ground (or is open collector), fit the 4.7 kΩ pull-up for that input. Never fit it for a switch that drives 12 V: the input would always read on.

## Assembly
- The daughterboard plugs into JD1/JD2 (8.5 mm sockets) on four M3 × 11 mm standoffs.
- Fitted by hand (all in `fab/self_order_bom.csv`): the harness header (salvage from a stock ECU or use a clone), the daughterboard sockets JD1/JD2, the LSU and IAT connectors, the AUX header, the JP1 header and its shunt (EXT or STOCK), the MAP sensor, the standoffs, and any not-fitted option links. JLCPCB fits only the SMD parts and USB-C. USB-C has through-hole shell pegs: check in JLC's quote whether that needs Standard PCBA.
- The case needs cut-outs in its bottom edge for the LSU, IAT, USB-C and MAP hose.

## Still to verify
- **The case outline, mounting holes and header position (provisional here).**
- 2K: tach output per three sources, "unused" per one; check on the harness.
- 3O feeds +12 V to the idle valve through F2 (2 A resettable).
- 3Q (VICS solenoid) is driven by the spare ULN2003 channel (OUT_MAINRLY net, 0.5 A): the main relay itself is key-switched on NB1.
- 1U (front O2 heater) uses the PWM low side normally used for VVT (NB1 has no VVT).
- Left open: 1A (battery backup), 1D/1L (diagnostic link), 1K/1N (A/T), 1T (alternator sense), 1H, 3K, 3P (EU fuel pump), the EGR stepper (2M-2P), purge (3L), CDCV (3U), rear O2 heater (3V), brake / power-steering / neutral switches.
