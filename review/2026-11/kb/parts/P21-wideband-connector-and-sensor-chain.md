# P21 - Wideband connector and sensor chain (LSU 4.9 -> AEM 30-3427 -> J2 -> motherboard -> JD2 -> daughterboard)

## Summary
1. Chain for all six sensor wires is consistent end to end on CURRENT boards (JST S08B-PUDSS-1) and ORDERED boards (Molex Micro-Fit 430450600, C127367): every wire reaches the correct wideband node. No wiring error found.
2. Bosch LSU 4.9 pin functions VERIFIED (Bosch datasheet p.2: 1 IP, 2 VM, 3 H-, 4 H+, 5 RT, 6 UN). Bosch wire colours NOT in Bosch sheet (secondary wbo2.com only).
3. AEM harness table (pin 1 green trim, 2 white H-, 3 orange COM, 4 n/u, 5 red pump, 6 black sense, 7 n/u, 8 brown H+) read today only through a secondary mirror (askmanual.pages.dev summary); AEM's own PDF not fetchable (Cloudflare/403). The repo says it read AEM 10-0300 itself on 2026-11-13 and the two agree.
4. JST drawing (ePUD catalog p.5) VERIFIES: header pitch 2.0 mm, circuit 1 is the pin 2 mm from circuit 2 in the row farthest from the boss; boss is 7.7 mm beyond pin 2 (matches the board: pin 2 y=201.4, NPTH y=209.1 = +7.7). So pad 1 / 2 / row order matches JST. Left-right order along the row (pin 1 at x min, 1-3-5-7 ascending) is NOT shown in JST's catalog drawing: it rests on the repo's owner photograph (not seen by me) = UNVERIFIED by document.
5. Where the convention can flip: (a) which end of the row circuit 1 is at; (b) which row is "odd" (checked OK vs boss, assuming plug enters from the boss side - inferred); (c) AEM numbering = JST numbering (not stated by AEM). A flip of (a) maps 1<->7 etc: RT->empty, H+(8)->2... would put H+ on the H- pin: heater run reversed/no heat, sensor not damaged (heater polarity-insensitive) but all four sense wires wrong. Recommended: continuity-check a real plug before first power (repo already says so).
6. Ordered boards: Micro-Fit pin n = LSU pin n; Molex drawing verifies 1-3 in one row, 4-6 in other, 1 opposite 4, peg 4.32 mm from row 1 (board NPTH 206.62 = 202.3+4.32). Owner must build a lead (Bosch 6-pin plug to Micro-Fit 43025-0600); no AEM harness fits.
7. Current: JST contact 3 A (AWG22) vs heater ramp RMS 2.2 A (3.9 A at -40 C per P04, cold R unverified) and 4.5 A peaks in PWM: thin, single contact per heater wire. Micro-Fit 8.5 A: fine.
8. Clearance: H+ (pad 8, 14 V) sits 0.8 mm edge-to-edge from UN (pad 6) - fine for 14 V; leakage on a 250 uA-max Nernst line only a contamination risk.
9. Product: AEM 30-3427 retail about $22-51 (secondary web listings, AEM page not reachable); hand-made pigtail BOM about $15-20 (Bosch kit $14-19 plus JST housing and 6 contacts $0.40).

## Chain table (CURRENT boards, all four motherboards identical; evidence/cur_mb*/pcb_pads.csv, kb/interconnect.md)
Status: V = verified from document/design file, I = inferred, U = unverified/secondary.

| Function | LSU pin (V Bosch p.2) | Bosch wire (U wbo2) | AEM wire/pin (U mirror; repo read PDF) | JST circuit / pad (V pcb_pads) | MB net | JD2 pin -> DB J2 pin (V interconnect.md) | DB node |
|---|---|---|---|---|---|---|---|
| Pump IP | 1 | red | red / 5 | 5 (125.5,199.4) | LSU_IP | 36 | R110.2 (62 ohm shunt), R112.2 |
| Virtual gnd VM | 2 | yellow | orange "COM" / 3 | 3 (123.5,199.4) | LSU_VM | 35 | F2.1 (nSMD010 PTC) -> WB_VMS |
| Heater - | 3 | white | white / 2 | 2 (121.5,201.4) | LSU_HTR_N | 37+38 | Q101 drain (VND14NV04) |
| Heater + | 4 | grey | brown / 8 | 8 (127.5,201.4) | HTR_PWR (via F1 3 A PTC from VBAT_IN) | not on JD2 (F1 on mb) | - |
| Trim RT | 5 | green | green / 1 | 1 (121.5,199.4) | LSU_RT | 34 | R108.1 R110.1 R111.2 R134.1 (pump drive node; module equation Ip_sense=10*(LSU_Ip-LSU_Rtrim), mck1117 sch line 3419) |
| Nernst UN | 6 | black | black / 6 | 6 (125.5,201.4) | LSU_UN | 33 | R137 22k (buffer), R114 bias, C102 |
Pads 4 and 7: no net (AEM unused). Heater return: Q101 source = HTR_GND on JD2.39/40 which the motherboard ties to GND ("NO" same-name flag in interconnect.md is intentional, HTR_GND is DB-only net, checked: mb net is GND).
Schematic (sch_netlist) and design.py:115-116 / mb_common.py:49-55 agree with PCB.

