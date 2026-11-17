# B07 - Current daughterboard (rev 0.10, 6-layer) layout review: signal integrity, analog, wideband, decoupling, EMC

STATUS: complete (2026-11-16). Method: board dumped with pcbnew to `work/B07-daughterboard-layout-signal-analog/board.json`
(tracks, vias, pads, zone fills), analysed with shapely/networkx (`lib.py`, `d*.py`, `c*.py`, `n*.py` in the work dir).
All coordinates are KiCad page mm (board spans x 100..225, y 50..126; U1 at 161,98; U102 at 200.5,98.5; J1/J2 along y=52.75 / 123.25).

## Summary

1. Stack (VERIFIED): F.Cu signal+GND pour, In1 solid GND plane, In2 signal+GND pour, In3 signal+GND pour, In4 solid +3V3 plane, B.Cu signal+GND pour. No stackup is defined in the PCB file (JLC default 6-layer assumed, UNVERIFIED). Plane coverage under tracks is continuous: no splits or slots under USB, CAN, HSE, NRST, ADC or wideband nets (In1 coverage 88 %, In4 82 % of board; tracks 85-100 % over both, remainder = via antipads).
2. Biggest decoupling weakness: the F407 VDDA/VREF+ pins (21,22) have NO capacitor at the pin; C11 1 uF and C12 100 nF sit at the ferrite FB1, 9.2-9.6 mm (pad to pad), 9.9-11.3 mm routed with 2 vias and a B.Cu hop. ST DS8626 wants the filter caps close to the chip.
3. VDD pins 11/19/28 of U1 share a single 100 nF (C3) 3.7 / 7.8 mm away; pins 6/100 share C1/C2 at 3.5-6.6 mm; all 3V3 pin vias are 2.4 mm from the pin (under the package) so via-to-cap-via distances are 5.5-9.7 mm. Medium/low risk, cheap fix.
4. Crystals: Y1 sits 9.4-9.8 mm from the F407 HSE pins; the two HSE traces run parallel 5 mm at 0.3 mm gap, HSE_OUT hops to B.Cu through 2 vias to cross HSE_IN, load caps are on the far side of the crystal (HSE_OUT to C14 = 8.2 mm). Y101 (wideband) 7.2 / 11.5 mm from its pins, OSC_OUT 7.45 mm on B.Cu with 2 vias. Works in practice at 8 MHz, but not the textbook placement.
5. HV clearance: every net pair HV (OUT_*, INJn_CL, VBAT_IN, VIGN_IN, +12V*, DAMP, BUCK_SW, LSU heater) vs 3.3 V logic is >= 0.19 mm on the same layer (min: LSU_HTR_N pad Q101.2 to /MCU/NRST track, F.Cu, 0.19 mm for ~10 mm). Nothing at 0.15 mm. Injector drain nets are >= 9.4 mm from any logic/analog net.
6. Analog: ADC inputs run only beside each other (a quiet bus), >= 17 mm from BUCK_SW, >= 20 mm from injector/clamp copper. Checked, good.
7. Buck (U2) hot loop is compact (SW trace 6.3 mm total, D9 and C17/C18 land on In1 through vias). Checked, acceptable.
8. Wideband: topology and net lengths comparable with the mck1117 reference module; heater return HTR_GND is physically separate from daughterboard GND (joins only on the motherboard). No megohm nodes (largest 100 k on the IS amp, 27 k on Nernst), no switching copper within 0.5 mm of LSU_UN.
9. Autorouter artefacts: none significant (0 dead-end stubs, 2 fold-back joints, all routes <= 1.4x Euclid, no tracks between fine pitch pads - DRC has no clearance violations).
10. Nothing found that blocks first power-up; findings are margin/robustness items.

## 1. Decoupling table (VERIFIED from pcb geometry; effect INFERRED)

"pin via" = nearest same-net via to the pin (all VDD pins reach In4 3V3 plane through it). "cap" = best 100 nF-class cap by via-to-via distance. pad-pad = Euclid between pin pad centre and cap pad centre. U1 is LQFP-100, pad pitch 0.5 mm.

