# R07 - Automotive electrical environment and ECU hardware practice

Status: COMPLETE for the electrical-transient part (primary standards text read); PARTIAL for EMC, thermal, connector, coating, capacitor topics (see Not checked). Written 2026-11-16.

## Summary (10 lines)

1. ISO 16750-2:2023 (full text read, third-party host) sets for 12 V: Us range 6/8/9/10.5..16 V (T3 p.3), jump start 26 V for 60 s (T5 p.5; older editions and ST AN2689 say 24 V), reverse -14 V 60 s through the fuse (T16 p.23), load dump test A 79-101 V / 0.5-4 ohm / 40-400 ms, test B clamp Us* 27/30/32/35 V by severity (T13/T14 p.20-21), ground/supply offset +-1 V (T17 p.25).
2. ISO 7637-2:2004 (full text read) pulses for 12 V: P1 -75..-100 V/10 ohm/2 ms; P2a +37..+50 V/2 ohm/50 us; P3a -112..-150 V and P3b +75..+100 V /50 ohm/100 ns; P4 -6..-7 V (crank, 15-40 ms); P5a 65-87 V (the 2012 revision of 16750-2 raised it to 79-101 V).
3. Whether a 1989-2005 Miata alternator clamps load dump: NOT established. Known: zener-avalanche clamping rectifiers existed from 1987 (SAE 872002, Motorola, abstract read) and ISO 7637-2:2004 says "most new alternators" are clamped. Nothing Miata-specific found. Treat as unknown; design to test B (35 V) as the baseline and survive test A only if cheap.
4. TVS energy arithmetic (worked below): a 1.5 kW 10/1000 us part (SMCJ/1.5SMC) cannot absorb ISO test A (101 V, 4 ohm, 400 ms) - it would see roughly 13 A and 600+ W for hundreds of ms; a 400 W SMAJ33A cannot either (Vc 53.3 V at only 7.5 A). Both are fine for clamped (test B, <=35 V) operation because a 33 V stand-off (36.7 V min breakdown) part does not conduct below 35 V.
5. A TVS whose stand-off is below the highest supply voltage conducts continuously and burns; this is the most common hobby error (several app notes).
6. ESD (ISO 10605): 150/330 pF with 330 ohm/2 kohm, contact 2-15 kV, air 2-25 kV, generator ground reference = battery ground (TI SLVA954B).
7. Cabin heat: measured parked-in-sun averages 47 C cabin air and 69 C dashboard after 1 h (ASU/Temperature 2018, 6 cars, secondary press page); a footwell electronics temperature measurement was NOT found. The 85 C review brief figure is a spec-class number, not a measurement I could confirm.
8. Checklist of 24 pass/fail items with sources is in section D. Items most often violated by hobby ECUs are marked (H).
9. The repo's own design (SMAJ33A on +12 V behind a PTC, SMCJ30A injector clamps, series resistors plus clamps on inputs) is consistent with the clamped-load-dump baseline; its VERIFICATION.md already states "an unsuppressed load dump" as a limit. No new error found in this scope.
10. Several promised items were not reached (CISPR 25 limit numbers, capacitor derating, conformal coating, connector derating numbers): listed under Not checked.

## A. Transient and supply conditions (VERIFIED from standard text unless noted)

Files: work/R07-automotive-environment-practice/dl/iso7637.txt (ISO 7637-2:2004(E) corrected 2004-09-15, 42 pp, downloaded from an E2E forum attachment), iso16750_2.txt (ISO 16750-2:2023(E), copy hosted at lisungroup.com; text partly garbled by a watermark, tables checked above). Both are copyrighted standards hosted by third parties; I read them for facts only. Page numbers below are the standard's printed pages.

