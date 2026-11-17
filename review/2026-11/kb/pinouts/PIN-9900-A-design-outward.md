# PIN-9900-A (design outward): 1999-2000 NB1 (BP-4W) pinout chain audit, boards cur_mb9900 / ord_mb9900

## Summary (10 lines)
1. Chain walked for all 64 car cavities: cavity -> motherboard net -> JD1/JD2 pin -> daughterboard net/conditioning -> MCU pin -> firmware. Net routing is identical in cur and ord boards except IAT (ord has JP1; cur is direct) and the AUX header (ord 2x8, no FLEX/N2O/D5; cur 2x10).
2. Every driven/sensed cavity (1B 1E 1I 1O 1P 1R 1S 1U 2B 2C 2D 2E 2F 2H 2I 2J 2K 2L 3A-C 3E 3F 3G 3H 3I 3J 3M 3N 3O 3Q 3W-3Z) agrees with at least 3 secondary sources (rusEFI wiki, Hellen NB1 yaml and PCB, DIY/AMP MSPNP Pro 9900 table, Alex Engineering NB manual). Haltech's NB1 page independently confirms the sensor-side facts (CKP/CMP 3-wire Hall fed 12 V switched, IAC valve pin1 = signal, pin2 = 12 V switched, alternator two wires P feedback / D duty, VICS energised below about 5200 rpm).
3. No primary Mazda FSM text for 1999/2000 was obtainable (wiring PDFs are image-only, no OCR tool here), so no cavity is "verified" against Mazda itself; all verdicts are "correct (secondary sources agree)".
4. IAC polarity checked: the rusEFI wiki 1999 page lists 3M = IAC power and 3O = IAC control; Hellen, MSPNP Pro, Alex and Haltech's valve description all say 3M = control (low side) and 3O = +12 V. The repo follows the majority. This matters (wrong way round would short a +12 V wire to ground through the driver); I could not find a Mazda document, so confidence is medium-high, not certain.
5. Cavity geometry of the 76-position header footprint matches Hellen's own 178780-1 footprint (pad X pitches identical, incl. the 5.7 mm gap before plug 2, and the cavity-letter -> position assignment checked at 20 cavities against Hellen's PCB). Checked, correct.
6. Functional gaps that the driver will notice: (a) charge lamp 1Q never driven and alternator loop 1O/1T open; (b) A/C condenser fan 1I is not commanded with A/C (fan2AcMode never set; default Disabled); (c) VICS 3Q never driven (no strategy); (d) no scan-tool diagnostics (1D/1L, 1K/1N open); (e) purge/EGR/CDCV/rear heater not driven (emissions only).
7. Power: ECU wakes when the key-switched main relay powers 1B; there is no ECU-held relay on NB1, so shut-off is instantaneous at key-off. VIGN_IN (JD1.3) is unconnected on this board and not used by the NB1 preset. 1A (battery keep-alive) open: only loses stock keep-alive memory, harmless for rusEFI.
8. Ordered board: default JP1 shunt is on EXT (J3 connector), so the stock air-temperature sensor on 2B is not read unless the shunt is moved to 1-2.
9. Everything the firmware assigns for NB1 matches the netlist (pin-by-pin table below).
10. Not done: Mazda FSM 1999/2000 primary check; wire colours (sources give almost none for NB1); ECUMaster/Link pinout (429 / not reachable).

## 1. Chain table (cur_mb9900 and ord_mb9900; harness cavities of the 64-position car plugs)
Notation: net = motherboard net; JD = daughterboard socket pin (same number on both boards, J1/J2 on the daughterboard); cond = conditioning on cur_db (from evidence/cur_db/pcb_nets.txt via work/.../chain.py); MCU = firmware pin (repo/firmware/board/miata_pins.h). Verdict: OK = correct per secondary sources; NC = unconnected by design.