| Pin | Net | pin->via (mm) | best cap(s) | pad-pad (mm) | via-via (mm) | note |
|---|---|---|---|---|---|---|
| U1.6 (VBAT) | +3V3 | 2.42 | C1 100n / C2 100n | 6.6 / 4.6 | 5.5 / 6.5 | shared with pin 100 |
| U1.100 | +3V3 | 2.42 | C1 100n / C2 100n | 3.5 / 4.6 | 5.5 / 6.5 | |
| U1.11 | +3V3 | 2.43 | C3 100n | 5.6 | 7.9 | shares C3 with 19, 28 |
| U1.19 | +3V3 | 2.43 | C3 100n | 3.7 | 6.5 | |
| U1.28 | +3V3 | 2.42 | C3 100n | 7.8 | 7.0 | next cap C5 at 13.6 mm |
| U1.50 | +3V3 | 1.53 | C5 100n (0 via-via, shares via) / C4 | 2.7 / 7.1 | 0 / 6.2 | good |
| U1.75 | +3V3 | 2.43 | C6 100n / C7 4.7u | 3.6 / 4.7 | 4.4 / 6.8 | ok |
| U1.21+22 (VREF+/VDDA) | +3V3A | 0.63 (own via) | C12 100n, C11 1u | 9.2-9.6 | 1.5 (to FB side via) | caps at FB1, route to pin 9.9-11.3 mm, 2 vias, B.Cu hop. DS8626 fig. 51/52 wants them at the chip |
| U1.49 VCAP1 | /MCU/VCAP1 | none (F.Cu) | C9 2.2u | 3.3 | route 4.23 mm, 0 vias | ok |
| U1.73 VCAP2 | /MCU/VCAP2 | none (F.Cu) | C10 2.2u | 2.8 | route 3.05 mm, 0 vias | ok |
| U102.1 | +3V3 | 0.30 | C112 100n | 2.9 | 2.8 | ok |
| U102.48 | +3V3 | 0.48 | C112 100n | 2.0 | 2.2 | ok |
| U102.36 | +3V3 | 0.30 | C121 100n | 2.9 | 2.8 | ok |
| U102.24 | +3V3 | 0.71 | C110 4.7u / C113 100n | 3.2 / 3.6 | 2.5 / 2.9 | ok |
| U102.9 (VDDA) | WB_VDDA | 4.63 | C109 100n | 1.9 (route 2.1, 0 vias) | | ok; C107 1u at 11 mm (route 12.5, 2 vias) sits at REF3033 output U103 |

GND side: every 100 nF cap pad has a GND via 0.2-0.7 mm away (exceptions C2 1.4, C5 0.9, C113 1.9, C65/C66/C68 1.6-2.0). GND pins of U1 (10,20,27,74,99) go to a GND via 1.45 mm away. The 3V3 plane In4 is 3 layers (about 1.2 mm in a typical 1.6 mm 6-layer) away from the F.Cu parts, so pin->via->plane->via->cap adds the via inductances; this is why short pin-via-cap geometry matters more here than on a 4-layer board with plane under the top layer.

ST reference: DS8626 Rev 9 (datasheets/txt/C12345_STM32F407VGT6.txt line 4742, power supply scheme note 1): "These capacitors must be placed as close as possible to, or below, the appropriate pins on the underside of the PCB". Line 8061-8065: VDDA/VREF decoupling per figure 51/52, "10 nF capacitors ... placed as close as possible to the chip".
Impact INFERRED: ~10 mm of 0.2 mm trace is ~10 nH, plus 2 vias; for the F407's 12-bit ADC at slow ECU sampling the effect is small (extra ripple/noise of a few LSB at most), but it removes the point of the ferrite filter at high frequency. Fix cost: 2 x 0402/0603 caps, no new part types.

## 2. Crystals (VERIFIED geometry)

