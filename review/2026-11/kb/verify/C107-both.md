# C107 verdict: confirmed (as a conditional geometry fact), severity low
Checked: evidence/cur_mb9900|9697|0105 pcb_pads.csv. Board origin (100,50), outline 154.0 x 161.5 (mb_na6.py:14). J2 NPTH pegs at y=209.1 -> 159.1 rel; J4 shield pads y=208.68 -> 158.68 rel (J4 centre 207.6). Against a 159.0 outline J2 pegs/body and the USB-C shield pads are outside/on the edge. Arithmetic true; J2 courtyard to ~162 too.
Hellen NB1 outline 154.0 x 159.0 R7, 1A at (15.99,21.42) per B11 notes (kb/B11 line 29); not re-extracted by me but consistent with the audit's script.
Caveats: (1) purely conditional; the 159 mm outline comes from Hellen's Camry-case (hellen-NB1 issue #3), not shown to match the customer's Miata case, and the repo already says the 1996-2005 outline/holes are NA placeholders (review brief s6; VERIFICATION). So the real action is to measure the stock case; J2/J4 move is a follow-up. (2) Header shift of 3.29 mm is down, away from the problem; J2/J4 would need >=2.5 mm up (not 3.5 needed; ~3.5 gives margin).
Ordered boards: no, the ordered 1996-2005 boards (rev 0.7) keep the same outline; the claim concerns a hypothetical new outline, so nothing to rework.
Already documented: partly (outline is a placeholder, documented); the J2/J4 consequence is not.
Fix: when the case is measured, set H and move J2/J4 up >=2.5 mm in the layout script and reroute.
