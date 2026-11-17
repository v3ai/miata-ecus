# P07 - Protected sensor 5 V supplies: TLS115B0EJ trackers U3 (V5_SENS) and U14 (V5_EXT)

STATUS: complete (2026-11-16). Tags: VERIFIED / INFERRED / UNVERIFIED as in review brief section 5.

## Summary

1. U3 / U14 = Infineon TLS115B0EJ (LCSC C3743696, PG-DSO-8 exposed pad), JLC EXTENDED, stock 554, $1.09 @30, $0.913 @100 (tools/lcsc.py today). Sole-source Infineon; the "D" variants (C3747428 stock 45, etc.) are different parts, not read, not recommended. Both boards need 2 per unit = 1 extended line, so stock covers ~270 boards.
2. Pinout checked on cur_db and ord_db (identical): 1 OUT, 3 GND, 5 ADJ=+5V, 7/8 IN and EN=+12V, EP=GND, N.C. 2/4/6 open. All correct (VERIFIED, pcb_pads.csv + design.py:244-247, 490-493 + datasheet p.6).
3. Footprint matches package drawing (p.26): 1.27 pitch, EP 2.65 x 3.00 (3.0 along the pin rows), pin 1 and numbering consistent.
4. Electrical stress is within ratings: IN is the PTC-fused +12V rail (abs max 45 V, -16 V), output short to GND or battery is a designed-for case (limit 350 mA typ, thermal shutdown).
5. Main design weakness is not the part but the system: sensors are ratiometric to the +5V buck rail, the ADC reference is the 3.3 V LDO, and NO ADC channel measures any 5 V rail. In the repo's own level II crank simulation +5V is 3.91 V, so sensor readings are about 22 % low during that pulse; static worst-case gain error between the two rails is about +-6.7 % (RSS about 4 %).
6. Output caps (1 uF 0603 X5R 50 V, C25 / C61) are exactly at the datasheet minimum; effective value after bias/temperature/tolerance is below it. Same value as Hellen One uses, ESR window is no problem for ceramics (stable region reaches down to 10 mOhm). Suggest 2.2-4.7 uF on V5_EXT (harness).
7. Two trackers: justified by short-to-battery on the harness 5 V wire (MAP sensor stays protected). One tracker (Hellen style) or U3 replaced by ferrite from +5V would save about $1.1 per board; trade-offs below.

## Datasheet digest (Infineon TLS115B0EJ Rev 1.14, 2024-12-27, datasheets/txt/C3743696_TLS115B0EJ.txt, all pages read; images p.13-15, 26)