| | HSE_IN (U1.12 - Y1.1) | HSE_OUT (U1.13 - Y1.2) | Y101 WB_OSC_IN | Y101 WB_OSC_OUT |
|---|---|---|---|---|
| pin to crystal | 9.8 mm F.Cu | 9.4 mm, 2 vias, 1.4 mm on B.Cu | 7.2 mm F.Cu | 11.5 mm, 2 vias, 7.45 mm B.Cu |
| crystal to load cap | 5.6 mm (C13) | 10.0 mm (C14, wraps round C13) | 2.6 mm (C119) | 3.1 mm (C120) |
| total net length | 12.1 | 16.2 | 5.2 | 9.5 |

- Crystal is the 2-pad YXC X50328MSB2GI, 8 MHz, CL = 20 pF (parts_manifest line 18), load caps 33 pF. CL = 33/2 + Cstray = 16.5 pF + strays (pin 5 pF + pads + about 12-16 mm of 0.2 mm trace over a plane, order 1-2 pF) = about 22-24 pF: 2-4 pF high, i.e. a few tens of ppm low frequency. Irrelevant for USB FS (0.25 %) and ADC timing. Not an error. (INFERRED, strays typical values UNVERIFIED.)
- Ground: In1 is a solid GND plane under both crystals (Y1 area 91 %, Y101 100 % covered), GND vias at about 2-3 mm around Y1. No guard ring, no keep-out of other nets on F.Cu.
- Noisy neighbours of the MCU oscillator (F.Cu, edge gap): HSE_IN-HSE_OUT 0.3 mm over 5 mm; HSE_OUT 0.3 mm to /MCU/NRST and 0.3 mm to /MCU/SWCLK (SWCLK diagonal at the C13 corner), 1.4 mm to SWDIO. SWCLK/NRST are static in normal use, so the real risk is only during debug. WB_OSC_IN 0.5 mm from WB_VDDA, 1.4 mm from WB_UN_SENSE; WB_OSC_OUT (B.Cu run) 0.68 mm from WB_UN_SENSE (B.Cu, about 4 mm parallel). UN_SENSE is an op-amp output (MCP6004) feeding an ADC pin; an 8 MHz coupling of the order 1 mV (INFERRED, assumed 0.04 pF) is about 1 LSB. Low.
- ST AN2867 (not read; recalled UNVERIFIED) says keep crystal and caps close to pins and avoid other signals under/near; the current placement is acceptable but 2x longer than needed. Fix: move Y1 + C13/C14 to the pin side (x 147-150) or at least swap the pair so HSE_OUT does not cross HSE_IN on two vias.

## 3. Reset, BOOT, SWD

- /MCU/NRST (VERIFIED, pcb_net_routing): 54 mm F.Cu + 55 mm In2 = 110 mm, 5 pads: U1.14, C15 100 nF (14.4 mm routed, 2 vias from the pin), J3.3 (TC2030), SW2 at x=219.5 (58 mm from MCU). Its F.Cu run lies 0.19 mm from the drain/tab pad Q101.2 (LSU heater, PWM, clamp about 40 V) for roughly 10 mm (distance script c2.py). Coupling INFERRED: gap 0.19, length 10 mm -> 4-6 pF; heater edge dV/dt assumed 0.1 V/ns -> 0.5 mA injected into a node that is held by internal pull-up and C15 at the far end; spike estimate <= 1 V for a few ns, below the STM32 NRST filter? (DS8626 NRST filter figures not looked up: UNVERIFIED). Low-medium. Fix: move that segment to In2 or add a GND guard track, and put C15 at U1.14.
- /MCU/BOOT0 (VERIFIED): 76 mm (19 F, 43 In2, 14 B), pulled down by R1 at x=214 (56 mm from U1.94) and SW1 at the board edge. BOOT0 is read only at reset; with a pull-down at the far end noise sensitivity is low. Low. Better: pull-down at the MCU pin.
- WB_NRST 55 mm (U1.58 -> U102.7, C116 11 mm from U102), WB_BOOT0 28 mm, WB_PROG_RX/TX 35 / 38 mm: slow control lines, long. Low.
- SWD: J3 = Tag-Connect TC2030-IDC-NL on the TOP face at (124,104.3): pin map 1 3V3, 2 SWDIO, 3 NRST, 4 SWCLK, 5 GND matches the TC2030 standard (SWO pin 6 not connected). SWDIO 60 mm (22 F + 37 B.Cu, 2 vias), SWCLK 49 mm. No series resistors/ESD. J102 (wideband SWD) is a Tag-Connect on the BOTTOM face (208.5,89), i.e. facing the motherboard: only usable with the boards unstacked (WB MCU can be flashed via F4 using WB_PROG/BOOT0/NRST per net names; firmware path not checked here). Low.

