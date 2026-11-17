# C094 verdict: partly (premise true for Speeduino, consequence does not transfer)
Checked:
- Speeduino NA6 v1.3 (ext/speeduino-hardware/PNPs/Miata NA6/Latest/outputs.sch ~l.529-696): fuel pump is a VN5160S-E HIGH-SIDE smart FET (U8) whose output goes to net ST_Sig (connector.sch l.117). A stock-wired 12 V on that pin back-feeds the high-side output. Field reports are therefore plausible (kb/research/R03: wiki, forum t=4583, SpeedyEFI review; I did not re-fetch the web sources).
- This project: OUT_FP is a LOW-SIDE ZXMS6004FFTA (Q9, C95063, 60 V IntelliFET) on J1.6 -> mb pin 2T (evidence/ord_db/pcb_nets.txt:174, ord_mb8993 pcb_nets.txt:40, sch_netlist Note "protected low side, FP"). Pin 1C is a separate input (VIGN_IN/starter) not the pump driver. A low-side switch with 12 V on its drain when off is the normal state; no back-feed damage mechanism, no fuse needs pulling. INSTALL.md 1990-93 section (l.170) already covers the real pump trap (AFM contact / F/P wire to 2T).
- Not in review brief/VERIFICATION as an open item; but not news-worthy either: no action on this project.
Affects ordered boards: no (topology identical there; hazard absent).
Corrected statement: Speeduino-specific trap (high-side driver on ST_Sig); this design's low-side driver on 2T is not exposed to it. Residual: confirm on first power-up that nothing on stock 2T is a driven source (low-side FET tolerates 12 V, rated 60 V).
Fix: none; optionally one INSTALL line noting no fuse removal is needed.
