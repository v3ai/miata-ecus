# C040 verdict: partly (hardware fact true; consequence unverifiable)
Checked:
- Ordered and current 2001-05 boards: net OUT_TACH has only J1.3O and JD1.11 (evidence/ord_mb0105/pcb_nets.txt:50; ord_mb9697 net is J1.4L). Q14 ZXMS6004 low side drives it. No pull-up on any 1996-2005 motherboard. True (ordered and current).
- Hellen NB2 (ext/hellen-miata-NB2/hellen72_NB2.xml:4312): 3O connects to OUT_PP2 of the output module M5, i.e. push-pull. True.
- BUT rusEFI hellenMiataNB2/NB1/NA96 connectors/main.yaml list tach as "type: ls" (low side), so "rusEFI maps it high-side" rests only on the Proteus wiki page and is contradicted by rusEFI's own Hellen yaml. Pin 3O tach pin, 2 pulses/rev OK.
- The real question (does the cluster/TCM input idle high without a driver) is not answered by any file. The scope image shows 0-12 V, which means the stock ECU either sources or the cluster pulls up; both are possible. Repo docs it only for the NB alternator wire (review brief s6 "NB alternator wire may need a pull-up"); the 3O/4L/2K tach pull-up is not documented, so partly new.
- Title says 1996-2005 "(3O)": 3O is only 2001-05; 96-97 is 4L, 99-00 is 2K.
Corrected statement: no 1996-2005 board has a tach pull-up and Hellen drives 3O push-pull; whether the stock cluster needs one is unmeasured. Risk of a dead tach (cosmetic, plus TCM IG- sharing on A/T), not damage. Medium is generous; low-medium.
Affects ordered boards: yes, hand rework possible (pull-up pad from 12 V to OUT_TACH, ~1-4.7k).
Fix: car test (key on, ECU unplugged, measure 3O/4L/2K); if 0 V, add 1k to a switched 12 V, else nothing.
