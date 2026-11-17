# P08: 3.3 V rail (U4 LDL1117S33R) and +3V3 shunt clamp (U15 TL431 + Q20 BCP53 + C63/C68)

Status: complete (run 2). Tags: VERIFIED = read/computed today from design files or datasheet; INFERRED = reasoned from verified numbers; UNVERIFIED = memory/guess.

## Summary (10 lines)
1. Pinouts and footprints of U4, U15, Q20 all check out against the datasheets (LDL1117 1 GND/2 OUT/3 IN, tab = OUT; TL431 DBZ 1 CATHODE/2 REF/3 ANODE; BCP53 SOT-223 1 B/2 C/3 E/4 C). Same on ord_db (rev 0.9). VERIFIED.
2. Clamp threshold: Vth = Vref x 1.425 + Iref*3.6k = 3.46 V (min corner) .. 3.57 V (typ) .. 3.68 V (max corner). LDO worst-case output is 3.3 x 1.03 = 3.399 V (-40..125 C, 10 mA, ST Table 4) plus about 15 mV load regulation, so the clamp stays off by at least 45 mV. The repo's "LDO max 3.37 V" is the +-2 % 25 C figure, not the full-temperature +-3 %.
3. The clamp's peak (repo sim: 3.93 V for a 1 A step at nominal 3.56 V) scales to about 4.05 V at the max-tolerance threshold 3.68 V, above the MCUs' 4.0 V abs max (INFERRED: same overshoot added to a higher threshold). The 1 A ideal step is unrealistic (real worst step is about 0.43 A), so low-medium.
4. IS THE CLAMP NEEDED? For the ordinary inputs (8 analog, 2 hall, 3 switch, flex, N2O, battery/ignition sense) NO: worst-case injection is 19.5 mA with every input shorted to 14.4 V at once, 40.7 mA at 24 V all at once, and a single input is at most 4.3 mA (hall at 24 V). The rail always draws more (F103 wideband MCU alone 20-35 mA running, plus LEDs, pull-ups; F407 at least 5 mA, 93 mA at 168 MHz). The only reason the clamp exists is the wideband pump / Vm drive clamps D40, D41 (B5819W) behind 47 ohm / 10 ohm: 0.22-0.43 A (RT/pump wire to 14.4/24 V), 0.7-1.7 A for Vm until PTC F2 trips. That far exceeds any load, so with D40/D41 present the shunt is required. Removing U15/Q20/R141-143/C63/C68 (about $0.43/unit at qty 100, 2 extended-part fees) is only valid together with removing D40/D41, which would let a harness short kill U101 / the MCUs through their ESD diodes. Verdict: keep.
5. LDO thermal: dissipation (5.0-3.3) x 0.2 A = 0.34 W typ, 0.5 W at 0.3 A; theta-JA 120 K/W (ST) -> Tj 126 C at 0.2 A and 146 C at 0.3 A with 85 C air; operating Tj limit is 125 C. The tab pad has one 0.3 mm via and a short trace as copper. Medium risk (INFERRED).
6. 200 uF of ceramics on the LDO output is outside ST's stability plot (1-22 uF, ESR 0.01-10 ohm); expected benign but not covered by the datasheet. C63/C68 are 6.3 V X5R parts at 3.3 V bias: effective capacitance likely 40-60 % of nominal (UNVERIFIED, no DC-bias curve in the LCSC Samsung sheet).
7. Parts identity, stock and price (live 2026-11-16): all four codes are what the BOM says; U4 and U15, Q20 are EXTENDED, C15008/C15850 BASIC.

## 1. Circuit as built (VERIFIED: repo/scripts/design.py:249-255 and 528-541; evidence/cur_db and ord_db pcb_nets.txt / pcb_pads.csv; identical on both)