- Function: high-precision voltage tracker; VOUT follows voltage on ADJ (2.0..14 V), 150 mA, short-to-GND / short-to-battery protected output, reverse-polarity protected input, thermal shutdown (175 C, 15 K hysteresis, p.12), current limit.
- Abs max (Table 1, p.7): VIN -16..45 V; VEN -16..45; VADJ -16..45; VOUT -5..45; VIN-VOUT -30..45; Tj -40..150; ESD HBM 4 kV. Note: protection not for continuous repetitive operation.
- Functional range (Table 2, p.8): VIN 4..45 V; VADJ 2..14 V; COUT >= 1 uF (applies at worst-case capacitance tolerance of 30 %, footnote 1); ESR <= 5 ohm.
- Tracking accuracy (Table 4): -5..+5 mV (VADJ-VOUT), for 5.5 V <= VIN <= 22 V, 0.1-150 mA, VADJ <= VIN-1 V; +-5 mV also to 32 V at <= 70 mA. Load reg -4..0 mV; line reg 0..4 mV. Dropout 250 mV typ / 500 mV max at 150 mA (VOUT 100 mV below nominal). Current limit 151 / 350 / 500 mA (VOUT = VADJ-0.1 V). Reverse current VIN=0, VOUT=16 V: -1.7 mA typ. IIN,rev at -16 V: -2 mA.
- Iq: 0.1 uA off (typ), 55 uA at <0.1 mA, 7 mA typ / 14 mA max at 150 mA load. IADJ 0.03 uA typ, 1 uA max. EN: off <= 0.8 V, on >= 2 V, 2 uA at 5 V; EN open = off (internal pull-down); "if enable not needed connect EN to IN" (p.6).
- Thermal (Table 3): RthJA 50 K/W (2s2p), 157 K/W (footprint only 1s0p), 77 (300 mm2), 63 (600 mm2); RthJC 18; RthJP 85.
- Current limit vs VIN (p.13 graph, image work/P07-5v-trackers/ds_p13_ilim_vin.png): about 360 mA (25 C) / 320 mA (150 C) flat 10-22 V, falling to 270 mA at 28 V and 60 mA at 40 V; limit collapses below about 5.5 V input.
- Stability (p.15 ESR graph): stable region from the bottom of the plot (10 mOhm) up to about 5 ohm for COUT = 1 uF, 6-15 V, whole Tj range. No lower ESR bound, ceramics are fine.
- Application (p.23-24): CIN1 100-470 nF ceramic close to IN; optional electrolytic CIN2 10-470 uF for ISO pulse 2a; overvoltage suppression diode D1 on the supply; COUT X5R/X7R on the same side, close to OUT and GND; EP to GND, to a heat sink.
- Pin table (PG-DSO-8): 1 OUT, 2 N.C., 3 GND, 4 N.C., 5 ADJ, 6 N.C., 7 EN, 8 IN, EP GND. Land pattern: package 3.9 x 4.9 mm, pitch 1.27, lead tip span 6.0, EP 3.0 x 2.65 (p.26).

## Usage audit

### a. Pin table (cur_db and ord_db; U3 at 113.0,100.6 rot 0; U14 at 128.4,73.5 rot 180 cur / 162.0,75.0 ord)

| Pad | Datasheet | U3 net | U14 net | Verdict |
|---|---|---|---|---|
| 1 | OUT | V5_SENS (-> J2.1 -> MB MAP) | V5_EXT (-> J1.13, D35.3, R33, R36) | OK |
| 2,4,6 | N.C. | open | open | OK (DRC lists them as no-net) |
| 3 | GND | GND | GND | OK |
| 5 | ADJ | +5V (buck out) | +5V | OK (ADJ range 2-14 V) |
| 7 | EN | +12V | +12V | OK (EN tied to IN allowed, p.6; 45 V abs max same as IN) |
| 8 | IN | +12V | +12V | OK |
| 9 (EP) | GND | GND | GND | OK |

Sources: evidence/cur_db/pcb_pads.csv, pcb_nets.txt (V5_SENS 3 pads, V5_EXT 6 pads, +12V list), repo/scripts/design.py:244-250 and 488-495 (same maps). Rev 0.9 (ordered) identical, including U14 (VERIFIED: evidence/ord_db/pcb_pads.csv). Pad numbering: KiCad library pad numbers, counter-clockwise from pin 1; U14 rotated 180 so pin 1 is bottom-right, checked consistent with the pin 5 diagonal.

Other parts: C24, C62 (1 uF 50 V X5R 0603 CIN at +12V, 1 per tracker, pads +12V / GND); C25, C61 (1 uF COUT: pad 1 = V5_SENS or V5_EXT, pad 2 GND). C1 1 uF + C2 10 nF on the motherboard V5_SENS add capacitance at the far end of U3's output. D35 = BAT54A common anode: anode pin 3 = V5_EXT, cathodes pins 1,2 = V5_H1 / V5_H2 (pcb_nets.txt:10,11,217); standard SOT-23 BAT54A has pin 3 as common anode (INFERRED, datasheet pin picture not viewed). Diode drop makes the hall pull-up supply about 4.7 V; harmless.

