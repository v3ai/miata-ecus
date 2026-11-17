# P12 - Analog input channels (dividers, filters, Schottky clamps, thermistor pull-ups, battery / ignition sense, knock amplifier)

STATUS: complete (2026-11-16). Tags: VERIFIED / INFERRED / UNVERIFIED as in review brief section 5.

## Summary

1. All pin maps checked and correct: U8 LMV321 SOT-23-5 pad-by-pad (1 IN+ = KN_P, 2 GND, 3 IN- = KN_N, 4 OUT, 5 VCC = +3V3) matches the TI datasheet p.3; BAT54WS clamps have K (pad 1) on +3V3 and A (pad 2) on the AN node (netlist pinfunction K/A); MCU pins PA1..PA7, PB0, PB1, PC4, PC5 match firmware ADC channel defines (miata_pins.h).
2. Thermistor firmware model is right: 2.7k pull-up to V5_EXT loaded by 15.6k = Thevenin 4.262 V behind 2.302 k, and rusEFI's ResistanceFunc really uses `custom_board_getThermistorSupplyVoltage` + `bias_resistor` that way (init_thermistors.cpp:51-52, resistance_func.cpp:33).
3. Scaling: 5 V x 0.641 = 3.205 V (97.1 % FS, 118 codes headroom). A 5.2 V output (3.333 V) just saturates the ADC at 4095 and cannot damage anything (clamp is not yet conducting: forward 33 mV). Sensor outputs above about 5.15 V read full-scale.
4. Real weakness (not in repo docs): the channels are NOT ratiometric. ADC reference = VDDA = +3V3 from LDL1117S33R (+-3 % over temperature, datasheet), sensors are fed from the +5V buck (4.88-5.12 V, P05 inferred) through the TLS115 trackers; rusEFI assumes exactly 3.3 V and 5 V (miata_board.cpp:30, 66-72). MAP reading error up to about +-7 kPa at 100 kPa and +-13 kPa at 200 kPa (worst corner), CLT/IAT up to about +-2 K at 25-80 C and about 7 K at -20 C (worst corner). Typical (RSS) values are about half.
5. Clamp leakage (BAT54WS Fig.2 / Fig.4, Diodes DS30098): 0.045 uA at 25 C, about 1.7 uA at 75 C, 25 uA at 125 C at 1.3 V reverse; interpolated about 3 uA at 85 C, about 9 uA at 105 C. Through the 3.6 k source: 11 mV (14 LSB) at 85 C, 32 mV at 105 C on the 5.6k/10k channels; on the battery divider (5.6 k source) 17 mV = 0.1 V of battery reading at 85 C.
6. Knock stage: gain 5.7 (47k/10k), bias 1.65 V, HPF about 16 Hz, closed-loop bandwidth about 175 kHz, output RC (330 R + 10 nF) 48 kHz, ADC 218.75 ksps (84+12 cycles at 21 MHz). Knock frequency of BP 1.6/1.8 cylinders: Draper first circumferential mode about 6.1-6.5 kHz (INFERRED, bore 78/83 mm), amplifier flat there. There is no real anti-alias filter above 109 kHz (Hellen's knock module has a multi-pole filter around the same LMV321).
7. Fault survival: sensor wire to 14.4 V / 24 V: 21 mW / 75 mW in the 5.6k 0603 (100 mW), clamp 0.5 / 1 mW, 1.9 / 3.6 mA into +3V3; CLT/IAT pull-up 33 / 134 mW (0603, 100 mW: 24 V case exceeds 100 mW rating briefly, see finding). Battery divider fine to 24 V, reverse battery injects 0.42 mA (limit 5 mA).
8. Cost: BAT54WS-7-F (Diodes, EXTENDED, $0.0937 @50, $0.0843 @150) x 11 on the board (D19-D26, D38, D39, D30). Same-footprint clones C7502694 (hongjiacheng, EXTENDED+PREFERRED, $0.0107 @500, stock 46.9 k) and C3040452 (Fuxinsemi, $0.0103 @500, stock 73 k) have identical VF/IR/CT limits; saving about $0.8 per board but the HJC 100 C leakage curve is visibly about 3x worse. Not removable: PA4/PA5 (TPS, MAP) are TTa pins with abs max 4.0 V (datasheet Table 11 "any other pin"), clamp is needed there.
9. Nothing was found that stops the board working. No error-class finding survived.

## 1. Identity (parts_manifest.md, lcsc.py 2026-11-16)

| Ref | LCSC | MPN | Pkg | Type | Stock | Price |
|---|---|---|---|---|---|---|
| D19-D26, D38, D39 (and D30) | C124205 | BAT54WS-7-F Diodes Inc | SOD-323 | EXTENDED | 62,746 | 0.1115@1, 0.0937@50, 0.0843@150, 0.0670@3000 |
| U8 | C7972 | LMV321IDBVR TI | SOT-23-5 | EXTENDED (PREFERRED) | 79,608 | 0.1226@1, 0.0989@50, 0.0868@150 |
| R27 etc | C23189 5.6k 0603 1 % UNI-ROYAL 75 V; C25744 10k 0402 1 %; C13167 2.7k 0603 1 %; C25779 33k 0402 1 % 50 V; C25917 6.8k 0402; C25879 2.2k 0402; C25803 100k 0603 | | | all basic (C25917 pref) | | |
| C36-C43 | C15195 10n 50 V X7R 0402 +-10 % | | | basic | | |
| C28/C29 | C1525 100n 16 V X7R 0402; C44/C47 C14663 100n 50 V 0603 | | | basic | | |

Identity of C124205 = BAT54WS-7-F SOD-323 single Schottky: correct (datasheet p.1: 30 V, 100 mA, cathode band; marking L9). C7972 = LMV321IDBVR SOT-23-5 (TI SLOS263W): correct.

## 2. Datasheet digests

### BAT54WS (Diodes DS30098 Rev 14-2, datasheets/txt/C124205_BAT54WS-7-F.txt; Fig. 1/2/4 viewed as images, work/P12-analog-inputs/bat54ws_fig*.png)
- Abs max: VRRM/VR 30 V, IO 100 mA, IF 200 mA, IFRM 300 mA, IFSM 600 mA (<1 s), PD 200 mW, RthJA 625 C/W, Tj -65..150 C.
- Electrical (25 C): V(BR) 30 V @100 uA; VF max 240 mV @0.1 mA, 320 @1 mA, 400 @10 mA, 500 @30 mA, 1000 @100 mA; IR max 2 uA @25 V; CT max 10 pF @1 V; trr 5 ns.
- Fig.2 typical IR vs VR (read at VR 1.3 V): 0 C 0.007 uA; 25 C 0.045 uA; 75 C 1.7 uA; 125 C 25 uA. At 25 V: 25 C 0.2 uA, 75 C 5 uA, 125 C 65 uA.
- Package SOD-323: pin 1 cathode (band side), pin 2 anode; KiCad D_SOD-323 pad 1 = K, pad 2 = A (netlist: `pinfunction K` on pad 1, `A` on pad 2).

### LMV321IDBVR (TI SLOS263W, datasheets/txt/C7972_LMV321IDBVR.txt p.3-6)
- Pins (DBV SOT-23-5, top view): 1 IN+, 2 GND, 3 IN-, 4 OUT, 5 VCC+ (p.3).
- Abs max: VCC 5.5 V; VID +-5.5 V; VI -0.2..5.7 V; Tj 150 C. Recommended VCC 2.7-5.5 V.
- At 2.7 V (the 3.3 V case is better): VIO 1.7 typ / 7 max mV, IIB 11 typ / 250 max nA, CMRR 63 dB, VICR 0..1.7 V (min), VO high VCC-10 mV typ (VCC-100 max), low 60/180 mV (RL 10k), ICC 80 typ/170 max uA, GBW 1 MHz, SR 1 V/us, Vn 46 nV/rtHz, 5-60 mA short-circuit source.
- Land pattern: standard SOT-23-5 0.95 mm pitch.

## 3. Usage audit

### 3a Pin tables (cur_db pcb_pads.csv + sch_netlist.xml + design.py)

U8 (cur_db pads at x 110.86 / 113.14, 0.95 pitch, pad 1 top-left, 4 bottom-right):

| Pad | Net | Datasheet | Verdict |
|---|---|---|---|
| 1 | KN_P | IN+ | OK |
| 2 | GND | GND | OK |
| 3 | KN_N | IN- | OK |
| 4 | KN_OUT | OUT | OK (feedback R48 taken at pad 4, before R50) |
| 5 | +3V3 | VCC+ | OK, C47 100n 3.3 mm away (111.2,114.6) |

ord_db identical (same netlist and footprint, VERIFIED pads).

D19-D26, D38, D39: pad 1 = +3V3 (K), pad 2 = AN_x (A): OK.
U1 pins: 24 PA1 AN_VBATT, 25 PA2 AN_VIGN, 26 PA3 AN_KNOCK, 29 PA4 TPS, 30 PA5 MAP, 31 PA6 CLT, 32 PA7 IAT, 33 PC4 AFR, 34 PC5 AUX1, 35 PB0 AUX2, 36 PB1 AUX3 (pcb_pads.csv, schematic nets agree, design.py:148-151, firmware miata_pins.h:58-67 same ADC channels). VDDA/VREF+ (pins 21,22) = /MCU/+3V3A via FB1.

### Signal paths (kb/interconnect.md; sensor roles from repo INSTALL.md, UNVERIFIED for sensor identity)

| Daughterboard in | 1989-95 motherboard (8995 / 8993 / 9495) | 1996-97 | 1999-2000 | 2001-05 |
|---|---|---|---|---|
| IN_TPS (J2.4) | harness 2M (via R30 0R from 2L, option) / 3F on 9697 | 3F | 3E | 4V |
| IN_MAP (J2.5) | on-board MPX5700AP U2 pin 1 + C3 470 p, not a harness pin | same | same | same |
| IN_CLT (J2.6) | 2Q | 3G | 2E | 4P |
| IN_IAT (J2.7) | 2P (stock IAT in AFM) | 3K | 2B | 4N |
| IN_AUX1/2/3 | 2L-via-R29 / 2N / (JP6 2O) | 3D / 3C / 3B | 3J / 2C / 2L | (AUX1 n/a) / 4W / 4X |
| IN_KNOCK (J2.3) | AUX header J5.6 only | J5.6 only | harness 2F + J5.6 | harness 4M + J5.6 |
| VIGN_IN (J1.3) | 1C (START signal, 1989-95) | not connected | not connected | 4S (IG1 sense) |
| VBAT_IN | 1B | | | |

The 1989-95 board carries two 4.7k pull-ups to V5_EXT (R27 AUX1, R35 FLEX) and 0R links R28/R29/R30; not part of this audit beyond noting that R29 and R30 both land on HARN_2L (a stuffing error would short IN_TPS to IN_AUX1; both are 0R options).

### 3b Footprints
SOT-23-5 pads 1.325 x 0.6 at 0.95 pitch, span 2.275 mm centre to centre: standard. SOD-323 pads 0.6 x 0.45... KiCad D_SOD-323: standard. 0402/0603 per design. Layout (evidence/cur_db/pcb_net_routing.csv, pads): every AN_x filter cap / clamp / divider cluster is at x 120-132 mm while the MCU pins are at x 153-160 mm, so each AN net is a 37-51 mm single-layer 0.2 mm trace (AN_TPS 50.8 mm, AN_MAP 48.3, AN_CLT 46.0, AN_IAT 43.7, AN_AFR 41.4, AN_AUX1 39.1, AN_AUX2 36.7, AN_KNOCK 37.1 + 4 on In2) carrying a 3.6 kOhm-source node with its filter cap at the far end. Not wrong, but noise pickup is not bypassed at the pin. INFERRED, low.

### 3c Electrical stress

Sensor input (TPS/MAP/AFR/AUX): Rs = 5.6k, Rb = 10k, C = 10 nF, ratio 0.641, FS(ADC) 3.3 V = 5.148 V in, LSB 0.806 mV at the ADC = 1.257 mV at the harness; 1 % resistors => ratio +-0.72 % worst (0.359 x 2 %).
- Source impedance seen by ADC = (5.6k + Rsensor) || 10k = 3.59 k at Rsensor = 0, below 3.59k-5.5k; STM32 limit: RAIN max formula (DS Table 67: CADC 4 pF, RADC 6k): rusEFI slow ADC sampling is 56 cycles @21 MHz (stm32_adc_v2.cpp:168) => RAIN max = (56-0.5)/(21e6 x 4e-12 x ln 2^14) - 6k = 62 k (table cap 50 k). Margin 14x. The 10 nF node is stiff vs the 4 pF sample cap (charge-share step <= 4pF/10nF x 3.3 V = 1.3 mV, 1.6 LSB worst case when the previous channel differed by full scale).
- Filter corner: 1/(2 pi x 3.59k x 10n) = 4.4 kHz (more with sensor impedance: TPS 5k pot up to about 2.9 kHz). Fine for TPS/CLT/IAT; for MAP with fast samples the corner gives little alias suppression (MAP also has 470 pF on the motherboard).
- Sensor output 5.0 V: 3.205 V (3977 codes). With V5 +2.4 % and 3V3 -3 %: 5.12 x 0.641 = 3.28 V vs 3.20 V: saturates above about 4.99 V sensor output. 5.2 V: 3.333 V > 3.3 V: saturated, no damage (clamp forward 33 mV: negligible).
- Short to 14.4 V / 24 V (clamp Vf about 0.3 V): R 21 / 75 mW (0603 100 mW), clamp 0.5 / 1 mW, injection 1.9 / 3.6 mA into +3V3 (shunt clamp U15 documented in P08). Pin voltage about 3.6-3.9 V vs abs max 4.0 V for TTa pins PA4 (TPS) / PA5 (MAP) (DS Table 11: "any other pin" -0.3..4.0 V; pin table 7: PA4/PA5 I/O TTa; the other analog pins are FT: PA6, PB0, PC4, PC5 FT verified in pin table; PA1/2/3/7/PB1 FT not read individually). Margin at 24 V with +3V3 at the TL431 clamp (3.56 V per design.py comment) = about 3.9 V: thin (0.1 V).
- CLT/IAT bias resistor shorted-sensor wire to 24 V: (24-5)^2/2.7k = 134 mW in a 100 mW 0603 (design.py comment says so); a 24 V jump-start wire fault is a double fault, repo documents rating.

Thermistor channels: Vth = 5 x 15.6/18.3 = 4.262 V, Rth = 2.302 k (miata_pins.h:72-77, test_miata_ecu.cpp:603). CLT -20 C (18k): node 3.78 V -> ADC 2.42 V; 120 C (100 ohm): 0.177 V -> 0.114 V = 141 codes, about 0.33 K/LSB; cold end 0.04 K/LSB. Adequate. Non-ratiometric temperature error (r = +-5.5 %, INFERRED, NTC B about 3900): +-1.8 K at 80 C, +-2.2 K at 25 C, +-7 K at -20 C worst corner.

Battery sense: 33k/6.8k, ratio 0.1709, FS 19.3 V, LSB 4.7 mV at 3.3 V (0.8 mV ADC => 4.7 mV battery), 14.4 V -> 2.46 V, cranking 6 V -> 1.03 V. Source impedance 5.64 k: OK (RAIN 62 k). Filter 5.64 k x 100 n = 282 Hz. Tolerance: 1 % resistors => +-1.66 % worst; plus 3V3 +-3 % => battery reading about +-5 % worst (0.7 V at 14.4 V), typical about +-2 % (0.3 V). 24 V: node 4.1 V, clamped to about 3.6 V, 0.62 mA in R11 (33 mW at 24 V, 62.5 mW rating) OK. SMCJ30A (D6) clamp up to VC 48.4 V at 12.4 A (datasheet from P06 not re-read): R11 0402 rated 50 V working voltage, 60 mW at 48 V: at limit only for ms-pulses. Reverse battery: D6 forward clamps VBAT_IN about -1..-5 V so the divider sees at most -14.4 V x 6.8/39.8 = -2.5 V: pin clamps at -0.4 V, injected 0.42 mA (< 5 mA per DS Table 12), ADC accuracy of other channels irrelevant unpowered. Rev 0.9 (ordered): R11 on +12V (after D7, F1): reads 0.3-0.6 V low (repo documented); D38/D39 present on both revisions (ord_db footprints verified).

Knock (R138 2.2k, C44 100n, R45 100k, R46/R47 100k/100k, C45 1u, R48 47k, R49 10k, R50 330, C46 10n):
- Gain 1 + 47/10 = 5.7 (15.1 dB); bias node 1.65 V (3V3/2, 50 k, decoupled by 1 u); same node is the inverting reference so output DC = KN_BIAS. HPF: C44 with R45 100k = 15.9 Hz. Piezo (about 1 nF, UNVERIFIED, repo says 23 k at 7 kHz): 100k/1nF source corner 1.6 kHz; passband loss at 6.5 kHz about 3 %.
- Offset: Ib 11 nA typ / 250 nA max x (100k - 8.3k) x 5.7 = 6 mV typ / 130 mV worst at output; Vos 7 mV max x 5.7 = 40 mV. Worst-case output offset about 170 mV of 1.65 V centre: clip level 284 mV in (documented) goes to about 245 mV worst.
- Bandwidth: GBW 1 MHz / 5.7 = 175 kHz; slew need 2 pi x 6.5 kHz x 1.55 V = 0.063 V/us << 1 V/us; closed-loop gain error at 6.5 kHz 0.07 %. Output R50 330 + C46 10 n = 48 kHz. R50 isolates the 10 nF from the loop (datasheet Fig. 9 stability vs CL); stable.
- ADC: KNOCK_SAMPLE_RATE = STM32_PCLK2/(4 x 96) = 218.75 kHz (84 MHz PCLK2 assumed, UNVERIFIED value of PCLK2; knock_config.h:13-14). Nyquist 109 kHz, only a 48 kHz single-pole + 175 kHz closed-loop BW in front: 100-200 kHz ignition / injector noise aliases into the 5-15 kHz knock band. INFERRED.
- Knock frequency: first circumferential mode f = 1.841 c / (pi B), c about 850-870 m/s burned gas, B = 83 mm (1.8) => 6.1 kHz; 78 mm (1.6) => 6.5 kHz. INFERRED (not measured; typical published knock band 5-15 kHz, UNVERIFIED).
- Fault: knock wire to battery: C44 passes the step; clamp by LMV321 input diodes, 14.4 V - 3.6 V over 2.2 k = 4.9 mA for tau 220 us (datasheet limits input VI to 5.7 V, input-diode current not specified). 1 kV level ESD on J5.6: 2.2 k + C44 + HBM 2000 V (datasheet p.1). Output node limited to 0..3.3 V by U8 supply: no clamp needed on AN_KNOCK. U8 powered from +3V3 (not +3V3A filtered): harmless.

### 3d Required external parts: LMV321 supply bypass C47 100n present. Unused pins: none. No sequencing issue (U8 and ADC same rail).

### 3e Reference designs
ext/hellen-one/modules/knock/0.1: LMV321 x2 (C7972) with 470k bias, 3.3n/330p/47p/680p filter network (multi-pole band-limited), 33k/100k/12k gain; the Miata board has one flat stage. Hellen Miata NA6/NB1 BOMs carry 10k and 6.8k 0603 dividers (not examined for clamps). The BAT54WS clamp is this project's own addition (design.py:471-477).

## 4. Cost and simplification
- Same-footprint BAT54WS clones (C7502694 hongjiacheng EXT+PREF; C3040452 Fuxinsemi EXT; C5251553 MDD $0.0103@500 etc.): datasheets read (datasheets/extra/BAT54WS_hongjiacheng_C7502694.pdf and _fuxinsemi_C3040452.pdf): VF max 240/320/400/500/1000 mV at 0.1/1/10/30/100 mA, IR 2 uA at 25 V, CT 10 pF: identical to Diodes. HJC cathode line = cathode end. HJC Fig.2 shows typical 100 C leakage about 20-30 uA (10-25 V), about 3x worse than Diodes. Fuxinsemi: pin polarity not extracted from text (page images not viewed): UNVERIFIED. Saving at 500 pcs-class pricing: 0.0937 -> about 0.011 = $0.08 per diode, 10 diodes (D19-26, D38, D39) plus D30 = about $0.9 per board; both clones are EXTENDED like the original so no library-type change.
- Cannot use 1N4148WS (basic, $0.0086) as clamp: Vf about 0.65 V at 2 mA puts the TTa pins at about 4.0 V (limit 4.0 V). INFERRED.
- Removals: none free. D19/D20 (TPS/MAP) are on TTa pins with abs max 4.0 V and a 5.6k from 14.4 V would give 9.2 V: required. D21-D26 on FT pins: removal would rely on analog-mode behaviour not documented by ST in the sheets read: not recommended. C28/C29/C36-C43 filter caps: remove only with firmware filtering; negligible cost ($0.002 each). R32/R35 (10k) on CLT/IAT cannot go while pulled up to 5 V.
- Option: pull CLT/IAT up to +3V3 (via 2.7k) instead of V5_EXT: node max 3.3 V, the 10k legs and exact 5 V dependence disappear and the measurement becomes ratiometric to VDDA (errors above vanish). Requires firmware change (supply 3.3 V, bias 2.7k) and the clamp stays. INFERRED idea, not tested.

## Sources actually read
the review brief; repo/scripts/design.py 250-264, 375-402, 470-530; repo/firmware/board/miata_pins.h:50-77, miata_board.cpp:15-45, 60-80, 120-130, 236-260, knock_config.h; firmware/ext/rusefi init_thermistors.cpp:51, resistance_func.cpp, adc_inputs.cpp:50-70, thermistors.cpp:33-46, stm32_adc_v2.cpp:167; evidence/cur_db and ord_db pcb_nets.txt, pcb_pads.csv, pcb_footprints.csv, pcb_net_routing.csv, sch_netlist.xml D19/U8; kb/interconnect.md; kb/parts P05/P06/P07/P08 (read-only); datasheets C124205 (text + Fig.1/2/4 images), C7972 p.3-6 text, C12345 STM32F407 Tables 11, 12, 67, 68, pin table text, C435835 LDL1117 accuracy +-3 %, C90152 MPX5700AP; ext/hellen-one knock module BOM and schematic; clone datasheets BAT54WS C7502694 and C3040452; tools/lcsc.py today.

## Not checked
- Pin type FT/TTa for PA1, PA2, PA3, PA7, PB1 individually; whether analog mode limits below VDDA+0.3 V (repo claim) as ST doesn't state it in the sheets read.
- Real piezo capacitance / output of the Miata knock sensor; real PCLK2 value; layer-image inspection around U8; JLC placement rotation of the SOT-23-5 / SOD-323 in JLC's preview.
- Fuxinsemi clone polarity (page images), SMCJ30A VC figure not re-read.
- Hellen NA6/NB1 analog front-end values (only grep'd).
