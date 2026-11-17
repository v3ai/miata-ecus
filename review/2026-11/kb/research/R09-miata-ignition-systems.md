# R09 - Ignition systems of 1989-2005 Miatas and how aftermarket ECUs drive them

Status: finished 2026-11-16. Evidence is thinner than intended in places:
no Mazda document gives the igniter input threshold for 1989-97, the NB coil-pack input resistance or the dwell limit, and
no teardown of the stock ECU output stage was found. Those are marked UNVERIFIED / not found; see "Not checked".

## Summary
1. The stock ECU drives every Miata ignition input active-HIGH (high = coil charging, falling edge = spark); at rest the
   FSM shows 0 V (key on) and ~0.2 V average at idle on 1G/1H/4N/4R, i.e. the safe/rest level is LOW. Haltech sets
   "Constant charge, falling edge" for NB1/NB2.
2. 1989-93 / 1994-95: external igniter, ECU 1G (#1&4) and 1H (#2&3) drive transistor bases (about 659 ohm to ground, from
   the 1990 FSM per R16); 2I (B/W) is the igniter's IGf return into the ECU. The stock ECU (per forum, one source) supplies
   a 1 k pull-up on 2I; the project's motherboards fit NO pull-up on 2I (only JP5, open). Consequence UNVERIFIED but plausible: no tach / "code 01" with a stock igniter.
3. 1996-97, 1999-2000, 2001-05: coil packs with built-in igniters, logic input. 2005 FSM bench test fires the coil from two 3 V
   dry cells (so the input threshold is below 3 V on NB2). NB2 pack pinout: A signal, B ground, C +12 V (Haltech); NB1: A +12 V, C ground, D signal.
4. Every aftermarket PnP I could read drives these inputs with a 5 V push-pull logic buffer: Hellen ign8 = SN74LVC4245A + 10 ohm
   series (5 V side); Speeduino NA6 PNP = TC4424A (5 V) directly after a 1 k + 100 k pull-down at its input; MS3Pro "logic level" = 0-5 V. No source uses open collector for Miata coils.
5. The project's stage (TC4427 + 100 ohm + B5819W + ZXMS6004FF low + 3.3 k pull-down + 10 k input pull-down) rests LOW in power-off
   and reset (VERIFIED from design.py), delivers about 4.0 V into a 659 ohm base and about 4.5 V into a high-impedance logic input (INFERRED), which is above the 3 V
   shown working on NB2. It is compatible in logic level with all years; the FET and Schottky are extra over Hellen/Speeduino practice.
6. rusEFI ships a flat 4 ms dwell with voltage correction 1.0 from 8 to 15 V and the board firmware sets none: no dwell-vs-voltage
   table for any coil, and rusEFI has no generic max-dwell guard (only for MC33810). Over-dwell is the documented killer of Miata coil packs (forum evidence only).

## 0. What this project's ignition stage is (VERIFIED from design files, first run)
- `repo/scripts/design.py:297-330`: IGNx_CTL (3.3 V, 10k pull-down RN1) -> TC4427 (U6/U7, +5V) -> 100 ohm 1206 (R15-R18) -> B5819W (D31-D34,
  anode at resistor) -> OUT_IGNx. OUT_IGNx also: 3.3k 1206 to GND (R144-R147) and the drain of ZXMS6004FF (Q16-Q19), gate = 74HCT04 (U13, +5V) inverse of IGNx_CTL.
- `evidence/*/pcb_nets.txt`: IGN1 -> 1G, IGN2 -> 1H (1989-95); 4N, 4R (1996-97); 3G, 3H (1999-2000); 3F, 3I (2001-05). IGN3/IGN4 only reach AUX J5 pins 1/2.
- `repo/firmware/board/miata_board.cpp:76-80,201,212`: wasted spark, ignitionPins[0]=IGN1 (1&4), [2]=IGN2 (2&3); cranking dwell 4 ms.
- `repo/firmware/ext/rusefi/firmware/controllers/algo/defaults/default_ignition.cpp:112-115`: `setConstantDwell(4)`, dwellVoltageCorr bins 8..15 V, all values 1.0. VERIFIED today. grep of controllers: max-dwell guard exists only for MC33810 (engine_controller.cpp:599).
- `evidence/cur_mb8995/pcb_nets.txt:12`: net HARN_2I = J1.2I, JP5.2 only (no pull-up, no sense input). Ordered boards: OUT_TACH wired straight to J1.2I (ord_mb8993 line 52, ord_mb9495 line 48) = ECU output on the igniter's IGf wire (already covered by R17).