## 4. ADC / sensitive analog routing

Aggressor-to-victim minimum distances (planar, all layers, mm; script c3.py):

| aggressor \ victim | AN_* | AN_VBATT/VIGN | KNOCK | VR/HALL in | +3V3A | HSE | NRST | USB | CAN | WB analog | WB osc |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BUCK_SW | 17.2 | 23.6 | 18.3 | 30.1 | 21.5 | 13.7 | 14.9 | 40.9 | 56 | 65 | 67 |
| DAMP | 26.6 | 33.3 | 28.3 | 40.0 | 30.8 | 22.4 | 24.3 | 46.5 | 62 | 71 | 73 |
| INJ OUT + CLAMP copper | 20.3 | 19.5 | 47.1 | 19.9 | 18.0 | 13.5 | 14.5 | 10.0 | 9.4 | 14.5 | 21.4 |
| LSU_HTR_N | 46 | 53 | 85 | 29 | 53 | 54 | 0.2 | 13.5 | 21 | 0 (layer-blind, see below) | 8.5 |

- LSU_HTR_N "0.0" to WB analog: Q101.2 pad (F.Cu) lies directly over the WB_IS_N/WB_IS_P B.Cu tracks (current-sense amp inputs, 10 k source). Separation is the full stack incl. solid In1 GND and In4 3V3 planes (VERIFIED coverage 94 % / 93 % under the pad), so coupling is shielded; checked, acceptable. WB_IS_N/P are 18.6 / 13.2 mm with 10 k series resistors R111/R112 and 100 k feedback.
- Neighbours of AN_TPS/MAP/CLT/IAT/AFR/AUX1/AUX2 (37-51 mm each, F.Cu): only other AN lines within 0.5 mm (script n1.py). KNOCK, KN_P/N, WB_UN_*, WB_PUMP_*, LSU_UN, WB_IP_SENSE, +3V3A: no foreign net within 0.5 mm on the same layer. Good.
- Topology: each AN channel has its series R, 10 k divider, 10 nF and BAT54WS clamp at the J2 end (D19.. at y=115), then a 37-51 mm F.Cu run to the MCU pin (source impedance about 3.6 k at the cap end). Acceptable at 3.6 k source (F407 12-bit needs <= about 10 k at fast sample times, UNVERIFIED), but the 10 nF is then 40-50 mm from the ADC pin; a cap at the MCU end would be better for HF pickup. Low.
- Return paths: signals referenced to In1 (F.Cu, In2) vs In4 (In3, B.Cu). Nets that change group through vias: 75 nets; for USB_DM/DP, CAN, SWDIO, HSE_OUT, SD the nearest GND via is 1.1-5 mm and the nearest 3V3 via 0.8-7.7 mm (table in r1.py output). Since In2/In3/B.Cu/F.Cu also carry GND pours stitched by about 590 GND vias (spacing about 2.5 mm), this is acceptable for 12 Mb/s USB / 500 kb CAN / 18 MHz SPI. Low.
- Inner signal layers In2/In3: broadside overlap of tracks on the two adjacent inner layers is small: worst pair WB_PROG_RX over WB_PROG_TX 10.7 mm (UART), SD_MISO over LED_RUN 4 mm, everything else <= 2 mm. Good (routing is orthogonal).
- Autorouter metrics: 0 dead-end stubs; 2 fold-back joints (+3V3 F.Cu at 188.75,80.25; SD_SCK at 165.5,106.75, both 0.5-0.75 mm); 2-pin nets mean detour <= 1.4x (worst WB_LED_B, BOOT1, MAINRLY_CTL); no 0.15 mm necks (min width 0.2 mm; VBAT_IN has 0.25 mm sense branch 37 mm to R120/R11 - low current, fine).