| Item (12 V system) | Value | Source |
|---|---|---|
| Supply range Us | min 6 / 8 / 9 / 10.5 V (codes A-D), max 16 V | 16750-2:2023 Table 3, p.3 |
| Jump start | 26 V, 60 +-6 s, rise/fall <=10 ms, USmin 10.8 V, at RT and Tmin; applies only to 12 V systems (simulates a 24 V source) | 16750-2:2023 4.3.1.2, Table 5, p.4-5. ST AN2689 p.6 says 24 V, 60 s (older text) |
| Transient overvoltage | 18 V, 400 ms, 5 pulses, 1 s rest | 16750-2:2023 Table 6, p.6 |
| Starting profile, level I-IV | US1 8 / 4.5 / 3 / 6 V; US 9.5 / 6.5 / 5 / 6.5 V; t1 15 ms, t2 50 ms; min status A/B/C by supply code | 16750-2:2023 Table 11, p.17-18 (level III = cold crank, aged battery: 3 V) |
| Pulse 4 (crank) | -6..-7 V, Ua -2.5..-6 V, t7 15-40 ms, t9 0.5-20 s. Note: -7 V normally seen only at the terminals of a solenoid starter | 7637-2:2004 Table 8 p.15; Annex B.2 p.20 |
| Load dump test A (no suppression) | Us 79-101 V, Ri 0.5-4 ohm, td 40-400 ms, rise 10 ms, 10 pulses at 1 min | 16750-2:2023 Table 13 p.20. (7637-2:2004 Table 9: 65-87 V) |
| Load dump test B (centralised suppression) | Us 79-101 V clamped to Us* = 27 (sev 1) / 30 / 32 / 35 V (sev 4), 5 pulses; requirement class C | 16750-2:2023 Table 14 p.21 |
| Reverse voltage | case 2: -14 V (12 V sys), 60 s, DUT connected and fused as in the car, no alternator/battery; after replacing blown fuses class A required. Case 1: -4 V for 60 s only if the alternator circuit is not fused and the rectifier withstands reverse. Not applicable to terminals with clamping diodes without external reverse protection | 16750-2:2023 4.7, Tables 15/16, p.22-24 |
| Ground and supply offset | +-1 V on GND and +-1 V on supply in 8 combinations; test "shall be agreed" | 16750-2:2023 4.8, Table 17, p.24-25 |
| ISO 7637 P1 | -75..-100 V, Ri 10 ohm, td 2 ms, 5000 pulses | 7637-2:2004 Table 3 p.9 and Table A.1 |
| ISO 7637 P2a | +37..+50 V, Ri 2 ohm, td 50 us, 5000 pulses | Table 4 p.11 (2011 ed. adds higher levels up to +112 V per a secondary Japanese summary - UNVERIFIED) |
| ISO 7637 P2b | +10 V, 0.2-2 s, Ri <=0.05 ohm | Table 5 p.12 |
| ISO 7637 P3a / P3b | -112..-150 V / +75..+100 V, Ri 50 ohm, td 100 ns, tr 5 ns, 1 h bursts | Tables 6,7 p.13-14 |
| P5a/P5b text | "In most new alternators, the load dump amplitude is suppressed (clamped) by the addition of limiting diodes" (2004). "Load dump may occur on account of a battery being disconnected as a result of cable corrosion, poor connection or intentional disconnection with the engine running" | 7637-2:2004 5.6.5 p.16 |
| ISO 7637-2 Annex B.2 | transients should be suppressed at the source; do not connect electronics to the starter terminals | p.20 |
| Ignition spikes | +150/-220 V spikes, radiated and conducted | ST AN2689 Fig.4 and text, p.6 (secondary description) |

Load dump with / without suppression: Diotec note says typical clamp "40 V in 12 V vehicles"; centralised suppression limits to 35 V (Diotec load_dump_v10 p.1 and p.2, VERIFIED text) and the surge "as high as 120 V, up to 400 ms". Monolithic Power primer: suppressed 32-40 V, unsuppressed peak "can exceed 100 V" (page fetch summary, UNVERIFIED-secondary). Nexperia AN50007 (Rev 1.0, 2021) p.13-18 reproduces the same Tables 2/3 (VERIFIED).