## 1. 1989-93 and 1994-95 (external igniter + 2 dual-post coils)
| Item | Finding | Tag / source |
|---|---|---|
| ECU pins | 1G = IB1 (brn/yel) cyl 1&4; 1H = IB2 (brn) cyl 2&3; 2I (blk/wht) = IGf into ECU; tach wire (yel/blu "TAC") from igniter to cluster | VERIFIED via R16 (1990 FSM F-127..130); Haltech NA6/NA8 igniter pin table: OC1, IB1, VB, TAC, IGf, GND, IB2, OC2 (https://support.haltech.com/portal/en/kb/articles/93-na8-1-6l-b6-ze, fetched today) |
| Input circuit | ~659 ohm base-to-ground per ECU output (R16, 1990 FSM) | VERIFIED in R16 (not re-read by me) |
| Levels at ECU pin | 1G/1H: 0 V key on, ~0.2 V idle (1989-93 and 1994 tables; R16/R17). So rest = LOW, charge = HIGH pulse | VERIFIED R16/R17 |
| Input threshold | no figure found for the Mitsubishi-type igniter (forum: J702T) | not found |
| Dwell: ECU or igniter? | The ECU's pulse width sets dwell (Haltech: "constant charge"-type control for NB; for external igniter Joe Perez scoped stock 1.6 coil about 3.7 ms at 2000 rpm, he judged coil not reaching full current: forum, https://www.miataturbo.net/megasquirt-18/ms-dwell-settings-cops-23550/) | UNVERIFIED (forum) |
| IGf / tach | 1990 FSM code 01 IGf: troubleshooting asks "does the tachometer operate?" then checks wire igniter -> ECU terminal 21 (wm1990_djvu.txt lines ~17640-17780). rusEFI wiki: igniters drive coils and provide tach; "the ECU provides only a pull-up to 5 V" (https://wiki.rusefi.com/Legacy-Miata-NA-48-pin-board-for-MRE s2.4, fetched today). Miata Turbo thread: Braineack says the ECU does not touch the tach wire but supplies the pull-up for the B/W coil-output wire from 2I; 1 k to +12 V, 1/4 W, needed "only if the factory ECU was removed"; Hellen NA6 94 doc has jumpers "2I tach pullup, used with stock coils" and "2I tach out, used with aftermarket coils OR 95.5" (https://www.miataturbo.net/ecus-tuning-54/tach-signal-wiring-specifics-58571/; Hellen doc via search snippet, ext/hellen-miata-NA6 pcb not traced) | Pull-up exists on stock ECU: INFERRED from 2 sources (rusEFI wiki, 1 forum); voltage 5 V vs 12 V DISAGREE between them. |
| Without IGf | stock ECU sets code 01; R16: "Ne/G/IGf faults: no fail-safe". The FSM bench text does not say what it does to injection | R16 |
| Wasted pairs | 1&4 on IB1, 2&3 on IB2; firing order 1-3-4-2 (BP and B6); standard B6/BP | UNVERIFIED (memory) - not re-checked; low importance |
| 1989-93 vs 1994-95 | 94-95 coil pack = two igniters in the pack, same drive scheme (R17). FSM 2I level: 1994 <0.5 V on / ~1 V idle, 1995 ~10 V / ~11 V (the manuals disagree; R17). A late-95 ECU in a '94 gave "no IGf" and no tach drive (forum, UNVERIFIED) | R17 |
| Coil | primary 0.78-0.94 ohm (1990 FSM; 1994 spec table `work/R09.../txt/Mazda-Miata-1994_specs.txt:86`); secondary 11.2-15.2 k (1990) / 8.7-12.9 k (1994 table) | VERIFIED |

## 2. 1996-97 and 1999-2005 (coil packs with built-in igniters)
- 1996-97: IGT1 on 4N, IGT2 on 4R, <1 V key on, ~0.2 V idle (R17, FSM). Coil pack mounts on the head behind the cam sensor.
- 1999-2000 (NB1): pack with internal igniters, 4-pin connector A +12 V switched, B n/c, C ground to head, D ECU signal; Haltech: waste spark, "Constant Charge, Falling Edge", "can be wired directly to the ECU" (https://support.haltech.com/portal/en/kb/articles/99-00-nb1-1-8l-bp-4w, fetched today). Mazda pin names 3G/3H.
- 2001-05 (NB2): two coil-on-plug packs (coil 1 on cyl 4 with lead to cyl 1, coil 2 on cyl 2 with lead to cyl 3); 3-pin A signal, B ground to head, C +12 V; same Haltech settings (https://support.haltech.com/portal/en/kb/articles/01-05-nb2-1-8l-w-vvt-bp-z3-bp-ve). ECU pins 3F (1&4), 3I (2&3).
- 2005 FSM (Mitchell, `work/R09.../txt/Mazda-Miata-2005_ignition_system.txt`, Fig. 3): operation test connects the coil to the car battery and fires the plug by switching **two 3 V dry cells in series (3 V per figure label)** to the signal terminals 1C/2C; secondary 7-11 kohm; insulation >10 Mohm. VERIFIED (figure read today: `work/R09.../nb2_coil_bench_test.png`). Note this proves the input triggers at or below 3 V; it does not give the threshold or the input resistance. The figure's two dry cells are labelled "3 V" total; I read the label from the image, I did not measure.
- Input resistance, max dwell, internal over-dwell protection: not published in anything I could read. Forum claims (UNVERIFIED): 99-00 coils tolerate less signal-voltage/dwell range than Toyota COPs and often die (miataturbo thread, quoted in a search summary); a stock-ECU test with a cheap O'Reilly coil died in a week while genuine Mazda survived; "dwell 8 ms stock default on long cranking" killed coils on one MegaSquirt (https://www.miataturbo.net/engine-performance-56/whats-killing-my-coils-96997/).
- Firing order 1-3-4-2 for BP; wasted-spark pairs 1&4 and 2&3 on every year (FSM statement, 2005: "No.1 and No.4 cylinders and No.2 and No.3 cylinders are ignited simultaneously", VERIFIED in the 2005 ignition text).

## 3. How other ECUs drive these inputs
| ECU | Output stage | Source |
|---|---|---|
| Stock ECU | unknown topology (no teardown/schematic found). Behaviour: 0 V at rest, short pulses to high at idle (average 0.2 V); forum: "6 ms pulses of +5 V" (UNVERIFIED single post) | FSM via R16/R17; miata.net thread via search |
| rusEFI Hellen NA6/NB1/NB2 | ign8 module: SN74LVC4245A (A side 3.3 V, B side 5 V "VA_5V") + 10 ohm series per channel; 5 V push-pull, no on-board pull-down visible in the text (OE pin handling not read) | `work/R09.../hellen/ign8-0.2-schematic.txt` (VERIFIED partly; schematic text only), `kb/research/R01` |
| Speeduino NA6 PNP v1.3 | MCU pin -> 1 k series, 100 k to GND at the TC4424A input; TC4424A supplied from VDD (5 V); output straight to IGN-x-OUT, plus LED+2.4 k; no output resistor/diode | `ext/speeduino-hardware/PNPs/Miata NA6/Latest/Fuel_Ignition.sch` (read; VDD net assumed 5 V from symbol name) |
| Speeduino v0.2 generic | jumper picks 5 V or 12 V for ignition outputs; wiki says never drive coil directly; "Dwell: igniters and coils can be permanently damaged if dwelled excessively" | search summary of wiki pages (page itself blocked: Cloudflare 403) UNVERIFIED |
| MegaSquirt/MSPNP | MS3Pro logic-level 0-5 V outputs, spark output polarity "going high"; for IGN-1A DIYAutoTune recommends a 270-330 ohm pull-up on self-built harnesses; MSPNP 90-93 page documents only "Tach Out on J3 pin 4I (1995.5+ Miata only)" (https://ampenginemanagement.com/blogs/mspnp-pro-documentation/pro-mm9093-installation, read today); search summary also: MS1 default dwell does not equal the commanded dwell | read / search summary |
| Haltech Elite | "Ignition Output 1/2" to IB1/IB2 (89-95); falling edge, constant charge for NB; IGf and TAC left unconnected (https://support.haltech.com/portal/en/kb/articles/na6-89-93-1-6l-b6-ze; the NA8 page was fetched) | VERIFIED page text |
| Link | no Miata-specific note found; IGN1A guide says always use minimum dwell | not Miata |
Warnings seen: Haltech gives none; Zetec guide (DIYAutoTune) warns wrong edge/polarity overheats igniters. Series resistors: Hellen 10 ohm, project 100 ohm, Speeduino none; nobody uses an open-collector with pull-up for Miata.

## 4. Safe state (what the line must rest at)
- Stock behaviour and Haltech "constant charge, falling edge" mean: HIGH = coil charging; spark when the line falls. Therefore the rest level MUST be LOW (below the igniter's threshold, which is below 3 V on NB2) when the ECU is unpowered, in reset, in the bootloader, and before firmware starts. INFERRED from the two sources above.
- A floating line: the 1989-95 igniter has a base resistor to ground (about 659 ohm, R16) so floating = LOW; NB packs: unknown whether the input has an internal pull-down (not documented; forum: crackle from the coil pack with no ECU plugged in, one anecdote, UNVERIFIED). A weak pull (above about 10 k) beside an NB coil whose threshold is ~1-2 V is not proven safe.
- Project: low in power-off (3.3k to GND; TC4427 and HCT04 unpowered), in reset (RN1 10 k pulls IGNx_CTL low -> TC4427 out low and HCT04 out high -> ZXMS on) and in bootloader. VERIFIED from design.py:297-330 and R144-R147/RN1; INFERRED for the sequencing. It rests LOW in every state I could think of.
- Hardware has no dwell limiter: a firmware crash with IGNx_CTL stuck HIGH charges the coil until the igniter overheats (forum: igniter "got very hot"). A watchdog or an RC high-pass between MCU and TC4427 would cap it; rusEFI has none for plain GPIO (grep today).

## 5. Dwell
- No manufacturer dwell table exists for these coils (searched; Haltech's tables are images, not in text). Facts: primary 0.78-0.94 ohm (FSM) -> 16 A at 14 V if it were not current-limited; Toyota COP forum values 3.5 ms cranking / 2.5 ms running (UNVERIFIED), 8.0 ms "stock default" blamed for burnt coils (UNVERIFIED), stock 1.6 coil about 3.7 ms at 2000 rpm (scope, UNVERIFIED).
- INFERRED starting table (not measured; scope each coil before driving): 6 V 6.0 ms cap, 8 V 5.0, 10 V 4.2, 12 V 3.6, 13.5-14.4 V 3.0-3.2, 16 V 2.6 ms, with a hard cap of about 6 ms. Reason: with a 0.86 ohm coil the current rises toward V/R, so energy at 14 V needs about 4/(14/12) of the 12 V time. This reproduces the rusEFI-style voltage correction; treat as a first draft only.
- Current project: flat 4 ms for every voltage (VERIFIED), so spark energy falls at the 6-8 V cranking dip and the coil gets the same 4 ms at 16 V.

## 6. Project assessment
- Logic: OK on all years, in INFERRED numbers: with a 659 ohm base load the pin sits near 4.0 V (5 - 0.35 Schottky, divided 100/(659||3.3k)); about 4.5 V unloaded-logic. Above the 3 V proven on NB2. 100 ohm is a good series value for ESD/short protection. Schottky + ZXMS + 74HCT04 + 3.3k are not required by any Miata coil; they protect the TC4427 against a coil wire shorted to battery and give the falling edge a defined, low-impedance pull-down (needed because the Schottky blocks the TC4427 from sinking).
- Simpler proven circuits: Hellen ign8 (LVC4245 + 10 ohm) and Speeduino NA6 (TC4424 straight) run Miata coils; the cheapest equivalent for this board is TC4427 (or even the MCU through a 74HCT-class buffer) + 100 ohm + a 10 k pull-down at the buffer input, dropping Schottky, FET, HCT04 and 3.3 k (4 x each saved, but only two channels are used by the harness). Saves the protection; keep it if short-to-battery ignition wires are a service concern. Cost not priced by me.
- Gap: 2I pull-up on 1989-95 (below).
- Gap: dwell table (below).

## Implications for this project
1. (goal 1, errors, medium-high, confidence medium) 1989-95 with the stock igniter: the stock ECU supplies a pull-up on 2I (rusEFI wiki says 5 V, a forum post 1 k to +12 V; Hellen has a "tach pull-up for stock coils" option). The project has none (cur_mb8995 HARN_2I = J1.2I + JP5 only; ordered boards drive OUT_TACH onto it). Expect: no tachometer signal and/or no IGf; verify with a scope on a real car; fix = footprint for 1 k from V5/V12 on 2I (DNP-able), and remove the OUT_TACH link on ordered boards. Evidence: files above, https://wiki.rusefi.com/Legacy-Miata-NA-48-pin-board-for-MRE, https://www.miataturbo.net/ecus-tuning-54/tach-signal-wiring-specifics-58571/.
2. (goal 1/4, firmware, medium) Replace flat 4 ms dwell with a voltage-compensated table and a hard maximum; document "scope your dwell". Evidence: default_ignition.cpp:112-115.
3. (goal 2/5, removal, low-medium) The FET/Schottky/HCT04 chain is not what any other Miata ECU uses; removing it would drop 2 x (ZXMS + Schottky + 3.3 k) + U13 if the short-to-battery protection is judged unnecessary. Keep the 3.3 k-class pull-down.
4. (goal 4, doc, low) NB coils trigger at under 3 V (FSM 2005 bench figure) so the 5 V push-pull levels are fine; no 12 V logic needed.
5. (goal 1, info) Safe state is LOW and is satisfied in power-off, reset and bootloader.

## Sources actually read
- `work/R09-miata-ignition-systems/nb2_coil_bench_test.png` (2005 FSM Fig. 3), `txt/Mazda-Miata-2005_ignition_system.txt`, `txt/Mazda-Miata-1994_specs.txt`, `work/R16-stock-ecu-1989-93/dl/wm1990_djvu.txt` (lines 17640-17780, 23290-23700), kb notes R16/R17, `ext/speeduino-hardware/PNPs/Miata NA6/Latest/Fuel_Ignition.sch`, `work/R09.../hellen/ign8-0.2-schematic.txt`, `work/R09.../dl/mm9093.html.txt`, `ext/hellen-miata-NA6/hellen64_NA6_94.kicad_pcb` (partial), repo files above.
- Web (fetched through page fetch summaries, not raw): support.haltech.com NA8 / NB1 / NB2 pages; wiki.rusefi.com Legacy Miata NA 48 pin page (curl'd, read raw); miataturbo.net threads ms-dwell-settings-cops-23550, whats-killing-my-coils-96997, tach-signal-wiring-specifics-58571; wiki.fome.tech Miata COP Conversion (no numeric dwell; Toyota pinout ground/signal/tach/12 V; tach not needed on late NA8 and NB1).
- Blocked: gitea.interbiznw.com (Cloudflare 403), grassrootsmotorsports.com (403).

## Not checked
- Stock ECU output-stage schematic/teardown (none found). Igniter input threshold 1989-97 and NB input resistance/dwell limits (not published). Actual 2I pull-up voltage and value (sources disagree). Hellen NA6 2I pull-up net (could not trace from KiCad files). Dwell images on Haltech and FOME pages. Link/Haltech series-resistor advice (none found). Firing-order claim only from memory.