### b. Footprint / layout
- Footprint Infineon_PG-DSO-8-27_3.9x4.9mm_EP2.65x3mm: pads 1.65 x 0.60 at 1.27 pitch, 5.25 mm centre span, EP 2.65 x 3.00 oriented with the 3.0 along the pin rows: matches p.26 (VERIFIED). Paste on EP split in 4 windows.
- Thermal vias in EP: U3 has 2 inside plus 2 on the edge (113,100.5; 113,101.5; 113.5,99.5; 113.5,102.5); U14 has 1 inside (128.5,73.25). Board is 6-layer with GND planes (cur). U14 has less via copper, but its normal dissipation is under 1 W.
- COUT / CIN placement: C25 at 107.4,103.0 is 3-6 mm from U3 pad 1 (110.4,98.7) on its own track; C61 at 130.4,77.2 is about 2.5 mm from U14 pad 1; both on the same side, with GND vias next to them. Fine.

### c. Stress

Rails: +12V is after D7 (SS34), F1 (PTC 1.1 A hold) and D12 (SMAJ33A); the TLS115 IN pins hang on +12V and need 5.5 V minimum for the 5 mV accuracy spec (4 V functional minimum).

| Condition | U3 | U14 | Verdict |
|---|---|---|---|
| Normal 14.4 V, 10 mA / 60 mA load | P = 9.4 V x 10 mA + 14 V x Iq(~0.1 mA) = 0.1 W | 9.4 V x 60 mA + 14.4 x ~3 mA = 0.6 W, rise about 30 K at 50 K/W | OK |
| 85 C air, max 150 mA | not applicable (10 mA) | 9.4 x 0.15 + 14.4 x 7 mA = 1.5 W -> 75 K at 50 K/W -> Tj 160 C: over; but real load is far below 150 mA (hall 2 x 5 mA pull-up + sensors) | OK for realistic load; INFERRED |
| Cranking 6 V at battery | IN about 5.9 V (PTC drop at tens of mA is small), VOUT = ADJ = +5V which itself sags (see below); dropout need 50-250 mV: fine | same | tracker OK; the +5V rail is the limit |
| 24 V jump | IN 24 V, 45 V max, accuracy spec to 32 V at <= 70 mA; P at 60 mA: 1.1 W | | OK |
| Load dump | D6 SMCJ30A (VBR 33-37 V) then D12 SMAJ33A; in a 101 V unsuppressed dump the node can reach about 45 V | | marginal vs 45 V abs max, INFERRED, see finding |
| Reverse battery | IN/EN rated -16 V, D7 blocks anyway (D12 forward-clamps the rail to -0.7 V behind F1) | | OK |
| Output shorted to GND | limit about 350 mA x 14.4 V = 5 W (24 V: 270 mA x 24 = 6.5 W) -> Tj reaches 175 C in seconds (50-157 K/W), shutdown, 15 K hysteresis, oscillates until the fault is removed | | designed-for (p.10) but note "not for continuous repetitive operation"; ECU keeps running since IN is a separate branch from the buck |
| Output shorted to battery 14.4 V / 24 V | VOUT up to 45 V allowed, VIN-VOUT >= -30 V; reverse current into +12V a few mA (IOUT,rev -1.7 mA typ at VIN = 0) | same; D35 BAT54A (30 V) reverse biased by hall wire shorts (documented fix) | OK |
| ADJ | 5 V on a pin rated 2-14 V; IADJ 0.03 uA: no loading of the buck | | OK |

V5_EXT load: stock harness sensors per motherboard (TPS pot, air flow meter on 1989-95, CAS/hall pull-ups through D35 about 5 mA each, 2.7 k CLT/IAT biases about 1-2 mA each, R35 4.7 k flex, J5-14 add-on header) all well under 150 mA; the allowed total is 150 mA continuous (350 mA limit). The add-on header J5-14 is not current limited separately: an external accessory over about 100 mA would run the tracker at 1 W+.

