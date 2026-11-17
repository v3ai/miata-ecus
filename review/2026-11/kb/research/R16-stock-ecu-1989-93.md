# R16 - Stock 1989-93 Miata / MX-5 / Eunos 1.6 (B6ZE) ECU and engine electrics

Status: FINISHED 2026-11-16. Coverage is strong for the 48-pin pinout, terminal voltages, diagnosis, codes and fail-safe (primary source: 1990 US workshop manual). Weak for hardware internals, part numbers by year, case dimensions, 1993 and market differences (see Not checked).

Tags: VERIFIED = read today in a primary source (cited); INFERRED = reasoning shown; UNVERIFIED = memory / single forum post / seller listing.

## Summary

1. VERIFIED (1990 US workshop manual F-127..F-130): the ECU has 48 terminals in two plugs: plug 1 = 22 cavities 1A..1V (no 1W..), plug 2 = 26 cavities 2A..2Z. Physical order (manual F-130): top row 2Y 2W 2U 2S 2Q 2O 2M 2K 2I 2G 2E 2C 2A | 1U 1S 1Q 1O 1M 1K 1I 1G 1E 1C 1A; bottom row 2Z 2X 2V 2T 2R 2P 2N 2L 2J 2H 2F 2D 2B | 1V 1T 1R 1P 1N 1L 1J 1H 1F 1D 1B.
2. VERIFIED: on 1989-93 (Lakey 90-93 MT chart + manual) cavities 1I, 1L, 1M, 1T, 2F, 2J, 2M, 2R, 2S, 2T, 2Y, 2Z carry NO wire on the manual car (Lakey, crossed boxes). The manual lists them as "-". The project's 1989-93 map uses some of these for outputs/inputs it calls stock (1L fan, 1M VSS, 2T fuel pump relay, 2M TPS): those are not stock-harness functions. 2F is tied to GND by the board; manual says 2F is unused (2J is the ground one).
3. VERIFIED: fan is NOT ECU-controlled: water thermoswitch drives the fan relay; the ECU only monitors it on 1R (0 V when fan on; "TFA" diagnosis terminal grounded forces fan on). So an ECU fan output on 1R (low side) acts in parallel with the thermoswitch: plausible; the 1L fan claim for 89-93 has no source.
4. VERIFIED: fuel pump is not driven by the ECU: circuit-opening relay (COR) is fed from the airflow-meter switch/ST SIG (1C start signal); ECU 2T is empty. Fuel pump relay output on 2T is a project invention (harmless if the wire does not exist).
5. VERIFIED: igniter: ECU outputs 1G (IB1, brn/yel) and 1H (IB2, brn) drive the igniter's transistor bases (about 659 ohm base to ground); 2I (blk/wht) is the igniter IG(f) confirmation input; the igniter drives the tach itself (TAC, yel/blu). 5 V push-pull sources (TC4427 via 100R) fit this.
6. VERIFIED: TEN (diagnosis connector) to GND = initial set: timing fixed at 10 deg +/-1 BTDC, idle 850 +/-50 rpm, and output-device checks run for 3 s after ignition ON. 1K is the ECU's TEN input (12 V, 0 V when grounded). The board leaves 1K open: harmless but the stock TEN jumper then does nothing.
7. VERIFIED: self-diagnosis codes 01 IGf, 02 Ne, 03 G, 08 AFM, 09 water temp, 10 intake air temp, 14 atmospheric pressure sensor (inside ECU), 15 O2 (<0.45 V 180 s), 17 feedback, 26 purge solenoid, 34 ISC valve. Memory is cleared by disconnecting the battery negative and pressing the brake 5 s.
8. Inputs the board does not map: 1O stop lamp, 1P P/S pressure switch, 1S blower, 1U headlight (electrical load), 1K TEN: the stock ECU raises idle for P/S, A/C, blower, E/L; the rusEFI side must do it itself.
9. UNVERIFIED: the ECU sits under the passenger floormat/protector cover (manual F-127 VERIFIED: "lift floormat in front of passenger seat, remove protector cover"; photo shows bracket bolted to the floor). A seller page (fs1inc) saying "under the console" contradicts the manual; disregard.
10. UNVERIFIED: processor guesses on forums (custom 68HC-family; same chip as 90-93 MR2); leaking electrolytic caps are a documented failure family on 1990-93 Japanese ECUs (general sources), 63 V 47 uF given in one miata.net post for NA8; nothing verified for the 1.6 board.

## Details