## Chain table (ORDERED boards, Micro-Fit J2, mb 0.7/0.9/0.11)
Pad 1 IP, 2 VM, 3 HTR_N, 4 HTR_PWR, 5 RT, 6 UN (pcb_pads ord_mb*). Pad n = Bosch pin n by design (ordered INSTALL.md:61). Pad 1 (129,202.3), pad 4 (129,199.3), pegs row +4.32 mm: matches Molex SD-43045-001 sheet 1 (6-CKT PCB layout: 1/2 in one row, 4 opposite 1). Heater pair H-/H+ pads 3 and 4 at 3.0 mm pitch diagonal. Library footprint itself not on this machine (no KiCad libs), compared by coordinates to the Molex drawing.

## Documents
- JST ePUD catalog (ttieurope copy, 8 pages): 3 A AC/DC (AWG22), 250 V, -25..+85 C incl. temp rise, contact 10 mOhm initial; SPUD-001T-P0.5 for AWG 26-22 (0.95-1.5 mm insulation), PUDP-08V-S housing; S08B-PUDSS-1 side entry 8 circuits, Wafer PA66 GF. No PCB hole/land recommendation in this catalog. Board pads 1.2 mm, drill 0.75 (contact tail size not given in the catalog; unchecked).
- Bosch LSU 4.9 (datasheets/extra/LSU49_bosch.pdf p.2): heater nominal 7.5 V / 7.5 W, supply 10.8-16.5 V, Nernst load <= 250 uA, connector temp <140 C.
- Molex SD-43045-001 H1 (datasheets/C127367_430450600.pdf p.1).

## Current rating
Heater per P04: cold R 3.2 ohm (secondary, U) -> 4.5 A pulses, RMS 2.2 A at ramp start (7 V eff), 1 A hot. JST 3 A is a continuous figure for AWG22 at temp rise <=30 C-ish; AEM wire gauge unknown (terminal covers 22-26 AWG, so up to 26 AWG whose 3 A figure does not apply). F1 hold 3 A at 25 C anyway. Verdict: acceptable but not generous; no margin in cold-start winter case; connector rating >= wire rating.

## 2 mm pitch / 12 V
Pad 8 (HTR_PWR 14.4 V, up to 24-30 V in jump/load dump clamps) next to UN pad 6 (0.8 mm gap, same row) and pad 7 (NC) between pad 8 and pad 5 IP... clearance fine electrically; flux/moisture leakage would corrupt only a high-impedance UN line (R137 22k input). Tracks on sense nets 0.2 mm, 85-125 mm long (P03 scope).

## Product question
- AEM 30-3427: listings found by search (not fetched, AEM page 403, shops 403/429): about $22.19-$51.65, typical $30-36 US; CAD 43.75, GBP 36.44. Availability: many US resellers list it; not verified stock. U.
- Seller pigtail: Bosch-type 6-pin LSU 4.9 mating connector: Bosch Motorsport shop AU $27.69 kit (housing, terminals, seals); Ballenger CONN-85772 pigtail with 12 in leads $18.99 (qty1) to $13.99 (500+); CONN-75762 kit $17.99; Race Spec kit $14.00; iWire $17.99; EFI Hardware $20 (qty1) / $14 (10+). Bosch shell number cited by wbo2: 1 928 404 692 (datasheet gives 1928.404.687 for sensor-side/D261.205.356-01 mating for motorsport; automotive mating connector number not stated in sheet). JST side: PUDP-08V-S C490532 $0.29-0.17 + SPUD-001T-P0.5 C267125 $0.018 each (JLC extended, stock 12k/131k); Micro-Fit side 430250600 C293525 $0.11-0.07 + crimps. So BOM about $15-20 + 6 wires, close to or below the AEM harness, with right length/seals. U (web prices).
- Others (repo research/other_miata_pnp_boards.md, secondary): nobody else uses AEM's harness; ME221/442 and AMP EFI ship their own lead; open boards leave the connector to the owner.
- JLC lists the header S08B-PUDSS-1 as C412098 (extended, stock 10084, $0.36-0.20): could be placed by JLC THT assembly instead of hand fitting (not checked).

## Sources actually read
kb/interconnect.md; evidence/cur_mb*/ord_mb*/pcb_pads.csv, pcb_footprints.csv, pcb_net_routing.csv, drc rpt; repo scripts mb_common.py, design.py, wideband.py, mb_na6.py; repo research/rev0.10_design_audit.md A13, VERIFICATION.md; ePUD.pdf pp.3,5,6; Molex sheet; Bosch LSU 4.9 pdf; kb/parts/P04; web: askmanual AEM 30-0300 mirror, wbo2.com/cable/lsuconns.htm, search listings.

## Not checked
AEM original PDF (blocked); AEM 30-3427 page and cable length/gauge; real harness continuity; KiCad library footprint file (not installed); in-row end of circuit 1 from a JST document; Bosch automotive mating connector number; Micro-Fit footprint vs Molex beyond coordinates.