### Sag and ratiometric error (the main system question)
- VERIFIED: the sensors are ratiometric to the 5 V supply (MPX5700AP: Vout = VS x (0.0012858 P + 0.04), datasheet C90152 p.? line 163; "ratiometric within 4.75-5.25 V", Table 1 line 67/82; supply current 7 mA typ, 10 mA max). VERIFIED: the ADC reference is the 3.3 V rail (VDDA from +3V3 via FB1, design.py:177; +3V3 = LDL1117S33R off +5V). VERIFIED: ADC inputs are AN_KNOCK, TPS, MAP, CLT, IAT, AFR, AUX1-3, VBATT, VIGN (design.py:148-151): none measures +5V, V5_SENS or V5_EXT.
- Reading error factor = (V5/5.0) / (V33/3.3) - 1.
  - +5V 3.91 V (repo VERIFICATION.md:580: level II crank, buck at its limit; the tracker follows ADJ with 5 mV): 3.91/5 = 0.782 -> -21.8 % (MAP 100 kPa reads about 78 kPa) for the pulse duration (ms to a few hundred ms). The LDL1117 holds 3.3 V down to about 3.7 V in (350 mV dropout, datasheet line 207), so the divisor stays 1.
  - +5V 4.5 V: -10 %; 4.75 V: -5 %. Below 4.75 V the MPX5700AP is outside its specified excitation range.
  - Tracker contribution: +-5 mV = +-0.1 %, negligible; the tracker needs VIN >= VOUT+0.5 V (5.5 V) and +12V is before D7, so the tracker has about 0.5 V more headroom than the buck and is never the limiting element.
- Static error from two independent tolerances: +5V = 0.75 V x (1+68k/12k) = 5.0 V; LMR14020 VFB 0.735-0.765 V over temperature (+-2 %, datasheet line 273) plus 1 % R9/R10 (about +-1.7 % worst) => 4.815..5.185 V (+-3.7 %). +3V3: LDL1117S33R +-3 % over temperature (line 197-199). Worst-case ratio error +-6.7 %, RSS +-4.1 %, typical well under 2 %. It is a pure gain error on MAP, TPS, MAF/AFM, CLT/IAT (bias divider) alike. For comparison MPX5700AP itself is +-2.5 % of span (+-17.5 kPa; repo VERIFICATION.md:692), larger than the rail mismatch at 100 kPa (4 % of reading = 4 kPa).
- Correction possible? Not with current hardware: STM32F407 VREFINT measures VDDA (3.3 V), not the 5 V rail. A divider from V5_EXT or V5_SENS to a spare ADC input (e.g. 10k/10k, 2.5 V) would let the firmware scale sensors (rusEFI support not checked). Or do nothing: affects fuel in the 15-100 ms crank dip only.

### d. External parts
- CIN 1 uF (C24 / C62): datasheet 100-470 nF ceramic minimum; 1 uF OK. The optional electrolytic CIN2 is covered by upstream C16 (10 uF 50 V on DAMP) and the TVS D12.
- COUT 1 uF 0603 CL10A105KB8NNNC (X5R, 50 V): equals the minimum. Footnote 1 says the 1 uF minimum holds at worst-case tolerance, i.e. nominal >= 1.43 uF; X5R +-10 % tolerance, DC bias at 5 V on a 50 V 0603 part (typically 10-20 % loss, UNVERIFIED, Samsung curve not read) and -15 % at 85 C puts effective C near 0.65-0.8 uF. Stability graph was measured at 1 uF, with no lower ESR bound, so risk is low; U3 has 1.01 uF more on the motherboard, U14 has harness capacitance. Fix: 2.2 uF 0603 X5R 16 V+ (one-line change).
- EN: tied to IN: permitted. No sequencing issues: ADJ source is the buck output, which comes up after +12V; tracker follows.
- Unused N.C. pins open: correct.

### e. Reference designs
- ext/hellen-one/modules/power_12and5V/0.3 BOM: single TLS115 (U411, LCSC C540242, "TLS115" same family) with +5V buck from the same LMR14020 (68k/12k divider, 10u caps) and 1 uF 0402 C414/C415. Hellen NB1 / NA6 boards U6 TLS115 (C540242). hellen-one/global-replace.csv:91: "TLS115 same power supply/same reference on all boards". So this design copies the topology, with one tracker split in two. Hellen's single tracker feeds all sensors including MAP.