| Ref | Value | LCSC | Footprint | pad -> net |
|---|---|---|---|---|
| U4 | LDL1117S33R | C435835 | SOT-223-3_TabPin2 at (134.6,96.4) rot 90 | 1 GND, 2 +3V3, tab(2) +3V3, 3 +5V |
| C26 | 10u 25V X5R 0805 | C15850 | | +5V / GND (LDO input), 6 mm from pin 3 |
| C27 | 10u 0805 | C15850 | | +3V3 / GND, 9 mm from pin 2 (also C7, C8 4.7u, C70 10u, 100n decoupling) |
| U15 | TL431AIDBZR | C23892 | SOT-23 | 1 SH_K, 2 SH_REF, 3 GND |
| Q20 | BCP53-16 | C85085 | SOT-223 | 1 SH_K, 2 GND, 3 +3V3, 4 (tab) GND |
| R141 | 1k | C21190 | 0603 | +3V3 / SH_K |
| R142 | 5.1k | C23186 | 0603 | +3V3 / SH_REF |
| R143 | 12k | C22790 | 0603 | SH_REF / GND |
| C63, C68 | 100u 6.3V X5R 1206 | C15008 | | +3V3 / GND |

Topology: R142/R143 divider senses +3V3; TL431 cathode node SH_K is pulled to +3V3 through R141 and drives the base of PNP Q20 whose emitter is +3V3 and collector GND. Above threshold the TL431 pulls SH_K down, Veb rises, Q20 sinks current from +3V3 to ground.

## 2. Datasheet digests

### LDL1117S33R (datasheets/txt/C435835_LDL1117S33R.txt, ST DocID030319 Rev 3; LCSC copy is ST's own, current rev)
- Abs max (Table 2): VIN -0.3..20 V; VOUT -0.3..VIN+0.3; Tj op -40..125, max 150; theta-JA 120 K/W, theta-JC 15 K/W (Table 3). Thermal shutdown 175 C (25 hyst).
- Table 4: VIN 2.6-18 V; UVLO on 2.3/2.4 V; VOUT +-2 % at 25 C, +-3 % over -40..125 C (10 mA) -> 3.201-3.399 V; load reg 5 typ/15 max mV (10 mA-1.2 A); dropout 350 typ / 600 max mV at 1.2 A; Iq 250 typ / 500 max uA; ISC 1.5 min / 2 typ A; SVR 87 dB 120 Hz.
- Caps (6.2, Fig 20/21): CIN >= 1 uF near pin; COUT ceramic, stability plot spans 1..22 uF and ESR 0.01..10 ohm at 100 kHz, must hold over temperature. Suggested 1 uF in / 4.7 uF out.
- Pin table (p.6): 1 GND, 2 VOUT, 3 VIN, tab = VOUT. Land pattern/package mech on p.16-17 (standard SOT-223, 6.3 mm span, 2.3 mm pitch).

### TL431AIDBZR (TI SLVS543N, C23892; current TI sheet)
- DBZ (SOT-23-3) top view (p.2): pin 1 CATHODE, pin 2 REF, pin 3 ANODE (the TL432 variant swaps 1 and 2; the part number is TL431, so cathode on 1 is right).
- Abs max: VKA 37 V; IKA -100..150 mA; Iref -0.05..10 mA; Tj 150. Recommended: VKA Vref..36 V, IKA 1..100 mA, TA -40..85 C (I grade). theta-JA 206 K/W (DBZ).
- TL431AI: Vref 2470/2495/2520 mV at 25 C, 10 mA; deviation over temperature (SOT-23-3) 14 typ / 34 max mV; Iref 2 typ / 4 max uA; Imin 0.4 typ / 0.7 max mA; Ioff 0.1 / 0.5 uA; zKA 0.2 / 0.5 ohm.
- Stability boundary figure (Fig 15) excludes SOT-23-3 devices: no datasheet stability guarantee vs cathode capacitance for the DBZ. Here the cathode load is only the Q20 base and R141, so capacitive loading is small.

### BCP53-16,115 (Nexperia/NXP BCP53_BCX53_BC53PA, C85085)
- SOT-223 pinning (Table 3): 1 base, 2 collector, 3 emitter, 4 collector (tab).
- Abs max: VCEO 80 V, VCBO 100 V, VEBO 5 V, IC 1 A (2 A pulse 1 ms), IB 0.3 A, Tj 150 C; Ptot 0.65 W standard footprint, 1.00 W at 1 cm2 collector copper, 1.35 W at 6 cm2 (Tamb 25 C); Rth(j-a) 192 / 125 / 93 K/W; Rth(j-sp) 16 K/W. hFE (-16) 100-250 at 2 V/150 mA; VBE <= 1 V at 500 mA; VCEsat <= 0.5 V at 500 mA.

