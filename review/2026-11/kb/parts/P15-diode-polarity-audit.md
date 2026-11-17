# P15 - Diode / TVS / LED polarity and rating audit (all eleven boards)

STATUS: complete (2026-11-16). Scripts and tables in work/P15-diode-polarity-audit/ (list_d.py, sch_pins.py, cpl_cmp.py, fp_geom.json).

## Summary
1. All 51 diode-class parts on cur_db (43 on ord_db) and every motherboard diode (D1-D5) were checked pad by pad against pcb_pads/pcb_nets, sch_netlist.xml pin names (K/A/COM) and design.py / wideband.py. No polarity error found on any of the 11 boards. VERIFIED.
2. Pad convention (stock KiCad footprints, geometry read from the .kicad_pcb, work/.../fp_geom.json): D_SMA, D_SMC, D_SOD-123, D_SOD-323, LED_0603: pad 1 = cathode (left at rot 0, silk bar on that side), pad 2 = anode. Schematic symbols Device:D / D_Schottky / D_Zener / LED have pin 1 = K, 2 = A. SOT-23: pad 1 top-left, 2 bottom-left, 3 right-middle.
3. SOT-23 duals: BAT54S (onsemi C19726 sheet: pin 1 anode, 2 cathode, 3 cathode/anode common). Pads: 1=GND, 2=+5V or +3V3, 3=signal: lower diode GND->signal, upper diode signal->rail = correct clamp (D15-18, D36, D37). BAT54A (JSMSEMI C916423; datasheet picture: pins 1 and 2 cathodes, 3 common anode). D35: 1=V5_H1, 2=V5_H2, 3=V5_EXT = correct OR-ing from V5_EXT to the harness hall supplies.
4. Injector clamp (cur_db D42-49): drain -> ES1D (anode OUT_INJn, cathode INJn_CL) -> 1.5SMC16A (cathode INJn_CL, anode VBAT_IN). In normal operation the TVS is forward biased (INJ_CL ~ VBAT_IN - 0.7), reverse voltage across it is about 0, so standoff 13.6 V vs 14.4/16/24 V charging is irrelevant (it is referenced to the battery rail). ES1D sees at most about VBAT_IN (<=48 V with D6) against 200 V. Correct.
5. Open risk: the placement file. Repo adds +180 deg to every SOT-23 (order_bom.py JLC_ROT); a community table (JLCKicadTools cpl_rotations_db.csv) has ^SOT-23 = -90. Not resolvable offline. All other diode packages go out with rotation = footprint rotation.
6. Cheapest saving: BAT54WS-7-F (11 per cur_db, $0.0937 at 50) -> hongjiacheng C7502694 ($0.0127), about $0.9 per board.
7. Minor: hot leakage of the BAT54WS analog clamps (about 20 LSB at 85-90 C), dim 0603 LEDs on 3.3 V / 1k, D35 30 V rating vs load dump on a shorted hall wire, D8 40 V rating vs clamp of D6.

