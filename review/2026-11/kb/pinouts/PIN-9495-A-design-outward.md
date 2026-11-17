# PIN-9495-A design-outward: 1994-95 (NA8 1.8 L, 48-pin) pinout chain audit

Boards: cur_mb8995 (rev 0.13, 94-95 jumpers: JP1/JP2 SEQ, JP3 94-95, JP4 fitted, JP5 open, JP6 AFM, no JP for IAT) and ord_mb9495 (rev 0.9, fixed wiring).
Status: COMPLETE in this pass (see Not checked).

## Summary
1. PRIMARY SOURCE obtained and read: 1994 Mitchell/Mazda "System Wiring Diagrams", Fig. 8 "1.8L Engine Performance" (mellens.net/mazda/Mazda-Miata-1994/wiring.pdf, PDF page 16 = ECU connector with all 1A..2Z wire colours and destinations; page 18 = sensors/actuators; page 10 = cooling fan; page 2 = A/C; page 12 = cruise). 1995 Mitchell diagram (miataforumz 95sys.pdf p.8) read for the 1995 differences. Crops in work/PIN-9495-A-design-outward/ (b1,b2,b3,ign94,inj94,top94,bot94,c95a,c95b).
2. The pin MAP of both boards agrees with the factory diagram for every populated function the board drives: 1E CEL, 1G/1H igniters, 1J A/C relay, 1L radiator fan relay, 1M VSS, 1Q A/C request, 1V clutch, 2E/2G CAS, 2K 5 V ref, 2M TPS, 2N O2, 2O airflow, 2P IAT, 2Q CLT, 2R PRC solenoid, 2S condenser fan relay, 2T fuel pump relay, 2U/2V/2Y/2Z injectors #1/#2/#3/#4, 2W idle valve, 2X purge. No wrong pin found.
3. The premise "hot-wire MAF" is NOT supported: FSM calls it "Airflow Meter" (code 8, terminals E=BLK/LT GRN, B=RED; IAT terminals C=BLK/BLU, D=RED/BLK) and Mitchell's diagram titles the box "Mass airflow sensor", but its 5 wires (12 V WHT/RED, signal RED, IAT RED/BLK, 2 grounds) carry no fuel-pump contact. Type (vane vs hot wire) is not stated by these sources; the repo and rusEFI treat it as a VAF-type analog input (UNVERIFIED). The firmware preset is speed-density (MAP) so the signal is unused anyway.
4. Fuel pump: on 1994-95 the ECU DOES switch the pump relay: 2T LT GRN goes to the coil of the fuel pump relay (VERIFIED, FSM p.16 and 95 p.8). This is different from 1990-93 (see PIN-8993). Board OUT_FP -> 2T and firmware fuelPumpPin are correct; prime default 4 s (rusEFI default_base_engine.cpp:570, board does not override).
5. Fan: on 1994-95 the ECU is the ONLY control of the radiator fan: relay coil is fed from ENGINE fuse (BLK/WHT) and grounded by ECU 1L (BLK/GRN) (FSM p.10, no thermoswitch in the circuit). Board 1L OUT_FAN is correct. Condenser fan relay (BLU/WHT) on 2S, ECU-switched, fed BLK/WHT; board JP3(94-95)/OUT_LS7 correct. If the ECU does not command the fan, the car overheats in traffic: the firmware preset (rusEFI NA94) sets fan1 (1L) ON 100 / OFF 96 C and fan2 (2S) ON 95 / OFF 91 C, fan AC mode = relay. Stock thresholds NOT found (cannot verify); radiator fan at 100 C is a late value for a single-fan car.
6. 2I (BLK/WHT) tach: the igniters' BLK/WHT terminals are joined, go to the instrument cluster tach AND to ECU 2I (FSM p.16). So 2I is an input to the ECU / signal from the igniters, not an ECU output. The microRusEFI wiki says the stock ECU supplies a pull-up to 5 V on this wire ("2I tach pullup: Y with stock coils", "ECU provides only a pull-up"). Both boards leave 2I with NO pull-up in stock configuration (cur: JP5 open, R37 pull-up is on the far side of JP5; ord: OUT_TACH hard-wired to a ZXMS6004FF drain, no R37). If the igniter output is open-collector, the cluster tach would not work. CANNOT VERIFY from the FSM (igniter internal drawing shows the BLK/WHT terminal on the coil-primary / output-transistor node). Ordered board cannot be changed without rework.
7. Unconnected by design with consequence: EGR vent solenoid 1R (YEL/BLK, 95: YEL) and EGR vacuum solenoid 1T (YEL/RED) and EGR function sensor 2J (LT GRN/RED): no EGR ever (US 1994-95 all have it): emissions/knock margin only. DLC lines 1D, 2H, 1K (BLK/LT GRN in 95): no self-diagnosis. 1P power-steering pressure switch (BLU/YEL), 1S heater control unit (BLU/ORG), 2L rear defroster (BLU/RED, goes to the AUX1 input but firmware does nothing with it): no idle-up. 1O stop lamp. A/T lines 1I/1N/1V.
8. PRC solenoid 2R: wired to OUT_ALT, but the NA94 preset leaves alternatorControlPin unassigned (miata_board.cpp setOutputs) so it is never energised. Stock use (Mazda PRC = fuel-pressure-regulator control, hot-restart vapour-lock aid; INFERRED) is lost; normal running not affected.
9. Charging is not ECU-controlled on 1994-95: generator (voltage regulator) is fed WHT/GRN from the main relay and no ECU pin (FSM 94 charging not read; 95 p.8 shows WHT/GRN to GENERATOR from the main relay). OUT_ALT on 2R is therefore NOT an alternator driver in this car.