### CL31A107MQHNNNE (Samsung, C15008): 100 uF 6.3 V X5R +-20 % 1206, basic. The LCSC file is the generic series catalogue with no DC-bias curve, so effective capacitance at 3.3 V cannot be quoted from it (UNVERIFIED, from memory 40-60 % for this class).

## 3. Usage audit

### a. Pin-by-pin (all VERIFIED: pcb_pads.csv, design.py, datasheet tables above)
| Part | Pad | Net | Datasheet function | Verdict |
|---|---|---|---|---|
| U4 | 1 | GND | GND | OK |
| U4 | 2 and tab | +3V3 | VOUT | OK |
| U4 | 3 | +5V | VIN | OK |
| U15 | 1 | SH_K | CATHODE (DBZ) | OK |
| U15 | 2 | SH_REF | REF | OK |
| U15 | 3 | GND | ANODE | OK |
| Q20 | 1 | SH_K | base | OK |
| Q20 | 2, 4 (tab) | GND | collector | OK (PNP, emitter on the rail, collector grounded: correct sink) |
| Q20 | 3 | +3V3 | emitter | OK |
Q20 Veb in use <= about 1 V (VEBO 5 V). C63/C68, C26/C27: non-polarised ceramics.
Schematic (sch_netlist.xml) and design.py agree with the PCB; the KiCad rev 0.10 / 0.9 nets are identical for all these parts (ord_db checked: same nets, same values; only the AUX UART/FLEX net names on D36/D37 differ).

### b. Footprints (VERIFIED from pcb_pads.csv)
- U4: pads 2.0x1.5 at 2.3 mm pitch, tab 2.0x3.8, span 6.3 mm: standard SOT-223. Tab copper: pad plus ONE 0.3 mm via (134.5,93.25) to the +3V3 plane on In4 and a trace; GND pour on F.Cu is separated by clearance. Heat-spreading copper is poor (see 3c).
- Q20: same SOT-223; tab (collector) is GND merged into the F.Cu GND pour with vias nearby (layer image): good thermal path.
- U15: SOT-23, pads 1.475x0.6, pitch 1.9 between pins 1 and 2: standard.

### c. Electrical stress
LDO: Vin 5.0 V (buck output, P05), +5V up to about 5.1 V. VIN abs max 20 V: no stress. Reverse: +5V cannot go below the LDO output except by the rails discharging together (the LDO in dropout conducts both ways; I looked for a reverse-current problem with 200 uF and did not find one that survives).
Dissipation (INFERRED, Vin 5.0, Vout 3.3): 0.2 A -> 0.34 W; 0.3 A -> 0.51 W; 0.35 A -> 0.60 W. Tj(85 C air) = 85 + P x 120: 126 / 146 / 157 C. Repo load budget (P05 3d): 0.2 A typ, 0.3-0.35 A peak with SD writes. So typical use sits at the 125 C limit, peaks go above abs max 150 C unless the real theta-JA is below ST's 120. Mitigation: more copper and 4-6 vias on the tab (free), or drop the SD socket load.
Clamp threshold (INFERRED arithmetic): fraction f = 12k/(5.1k+12k) = 0.7018; with 1 % resistors f = 0.6976..0.7059; Vref 2.436..2.554 V (2.47-0.034 .. 2.52+0.034 incl. temperature deviation); Iref 2-4 uA x (5.1k||12k = 3.58k) = 7-14 mV. Vth = (Vref + Iref*3.58k)/f -> min (2.436+0.007)/0.7059 = 3.46 V, typ 3.56-3.57 V, max (2.554+0.014)/0.6976 = 3.68 V. LDO max 3.399 V + 15 mV. Margin to clamp turn-on >= 45 mV (the TL431 reference does not switch hard: Imin 0.4-0.7 mA only at Vref, so current at 50 mV below is far smaller). Divider standing current 3.4/17.1k = 0.2 mA; Ioff <= 0.5 uA; hot leakage of BCP53 (ICBO 100 nA at 25 C) is negligible against the 1k pull-up. TL431 current at turn-on: (3.56 - Vk)/1k with Vk >= Vref 2.5 V gives about 1 mA, above Imin max 0.7 mA: OK. TL431 TA limit 85 C equals the stated cabin maximum (inside the case it is hotter; the part conducts almost nothing so self-heating is nil).
Clamp peak: the repo sim gives 3.93 V (1 A step, nominal 3.56 V). At the max threshold 3.68 V the same overshoot gives about 4.05 V against 4.0 V abs max of both MCUs (INFERRED; real worst step is 0.43 A, so less).
Q20 sinks I_inj - I_load. RT shorted to 24 V: I = 0.43 A (below), Q20 power = 3.56 V x (0.43 - 0.15) = 1.0 W to 1.5 W if the rail load is small, Tj = 85 + 1.2 x about 60-90 K/W -> above 150 C if it lasts more than seconds; R108 (47 ohm 1206, 8.6 W) fuses open first, ending the fault (repo documents R108-R110 as sacrificial). Fine for a one-time fault; Q20 is not rated for a continuous fault.
Loop stability: not simulated by me (UNVERIFIED). Plant is a current sink into a 200 uF-class capacitor plus a low-impedance LDO, controller a TL431 (single pole) plus R141: probably fine, the repo reports a simulation (VERIFICATION.md line 574) that I did not re-run.