### Connector, wires (Lakey 90-93 manual-transmission chart, miata.net, file kb/research/files/R16/miata_net_Lakey_ECU_pinout_90-93_MT_v1.2.pdf; read from the crops lakey_c1/c2.png; UNVERIFIED for any wire colour I could not align exactly, treat as indicative)
Plug 1 (top row 1U..1A): red/blk, blu/org, Lt grn/blk, grn, none, Lt grn/yel, none, brn/yel, yel/blk, violet, blu/red. Bottom (1V..1B): brn/wht, none, blk/grn, blu/yel, red, none, blu/blk, brn, wht/yel, wht/grn, wht/red.
Plug 2 (top 2Y..2A): none, blu/org, yel, none, blu/wht, red, none, Lt grn/red, blk/wht, yel/blu, wht, blk/Lt grn, blk. Bottom (2Z..2B): none, yel/red, yel/blk, none, none, red/grn, red/blu, Lt grn/wht, none, red/wht, none, blk/Lt grn, blk.
Note: the Lakey chart puts 1N = throttle position sensor IDL wire and 2L = POW wire (grounded = WOT); manual says 1N idle point, 2L "power terminal" 5 V closed / 0 V WOT. Both agree: the manual-car throttle "sensor" is a two-contact switch, not a potentiometer.

### Terminal voltage table (1990 US workshop manual F-128..F-130, VERIFIED; scans in kb/research/files/R16/wm1990_pdfpage27x_F-1xx.png)
1A battery 12 V (backup). 1B main relay 0 V off / 12 V on. 1C start 10 V cranking / 0. 1D self-diagnosis monitor lamp (5 V / 12 V). 1E MIL below 2.5 V lamp on / 12 V off. 1F buzzer/code output. 1G, 1H igniter 0 V key on, 0.2 V idle. 1J A/C relay 12 V on, below 2.5 V A/C on. 1K diagnosis (TEN) 12 V / 0 V grounded. 1N idle contact 0 V released / 12 V depressed (manual voltage, ignition on). 1O stop lamp 0/12 V. 1P P/S 12 V off / 0 V on (idle). 1Q A/C switch below 2.5 V on. 1R fan switch 0 V fan operating (coolant above 97 C or TFA grounded) / 12 V off. 1S blower 0 V mid-high / 12 V off-low. 1U headlights 12 V on / 0 off. 1V neutral/clutch 0 V neutral or clutch in / 12 V in gear. 2A injector ground, 2B output ground, 2C CPU ground, 2D input ground. 2E Ne 0/5 V, idle ~2 V. 2G G-signal 0/5 V, idle ~1.5 V. 2H ground on California, open (~2 V) Federal/Canada. 2I igniter <0.5 V key on, ~1 V idle. 2J ground. 2K AFM 5 V ref 4.5-5.5 V. 2L throttle POW 5 V / 0 V. 2N O2 0 V cold/key on; 0-1 V warm; 0.5-1 V rev; 0-0.4 V decel. 2O AFM 3.8 V key on, 3.3 V idle. 2P intake air temp 2.5 V at 20 C. 2Q water temp 2.5 V at 20 C, 0.4 V warm. 2U/2V injectors 12 V key on, 12 V idle (pulses). 2W ISC valve 7 V key on, 9 V idle (duty). 2X purge solenoid 12 V. Unused ("-"): 1I, 1L, 1M, 1T, 2F, 2M, 2R, 2S, 2T, 2Y, 2Z.
Lakey chart values differ slightly (UNVERIFIED, owner measurements): 2O 4-5 V vane closed, 0-0.5 V open; 2Q ~2.2 V cold/0.4 V hot, thermosensor 2200-2700 ohm cold, 290-350 hot; 2P 2.18 V; 2W valve 11-13 ohm; injectors 12-16 ohm (high-impedance per manual "high-ohmic injector, single port"). 2H "2.3-2.5 V" there.
Caveat: manual is the 1990 US edition; 1991-93 manuals not read.

### Functions (manual F-outline, VERIFIED)
- Control outputs: A/C cut (relay), fail-safe, injectors, ISC valve, igniter, monitor lamp, purge solenoid. Inputs: A/C switch, O2, atmospheric pressure sensor (inside ECU), stoplight, start signal, cooling fan relay (monitor), light and turn relay, blower, water temp, Ne, neutral/clutch, airflow meter, intake temp, G, P/S, diagnosis, throttle IDL and POW.
- Injectors paired: 2U = Nos.1,3; 2V = Nos.2,4 (manual and Lakey). Repo comment "1&4 / 2&3" for ignition (wasted spark) and for injectors earlier revs; ISC: duty-driven bypass valve; purge duty-driven on California cars; 2H grounded = California.
- Diagnosis connector (21-pin, black) groups EGI self-diagnosis (TEN), initial set, fuel pump check (FP), cooling fan check (TFA).
- Timing: 10 deg BTDC with TEN grounded; adjusted by rotating the crank angle sensor (distributor-like CAS, bolt 19-25 Nm). Without TEN, timing advances.
- Fail-safe values: AFM fault: fixed basic injection amount (two modes by idle switch); water/intake temp fault: assumes 20 C; atmospheric sensor fault: sea-level pressure; O2 faults: cancel feedback. Ne/G/IGf faults: no fail-safe (engine stops or limps).