| Cavity | Stock function (sources) | MB net / parts | JD | Daughterboard conditioning | MCU / firmware NB1 | Verdict |
|---|---|---|---|---|---|---|
| 1A | +12 V battery keep-alive (wiki: BLU/RED hot at all times; Hellen 12V all times; MSPNP N/C) | none | - | - | - | NC. Stock keep-alive memory lost, nothing else. Harmless for rusEFI |
| 1B | +12 V from main relay (WHT/RED, wiki) | VBAT_IN; F1 (LSU heater PTC), F2 (IAC), F4 (AUX), R20-22 (DNP pull-ups) | JD1.1,1.2 | D7/F1 reverse-protection, ECU supply | VBAT ADC PA1 | OK |
| 1C 1D 1F 1G 1H 1J 1K 1L 1M 1N 1V | N/C / DLC (1D,1L) / TCM (1K,1N) / brake 1F, PS 1G, neutral 1V (Hellen only) / 1H "12 V inj 30 A"? | none | - | - | - | NC. Consequence: no scan-tool link, no PS-idle-up, no brake/neutral inputs (see section 3) |
| 1E | MIL, low side (wiki output/low) | OUT_CEL | JD1.10 | Q13 ZXMS6004FF low side | PE4 malfunctionIndicatorPin | OK |
| 1I | A/C (condenser) fan relay (wiki "A/C fan", Hellen 1I AC Fan Relay, MSPNP Fan2/A/C relay, Alex FAN2 (AC)) | OUT_LS7 | JD1.12 | Q15 | PE2 fan2Pin; fan2AcMode never set (default Disabled) -> on only above 95 C | Wiring OK; firmware gap (finding) |
| 1O | Alternator field/duty (wiki "alternator field"; Haltech: D = duty from ECU, Grey/Red, active High) | OUT_ALT, also J5.4 | JD1.40 | Q8 VND7NV04 low side | PD5 alternatorControlPin; control disabled by default | OK but open-collector vs Haltech's driven-high output; repo documents the pull-up question |
| 1P | A/C switch in (wiki "A/C system"; Hellen "A/C pressure in") | IN_SW2; R21 4.7k to 12 V (DNP) | JD2.16 | R67 22k/R68 10k, C54, D28 | PE10 acSwitch | Wiring OK; signal polarity/level NOT given by any source: cannot verify |
| 1Q | Charge (battery) warning lamp, low side (wiki "low battery light"; Hellen; MSPNP Charge Lamp; Alex Batt low lamp) | none | - | - | no function | NC: lamp never driven (finding) |
| 1R | Radiator fan relay low side | OUT_FAN | JD1.9 | Q12 | PE5 fanPin, fan1AcMode Relay, on 92 C / off 88 C (rusEFI default) | OK |
| 1S | A/C compressor relay low side | OUT_AC | JD1.8 | Q11 | PE6 acRelayPin | OK |
| 1T | Alternator sense (generator terminal P: Haltech "feedback volts to ECU", Grey) | none | - | - | - | NC (finding with 1O/1Q) |
| 1U | Front HO2S heater low side (Hellen; MSPNP Pro grounds it; wiki blank) | OUT_VVT | JD1.34 | Q6 VND7NV04 | PD7 -> o2heaterPin | OK |
| 2A | Fuel tank pressure sensor | none | - | - | - | NC, EVAP monitoring absent |
| 2B | IAT (thermistor, in air filter box) | cur: IN_IAT; ord: HARN_IAT -> JP1.1 | JD2.7 | R36 2.7k to V5_EXT, R34 5.6k/R35 10k, C39 | ADC PA7 | OK; ord: JP1 default EXT, must be 1-2 (finding) |
| 2C | Front HO2S signal | IN_AUX2 | JD2.10 | 5.6k/10k, BAT54 clamp | PB0 AUX2, not used for control | OK (raw ADC only) |
| 2D | Vehicle speed sensor | IN_SW1; R20 DNP | JD2.15 | R65 22k/R66 10k, C53, D27 | PE9 vehicleSpeedSensorInputPin | OK (signal type 12 V vs open collector not verified; DNP pull-up option exists) |
| 2E | CLT thermistor | IN_CLT | JD2.6 | R33 2.7k to V5_EXT, 5.6k/10k | PA6 | OK |
| 2F | Knock sensor (piezo) | IN_KNOCK, J5.6 | JD2.3 | R138 2.2k -> KN_IN -> amp (KN_BIAS) | PA3, enableSoftwareKnock | OK; 2F is also on J5.6 (second tap on the same net, fine) |
| 2H | Cam sensor CMP, 3-wire Hall fed 12 V | IN_HALL2 | JD2.14 | R64 1k to V5_H2 (5 V via BAT54A), R63 4.7k, C52 1n, D14 | PE8 camInputs[0] | OK |
| 2I | +5 V sensor reference out | V5_EXT, J5.14 | JD1.13 | protected TLS115 regulator | - | OK |
| 2J | Crank sensor CKP, 3-wire Hall fed 12 V | IN_HALL1 | JD2.13 | R62 1k to V5_H1, R61 4.7k, C51 | PE7 triggerInputPins[0], TT_MIATA_VVT | OK |
| 2K | Tach out (wiki, Hellen, MSPNP Pro Tach Out; Alex calls 2K "stock unused pin") | OUT_TACH | JD1.11 | Q14 | PE3 tachOutputPin, 2 pulses/rev | Likely OK; Alex dissent, cannot resolve (repo documents) |
| 2L | MAF signal | IN_AUX3 | JD2.11 | 5.6k/10k | PB1 mafAdcChannel (not used in the speed-density preset) | OK |
| 2M-2P | EGR stepper coils (Hellen test pads, Alex uses 2O/2P as spare ignition outputs) | none | - | - | - | NC; EGR valve stays closed |
| 3A 3B 3C | Power grounds | GND | JD1.4/5 etc. | - | - | OK |
| 3D | N/C (Hellen: ext MAP; Alex: WMI/NITRO) | none | - | - | - | NC |
| 3E | TPS | IN_TPS | JD2.4 | 5.6k/10k, C36 | PA4 | OK |
| 3F | Sensor ground | GND (not separate) | - | - | - | OK (Hellen does the same) |
| 3G 3H | Igniter 1&4 / 2&3 (coil packs with built-in igniters, 5 V logic) | OUT_IGN1/2 | JD1.14/15 | TC4427 5 V push-pull via 100R + Schottky, ZXMS pull-down | PE1/PE0 | OK |
| 3I | Clutch switch (MT) | IN_SW3 | JD2.17 | 22k/10k | PE11 clutchDownPin | OK |
| 3J | Rear HO2S signal | IN_AUX1 | JD2.9 | 5.6k/10k | PC5, unused | OK |
| 3K | N/C (wiki: fuel gauge) | none | - | - | - | NC |
| 3L | Purge solenoid | none | - | - | - | NC: canister never purged |
| 3M | IAC valve control, low side | OUT_IACV, D1 SS34 | JD1.31 | Q5 VND7NV04 | PB3 idle.solenoidPin, default solenoid frequency 300 Hz (rusEFI) | OK (wiki swaps 3M/3O; see summary 4) |
| 3N | Fuel pump relay low side (US) | OUT_FP | JD1.6 | Q9 | PC14 fuelPumpPin | OK |
| 3O | IAC +12 V (wiki ORG; MSPNP "+12 V ignition") | IAC_12V via F2 2 A to VBAT_IN; D1 | - | - | - | OK; board feeds this wire from 1B, paralleling the harness source if there is one |
| 3P | Fuel pump relay, European/immobiliser cars | none | - | - | - | NC: EU cars would not run (repo documents no immobiliser) |
| 3Q | VICS solenoid low side | OUT_MAINRLY, J5.5 | JD1.7 | Q10 | PC13, mainRelayPin Unassigned on NB1: never driven | wiring OK; function missing |
| 3R-3V | N/C, EGR boost sensor 3S, 3T solenoid, CDCV 3U, rear heater 3V | none | - | - | - | NC |
| 3W-3Z | Injectors 1-4 low side | OUT_INJ1-4 | JD1.19/22/25/28 | VND7NV04 + ES1D/1.5SMC16A clamp | PB7/6/5/4 sequential | OK |
| XA-XL (cur, 76P only) | not in car | none | - | - | - | NC, by design |

