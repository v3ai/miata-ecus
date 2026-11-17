# C014 source verification
Verdict: partly (facts true; not news; severity overstated)
Checked:
- evidence/ord_mb9900 parts_list/self_order_bom: J1 = TE 176122-6, footprint TE_176122-6_64P, hand-fit, "salvage or clone". pcb_pads: 64 positions (22+16+26) + 4 pegs.
- tools/lcsc.py C5171845: JLC "176122-6" extended, stock 0, $0.0398@1 (data error); not on LCSC.
- Distributor numbers (Avnet/Newark MOQ 1600, Sager 160 @ $12.61, 0 stock) come from Findchips snapshots in notes; I did not re-pull them (secondary, unverified by me).
- 76P vs 64P footprint: 2A is 5.95 mm after 1V in the 64P layout (pads), the 76P adds a 12-bay between plugs (P19b note: 20.7 mm shift). Not re-derived from the 76P footprint myself.
- Already documented: repo/VERIFICATION.md line 1113 says 176122-6 is obsolete at Mouser, buy headers ahead, TE "not currently available"; review brief section 6 lists "harness headers are hard to buy". README.md:176 notes the car's own is the 64-pos 176122-6.
Affects ordered board: yes (rev 0.7 ordered 1999-2000), but the part is hand-fitted and not in the JLC BOM, so it only blocks assembly, not fabrication.
Corrected statement: the ordered 1999-2000 board needs a 64-pos TE 176122-6 (or 174518-7 equivalent), with no authorised cut-quantity stock found (reel MOQ 1600; broker/Sager ~ $12-18); the repo already knows headers are hard to buy. Severity: medium (supply, known). The "not this part" JLC listing is a stock-0 price error.
Fix: salvage from stock ECU (the car's own ECU has it) or Sager/broker quote for few pieces; Ballenger CONN-100747 identity unverified; do not swap to 76P on ordered board.
