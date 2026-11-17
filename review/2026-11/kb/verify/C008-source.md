# C008 source verification
Verdict: partly (fact true; not news; severity overstated as "high")
Checked:
- evidence/ord_db/pcb_nets.txt: /Outputs/INJ1_IN..INJ4_IN, IACV_IN, VVT_IN, BOOST_IN, ALT_IN each = Qn.1 + R19-R26.1 + U11.x directly (no series R). cur_db has R152-R159 (220R) between U11 and Qn.1/R19-26.
- Datasheet C155605 txt line 284: RIN MIN 150 ohm (abs max table, IIN +-20 mA); Eas/tr/tf quoted with Rgen=150 ohm.
- Repo already documents it: VERIFICATION.md A1 (line ~746) "applies to ordered rev 0.9", and "The ordered rev 0.9 boards" section gives the hand rework (lift pin 1, bridge 220R 0603). So not news.
- Mechanism not quantified by ST (B18.04): at 5 V drive IIN ~0.1 mA, below clamp 6-8 V; risk only under excursions/ESD. The uaEFI field-precedent (R01.04) was not re-checked by me; leads only.
Corrected statement: Ordered rev 0.9 daughterboard has no series resistor on the 8 VND7NV04 inputs (U11 outputs drive pin 1 directly), violating ST's 150 ohm RIN MIN rating; effect unquantified, normal drive well inside limits. Already documented as A1 with rework. Severity medium.
Fix: optional hand rework as in VERIFICATION.md (8 sites, 220R 0603 in series with pin 1), or accept and scope at bring-up.