## 2. External evidence used
- rusEFI wiki Mazda-Miata-1999 (curl, work/.../Mazda-Miata-1999.md): lists 1Q "low battery light", 1I "A/C fan", 1O "alternator field", 1E "check engine", 3N fuel pump, 3Q VICS; 3M "IAC power" and 3O "IAC control" (swapped relative to all others); colours only 1A BLU/RED, 1B WHT/RED, 3H BRN, 3M ORG.
- MSPNP Pro MM9900 (megasquirtpnp.com mspnp_gP_mm9900.php; their numbering plug 3 = OEM 2, plug 4 = OEM 3): 1B +12 V ignition, 1E CEL, 1I A/C relay, 1O alternator field coil (PWM), 1P A/C switch in, 1Q charge lamp, 1R fan 1 relay, 1S A/C relay, 1T alternator sense, 1U ground (heater), OEM 2B IAT, 2C front O2, 2D VSS, 2E CLT, 2F knock, 2H CMP, 2I +5 Vref, 2J CKP, 2K tach out, 3E TPS, 3F sensor gnd, 3G/3H coils, 3I clutch, 3J rear O2, 3M IAC (PWM1), 3N fuel pump USA, 3O +12 V ignition, 3P fuel pump Europe, 3Q VICS, 3V O2 heater ground, 3W-3Z injectors.
- Alex Engineering NB manual (pdftotext): IACV 3M, CKP 2J, CMP 2H, injectors 3W-3Z, IGN 3G/3H, FAN 1R, FAN2(AC) 1I, fuel pump 3P/3N, purge 3L, tach 2K "stock unused pin", VICS 3Q, battery lamp 1Q, MIL 1E, PSP 1G, AC input 1P, AC solenoid 1S, clutch 3I, VSS 2D, o2 heater 1U.
- Haltech support page "99-00 NB1 1.8L BP-4W": CKP and CMP A = 12 V switched (red), B = trigger (yellow), C = signal ground (blue); IAC valve pin 1 open/signal, pin 2 power 12 V switched; alternator P (grey) feedback to ECU, D (grey/red) duty from ECU; VICS energised below about 5200 rpm; IAT/CLT need 1k pull-up.
- AMP EFI MM9900 install pages: fuel pump jumper "Europe w/ immobiliser" confirms 3P/3N split.
- Hellen NB1 (ext/hellen-miata-NB1 PCB + repo/firmware/ext/.../hellenMiataNB1/connectors/main.yaml): 1I AC Fan Relay, 1Q Alternator Warning Lamp, 1R ECF, 3M OUT_IDLE ("IAC negative, with diode"), 3O +12 V, 3Q VICS.
- Not independent of each other: Hellen sheet, MSPNP and Alex all trace to the same owners; the Haltech page is the one clearly independent source, and it only covers sensor-side wiring.
- Forum (UNVERIFIED): a miataturbo thread reports a 1999 NB with an open in "the two alternator signal wires to the ECU" showing battery light and no charging (no resolution). No FSM text.

