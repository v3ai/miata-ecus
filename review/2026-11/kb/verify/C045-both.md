# C045 verdict: confirmed (true, but already documented; ordered boards affected)
Checked: evidence/ord_db/pcb_nets.txt line 2: +12V includes R11.1, F1.2, D12.1, L1.1; line 201: VBAT_IN (J1.1/2, D7.2, D6.1, R120.1) has no R11. So R11 (33k, divider into AN_VBATT) sees the voltage after D7 (SS34) and F1 (nSMD050 PTC). The divider only draws ~0.3 mA, but the drop is that of the whole board load (buck converters, ECU) through D7+F1, hence load/temperature dependent.
Magnitude: repo/VERIFICATION.md says 0.3-0.4 V (line 251) and 0.4-0.6 V (line 678). Claim says 0.4-0.8; I did not measure, 0.4-0.6 is the repo's figure.
Already documented: VERIFICATION.md lines 251 and 678 (confirmed for next revision, not changed); firmware note 6.
Affects ORDERED: yes (ord_db rev 0.9). Hand rework: cut R11 pad 1 and wire to VBAT_IN (J1 pin 1); or firmware offset trim.
Corrected statement: ordered db R11 senses +12V after D7 and F1; VBATT reads ~0.4-0.6 V low, load dependent. Known item, not news.
