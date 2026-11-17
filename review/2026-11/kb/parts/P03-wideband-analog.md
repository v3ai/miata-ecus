# P03 - Wideband analog front end (U101 MCP6004, U105 AD8628, R/C network, F2, D40/D41)

## Summary
1. CRITICAL (VERIFIED): R110 (pump current sense, 62 ohm) is LCSC C25341 = UNI-ROYAL 1206W4F620**L**T5E = **0.62 ohm** (11th code L = 10^-3; datasheet C25341 sec 2.4.3; LCSC/JLC description "620mOhm"). Present in cur_db AND ord_db BOM/CPL (ordered-boards/.../rev0.9_jlcpcb_bom.csv:76). Pump current reading is 100x too small; lambda reads ~1.0 flat. Fix: C17971 (1206W4F620JT5E, 62 ohm 1%, ext, stock 123k, $0.0053) or C23222 (0603, but 0.1 W) -> rework by hand on ordered boards.
2. Netlist vs reference (board_module rev C, via PCB): every net/pad matches apart from the intended changes (U102 F103 pinout owned elsewhere, J1/J3/U9/D4/R18 dropped, F2/R137/D40/D41 added, PA1 left unconnected). U101 and U105 pinouts checked correct against datasheets.
3. VM_RESISTOR_VALUE=11.6 assumes F2 = 1.6 ohm, which is the datasheet MINIMUM (Rimin 1.6, R1max 15 ohm). It does not enter lambda at all; only the ESR/temperature subtraction (~0.45 degC per ohm near 300 ohm).
4. Pump sense is differential across R110 (U105), referenced to the VM op-amp output; F2 / R109 are in the return path outside every feedback loop and outside the Nernst sense (taken at the sensor-side node WB_VMS). F2 cannot hurt loop stability or lambda; it only costs ~1.6-15 ohm x Ip (<=2.25 mA) = <=34 mV of pump compliance.
5. LSU_SENSE_R is 61.9 in firmware (wideband_config.h:27, not overridden by the miata_f1 port): a correct 62 ohm part gives +0.16 % current error (negligible); tolerance 1 % dominates.

## Netlist comparison (work/P03-wideband-analog/netcmp.py, reference = ext board_module PCB, refs +100; VERIFIED)
Run on cur_db; ord_db pads for U101/U105/F2/D40/D41/R137 are identical (pcb_pads.csv).
Deviations: R108/R109/R110 0402/0402/0603 -> 1206 (fault current); R110 value 61.9 -> 62 (and wrong LCSC, see above); C103 33n Y5V -> X7R C106862 (improvement: Y5V loses up to 80 % C with bias/temperature); U105 TSOT-23-5 -> SOT-23-5 (same pads); R137 22k added (LSU_UN -> WB_UN_IN; U101.10 no longer straight on LSU_UN); F2 nSMD010 between LSU_VM and WB_VMS (R109.1, R103.1, C104.1 moved behind it); D40 (+3V3 cathode pad1 / WB_PUMP) and D41 (+3V3 / WB_VM) Schottky clamps (anode on op-amp output; orientation correct); PA1 sense of VM removed (firmware ADC uses PA0, PA2, PA3, PB0 only: miata_f1/port.cpp:40-49 - harmless). All other values identical (R101..R134, C101..C117). Source comment says R137 10k in rev 0.7, now 22k (wideband.py R137 / PCB both 22k).
R137 effect: MCP6004 Ib ~pA, 22k x 1 nA(85C worst) = 22 uV; negligible. Pole with ~6 pF + trace: >1 MHz.

## Pin audit (VERIFIED, pcb_pads.csv cur_db = ord_db)
U101 MCP6004 TSSOP-14 (datasheet DS20001733L pin table: 1 OUTA,2 INA-,3 INA+,4 VDD,5 INB+,6 INB-,7 OUTB,8 OUTC,9 INC-,10 INC+,11 VSS,12 IND+,13 IND-,14 OUTD):
1 WB_PUMP (A out), 2 WB_PUMP_N, 3 WB_PUMP_P, 4 +3V3, 5 WB_UN_P, 6 WB_UN_N, 7 WB_UN_SENSE, 8 WB_UN_BUF (C out) tied to 9 (C-) feedback, 10 WB_UN_IN (C+ via R137), 11 GND, 12 WB_VM_REF (D+), 13/14 WB_VM (D- tied to out = follower). All OK. Footprint pitch 0.65, pad centres 5.725 mm = KiCad TSSOP-14 4.4 mm.
U105 AD8628ARTZ SOT-23-5 (ADI pin config: 1 OUT, 2 V-, 3 +IN, 4 -IN, 5 V+): 1 WB_IS_OUT, 2 GND, 3 WB_IS_P, 4 WB_IS_N, 5 +3V3. OK, differs from generic (+IN is pin 3, -IN pin 4); pad geometry 0.95 pitch, 2.275 span standard.
Stress: 3.3 V rail vs abs max 7.0 V (MCP) / 6 V (AD8628) fine; inputs limited to VSS-1 .. VDD+1 and 2 mA (MCP sec 4.1.2): LSU wire faults go through R111/R112 10k, R137 22k, R103 10k, so battery short = ~1 mA each (OK at 14.4 V; documented area). MCP6004 stable with 500 pF load (PM 90 deg typical, datasheet p.1), D40/D41 Schottky capacitance (~100-200 pF, UNVERIFIED) is within that.