Does a 1990s alternator clamp it? Findings: (a) SAE 872002 (Oct 1987, Motorola) introduced alternator rectifiers switching to zener avalanche below 40 V "if a connection becomes intermittent during high charge" - so the technology predates the Miata (VERIFIED abstract via saemobilus.sae.org/content/872002). (b) ISO 7637-2:2004 says most new alternators are clamped (VERIFIED). (c) No source found for the specific Mazda/Nippondenso/Mitsubishi Miata alternators; a forum thread about a burned diode in a 1993 ECU is anecdotal. Verdict: UNKNOWN for Miata. INFERRED: clamping rectifiers were common in the 1990s but a worn or replaced aftermarket alternator may be unsuppressed. A battery-disconnect-while-running event is rare in normal use; the realistic trigger is a loose/corroded battery terminal.

## B. Worked TVS energy examples (INFERRED, arithmetic from datasheet numbers)

Method per MCC AN0005 (mccsemi.com AN5001/Rev02/070726, p.7-13, VERIFIED): Ipp = (Vs - Vc)/Ri; Ppp = Vc * Ipp; compare with pulse-power curve at td (derated ~45% at 105 C ambient; 50% margin). Their example: Vs 101 V, Ri 4 ohm, td 400 ms, Vc 35 V -> Ipp 16.5 A, Ppp 577.5 W; SM8S (6.6 kW) allows 2000 W at 88 ms; chosen SM8S22CA.

Cases for this project's parts (Vc, Ipp from kb/parts_manifest.md; test A worst case 101 V, 4 ohm, 400 ms):
- SMAJ33A (400 W, Vbr 36.7-40.6 V, Vc 53.3 V at Ipp 7.5 A): needed Ipp = (101-53.3)/4 = 11.9 A > 7.5 A rating, and the pulse is 400x longer than the 1 ms rating basis. FAILS test A. Clamped test B: Us* <= 35 V < 36.7 V, no conduction. PASSES by not conducting.
- SMCJ30A / 1.5SMC (1.5 kW, Vc 48.4 V at 31 A for SMCJ30A): Ipp = (101-48.4)/4 = 13.2 A, Ppp = 640 W; energy of exponential with tau = td/ln2 = 0.58 s: Q about 7.6 C, E about 370 J (an upper estimate, truncation at 14 V reduces it). Scaling the SM8S curve ratio (6.6 kW -> 2 kW from 1 ms to 88 ms, exponent about -0.27) to 400 ms gives about 0.3 kW for a 1.5 kW part at 25 C, less when hot. FAILS by about 2x or worse. A 5 kW part (SM8S/5KP) gives about 1 kW at 400 ms, about 0.55 kW at 105 C: marginal against 640 W. Hence MCC/Diotec use 6.6 kW SM8S for test A.
- Takeaway: for test A, TVS alone is the wrong tool for a small board; use series element (surge stopper / PFET with gate zener) or accept that the ECU will rely on the alternator being clamped. This is an exponent extrapolation from one datasheet curve, tagged INFERRED, confidence medium-low on the absolute number, high on "1.5 kW cannot do test A".
- ST AN2689 example (p.14-15, VERIFIED): Rd = (Vcl - Vbrmax)/Ipp; SM6T27AY with PPP = 392 W for ISO 7637 pulse; Vcl = Vbr + Rd*Ipp.
- Standoff rule (UNVERIFIED-secondary, several vendors and ST AN2689 p.13 "Vrm >= 13.5 V nominal"): TVS stand-off must be >= max continuous supply (16 V per 16750-2 Table 3, 24-26 V for jump start if the ECU must live through it). A 16 V stand-off part on a 12 V supply conducts in a jump start (26 V) and in a 35 V dump.