## Pad / net table (cur_db; ord_db identical except as noted)
Convention: pad1 = K (cathode), pad2 = A (anode).
| Ref | Part / pkg | K (pad 1) net | A (pad 2) net | Function | Verdict |
|---|---|---|---|---|---|
| D1-D5 | KT-0603 LED | GND | LED_x_A (via 1k from MCU / +3V3) | status LEDs | OK |
| D101 | KT-0603R | GND | WB_LED_H | wideband heater LED | OK |
| D102/D103 | KT-0603G/B | WB_LED_GK/BK (to 1k to GND) | WB_LED_G/B (F103 PB9/PB8 high) | wideband LEDs | OK |
| D6 | SMCJ30A SMC | VBAT_IN | GND | load-dump TVS | OK (Vrwm 30, Vbr 33.3-36.8) |
| D7 | SS34 SMA | +12V_IN | VBAT_IN | reverse battery | OK |
| D8 | B5819W SOD-123 | +12V_IN | VIGN_IN | ignition wake OR | OK |
| D9 | B360A SMA | BUCK_SW | GND | buck catch | OK |
| D10 | B5819W | +5V | USB_VBUS | bench power | OK |
| D12 | SMAJ33A SMA | +12V | GND | logic-rail TVS | OK (Vbr min 36.7 above 35 V dump) |
| D13,D14,D27-29 | 1N4148WS | +3V3 | HALL1/2, SW1-3 | upper clamp | OK |
| D19-26,D38,D39 | BAT54WS | +3V3 | AN_x | analog clamp (after 5.6k) | OK |
| D30 | BAT54WS | +3V3 | WB_VDDA | VDDA not above VDD | OK |
| D31-34 | B5819W | OUT_IGNn | IGNn_SRC | source diode, blocks short to battery | OK |
| D40/D41 | B5819W | +3V3 | WB_PUMP / WB_VM | op-amp output clamp | OK |
| D15-18 | BAT54S | pad2 +5V, pad1 GND | pad3 VRx input | VR clamp | OK |
| D36/D37 | BAT54S | pad2 +3V3, pad1 GND | pad3 FLEX_M / N2O_ARM_M (ord_db: UART_TX_M/RX_M) | input clamp | OK |
| D35 | BAT54A | pads 1,2 V5_H1/H2 | pad 3 V5_EXT | hall supply OR | OK |
| D42-45 | ES1D | INJn_CL | OUT_INJn | injector clamp diode | OK (cur_db only) |
| D46-49 | 1.5SMC16A | INJn_CL | VBAT_IN | injector clamp TVS | OK (cur_db only) |
Motherboards: D1/D2 SS34 K=VBAT_IN (89-95) or IAC_12V / OCV_12V (99-05), A=OUT_IACV / OUT_VVT: solenoid flyback, correct. D5 SS34 K=AUX_VBAT, A=OUT_BOOST correct. D3/D4 SMCJ30A K=OUT_INJ1/2, A=GND (1989-93 only; cur_mb8995 D3/D4 are optional, no LCSC code, not in CPL; ord_mb8993 has them fitted and in the CPL).
Ordered vs current: ord_db has no D42-D49 (injector clamp lives in the NCV8406 drivers / mb8993 D3,D4), D36/D37 clamp UART_TX_M / UART_RX_M; everything else the same.

## Ratings (VERIFIED from datasheets in datasheets/txt unless marked)
- D6 SMCJ30A Vrwm 30 V, Vbr 33.3-36.8 V, Vc 48.4 V at 31 A: no conduction at 24 V; clamps load dump. D12 SMAJ33A Vrwm 33 V: no conduction at 24 V.
- D7/D8 SS34/B5819W 40 V. D7 reverse in reverse battery is 14 V. D8 reverse = +12V_IN - VIGN_IN: with ignition off, a battery-rail transient up to D6's clamp (about 37-48 V) exceeds 40 V (INFERRED). Same trio (B5819W C8598, SS34 C8678, SMCJ30A) is in ext/hellen-one power_12and5V BOM (VERIFIED), so inherited topology.
- D9 B360A 60 V 3 A vs SW node <= 53 V clamp: OK.
- D31-34: reverse 24 V (jump, shorted coil wire) or 35 V (load dump) vs 40 V: OK with 5 V margin at load dump.
- BAT54S/A 30 V, 200 mA. D35: V5_Hx wire shorted to battery reverses it by Vbat - 5: 9.4 V (14.4), 19 V (24 V), 30 V at a 35 V dump = at the 30 V rating (INFERRED, low).
- D40/D41 forward fault current: pump path 47+62 ohm: <0.25 A. VM path 10 ohm + F2 1.6 ohm: 1.8 A at 24 V until F2 trips, over the 1 A average rating but far under 9 A surge (INFERRED, low).
- ES1D: injector flyback average about 0.2 A at 4 A peak, 8 mH, 50 Hz: OK vs 1 A / 30 A.
- 24 V jump start and the injector TVS: TVS threshold = VBAT_IN + 15.2..16.8 V + ES1D Vf; above about VBAT_IN 18 V it exceeds the driver's 36 V minimum clamp (design.py comment), so in a 24 V jump start the driver clamp, not the TVS, takes the flyback. Intended trade-off ("nothing conducts when supply is high"); energy question belongs to P09.
- BAT54WS leakage (Diodes datasheet p.3 fig 2/4): 2 uA max at 25 V, 25 C; at 3 V reverse about 1.8 uA at 75 C, about 30 uA at 125 C. With 5.6k series plus sensor source, 3 uA at about 90 C gives about 17-25 mV = 20-30 LSB of 12-bit/3.3 V on AN_ inputs (repo comment only covers room temperature) (INFERRED, low).
- LEDs: KT-0603G/B VF 2.6 (min) - 3.1 (max) at 5 mA, 5 V reverse. On 3.3 V with 1 k: roughly 0.2-0.6 mA, a dim indicator (power LED D5 from +3V3 is the worst). Not a failure (INFERRED, low).