## F2 / VM analysis
- nSMD010 (C70065 datasheet): Ihold 0.10 A, Itrip 0.25 A, Rimin 1.6, R1max 15 ohm, 60 V; LCSC op range -40..85 C (hold current derates at 85 C; normal VM current <= 2.25 mA, no trip risk).
- Circuit: U101D follower output WB_VM (feedback taken at output, before R109/F2). Pump amp U105 output = Vvm + 10 (Vip - Vrt) (R112/R115 = R111/R117 = 10k/100k), so firmware pumpCurrentSenseVoltage = Vout - Vvm_adc gives 10 x Ip x R110 irrespective of R109/F2. sampling.cpp:44 ratio = -1000/(10 x LSU_SENSE_R); ConvertLambda(Ip). Nernst: U101B gain 2.7 on UN_BUF - WB_VMS (sensor side), pump PID closes on that (pump_control.cpp:70, NERNST_TARGET 0.45). So F2 drop is excluded; lambda error from F2 = 0 (INFERRED from netlist+firmware, high confidence).
- ESR: sampling.cpp:91 totalEsr - VM_RESISTOR_VALUE. Because the Nernst tap is at the sensor side of R109/F2, the subtraction is itself a small bias (reference: -10 ohm; here -11.6). LSU4.9 table slope near 300 ohm: 806 degC@250 -> 761@350 = 0.45 degC/ohm, so bias ~5 degC, and if F2 really were in the measured path (R up to 15 ohm) another <=7 degC. Low.
- Bosch LSU 4.9 datasheet (datasheets/extra/LSU49_bosch.txt p.2): Nernst cell 300 ohm nominal, max Nernst load 250 uA, Ip table -2.000 mA (lambda 0.65) to +2.250 mA (lambda 10.1), pins 1 IP, 2 VM, 3 H-, 4 H+, 5 RT, 6 UN, heater 7.5 V nominal / 10.8-16.5 V system, heater control >= 100 Hz. Pump sense full scale: 2.25 mA x 62 x 10 = 1.4 V span OK; with R110 = 0.62 ohm only 14 mV.
- Fault: VM wire to 14.4 V -> ~0.9 A through R109+F2 until F2 trips (R109 1206 0.25 W takes ~8 W momentarily); sacrificial R108-R110 already documented; not re-reported.

## Parts / cost (lcsc.py today)
C50282 MCP6004T-I/ST ext stock 1747, $0.391@30 / $0.339@100 (low stock for a volume build). C29309 AD8628ARTZ ext stock 22.9k, $2.27@30 / $2.03@100 (biggest cost item here; reference part; alternative not evaluated). C70065 nSMD010 ext stock 941k, $0.024@200. C106862 ext 412k. C25341 WRONG VALUE. C17903 basic. C8598 B5819W basic, $0.0195@200. C23222 62 ohm 0603 ext 177k (fallback only).
AD8628 offset 1 uV vs MCP6004 4.5 mV: pump sense needs the precision part (10 x 62 ohm x 1 mA = 0.62 V, MCP offset would be 0.7 % of 1 mA - tolerable, but not evaluated as replacement).
Resistor ratio note: 1 % R112/R115/R111/R117 gives worst-case common-mode error ~0.018 V/V x (Vip-Vvm) (INFERRED); at pump-cell voltages ~0.2 V this is ~0.2 % of 2.5 mA; same as reference.

## Sources actually read
the review brief; repo/scripts/wideband.py; ext/wideband-mck1117/firmware/{sampling.cpp,pump_control.cpp,pump_dac.cpp,wideband_config.h,boards/f0_module/*}; repo/firmware/wideband/miata_f1/{wideband_board_config.h,port.cpp}; evidence/{cur_db,ord_db}/pcb_pads.csv, pcb_footprints.csv, fab BOM; datasheets C50282, C29309 (pin config, abs max), C70065, C25341 (part-number system), extra/LSU49_bosch.txt; tools/lcsc.py live lookups.

## Not checked
Schematic-image comparison (netlist from PCB only, sch_netlist.xml not diffed); AD8628 abs-max/input current under 14 V faults in detail; layout images (decoupling, loop area); B5819W leakage/capacitance at 85 C; cheaper sense-amp alternates; exact PTC trip time vs R109 pulse rating; Bosch IC-level Nernst/ESR frequency details.