## C. Reverse polarity, sensor supplies, inputs, inductive loads (design practice)

- Reverse battery options (costs are from kb/parts_manifest.md JLCPCB prices where cited, else UNVERIFIED): series Schottky (SS34 0.0351 USD each at stock quantity per manifest; drops 0.5 V, cannot be used above the ECU current; B360A 0.1146 USD); P-FET high side (about 0.1-0.3 USD, low drop, needs gate clamp); the "fuse plus TVS crowbar" (TVS forward-conducts and blows fuse: the ISO test requires "after replacing blown fuses class A", i.e. a blown fuse is allowed, ISO 16750-2 4.7.3 p.24). Note the standard says a DUT with clamping diodes without external reverse protection is exempt from the test, which is the hobby-board loophole: the clamp then conducts in reverse through the wiring.
- Logic inputs wired into the car: series R and clamp to rail are fine only if the rail can sink the clamp current; if the clamp current exceeds the rail's load the rail rises (a 3.3 V LDO or buck cannot sink). The repo's N2/N9 fixes (BAT54WS to +3V3 after 5.6 k) are the textbook pattern; checking the rail pump-up needs a bleed load. UNVERIFIED as general practice (no primary source read); the repo simulates this itself.
- Inductive loads: a plain diode across an injector slows closing (forum, UNVERIFIED); TVS-clamp from drain gives a higher clamp (repo already does this). Fast clamp voltage vs closing time is outside what I could source primary.
- Ignition noise: ISO P3a/b 100 ns bursts at +-150 V/50 ohm (VERIFIED) are the model; the actual noise level in a Miata is not available to me.
- Ground: ISO 16750-2 4.8 requires tolerance of +-1 V GND offset between separate grounds (VERIFIED). For an ECU with separate sensor and power returns, sensor return must reference the same node as the ADC ground at the ECU; a +-1 V offset on a 0-5 V sensor is 20% of full scale, so ratiometric sensors referenced to ECU ground are the practice (INFERRED).

## D. Checklist of pass/fail criteria (each with source). (H) = most often violated by hobby ECUs (judgement, UNVERIFIED as a frequency claim; based on the common failure modes the sources emphasise)

