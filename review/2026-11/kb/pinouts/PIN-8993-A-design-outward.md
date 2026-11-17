# PIN-8993-A design-outward: 1989-93 (NA6 1.6 L, 48-pin) pinout chain audit

Boards: cur_mb8995 (rev 0.13, JP1/JP2 open, JP3=90-93, JP4 open, JP5 open, JP6=AFM) and ord_mb8993 (rev 0.11, fixed links).
Status: COMPLETE (partial; see Not checked).

## Summary
1. Primary source obtained: the 1991 Mazda MX-5 wiring diagram scan (mellens.net 1991_wiring.pdf, Fig. 2 "Computer Engine Control", sheet 50G06750) shows ECU CONN #1 / CONN #2 with a wire colour on every populated pin and its destination. Only 1991 was read; 1989, 1990, 1992, 1993 were NOT independently read (rusEFI 1990 table agrees with it where it has data).
2. The design's pin MAP matches the FSM for: 1B, 1C, 1E, 1G, 1H, 1J, 1N, 1R, 2A-2E, 2G, 2K, 2L, 2M, 2N, 2O, 2P, 2Q, 2U, 2V, 2W, 2X, 2Z.
3. 2T "fuel pump relay": NO wire on 1991 ECU pin 2T. On 1990-93 the pump runs via the circuit-opening relay, switched by the vane airflow meter's fuel-pump contact and the starter signal, not by the ECU. The board's OUT_FP output goes nowhere; if the vane AFM is removed (speed-density, the board's whole point) the pump will not run unless the AFM-connector pump contact is bridged. README does not say so.
4. 1L (fan) and 1M (VSS): NO wire on 1991 ECU (rusEFI 1990 table also N/C). The fan relay is on 1R (BLK-GRN). README/firmware label 1L "radiator fan relay" and 1M "vehicle speed" for 1989-93: wrong for the cars read; harmless (nothing connected) but the fan must be configured on fan2 (1R).
5. 2I: FSM shows 2I (BLK-WHT) comes FROM igniter terminal E; the tach (YEL-BLU) is fed straight from igniter terminal D. So 2I is an input and the stock igniter drives the tach: repo choice (JP5 open, no tach output) is CORRECT. This resolves the repo "unresolved 2I" open item for 1991. The ORDERED board hard-wires OUT_TACH to 2I (no jumper).
6. 1V: M/T: BRN-WHT to clutch switch (switch to ground) and cruise-control unit; A/T: BLK-BLU to ignition switch (12 V with key on). Firmware assigns clutchDownPin = SW3 on every year: on an automatic it would read "clutch down" permanently.
7. Stock inputs with no board connection: 1A (hot-at-all-times), 1D/1F/1K (diagnosis connector), 1O (stop lamp), 1P (power-steering pressure switch), 1S (heater control unit), 1U, 2H. Driver-visible: no idle-up for PS / blower, no self-diagnosis.
8. Purge 2X: wired and freewheel-diode protected, but firmware assigns no pin (vvt pin unassigned) so the purge valve is never opened. No EGR wire exists at the 1991 ECU.

## Sources actually read
- S1 (primary) 1991 Mazda wiring diagram scan, http://www.mellens.net/mazda/Mazda-Miata-1991-1993/1991_wiring.pdf, page 4 (Fig. 2); crops in work/PIN-8993-A-design-outward/c1.png c2.png d1.png d2.png e1.png f1.png g1.png. Colours read from the image; column-to-letter alignment checked by the constant -20 px label offset and by cross-checks (CONN#2 colours E,G,K,L,M,N,O,P,Q,U,V,W all equal rusEFI table colours).
- S2 rusEFI wiki "Mazda Miata 1990" (raw.githubusercontent.com/wiki/rusefi/rusefi/Mazda-Miata-1990.md, saved w_Mazda-Miata-1990.md): 1990 US 1.6 table. Partly derived from the same Mazda data, so only semi-independent.
- S3 rusEFI wiki "Legacy Miata NA 48 pin board for MRE" (mre.txt): same table plus jumper notes: "2I tach pullup: Y with stock coils; tach out only with aftermarket coils", "JP56 1M pull-up VSS (untested, 94+)", "AC fan 93-" separate from "94+", injectors 3/4 parallel on 93-.
- S4 AMP MSPNP2 MM9093 install page (amp.txt): thermoswitch also runs fan; 93 California cars already wired for sequential; text only, pinout images not read.
- S5 allpinouts.org 1990-95 ECU (ap.txt): lists 2I as "Tachometer Output", 1O "Brake Switch", 2O "Mass Air Flow". Conflicts with S1 on 2I and with the vane-type fact; treated as low quality (no wire colours, appears generated).
- Repo: kb/interconnect.md (cur_mb8995 and ord_mb8993 harness tables), motherboards/1989-95/README.md, firmware/board/miata_board.cpp, miata_pins.h, rusEFI mazda_miata_1_6.cpp, fan_control.cpp:264-266, scripts/design.py:204 (D8).
- Not obtainable: Miata.net ECU Pin-Out 90-93 MT.pdf (Cloudflare block), Scribd copy, Link/Haltech/ECUMaster pinouts (not found in budget), the 1991 engine FSM (mechanical pages only).

## Chain table (cur_mb8995 harness J1; ord_mb8993 differences in the last column)
Chain: cavity -> MB net (+parts) -> JD socket pin (same number on daughterboard J1/J2) -> db conditioning -> MCU pin -> firmware. Colours/functions from S1 unless stated. Verdict relates to cars read (1991).

| Cav | FSM colour / function (S1) | MB net and parts | JD pin | MCU / firmware (NA6 preset) | Verdict | ord_mb8993 diff |
|---|---|---|---|---|---|---|
| 1A | BLU-RED room fuse, hot at all times | none | - | - | unconnected-by-design: ECU keep-alive memory not needed (rusEFI stores in flash); ECU is off with key off, as stock main-relay supply | same |
| 1B | WHT-RED main relay output (key switched) | VBAT_IN (D1,D2,F1,F4,R20-22,R37 anodes/pull-ups) | JD1.1,2 | power rail | correct | same (no R37) |
| 1C | VIO "ST SIGN FUSE" = starter signal | VIGN_IN | JD1.3 | AN_VIGN PA2; D8 ORs it onto +12V_IN (design.py:204, INFERRED polarity); ign sense unassigned | correct (live only while cranking) | same |
| 1D | (no ECU wire label read; diag conn WHT-GRN goes here) | none | - | - | unconnected: diagnosis connector line | same |
| 1E | YEL-BLK check engine lamp | OUT_CEL | JD1.10 | Q13 low side, PE4, malfunctionIndicatorPin | correct (low-side sink, lamp fed from cluster) | same |
| 1F | WHT-YEL (diag connector) | none | - | - | unconnected: diagnosis connector | same |
| 1G | BRN-YEL igniter 1&4 signal (rusEFI: 5 V logic out) | OUT_IGN1 | JD1.14 | IGN1 PE1 -> level shifter; ignitionPins[0] | correct | same |
| 1H | BRN igniter 2&3 | OUT_IGN2 | JD1.15 | IGN2 PE0; ignitionPins[2] | correct | same |
| 1I | none | none | - | - | correct | same |
| 1J | BLU-BLK A/C relay (ECU sinks) | OUT_AC | JD1.8 | Q11, PE6 acRelayPin | correct | same |
| 1K | LT GRN-YEL diag connector TEN (S2) | none | - | - | unconnected: self-test unusable | same |
| 1L | NO wire | OUT_FAN | JD1.9 | Q12 PE5, fanPin | cavity empty: output goes nowhere on 1990-91 | same |
| 1M | NO wire | IN_SW1 (R20 pull-up not fitted) | JD2.15 | PE9 VSS | cavity empty: no speed signal | same |
| 1N | RED throttle idle contact (M/T switch and A/T sensor), closes to ground at idle | HARN_1N, R28 (0R not fitted) to V5_EXT | - | none | correct; never fit R28 on A/T or with stock switch | same |
| 1O | GRN stop lamp switch | none | - | - | unconnected: no brake input (A/T idle-up / not needed on M/T) | same |
| 1P | BLU-YEL power-steering pressure switch | none | - | - | unconnected: no PS idle-up | same |
| 1Q | LT GRN-BLK A/C thermo switch (A/C request) | IN_SW2 (R21 pull-up not fitted) | JD2.16 | PE10 acSwitch | pin function correct; polarity (12 V or ground when requested) CANNOT VERIFY | same |
| 1R | BLK-GRN cooling fan relay (ground-switched coil, also to diag connector); rusEFI calls it "A/C extra cooling fan relay" | HARN_1R -> JP3.1 (90-93 position) -> OUT_LS7 | JD1.12 | Q15 PE2 fan2Pin | correct; this is THE fan output on 1989-93 | OUT_LS7 direct |
| 1S | BLU-ORG heater control unit | none | - | - | unconnected: no blower idle-up | same |
| 1T | none | none | - | - | correct | same |
| 1U | RED-BLK, destination not traced | none | - | - | cannot verify | same |
| 1V | M/T BRN-WHT clutch switch (to ground) + cruise unit; A/T BLK-BLU ign switch | IN_SW3 (R22 not fitted) | JD2.17 | PE11 clutchDownPin | pin correct for M/T; A/T reads constant 12 V (see finding) | same |
| 2A-2D | BLK, BLK, BLK-LT GRN, BLK-LT GRN (power / sensor grounds) | GND | JD1.4.. | - | correct (power and signal ground tied on board, fine) | same |
| 2E | WHT crank angle #1 (CAS SGT, open collector; CAS Vcc is WHT-RED = main relay 12 V) | IN_HALL1 | JD2.13 | PE7 | correct | same |
| 2F | NO wire (S3: "additional signal ground, not populated on stock") | GND | - | - | harmless; README label "AFM ground" wrong (AFM ground is BLK-LT GRN on 2C/2D) | same |
| 2G | YEL-BLU crank angle #2 (SGC) | IN_HALL2 | JD2.14 | PE8 | correct | same |
| 2H | RED-WHT, destination not traced | none | - | - | cannot verify | same |
| 2I | BLK-WHT FROM igniter terminal E (input to ECU); tach fed from igniter D | HARN_2I -> JP5 (open); R37 1k pull-up to VBAT on OUT_TACH side | JD1.11 via JP5 | PE3 tachOutputPin Unassigned by miataNoTachOutput | correct | OUT_TACH wired straight to 2I, no jumper |
| 2K | LT GRN-RED 5 V reference to AFM and TPS | V5_EXT | JD1.13 | protected 5 V | correct | same |
| 2L | LT GRN-WHT M/T throttle switch other contact (full throttle) | HARN_2L; R29 0R fitted -> AUX1, R30 not fitted | JD2.9 | PC5 | correct | same |
| 2M | RED-BLK TPS signal (A/T only) | IN_TPS | JD2.4 | PA4 tps1 | correct | same |
| 2N | RED-BLU oxygen sensor (narrowband) | IN_AUX2 | JD2.10 | PB0 | correct | same |
| 2O | RED vane airflow signal (AFM terminal F) | HARN_2O -> JP6 (AFM) -> IN_AUX3 | JD2.11 | PB1 mafAdcChannel; NA6 map is MAP-based so unused | correct | IN_AUX3 direct |
| 2P | RED-GRN intake air temp (AFM terminal G) | IN_IAT | JD2.7 | PA7, 2.7k pull-up | correct | via JP1 IAT SEL (shunt must be on STOCK) |
| 2Q | BLU-WHT coolant temp | IN_CLT | JD2.6 | PA6 | correct | same |
| 2R, 2S, 2T | NO wire | HARN_2R/JP4, HARN_2S/JP3.3, OUT_FP (2T) | JD1.6 for 2T | PC14 fuelPumpPin | 2R/2S correct (empty); 2T empty: see finding on fuel pump | 2T same |
| 2U | YEL injectors 1 and 3 | OUT_INJ1 (D3 clamp, JP2.1) | JD1.19 | PB7 slot1, batch | correct | + R23 0R paralleling INJ4 |
| 2V | YEL-BLK injectors 2 and 4 | OUT_INJ2 (D4, JP1.1) | JD1.22 | PB6 slot2 | correct | + R24 0R paralleling INJ3 |
| 2W | BLU-ORG idle speed control solenoid, 12 V feed WHT-RED | OUT_IACV, D1 SS34 to VBAT_IN | JD1.31 | PB3 idle.solenoidPin | correct low-side; stock frequency CANNOT VERIFY (rusEFI default 300 Hz per generated header) | same |
| 2X | YEL-RED purge solenoid, 12 V feed WHT-RED (rusEFI says White/Blue, colour differs from FSM) | OUT_VVT, D2 to VBAT_IN | JD1.34 | PD7 vvtPins Unassigned | wiring correct; never driven | same |
| 2Y | NO wire | HARN_2Y via JP1.3 SEQ | - | - | correct (empty) | R25 not fitted |
| 2Z | LT GRN to A/T control unit | HARN_2Z via JP2.3 SEQ | - | - | correct; unconnected on default | R26 not fitted |

## Functional view (1989-93)
- Power and wake: 1B is the key-switched main-relay supply (S1: main relay WHT-RED output, relay coil from ignition switch BLU). ECU is on with key on, off with key off. 1C is the starter signal only, also ORed onto the rail by D8 (rusEFI treats it as no ignition sense: correct). 1A hot supply unused. Nothing keeps the ECU alive after key-off (same as stock, no after-run fan).
- Fuel pump: see finding 1. Stock = AFM contact + circuit-opening relay + starter signal, ECU not involved. The rusEFI prime pulse is irrelevant on these cars.
- Fan: stock ECU only grounds the cooling-fan relay on 1R (A/C); the coolant thermoswitch still runs the relay by itself (S2, S4), so no fan is lost if the thermoswitch is kept. ECU fan2 (1R) defaults are 95 C on (fan_control.cpp:264-266, INFERRED to be the default set), thermoswitch 97 C per S2. The firmware's "fan 1" on 1L drives nothing.
- A/C: 1J relay output fine; request input 1Q needs a polarity check on the car. A/C idle-up/compressor cut depends on that input.
- Idle valve: low-side, valve +12 V from main relay (S1), freewheel diode on board. Duty polarity and frequency unverified against stock.
- Tach: stock igniter drives it; ECU does nothing; nothing lost. CEL: lamp output ok; self-diagnosis connector (TEN 1K, 1D, 1F) not connected.
- Throttle: M/T has idle contact (1N RED) and full-throttle contact (2L LT GRN-WHT); A/T sensor also has the idle contact on 1N plus 5 V (2K), signal 2M. Board assumptions in README confirmed by S1.
- Injectors: two per wire confirmed (2U YEL = 1&3, 2V YEL-BLK = 2&4, supply WHT-RED). 1993 California sequential variation: only S4 says so; wire assignment on 2Y/2Z NOT verified.
- Charging: not ECU-controlled on these cars (no alternator wire in S1 CONN#1/#2). Auto trans: only 2Z (LT GRN) and, on A/T, 2M and 1V/BLK-BLU; board leaves 2Z open by default.
- Purge/EGR: purge valve never driven; no EGR at the ECU.

## Not checked
1989, 1990, 1992, 1993 factory diagrams (only 1991 read; California differences unread); 1U, 2H wire destinations; polarity of 1Q; stock ISC frequency; Link/Haltech/ECUMaster pinouts; whether ZXMS6004FF off-state leakage on 2I matters (datasheet not read for this task).