## 5. USB, CAN, SD

- USB_DM 36.4 mm (2.56 F + 33.88 B), USB_DP 38.9 mm (6.33 F + 10.41 In3 + 22.2 B): mismatch 2.5 mm = about 15 ps, irrelevant at 12 Mb/s. The pair is not tightly coupled and uses different layers for part of the way; fine for FS. ESD: USBLC6-2SC6 U4 is on the motherboards next to the USB-C (kb/interconnect.md lines 168-169, 283); nothing on the daughterboard, so the ESD clamp is about 37 mm from the F407 pins and the header adds a stub. Acceptable; add a note.
- CAN_H 40.3 mm (32.4 F, 4.0 In3, 3.9 B), CAN_L 41.2 mm (8.3 F, 32.9 B): the pair is on different layers for most of its length, so it is not a coupled pair (INFERRED EMC/mode-conversion penalty, low at 500 kb/s). Both nets serve J2.28/27, U10 (main MCU) and U106 (wideband): the U106 branch is a roughly 30 mm stub. Termination and common-mode choke not in scope here.
- SD (SPI mode signals on J4 at x=214.7): SD_SCK 62 mm, MOSI 58 mm, MISO 56 mm, CS 61 mm, each with 3-4 vias over F/In2/B or In3. No termination seen. Low EMC risk, no functional problem expected.

## 6. Buck U2 LMR14020 (TI SNVSAA5B section 11.1 read: CIN close to VIN and ground, L close to SW, FB away from noise, single ground tie)

- BUCK_SW copper: 4 segments 0.8 mm wide, total 6.3 mm, no vias, no pour (VERIFIED). U2.8 -> D9.1 (3.4 mm) -> L2.1.
- C17/C18 (10 uF/50 V) are 4.3 / 7 mm pad-pad from VIN pins 2/3 with the GND pads on vias to In1; D9.2 GND via pair at 4 mm from U2 GND pad. Loop is closed through In1 (solid plane directly under F.Cu), so effective loop area small. Acceptable; TI example puts CIN within about 2 mm - minor.
- FB: U2.5 to R9/R10 ~9 mm on F.Cu 0.2 mm, passes 4 mm from SW pad over In1; acceptable.
- Large B.Cu VBAT_IN diagonal (1.0 mm) passes under the buck area with In1/In4 planes between: fine.

## 7. Wideband layout vs reference (ext/wideband-mck1117 = repo/scripts/wideband_ref/wideband_controller.kicad_pcb)

Reference: 4-layer 29 x 21 mm, STM32F042, MCP6004 + AD8628 + REF3033 + VND14NV04, GND on In1, 3V3 on In2, whole front end inside about 12 mm. Net lengths (mm, ref -> this board): LSU_Un 8.7 -> 14.5, Un_sense 13.5 -> 10.8, Vm 27.7 -> 25, Ip_dac 6.5 -> 16.6, VDDA 31 -> 20, Rtrim/RT 17.8 -> 12.5. So lengths are of the same order; the new board does carry WB_IP_DAC, WB_ESR (23 mm), WB_VMS (15 mm), WB_HTR_PWM (24 mm) partly on In3 with vias. No evidence of worse analog routing than the reference; the repo already states the layout is new.

