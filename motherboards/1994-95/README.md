# Miata ECU motherboard 1994-1995 (NA8), rev 0.6

The motherboard replaces the stock Mazda ECU board inside the **stock ECU case**. It carries:

- the stock harness header;
- the year-independent I/O: the LSU 4.9 wideband sensor connector, IAT, USB-C and the MAP sensor;
- the sockets for the universal daughterboard, which does all the engine control (including the wideband controller).

## Changes in this revision
- Rev 0.6: freewheel diode D1 on the idle valve and D2 on the purge solenoid (2X) to its +12 V feed (the PWM turn-off energy no longer goes into the daughterboard driver); F4 resettable fuse on the AUX +12 V pin J5-15; not-fitted 12 V pull-up options R20-R22 for the VSS / A/C / clutch inputs.
- Rev 0.5: IAT source is now a removable jumper (JP1, 1x3 2.54 mm header + shunt) instead of the R4 / R5 0R links: shunt on EXT (default) reads the IAT connector J3, on STOCK the stock harness sensor; labelled on the silkscreen.
- Rev 0.4: MAP sensor is now the MPX5700AP (absolute, case 867B, one barb; LCSC C90152) instead of the MPX5700DP: new footprint with the real lozenge body and offset barb, holes on the NXP 23.11 mm spacing with 3.3 mm M3 clearance drills.
- Rev 0.3: first release, from the 89-93 rev 0.3 template: same case, outline, holes and 48-pin header; 94-95 pin map (rusEFI "Mazda Miata 1994" page and the Hellen NA6/94 connector map).

## Files
| Path | What |
|---|---|
| `miata_mb_9495.kicad_pro / .kicad_sch / .kicad_pcb` | KiCad 7 project. Root schematic plus three sheets: harness, daughterboard, I/O |
| `miata_mb_9495_schematic.pdf` | Schematic PDF |
| `fab/jlcpcb_gerbers.zip`, `fab/jlcpcb_bom.csv`, `fab/jlcpcb_cpl.csv` | JLC fabrication and assembly files (2 layers, 1.6 mm). The JLC BOM is the SMD parts and USB-C only |
| `fab/self_order_bom.csv` | Everything you order and fit yourself: harness header, through-hole connectors, MAP sensor, shunt, standoffs and screws, plus the not-fitted options. Its columns load into LCSC's BOM tool |
| `fab/parts_list.csv` | Every part, including the hand-fitted and not-fitted ones |
| `fab/drc_report.txt` | KiCad DRC |
| `ecu_mb.pretty/`, `fp-lib-table` | Project footprints (harness header, MAP sensor lying flat, USB-C, M4 case hole) |
| `renders/` | Top and bottom copper |
| `../../scripts/` (repo top level) | The design source; `mb_make.sh` rebuilds the whole board |

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
| 1C | `VIGN_IN` | ignition switch sense | VIO: ignition switch (input only) |
| 1E | `OUT_CEL` | check engine lamp |  |
| 1G | `OUT_IGN1` | ignition 1 (5 V logic) | igniter 1&4 (wasted spark) / COP 1 |
| 1H | `OUT_IGN2` | ignition 2 (5 V logic) | igniter 2&3 (wasted spark) / COP 2 |
| 1J | `OUT_AC` | A/C relay | A/C relay |
| 1L | `OUT_FAN` | fan relay | radiator fan relay |
| 1M | `IN_SW1` | 12 V switch input 1 | vehicle speed sensor |
| 1Q | `IN_SW2` | 12 V switch input 2 | A/C pressure switch |
| 1V | `IN_SW3` | 12 V switch input 3 | clutch switch (MT) / AT control unit |
| 2A | `GND` | ground |  |
| 2B | `GND` | ground | power ground |
| 2C | `GND` | ground |  |
| 2D | `GND` | ground | signal ground |
| 2E | `IN_HALL1` | hall input 1 (crank) | CAS crank (SGT, open collector) |
| 2F | `GND` | ground | AFM ground |
| 2G | `IN_HALL2` | hall input 2 (cam) | CAS cam (SGC) |
| 2I | `OUT_TACH` | tach out |  |
| 2K | `V5_SENS` | sensor 5 V reference (out) | 5 V sensor reference |
| 2L | `IN_AUX1` | spare analog 1 | electrical load (rear defroster) -> idle up |
| 2M | `IN_TPS` | TPS | TPS signal (AT / VTPS conversion) |
| 2N | `IN_AUX2` | spare analog 2 | heated O2 sensor (narrowband) |
| 2O | `IN_AUX3` | spare analog 3 | air flow meter signal (vane AFM; rusEFI's 1994 page calls it MAF) |
| 2P | `HARN_IAT` | stock air-temp sensor (JP1 on STOCK) | intake air thermosensor in the AFM (IAT jumper JP1 on STOCK to use it) |
| 2Q | `IN_CLT` | coolant temp |  |
| 2R | `OUT_ALT` | PWM low side (alternator driver) | pressure regulator control solenoid (generic low side) |
| 2S | `OUT_LS7` | spare low side | condenser fan relay |
| 2T | `OUT_FP` | fuel pump relay | fuel pump relay |
| 2U | `OUT_INJ1` | injector 1 | injector No.1 (94-95: one wire per injector, sequential) |
| 2V | `OUT_INJ2` | injector 2 | injector No.2 |
| 2W | `OUT_IACV` | idle air valve |  |
| 2X | `OUT_VVT` | PWM low side (VVT driver) | purge solenoid (VVT driver reused, set as purge / generic PWM) |
| 2Y | `OUT_INJ3` | injector 3 | injector No.3 |
| 2Z | `OUT_INJ4` | injector 4 | injector No.4 |

Not connected: 1A, 1D, 1F, 1I, 1K, 1N, 1O, 1P, 1R, 1S, 1T, 1U, 2H, 2J.

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
- The case geometry, as for 89-93: one stock case with calipers.
- 1C (VIO): ignition-switch sense on the 1990 diagram, unlabelled on the 1994 page; it is only an input here (diode-isolated on the daughterboard).
- LCSC stock for the extended parts (C124412, C127367, C587650, C3020560, C410772, C46641168, C3406).