## Cost and simplification
- Is a tracker needed at all? A harness 5 V wire in a Miata (TPS, AFM, etc. running to the engine bay) can be shorted to battery or ground; a bare buck rail (+5V) would be dragged down or back-fed and would take the ADC reference and logic with it, so one tracker (as Hellen) is needed. Typical other ECUs use a 5 V LDO with series resistor/sensor-supply tracker (MC33xxx, TLE4250) or just a protected regulator.
- Two vs one: U3 isolates the on-board MAP (MPX5700AP, hand-fitted, not in the harness) from V5_EXT faults. Removing U3 and feeding V5_SENS from +5V through a ferrite bead (FB1-type BLM18PG221, C80165, already on the BOM) saves about $1.09 + C25 $0.008 + share of C24, about $1.1 per board (0.3 % of price). It also makes MAP work on USB-only bench power. Cost of removal: MAP loses its isolation from +5V ripple (3 x 10 uF + buck ripple, 7-10 mA is a light load, MAP has 1 uF + 10 nF locally) and the PCB must change (not worth reworking on the ordered rev 0.9). The extended-part line stays because U14 is still fitted, so no setup-fee saving. A single TLS115 for both, MAP and harness on V5_EXT, saves the same but exposes the MPX5700AP to short-to-battery (its max Vs is not in the datasheet text I read; UNVERIFIED).
- Alternates: TLE4250-2G (C976300, $0.27-0.60, stock 15, 50 mA, SCT595-5) cannot supply the harness (too little current, stock 15). TLS115D0EJ (C3747428, stock 45) and TLS115B0LD (C540241, stock 6, TSON-10) are other variants, not drop-ins, datasheets not read: no recommendation. No basic part exists with the tracker function. Stock risk: 554 total.

## Findings detail (the ones in the structured answer)
See structured result. Extra notes:
- USB-only bench: the repo documents +12V back-feed to about 4 V when powered from USB; at 4 V the tracker is at its 4 V minimum, EN at the 2 V threshold ok, but VOUT = min(ADJ, VIN - dropout) so V5_SENS/V5_EXT would be at or below 3.5-4 V (INFERRED): MAP not valid on a USB-only bench.
- U14 shorted output cycling: 5 W peak into a package whose EP has one via: Tj cycles 160-175 C; the tracker is rated for this as protection, repeated for the life of a pinched wire is a reliability question only.

## Sources actually read
- datasheets/txt/C3743696_TLS115B0EJ.txt (all), page images p.13, 15, 26
- datasheets/txt/C90152_MPX5700AP.txt (lines 60-120, 160-170), C435835_LDL1117S33R.txt (accuracy, dropout), C187824_LMR14020SDDAR.txt (VFB, dropout paragraph), C916423_BAT54A.txt (header)
- repo/scripts/design.py (power, U3/U14, D35, ADC map), mb_*.py grep, repo/VERIFICATION.md lines 506-580, 692, 1157
- evidence/cur_db and ord_db: pcb_pads.csv, pcb_nets.txt, pcb_footprints.csv, via listing via work/P07-5v-trackers/dump_pcb.py
- kb/interconnect.md, kb/parts_manifest.md, tools/lcsc.py live lookups
- ext/hellen-one/modules/power_12and5V/0.3/*-BOM.csv, ext/hellen-one/global-replace.csv, ext/hellen-miata-NB1/NA6 BOMs

## Not checked
- Layer images around U3/U14 not viewed (via/track data used instead); track width on +12V to pads 7/8 not measured.
- Exact +5V value at the real crank dip (took the repo's simulation, 3.91 V level II) - not re-simulated.
- Samsung CL10A105KB8 DC-bias derating curve (not read).
- rusEFI handling of a 5 V rail ADC channel; spare ADC pin availability.
- BAT54A pin diagram image not viewed.
- MPX5700AP absolute max supply voltage (not in the datasheet text).