## Placement (CPL) check
Script: repo/scripts/order_bom.py lines 212-261 (JLC_ROT table, applied by bom.py). cpl_cmp.py compares evidence CPL to footprint rotation on all 11 boards:
- D_SMA, D_SMC, D_SOD-123, D_SOD-323, LED_0603: CPL rotation = footprint rotation (delta 0) on every board. Relies on JLC's models for these packages having the cathode at KiCad's pad 1 side at 0 deg. The repo comment says this matched in JLC's preview of the rev 0.5 daughterboard; community correction tables list no offset for these footprints. UNVERIFIED by me (no JLC preview access).
- SOT-23 (7 per daughterboard: D15-18, D35, D36, D37): CPL = footprint + 180. Repo says "seen" in the preview of rev 0.5. The community table in matthewlai/JLCKicadTools has ^SOT-23 = -90 (secondary source, old; models differ by part). The two disagree by 90 deg, so at most one is right for these parts; a wrong rotation of a BAT54S/A shorts rails or leaves it off pad. JLC's own polarity guide only says to check the datasheet for common pin. Ordered boards use the same +180. Check D15-18/35-37 in JLC's order placement preview (cheap, before assembly).
- cur_mb8995 D3/D4 are absent from the CPL on purpose (optional).

## Reference designs
ext/hellen-one/modules/power_12and5V/0.2 BOM: B5819W D416/D417 (C8598), SMCJ30A D418 (C310046), SS34 D420 (C8678): same input protection family. Hellen CPL lists D416 SOD-123 at rotation 180 top, D418 SMC at 0, D420 SMA at 0 (different footprint origins, not conclusive).

## Cost / alternates (lcsc.py 2026-11-16)
- BAT54WS-7-F C124205 extended $0.0937@50, 62.7k stock -> BAT54WS hongjiacheng C7502694 (extended+preferred, $0.0127, 46.9k stock): datasheet read (datasheets/extra/BAT54WS_hongjiacheng_C7502694.pdf): VRRM 30 V, IFAV 200 mA, IFSM 600 mA, IR 2 uA at 25 V, Tj -55..125 C, SOD-323 cathode line. Hot-leakage graph not compared. Also C3040452 FUXINSEMI ($0.0128, 73k, params only, datasheet not read). Saving about 11 x $0.081 = $0.89 per daughterboard.
- Other parts already cheap; basic: SS34, B5819W, 1N4148WS, KT-0603R. No basic 0603 green/blue/yellow LED found by keyword search. Stock today: all 15 codes in stock (1.5SMC16A lowest at 1,699; SMCJ30A 11.8k).
- Removal: nothing free to remove (every diode has a function per design.py comments).

## Sources actually read
evidence/*/pcb_footprints.csv, pcb_pads.csv, sch_netlist.xml (cur_db), fab_*cpl.csv (all 11), repo/scripts/design.py (power, injector, clamps, LEDs, ignition), wideband.py, order_bom.py, kb/interconnect.md (IAC_12V), kb/parts_manifest.md, datasheets: C19726 BAT54S pin table, C916423 BAT54A pin picture, C124205 BAT54WS p.2-3, C2288/C12624 KT-0603 tables, hongjiacheng BAT54WS; ext/hellen-one power_12and5V BOM/CPL; JLCKicadTools rotation csv (GitHub); lcsc.py live lookups.

## Not checked
JLC order preview for placement; full digest of ES1D/SS34/B360A/1N4148WS sheets (only ratings from manifest/LCSC params); land patterns of SMA/SMC against each datasheet (KiCad stock pads, 2.5x1.8 at +-2.0 and 3.3x2.5 at +-3.4, are the standard IPC pattern: INFERRED); layout/thermal of injector TVS (P09); 3V3 rail sink capability for clamp currents (P08).