- Heater return: net HTR_GND = {J2.39, J2.40, Q101.3} only (VERIFIED pcb_nets): heater current returns via the motherboard, never touches daughterboard GND copper. Good. Side effect (INFERRED): Q101 input is driven from the MCU's GND but referenced to its source on HTR_GND; the difference is the motherboard IR drop (e.g. 3 A x 20 mOhm = 60 mV): harmless.
- Pump sense: R110 (62 R) between LSU_RT (R110.1) and LSU_IP (R110.2); taps are R111 (10 k, on LSU_RT) and R112 (10 k, on LSU_IP). Route lengths: R110.1 -> R111.2 8.8 mm (2 vias, In2); R110.2 -> J2.36 2.7 mm then -> R112.2 7.5 mm more: the IP tap is taken at the connector, not at the R110 pad, so the main current flows through 2.7 mm of 0.2 mm trace before the tap. Error: 13 squares x 0.49 mOhm/sq = 6.5 mOhm vs 62 Ohm = 0.01 % (INFERRED). With 10 k sense resistors this is irrelevant: Kelvin connection is not needed here. Checked, not an issue.
- High-impedance nodes: Nernst LSU_UN path R137 22 k, R114/R104/R105/R107 10-27 k; no megohm node. No foreign net within 0.5 mm of LSU_UN, WB_UN_P/N/SENSE (except WB_OSC_OUT on B.Cu 0.68 mm from UN_SENSE, op-amp output). No switching 12 V copper nearby (heater drain pad about 5 mm from the IS amp traces, shielded by In1). Guard ring not required at 27 k.
- VM / reference: WB_VM (7 pads, 25 mm, 4-5 vias) and VM_REF (5.8 mm) similar to reference (27.7 mm). Fine.

## 8. HV clearance and ESD

- Script c2.py (all same-layer pairs, tracks+pads+vias, 64 pairs under 0.45 mm). Smallest: 0.19 mm (Q101.2 / NRST), 0.207 mm (VIGN_IN 0.4 trk vs SWDIO via and vs V5_EXT via), 0.22 mm (VBAT_IN via vs +3V3 pad R162.1 at (188,82.5)), 0.24 mm (VBAT_IN R11.1 vs AN_VBATT via), 0.245 mm (+12V trk vs V5_SENS U3 pad). None under 0.15 mm. These are 12-14 V nets (VBAT_IN, VIGN_IN, +12V); the 30-45 V injector drain/clamp nets (OUT_INJ*, INJn_CL) have no logic neighbour within 0.45 mm. Pour clearances (zone clearance 0.25 mm) not re-measured. IPC-2221 coated-conductor spacing for 31-50 V is 0.13 mm (recalled, UNVERIFIED), so 0.19 mm with solder mask is adequate.
- ESD entry points: USB (TVS on motherboard), harness pins (motherboard), add-on header (motherboard, 20-pin), J2 analog pins (BAT54WS clamps D19-D26 at the connector). J3 / J102 / J4 (SD) have no protection but are internal.

## Sources actually read

- the review brief; evidence/cur_db: pcb_nets.txt, pcb_net_routing.csv, pcb_stats.json, drc_kicad9.json (types only), layers/top_all.png, fab_track_current.txt; repo/daughterboard/miata_ecu_daughter.kicad_pcb (via pcbnew copy in work/); kb/interconnect.md (HTR_GND, USB); kb/parts_manifest.md (Y1/Y101, USBLC6); datasheets/txt/C12345_STM32F407VGT6.txt (lines 4740-4746, 8058-8066); datasheets/txt/C187824_LMR14020SDDAR.txt (section 11.1); repo/scripts/wideband_ref/wideband_controller.kicad_pcb (footprints, net lengths); repo/scripts/design.py lines 113-116.

## Not checked

- AN2834/AN4488/AN2867 not downloaded (web not used); their numbers are not quoted. STM32 NRST filter spec, ADC source impedance limit, crystal CL not looked up beyond the manifest.
- Impedance/stackup (no stackup in file; JLC 6-layer thicknesses assumed); zone clearances; thermal; DNP/ordered rev 0.9 (4-layer) board not analysed here (it has different routing).
- Wideband schematic function of R108/R110/LSU_RT (trim pin used as pump node) not verified (schematic owner: other audits).
- Silkscreen/mask (acid traps) not reviewed.