### d. External parts and stability
LDO input 10 uF (min 1 uF): OK. LDO output: 10 uF C27 + C7/C8 4.7 uF x2 + C70 10 uF + 100 nF x about 12 + C63/C68. ST only characterises 1-22 uF; with ceramic ESR of a few mOhm the ESR is below the 0.01 ohm axis edge. Expected stable (large C pushes the output pole low), but not covered. INFERRED/UNVERIFIED. TL431 and BCP53: no extra parts required beyond the divider; no unused pins.

### e. Reference designs
Hellen and mck1117 boards in ext/ use the wideband module without any +3V3 clamp (mck1117 wideband_controller.kicad_sch has no TL431, no clamp diodes except an LED). The clamp, D40/D41, D30 are repo additions. rusEFI Hellen Miata boards use their own supplies (not compared in detail).

## 4. Fault-current budget (the key question; VERIFIED values from pcb_pads.csv, arithmetic in work/P08-3v3-rail-and-clamp/inj.py)
Model: I = (Vfault - (Vrail + Vf))/Rseries - (Vrail + Vf)/Rshunt, Vrail = 3.4 V, hot low-Vf (BAT54WS 0.2 V, 1N4148WS 0.45 V).

| Group | n | Rseries / Rshunt | Per input @14.4 / 24 / 35 V | All of the group @14.4 / 24 / 35 V |
|---|---|---|---|---|
| AN_TPS..AUX3 D19-26 | 8 | 5.6k / 10k | 1.57 / 3.28 / 5.25 mA | 12.5 / 26.3 / 42 mA |
| HALL1/2 D13/14 | 2 | 4.7k / none | 2.24 / 4.29 / 6.63 | 4.5 / 8.6 / 13.3 |
| SW1-3 D27-29 | 3 | 22k / 10k | 0.09 / 0.53 / 1.03 | 0.3 / 1.6 / 3.1 |
| FLEX, N2O D36/D37 (ord: UART) | 2 | 10k / none | 1.08 / 2.04 / 3.14 | 2.2 / 4.1 / 6.3 |
| AN_VBATT / AN_VIGN D38/D39 | 2 | 33k / 6.8k | 0 / 0.09 / 0.42 | 0 / 0.2 / 0.8 |
| TOTAL | 17 | | | 19.5 / 40.7 / 65.4 mA |
| WB pump D40 via R108 47 ohm (RT short) | 1 | 47 / none | 0.22 A / 0.43 A | (35 V: 0.67 A) |
| WB pump via R110+R108 (IP short) | 1 | 109 | 0.096 A / 0.184 A | |
| WB Vm D41 via R109 10 ohm + PTC F2 (1.5-5 ohm cold) | 1 | 11.5-15 | 0.7-0.9 A / 1.3-1.7 A until F2 trips; then residual about tens of mA | |
Not clamped to +3V3 (no injection): IN_KNOCK, VR inputs, LSU_UN (62k pull-up only: 0.33 mA at 24 V, resistive).
Minimum always-on 3.3 V load (INFERRED from P05 3d and datasheets): F103 wideband MCU powered whenever the rail is up (datasheet 72 MHz 33-50 mA; even at low clock it is >10 mA), LEDs (R6 1k etc.), pull-ups 0.2-1 mA each, op-amps; F407 in reset about 1 mA or less (UNVERIFIED), 5 mA typ at 16 MHz peripherals off (datasheet Table 20 line 5235), 93 mA typ at 168 MHz. Worst case "everything dead-quiet" is about 25 mA (F103 running) -> still above any single ordinary-input fault (max 4.3 mA) and above the all-inputs-at-14.4 V sum (19.5 mA), below the all-inputs-at-24 V sum (40.7 mA, which needs 17 simultaneous shorts, with F407 in reset).
Conclusion: the shunt is not needed for input clamps D13-D14, D19-D29, D36-D39. It is required for D40/D41 (hundreds of mA, far above any load). Removing group {U15, Q20, R141-143, C63, C68} saves about $0.43/unit at qty 100 (U15 0.0614@50 / 0.0534@150, Q20 0.2219@50 / 0.1949@150, C63+C68 2 x 0.0743@100, resistors about 0.01) and two EXTENDED-part setup fees, but only if D40/D41 are also removed, which exposes U101 (MCP6004) and U102 pin PB0-class VM node to a 14.4-24 V wire short (the mck1117 reference accepts that risk). Recommendation: keep unless the owner accepts that risk. If the owner wants to cut cost, remove one of C63/C68 only after re-running the repo's step-response sim (UNVERIFIED benefit).