### Part numbers (UNVERIFIED, seller listings only, search results 2026-11-16)
B61P-18-881A / -881B (manual, 1.6, 1990-93, redlineautoparts, ebay.ca listing 116808026872); B6AW-18-881 (1993 California, sellers); B64J-18-881 (one seller). Automatic and Japan/Europe numbers not found. Sellers' fitment claims are inconsistent.

### Markets
UNVERIFIED (DIYAutoTune product page, today): the competitor plug-in AMP/MSPNP lists fitment 1990-93 NA6 1.6 B6ZE manual and 1994-97 JDM and EUR 1.6 B6ZE manual; another source says the 94-97 JDM/EUR 1.6 wiring resembles 90-93 USDM. Not verified against a manual.

### Known problems (UNVERIFIED, search summaries; miata.net threads returned 403 to me)
Leaking electrolytics corroding the board; idle problems from capacitor/diode failure (miata.net thread titles only). General family evidence: ecmtuning wiki says leaking caps a major concern for 1990-93 Japanese ECUs. Not Miata-1.6 specific.

## Implications for this project
1. Check the 1989-93 map against the manual: 1L (fan), 1M (VSS), 2T (fuel-pump relay), 2M (TPS) have no stock wire on a 1990-93 MT harness; 2F is tied to GND but 2J is the manual's ground. Effect: documentation claims for these pins should say "no stock function"; low risk to hardware. Confidence medium-high (manual + Lakey agree).
2. 1R is a monitor input of the stock fan circuit (thermoswitch node, 0 V when fan on). A low-side output on 1R works as a parallel fan-on path; document that the stock thermoswitch remains in control and that a stuck-low output makes the fan run. Confidence medium.
3. Stock idle compensation inputs (P/S 1P, blower 1S, headlights 1U, stop lamp 1O) and TEN 1K are not wired through: a car whose idle relied on the ECU's P/S/E-L idle-up loses it unless the daughterboard AUX inputs are mapped. UX/firmware item. Confidence medium.
4. Igniter interface: 5 V push-pull into ~659 ohm transistor base, IGf return on 2I; matches TC4427 design (checked, consistent). Keep JP5 open (tach is the igniter's own).
5. Throttle: manual cars have a two-contact switch (idle 1N, power 2L): confirmed by manual and Lakey; TPS conversion statements in the repo are consistent.
6. Mounting: ECU is under the passenger floormat with a protector cover (manual F-127); case dimensions/construction were NOT found: the "caliper check" in the repo VERIFY list stays necessary.
7. Selling point for refurbishing: customers' stock ECU (the case is reused): cap leakage risk on the donor board; corrosion under caps may reach connector pads: advise inspecting case/header.

## Sources actually read
- work/R16-stock-ecu-1989-93/dl/wm1990_djvu.txt and wm1990.pdf (archive.org 1990 Mazda MX-5 Miata workshop manual, F section); pages saved: kb/research/files/R16/wm1990_pdfpage271_F-127.png, 272 F-128, 273 F-129, 274 F-130, 224 F-80 (codes)
- kb/research/files/R16/miata_net_Lakey_ECU_pinout_90-93_MT_v1.2.pdf (+ png of pinout 2010), crops in work dir
- repo/scripts/mb_na6.py, kb/interconnect.md, repo/firmware/ext/rusefi hellenMiataNA6 main.yaml (not relied on)
- Web search results (summaries only): redlineautoparts, diyautotune.com mspnp2-mm9093 (fetched), fs1inc blog (fetched; SEO text, contradicted), ecmtuning/3swiki/clublexus (generic cap failures), forum.miata.net threads (403, titles only), vkmotorsports ECU hacking blog (title only).

## Not checked
- Maker (Mazda-Denso/other), internal parts, case size/construction, 1991-93 manuals and 1993 differences, automatic ECU, Eunos/Europe/Australia pinouts, thermowax air valve, AFM fuel pump switch details, EGR/purge on California, MIL lamp details, radiator fan relay wiring, 1989 Japan part numbers, wire colours exactly aligned in Lakey crops.
