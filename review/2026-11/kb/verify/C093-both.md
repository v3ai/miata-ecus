# C093 verdict: confirmed as a fact, but not news and not a defect
- Fact: repo/research/pinouts_9605.md lines 8, 164, 254, 256 already record the NB CKP/CMP as 3-wire Hall sensors fed +12 V from main relay terminal D (A), signal (B), ground to PCM 4A (C), citing the 2005 FSM, Haltech and Hellen NB2. Independent sources agree. I did not re-read the Mitchell manual text.
- Design: ord_mb0105 pcb_nets: IN_HALL1 = J1.3Y-JD2.13, IN_HALL2 = J1.3V-JD2.14. The motherboard only passes the signal through. The pull-up is on the daughterboard (ord_db: R61/R62 for HALL1, R63/R64 for HALL2, 4.7k series and 1k pull-up, then a 1N4148WS clamp to 3V3 in rev 0.10). It is not on the motherboard and does not supply the sensor, as the claim says.
- The suggested check is moot. The sensor output is open-collector, so its 12 V supply does not set the logic high level. The high level comes from the 5 V pull-up, which does not change with the 12 V supply. VERIFICATION.md covers the hall inputs with sims and real NB2 captures.
- MAF is not a board input. The grep of the 2001-05 nets shows no MAF net. The claim's MAF part is unchecked and irrelevant to the board.
- Ordered boards: they carry the same pass-through, so nothing needs reworking.
- Fix: none. Severity is info.
