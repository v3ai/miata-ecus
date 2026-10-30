# Miata ECU motherboard 2001-2005 (NB2, VVT), rev 0.3

The motherboard replaces the stock Mazda ECU board inside the **stock ECU case**. It carries:

- the stock harness header;
- the year-independent I/O: the LSU 4.9 wideband sensor connector, IAT, USB-C and the MAP sensor;
- the sockets for the universal daughterboard, which does all the engine control (including the wideband controller).

## Changes in this revision
- Rev 0.3: IAT source is now a removable jumper (JP1, 1x3 2.54 mm header + shunt) instead of the R4 / R5 0R links: shunt on EXT (default) reads the IAT connector J3, on STOCK the stock harness sensor; labelled on the silkscreen.
- Rev 0.2: MAP sensor is now the MPX5700AP (absolute, case 867B, one barb; LCSC C90152) instead of the MPX5700DP: new footprint with the real lozenge body and offset barb, holes on the NXP 23.11 mm spacing with 3.3 mm M3 clearance drills.
- Rev 0.1: first release (design complete, case geometry provisional).

## Files
| Path | What |
|---|---|
| `miata_mb_0105.kicad_pro / .kicad_sch / .kicad_pcb` | KiCad 7 project. Root schematic plus three sheets: harness, daughterboard, I/O |
| `miata_mb_0105_schematic.pdf` | Schematic PDF |
| `fab/jlcpcb_gerbers.zip`, `fab/jlcpcb_bom.csv`, `fab/jlcpcb_cpl.csv` | JLC fabrication and assembly files (2 layers, 1.6 mm) |
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
| H1 | 17.0, 7.3 |
| H2 | 137.0, 7.3 |
| H3 | 4.0, 84.0 |
| H4 | 150.0, 84.0 |
| H5 | 4.0, 143.0 |
| H6 | 150.0, 143.0 |

All holes are 4.5 mm plated with a 7 mm pad, tied to GND, for M4 screws. Harness header terminal 1A sits at (40.95, 16.60) mm (lower pin row).

## Harness header
TE **353830-5** (alt. 1123038-2), 72 positions in three rows: OEM plug 2 = 2A-2R without 2L (17), plug 3 = 3A-3Z without 3G/3R (24), plug 4 = 4A-4AH without 4G/4Q/4Y (31). There is no plug 1. Fitted by hand.

| Pin | Net | Use | Stock function / note |
|---|---|---|---|
| 2A | `OUT_INJ1` | injector 1 | injector No.1 |
| 2B | `OUT_FAN` | fan relay | cooling fan relay |
| 2C | `OUT_LS7` | spare low side | condenser fan relay |
| 2D | `OUT_INJ2` | injector 2 | injector No.2 |
| 2G | `OUT_INJ3` | injector 3 | injector No.3 |
| 2J | `OUT_INJ4` | injector 4 | injector No.4 |
| 2K | `OUT_AC` | A/C relay | A/C relay |
| 2M | `OUT_FP` | fuel pump relay | fuel pump relay |
| 2P | `IAC_12V` |  | idle valve +12 V supply (fused, F2) |
| 2Q | `OUT_IACV` | idle air valve | idle valve (low side) |
| 2R | `OUT_CEL` | check engine lamp | MIL |
| 3A | `GND` | ground | injector (power) ground |
| 3B | `GND` | ground | PCM ground |
| 3F | `OUT_IGN1` | ignition 1 (5 V logic) | igniter cylinders 1 & 4 |
| 3H | `OUT_MAINRLY` | main relay control | main relay control (2003-05; unused on 2001-02) |
| 3I | `OUT_IGN2` | ignition 2 (5 V logic) | igniter cylinders 2 & 3 |
| 3M | `OUT_ALT` | PWM low side (alternator driver) | generator field coil control |
| 3O | `OUT_TACH` | tach out | tachometer (shared with the A/T TCM) |
| 3T | `IN_SW1` | 12 V switch input 1 | vehicle speed |
| 3V | `IN_HALL2` | hall input 2 (cam) | cam position sensor (hall) |
| 3Y | `IN_HALL1` | hall input 1 (crank) | crank position sensor (hall) |
| 4A | `GND` | ground | device ground (CKP return) |
| 4AA | `IN_AUX1` | spare analog 1 |  |
| 4AF | `VBAT_IN` | ECU power (main relay) |  |
| 4D | `OCV_12V` |  | VVT oil control valve +12 V supply (fused, F3) |
| 4F | `IN_SW2` | 12 V switch input 2 | A/C refrigerant pressure switch |
| 4I | `IN_SW3` | 12 V switch input 3 | clutch switch |
| 4L | `V5_SENS` | sensor 5 V reference (out) | +5 V reference |
| 4M | `IN_KNOCK` |  | knock sensor |
| 4N | `HARN_IAT` | stock air-temp sensor (JP1 on STOCK) | intake air temperature (IAT jumper JP1 on STOCK to use it) |
| 4O | `GND` | ground | analogue sensor ground |
| 4P | `IN_CLT` | coolant temp | coolant temperature |
| 4R | `OUT_VVT` | PWM low side (VVT driver) | VVT oil control valve (low side, PWM) |
| 4S | `VIGN_IN` | ignition switch sense | IG1 ignition switch sense (2003-05) |
| 4V | `IN_TPS` | TPS | throttle position sensor |
| 4W | `IN_AUX2` | spare analog 2 | front HO2S |
| 4X | `IN_AUX3` | spare analog 3 | MAF signal |

Not connected: 2E, 2F, 2H, 2I, 2N, 2O, 3C, 3D, 3E, 3J, 3K, 3L, 3N, 3P, 3Q, 3S, 3U, 3W, 3X, 3Z, 4AB, 4AC, 4AD, 4AE, 4AG, 4AH, 4B, 4C, 4E, 4H, 4J, 4K, 4T, 4U, 4Z.

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

## Assembly
- The daughterboard plugs into JD1/JD2 (8.5 mm sockets) on four M3 × 11 mm standoffs.
- Fitted by hand: the harness header (salvage from a stock ECU or use a clone), the IAT jumper shunt on JP1 (LCSC C5305; EXT or STOCK), and any not-fitted option links.
- The case needs cut-outs in its bottom edge for the LSU, IAT, USB-C and MAP hose.

## Still to verify
- **The case outline, mounting holes and header position (provisional here).**
- Mazdaspeed (turbo) cars: 4R is the second IAT sensor input there, not the VVT valve: do not fit this board unmodified.
- 2P (idle valve +) and 4D (VVT valve +) are fed +12 V through F2 / F3 (2 A resettable each).
- 3H drives the main relay on 2003-05 (unused on 2001-02); 4S reads the ignition switch on 2003-05.
- Left open: 3Q (K-line), 3S (immobilizer), 4E (DLC TEN), 4Z/4AC (A/T), 4AD (fuel gauge), 4AG (battery backup), 4T (generator voltage), the EGR stepper (2E/2F/2H/2I), purge (3C), 3D, 3E, 3K, VTCS (2N, 4J), O2 heaters (3J, 3P), generator lamp (3U), brake / power-steering / neutral switches, EGR boost sensor (4AE), 4AB, 4AH.