1. Operate 9-16 V continuous; recover to full function from cranking dips down to 6 V (level I/IV) and 3-4.5 V for 15 ms (levels II/III) without a reset loop. Source: 16750-2:2023 Table 3, 11. (H: brown-out/reset behaviour in cranking)
2. Survive 26 V (older: 24 V) for 60 s with no permanent damage; function class C. Source: 16750-2:2023 Table 5. (H)
3. Survive -14 V for 60 s with the vehicle fuse in series; only the fuse may blow. Source: 16750-2:2023 Table 16, 4.7.3. (H)
4. Survive load dump test B (up to 35 V clamped, 5 pulses). Test A (101 V/4 ohm/400 ms, 10 pulses) only if the product is sold with no assumption about the alternator. Source: Tables 13/14.
5. TVS stand-off >= highest continuous supply (16 V; 26 V if jump start must be survived) and minimum breakdown above the clamped dump (35 V -> 33 V stand-off, 36.7 V min Vbr). Source: Diotec note p.1-2; MCC AN0005 p.7. (H: wrong stand-off)
6. TVS energy check: Ipp = (Us-Vc)/Ri, Ppp = Vc*Ipp, compare at the real pulse width with temperature derating (about 45% at 105 C) and 50% margin; a 1 ms rating is not a 400 ms rating. Source: MCC AN0005 p.7-13. (H)
7. P1 -100 V/10 ohm/2 ms through the supply: every part on the supply side withstands the negative spike (reverse-blocking diode, TVS bidirectional or clamped). Source: 7637-2 Table 3.
8. P2a +50 V/2 ohm/50 us on the supply: input TVS Vc below the weakest downstream rating at Ipp = 25 A. Source: Table 4; ST AN2689 p.21.
9. P3a/3b coupled bursts +-150 V/50 ohm: inputs have series R plus capacitor/clamp. Source: Tables 6/7.
10. Never connect a module to the starter terminal. Source: 7637-2 B.2 p.20.
11. Every wire leaving the case: series resistance and a clamp that survives battery short and 24-26 V; clamp current must be sinkable by the rail it clamps to (bleed or TVS at rail). Source: ST AN2689 3.1; repo N2. (H)
12. Sensor supply outputs (5 V sensor feed) are short-proof to battery and ground, with reverse-current blocked. Source: practice, UNVERIFIED (no primary read).
13. Ground offset +-1 V supply/ground combos: no false trips and no damage between power and sensor grounds. Source: 16750-2:2023 Table 17. (H)
14. ESD: every external pin protected against 8 kV contact / 15 kV air with 330 pF/2 kohm at least on pins reachable by hand; USB port on the dash side needs a TVS. Source: TI SLVA954B Table 2-1, 2-2; ST AN2689 p.5. (H)
15. Inductive loads: every inductive output has a defined clamp; injector clamp voltage vs closing time must be quantified. Source: repo VERIFICATION 'sim_inj_clamp'; forum, UNVERIFIED.
16. No device on the supply rated below the clamp voltage that can occur: 35 V at least (dump), 40 V where unknown. Source: Diotec p.1; ISO 7637-2 5.6.5.
17. Series Schottky or FET in the supply path rated for the fuse current. Source: practice UNVERIFIED.
18. Connector and terminal ratings used at actual current with temperature rise (typical 30 C rise rating; derate at 85 C ambient). Source: WE/Hirose/Harwin derating notes (search result only, not read) - UNVERIFIED.
19. Thermal: parts rated for 85 C cabin air plus local rise; on a footwell ECU no measured data found. Source: see section E.
20. Capacitors: voltage derating >= 35 V dump at the supply (so a 50 V part, not 25 V, on the raw supply) unless protected by a TVS; ceramic DC bias loss. Source: practice, UNVERIFIED.
21. CISPR 25 class 5 not required for a retrofit, but a buck regulator needs a small input filter and short hot loops; 2-layer feasibility shown by MPS application note and TI PMP30794 (both secondary, not read in full).
22. Moisture: conformal coat or at least connector sealing is recommended where condensation under carpet is plausible. Source: none read; UNVERIFIED.
23. Test: bench-test with a programmable supply for items 1-3 before first car use.
24. The fuse is part of the protection: size the fuse so that reverse-battery current through the TVS/FET blows it, not the traces. Source: ISO 16750-2 4.7.2.1 ("connect and fuse the DUT as in the real vehicle").

## E. Thermal environment (cabin)