## Chain table (both boards). Colours/function: FSM 1994 p.16/18 (S1) unless stated; 95 differences from S2.
Chain: cavity -> MB net (parts) -> JD pin (same number on db J1/J2) -> db conditioning -> MCU pin -> firmware (NA94 preset). cur / ord differ where stated.

| Cav | FSM colour, function, electrical character | MB net and parts (cur; ord) | JD pin | MCU/firmware | Verdict |
|---|---|---|---|---|---|
| 1A | BLU/RED hot at all times (room fuse), memory feed | none; none | - | - | unconnected-by-design: keep-alive not needed (flash tune); stock ECU also dead-times nothing important |
| 1B | WHT/RED main relay output, 12 V key-run; also feeds solenoids/injectors/pump relay coil | VBAT_IN (D1,D2,F1,F4,R20-22,R37; ord same w/o R37) | JD1.1,2 | supply rail | correct. Main relay is switched by the ignition (coil BLK/WHT from ENGINE fuse, BLK to ground; 95 p.8), not by the ECU: ECU powered only in RUN/START |
| 1C | VIO START signal from ST SIGN fuse, 12 V only while cranking | VIGN_IN | JD1.3 | AN_VIGN PA2, ignKey sense unassigned | correct (not used as ignition sense, firmware comment confirms) |
| 1D | WHT/GRN data link connector | none | - | - | unconnected: no diagnosis (consequence only for factory tester) |
| 1E | YEL/BLK check-engine lamp, ECU sinks (lamp fed from METER fuse) | OUT_CEL | JD1.10 | Q13 PE4, malfunctionIndicatorPin | correct |
| 1F | no wire (rusEFI wiki "extra analog input") | none | - | - | correct |
| 1G | BRN/YEL igniter #1&4 signal | OUT_IGN1 | JD1.14 | PE1 ignitionPins[0] | correct |
| 1H | BRN igniter #2&3 signal | OUT_IGN2 | JD1.15 | PE0 ignitionPins[2] | correct |
| 1I | BLU/WHT to A/T control module (95: "A/T only") | none | - | - | unconnected: A/T interaction lost (untested, INFERRED) |
| 1J | BLU/BLK A/C relay coil, ECU sinks (coil fed BLU, K35) | OUT_AC | JD1.8 | Q11 PE6 acRelayPin | correct |
| 1K | 94 BLK (M/T only, grounded jumper = M/T id); 95 BLK/LT GRN | none | - | - | unconnected: stock ECU transmission-type id lost, no effect on rusEFI |
| 1L | BLK/GRN radiator fan relay coil, ECU sinks, coil from ENGINE fuse; also DLC | OUT_FAN | JD1.9 | Q12 PE5 fanPin; fan ON100/OFF96 | correct; ECU is sole fan control |
| 1M | GRN/RED vehicle speed from cluster (2-terminal sensor to cluster ground) | IN_SW1 (R20 4.7k to VBAT NOT fitted) | JD2.15 | PE9 VSS | pin correct; passive 2-wire sensor needs a pull-up: MRE has "JP56 1M pullup VSS 94+ (untested)". Without R20 no speed signal (INFERRED, medium) |
| 1N | RED TPS idle contact (to ground at idle) and A/T control module | cur: HARN_1N, R28 0R to V5_EXT (not fitted); ord: none | - | - | correct as long as R28 stays unfitted (fitting puts 5 V on the TPS idle contact/A-T module) |
| 1O | GRN/BLK stop lamp switch (95 "M/T only" note) | none | - | - | unconnected: no brake input |
| 1P | BLU/YEL power-steering pressure switch | none | - | - | unconnected: no PS idle-up |
| 1Q | LT GRN/BLK A/C request: A/C switch -> thermo switch -> refrigerant pressure switch -> ECU, 12 V when compressor requested, open otherwise (FSM p.2, INFERRED polarity) | IN_SW2 (R21 not fitted) | JD2.16 | PE10 acSwitch | correct incl. polarity (R21 must stay unfitted) |
| 1R | 94 YEL/BLK, 95 YEL: EGR vent solenoid (12 V fed, ECU sinks) | cur: HARN_1R->JP3.1 (open on 94-95 position); ord: none | - | - | unconnected: EGR never operates. If cur JP3 left on 90-93, OUT_LS7 would drive EGR vent solenoid |
| 1S | BLU/ORG heater control unit (blower) signal | none | - | - | unconnected: no blower idle-up |
| 1T | YEL/RED EGR vacuum solenoid | none | - | - | unconnected: see 1R |
| 1U | RED/BLK, destination not found on the pages read | none | - | - | cannot verify |
| 1V | BRN/WHT clutch switch (M/T, to ground) and A/T module | IN_SW3 (R22 not fitted) | JD2.17 | PE11 clutchDownPin | pin correct for M/T; on A/T cars the line is not a clutch switch (clutchDownPin would misread) |
| 2A,2B | BLK power ground | GND | JD1/2 gnd | - | correct |
| 2C,2D | BLK/LT GRN, BLK/BLU logic/sensor ground (O2, AFM, CLT, EGR, TPS grounds are BLK/BLU) | GND | - | - | correct |
| 2E | WHT CAS SGT (rusEFI: crank #1, 4-pulse), CAS fed 12 V WHT/RED | IN_HALL1 | JD2.13 | PE7 | correct |
| 2F | BLK/RED AFM ground (via J/C to BLK/LT GRN) | GND | - | - | correct; README "AFM ground" label ok on 94-95 |
| 2G | YEL/BLU CAS SGC (FSM code 4 "SGC signal") | IN_HALL2 | JD2.14 | PE8 (primary trigger) | correct |
| 2H | LT GRN/YEL DLC | none | - | - | unconnected: see 1D |
| 2I | BLK/WHT igniter tach signal, shared with cluster tach | cur: HARN_2I->JP5 (open), R37 1k to VBAT on OUT_TACH side; ord: OUT_TACH direct, no R37 | JD1.11 | PE3 tachOutputPin = Unassigned (miataNoTachOutput) | direction right (input); pull-up missing: see finding |
| 2J | LT GRN/RED EGR function sensor signal | none | - | - | unconnected: no EGR |
| 2K | LT GRN/WHT 5 V reference to TPS and EGR sensor | V5_EXT (J5.14, R27, R28/R35 cur) | JD1.13 | protected 5 V | correct |
| 2L | BLU/RED rear defroster relay (12 V when on) -> idle-up input | cur: HARN_2L, R29 0R to AUX1 (R30 not fitted); ord: IN_AUX1 direct | JD2.9 | PC5 AUX1, no firmware function | correct pin; function unused (no idle-up) |
| 2M | RED/BLK TPS signal (TPS potentiometer, 5 V) | IN_TPS | JD2.4 | PA4 tps1 | correct |
| 2N | RED/BLU heated O2 narrowband signal; heater powered from METER fuse (BLK/YEL), not ECU | IN_AUX2 | JD2.10 | PB0 | correct |
| 2O | 94 RED, 95 RED/WHT airflow meter signal | cur: HARN_2O->JP6 (AFM)->IN_AUX3; ord: IN_AUX3 | JD2.11 | PB1 mafAdcChannel, unused | correct pin; AFM output range not verified (board scales 5.6k/10k: 5 V -> 3.2 V ADC) |
| 2P | RED/BLK intake air temp (in AFM, C=BLK/BLU ground) | cur: IN_IAT direct per interconnect? see note; ord: HARN_IAT->JP1.1, shunt 1-2 STOCK required | JD2.7 | PA7 2.7k pullup | correct; ord needs the JP1 shunt on STOCK (default EXT would leave 2P floating) |
| 2Q | BLU/WHT coolant temp | IN_CLT | JD2.6 | PA6 | correct |
| 2R | YEL/GRN PRC solenoid, +12 V WHT/RED, ECU sinks | cur: HARN_2R->JP4 (fit)->OUT_ALT; ord: OUT_ALT (+J5.4) | JD1.40 | PD5 alternatorControlPin Unassigned | wiring correct; never driven |
| 2S | BLU/WHT condenser fan relay coil, ECU sinks | cur: HARN_2S->JP3.3->OUT_LS7; ord: OUT_LS7 | JD1.12 | PE2 fan2Pin; fan2 ON95/OFF91 | correct |
| 2T | LT GRN fuel pump relay coil, ECU sinks | OUT_FP | JD1.6 | PC14 fuelPumpPin; 4 s prime | correct |
| 2U | YEL injector #1 (+12 WHT/RED) low side | OUT_INJ1 (cur D3 not fitted w/ db 0.10; ord none) | JD1.19 | PB7 slot 1 | correct |
| 2V | YEL/BLK injector #2 | OUT_INJ2 | JD1.22 | PB6 | correct |
| 2W | BLU/ORG idle air control valve, +12 V WHT/RED, ECU sinks PWM | OUT_IACV, D1 SS34 flyback | JD1.31 | PB3 solenoidPin, 300 Hz default | correct; stock PWM frequency and polarity cannot verify |
| 2X | YEL/RED purge solenoid, +12 V WHT/RED | OUT_VVT, D2 flyback | JD1.34 | PD7 vvtPins Unassigned | wiring correct; never driven (documented no-purge) |
| 2Y | GRN/WHT injector #3 | cur HARN_2Y via JP1 SEQ; ord OUT_INJ3 | JD1.25 | PB5 slot 3 | correct (cur: needs JP1 shunt on SEQ) |
| 2Z | GRN injector #4 | cur HARN_2Z via JP2 SEQ; ord OUT_INJ4 | JD1.28 | PB4 slot 4 | correct |

(cur 2P: interconnect.md cur_mb8995 shows 2P -> IN_IAT directly, no jumper; the ord board has JP1.)

## Functional view 1994-95
- Power/wake: 1B main-relay 12 V, relay switched by key RUN. ECU alive only with key on; 1C START only while cranking; 1A unused. Off with key. Same as stock apart from lost keep-alive memory.
- Fuel pump: ECU-controlled (2T). rusEFI prime 4 s then on while running/cranking; equals stock behaviour. No pump switch in AFM on these cars.
- Fans: radiator fan 1L and condenser fan 2S both ECU only. Preset ON thresholds above. Misconfigured/dead output = overheating risk; A/C: fan1 and fan2 AC mode Relay (fan runs with A/C request).
- A/C: request 12 V on 1Q (needs R21 unfitted), compressor relay sink on 1J; works if acSwitch/acRelay logic is enabled in the tune (pins preset).
- Idle valve: low-side PWM, valve +12 V from main relay, freewheel diode D1 on MB. Stock frequency/polarity unknown.
- Tach: stock igniters drive cluster tach; ECU no output (firmware). Pull-up question (finding).
- CEL: 1E sink, fine; no self-test.
- Charging: not ECU-related on 1994-95.
- Injectors: four wires, sequential preset; FSM injector numbering = cylinder numbers.
- EGR/purge/PRC: none driven; sensors/solenoids unconnected.
- Auto trans: 1I, 1N, 1V, (2Z not used on 94-95) carry A/T signals; unconnected/untested.
- 1994 vs 1995 (FSM): same cavities; wire colour changes 1K BLK -> BLK/LT GRN, 1R YEL/BLK -> YEL, 2O RED -> RED/WHT; 95 shows generator regulator supply WHT/GRN from main relay. Federal vs California: the pages read show no separate California diagram; EGR/purge present on the one diagram (CANNOT VERIFY differences, only one diagram per year read).

## Sources actually read
- S1 1994 Mitchell wiring PDF (https://www.mellens.net/mazda/Mazda-Miata-1994/wiring.pdf), pages 2, 10, 12, 16, 18. Also 1994 "tests_with_codes.pdf" text (terminal/wire tables for airflow meter, PRC, EGR vacuum/vent solenoids).
- S2 1995 Mitchell wiring PDF (https://www.miataforumz.com/1990-200-Miata-Wiring/95sys.pdf) p.8.
- S3 rusEFI wiki "Mazda Miata 1994" / "1995" (raw.githubusercontent.com/wiki/rusefi/rusefi/Mazda-Miata-1994.md). Agrees with S1 on every colour read (1L,1M,1O,1Q,2E-2Z) except it mislabels nothing found.
- S4 MRE wiki (work/PIN-8993-A-design-outward/mre.txt): tach pull-up, JP56 VSS pull-up.
- S5 hellen NA6-94 KiCad netlist (ext/hellen-miata-NA6/hellen64_NA6_94.xml): 3I (=2I) via jumper pad to a tach net with R27; 2S fan2 pin D9 ("A/C Fan 94-95") in rusEFI mazda_miata_1_6.cpp:288.
- Repo: kb/interconnect.md (cur_mb8995 lines 184-284, ord_mb9495 1257-1343), motherboards/1989-95 README, ordered 1994-95 README, scripts/mb_na8.py, firmware/board/miata_board.cpp, miata_pins.h, rusEFI mazda_miata_1_6.cpp:269-290, default_base_engine.cpp:570.

## Not checked
- Link/Haltech/ECUMaster/AMP pinouts for 1994-95 (not retrieved in this pass); only FSM-class sources (S1, S2) plus rusEFI/MRE/Hellen, which derive partly from the same Mazda data. Wire-colour independence therefore limited.
- Airflow meter electrical range/type; stock idle PWM frequency; stock fan-on temperatures; 1U destination; California-specific diagram; the igniter internal drawing resolution; 1995 colours beyond the crops read; second-source check of 1P/1S directions.