## 3. Functional view (what the stock ECU did, what this board does)
- Power/wake: key on -> key-switched main relay -> 1B -> VBAT_IN -> F1/F2/F4 branches + daughterboard regulators. ECU is "awake" only while the key is on (no ECU-held relay, no IG sense; VIGN_IN not routed). Shut-off: key off drops 1B; engine stops injecting immediately, pump relay releases, rusEFI has no time to write data (it does not do so anyway).
- Fuel pump: 3N low side (US); rusEFI primes at power-up (default prime time) and runs while cranking/running. EU 3P not wired.
- Fans: radiator fan 1R on at 92 C / off 88 C, on with A/C (fan1AcMode Relay). Condenser fan 1I: only above 95 C (fan2OnTemperature default) because fan2AcMode is Disabled; A/C on at idle in traffic: condenser fan not forced on by the ECU.
- A/C: request 1P -> SW2 (12 V input, no pull-up fitted; polarity unknown), compressor 1S low side. No A/C pressure/compressor protection logic in the ECU path other than rusEFI's own cutoffs.
- Idle valve: 3M low side, 300 Hz default (stock frequency unknown), flyback D1 to 3O supply (F2 2 A PTC), 3O powered through F2 from battery rail.
- Tach: 2K via ZXMS6004 low side, 2 pulses/rev; cluster-side level unknown (sources do not give it).
- MIL: 1E low side; the CEL lamp lights during fatal firmware error (rev 0.10 only).
- Charging: stock ECU monitored alternator (1T) and drove the lamp (1Q) and a duty signal (1O). Here 1Q, 1T are open; 1O is open-collector and the alternator control ships OFF. Lamp is dead; whether the alternator charges normally with 1O/1T open is not verified (one forum report suggests trouble when the ECU signals are open).
- VICS: stock energises the solenoid below about 5200 rpm (Haltech); here never driven.
- Not done by this board: EGR, purge, CDCV, rear HO2S heater and monitoring, EVAP pressure, OBD-II/DLC (1D/1L, K-line), TCM link (1K/1N, A/T), brake/neutral/PS switches (Hellen lists 1F/1G/1V as inputs; unconnected here: no PS idle-up), immobiliser/EU pump path. Front HO2S heater is driven but sensor is not used for closed loop (wideband on board).
- Coil packs with built-in igniters: 3G/3H 5 V logic: OK per all sources. Knock: single piezo 2F into the on-board amp. Crank/cam: Hall sensors fed 12 V from the car's main relay (not by the ECU), so no sensor supply needed from the board.