## 5. Part audit
1. Identity (live tools/lcsc.py 2026-11-16): C435835 = LDL1117S33R ST SOT-223, EXTENDED, stock 47.6k, $0.3241@30 / 0.2766@100. C23892 = TL431AIDBZR TI SOT-23-3, EXTENDED, stock 235k, $0.0614@50 / 0.0534@150. C85085 = BCP53-16,115 Nexperia SOT-223, EXTENDED, stock 21.4k, $0.2219@50 / 0.1949@150. C15008 = CL31A107MQHNNNE Samsung 1206 100 uF 6.3 V X5R, BASIC, stock 2.3 M, $0.0743@100. C15850 10 uF 25 V BASIC. All match the BOM (kb/parts_manifest.md).
2. Alternates: none recommended (no alternate datasheet read). AMS1117-3.3 was the pre-0.7 part (0 C minimum, 1 V dropout; repo rationale accepted).
3. 3.3 V rail alternatives not worth chasing: $0.28 for U4.

## Sources actually read
design.py 240-260, 515-545; pcb_nets/pcb_pads/pcb_footprints (cur_db, ord_db); datasheets/txt C435835 (all), C23892 (pins, abs max, electrical, stability fig), C85085 (pinning, ratings, thermal), C12345 (Table 20 line); C435835 p.14 image; kb/parts/P05 (3d), P06, P02; repo/VERIFICATION.md 573-583; layer crops work/P08-3v3-rail-and-clamp/*.png; vias.py; tools/lcsc.py for the five codes; ext/wideband-mck1117 schematic (no clamp parts).

## Not checked
Loop stability of the TL431/Q20 loop with 200 uF (no sim); DC-bias capacitance of C15008 at 3.3 V; STM32F407/F103 current in reset and in the ROM bootloader (not in datasheet tables I read); LDL1117 dropout figure the repo quotes (0.15/0.3 V; datasheet gives 0.35/0.6 V at 1.2 A, lower at 0.2 A: curve not read); real theta-JA of U4 with the actual copper (no thermal sim); In4 plane shape near U4; layer 3D thermal behaviour of Q20.