- ASU press release (Temperature, 2018; six cars, Tempe AZ summer days "in the 100s F"): average cabin air 116 F (47 C), dashboard 157 F (69 C), seat 123 F after 1 hour in sun; shaded cabin average 100 F (38 C). VERIFIED as what the page says (page fetch https://news.asu.edu/node/78070 and search result), but it is a press page, not the paper; maxima are not given.
- A Jordan JMIE study reports up to 70 C cabin air and about 100 C dashboard for one car in Iraq (search snippet only, UNVERIFIED).
- No measurement of footwell ECU-location temperature was found. The 85 C figure in review brief is a standards-class number; ISO 16750-4 Table 1 (paid) not read.

## F. Implications for this project

| # | Implication | Evidence | Confidence |
|---|---|---|---|
| I1 | Document the protection baseline as "clamped alternator (test B, 35 V) only; an unclamped load dump (101 V, 4 ohm, 400 ms) would destroy D12 (SMAJ33A) and the SMCJ30A clamps". State this in install docs (unknown alternator condition, battery terminals must be tight, never disconnect the battery with the engine running). | Sections A, B | high for arithmetic, medium for energy extrapolation |
| I2 | The 26 V jump start (2023 edition; 24 V before) must be survived by every part on the raw supply; confirm all rail components have >=35 V (repo already lists 24 V as a design case). | 16750-2 Table 5 | high |
| I3 | Reverse battery: the repo relies on D1/D2 body-diode paths and fuses; ISO says test through the car's own fuse for 60 s and the fuse may blow. Reviewers should check which element blows and whether the PCB survives, not just the fuse. | 16750-2 4.7.3 | medium |
| I4 | Cold-crank brown-out: 3 V for 15 ms (level III) is the severe case; the board should hold the 3.3 V rail and not reset for at least 6 V. Check the buck's drop-out and the bulk capacitor. | Table 11 | medium |
| I5 | Ground offset +-1 V between sensor return and power return needs checking on the motherboard (sensor returns to ECU analog ground at a single point). | Table 17 | medium |
| I6 | ESD at the USB-C port (mounted inside the stock case, dash accessible via harness) needs ISO 10605-grade TVS, not only the USBLC6 (rated IEC 8 kV contact). USBLC6-2SC6 listed in manifest at 0.157 USD; fine for 8 kV, not for 25 kV air. | TI SLVA954B Table 2-2; manifest | medium |
| I7 | Heat: no real footwell temperature datum found; keep the repo's 85 C assumption but state it as assumption. | Section E | medium |

## Sources actually read

- ISO 7637-2:2004(E) corrected 2004-09-15 (E2E attachment): work/.../dl/iso7637_2004_e2e.pdf, tables pp.9-17, Annex A p.18-19, B p.20, F p.33-36.
- ISO 16750-2:2023(E) (lisungroup.com copy): dl/iso16750_2.pdf, pp.3-25.
- Nexperia AN50007 Rev 1.0, 2021-04-08, pp.3, 13-18: dl/nexperia_an50007_mirror.pdf.
- MCC (mccsemi.com) AN5001/Rev02 Quick guide load dump: dl/mcc_an0005_load_dump.pdf p.7-13.
- Diotec load dump brochure v10: dl/diotec_load_dump_v10.pdf.
- ST AN2689 Doc ID 14310 Rev 3: dl/st_an2689_e2e.pdf p.5-6, 13-15, 21.
- TI SLVA954B (Oct 2021 rev Aug 2022), ISO 10605: dl/ti_slva954.pdf p.2-3.
- Vishay 88490 / SM8S 88387 TVS notes (downloaded in the earlier run; only grepped for power rating text).
- Web (read through page fetch/web search summaries only, hence secondary): SAE 872002 abstract; Monolithic Power load dump primer; ASU hot-car press release; search summaries of MPS two-layer CISPR 25 note and TI PMP30794.
- Repo and kb: repo/VERIFICATION.md (grep), kb/parts_manifest.md (TVS rows).

## Not checked

- CISPR 25 limit numbers and test method (only secondary summaries).
- Capacitor voltage derating practice, ceramic DC-bias, conformal coating and humidity: no source read.
- Connector derating: search found general notes only; no TE/USCAR curve for the project's header.
- Footwell temperature measurement, ISO 16750-4 Table 1 (paywalled).
- ISO 7637-2:2011 (current pulse tables beyond secondary summaries); Mazda alternator rectifier type; ignition noise measurements; low-cost EMC for the two-board stack beyond MPS/TI summaries.
- Pre-existing downloads from the earlier run (Vishay) were not re-read in detail.
- The TVS energy figure for 400 ms is an extrapolation from one datasheet curve ratio.

## Files index (kb/research/files/R07/)
st_an2689_e2e.pdf (ST AN2689), mcc_an0005_load_dump.pdf, nexperia_an50007_mirror.pdf, diotec_load_dump_v10.pdf, ti_slva954.pdf (ISO 10605), iso7637.txt and iso16750_2.txt (text extracts of the standards, for reviewers to grep; printed page numbers inside).