## 4. Connector: car = three plugs, 64 positions (22+16+26); cur board = TE 178780-1 76 positions (22+12+16+26), ord board = TE 176122-6 64 positions
- cur: 12 extra positions XA-XL between plug 1 and 2, unconnected, no plug in the car. VERIFIED footprint geometry equals Hellen P2 (178780-1) footprint: 42 distinct X columns, identical pitches (3.0/3.1/3.5 mm, 5.7 mm gap at plug 2, 2.85 mm and 3.1 mm steps), and the letter -> position map (1A-1U, 2B, 2K, 3A-3Z checked at 20 cavities) matches Hellen's netlist. Headers' availability is covered elsewhere.
- ord: 64P footprint; plug gaps 5.95 mm; I did not verify against a TE drawing.

## 5. Findings summary (see structured output)
1. Charge lamp 1Q dead and 1T/1O loop open.
2. fan2 (1I A/C condenser fan) not tied to A/C in firmware.
3. VICS 3Q never driven.
4. Ord board JP1 default EXT leaves stock IAT unread.
5. 1P A/C input polarity unknown / no pull-up.
6. Diagnostics/EVAP/EGR/purge gaps (emissions, scan tool).
7. IAC 3M/3O: checked, wiki is the outlier.
8. 76P footprint matches Hellen: checked.
9. IAC frequency default 300 Hz vs stock unknown.

## Sources actually read
kb/interconnect.md (cur_mb9900 and ord_mb9900 sections), repo/motherboards/1999-2000/README.md, repo/ordered-boards/2026-11/motherboards/1999-2000/README.md, repo/research/pinouts_9605.md (NB1 section), repo/firmware/board/{miata_pins.h,miata_board.cpp,board_configuration.cpp,connectors/daughterboard.yaml}, rusEFI fan_control.cpp (defaults), hellenMiataNB1 yaml/board_configuration.cpp, ext/hellen-miata-NB1 PCB (P2 footprint), evidence/cur_db/pcb_nets.txt + footprints (chain.py), wiki Mazda-Miata-1999, MSPNP Pro 9900 page, Alex Engineering NB PDF, AMP EFI 9900 pages, Haltech support article, miataturbo / msextra threads (via page fetch, unverified).

## Not checked
Mazda FSM/wiring diagram 1999-2000 (image-only, no OCR); wire colours for NB1 (sources give almost none); ECUMaster and Link pinout documents (ECUMaster page rate limited, Link not searched); stock idle valve frequency; stock fan switching temperatures; 1P/2D/2K signal levels; ordered 64P footprint against a TE drawing; daughterboard rev 0.9 differences beyond the netlist.
