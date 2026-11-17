# C058 verification: buck output capacitance vs TI 47 uF remark

Verdict: PARTLY (facts true, "risk" unprovable either way; already documented in part).

Checked
- TI LMR14020 datasheet text (datasheets/txt/C187824_LMR14020SDDAR.txt, section 9.2.2.4 in this revision A copy; claim cites 7.2.2.4 of rev B): quote "For stability consideration, one 47 uF output capacitor is needed at least" is verbatim. It sits in the 1 MHz, 7-36 V, 5 V/2 A design example (line ~983-1098). No scaling formula for fSW or L is given. True.
- Board: C22, C23, C59, C26 are all 10u 0805 C15850 on +5V, in BOTH ord_db and cur_db (evidence/*/pcb_footprints.csv), plus 1 uF C34/C35 and 100 nF parts on the rail. 4 x 10 uF = 40 uF nominal, so it is below 47 uF nominal; X5R derating at 5 V plausibly leaves ~25-30 uF (not measured). RT 10 k gives ~2.3 MHz, L2 10 uH (design.py:225-241). True.
- Ordered boards (rev 0.9) already include C59, so the ordered count matches current.

Not true or overstated
- The TI sentence is the most stringent criterion of an example, not a stated stability requirement of the part. The part has internal compensation and a 200 kHz-2.5 MHz range; at 2.3 MHz (2.3x the example) with the same crossover physics a smaller Cout is generally tolerable. Nothing in the datasheet shows instability here. Evidence of a defect: none. It is an unmeasured margin question.
- Not news: repo/VERIFICATION.md line 218 lists "Buck output capacitance about 20 uF (TI example 47 uF)" and the fix (third 10 uF, C59). What is not documented is the residual shortfall after the fix.
- Suggested hedge "22 uF 10 V 0805 X5R" loses most capacity at 5 V DC bias, so it adds little; a 22 uF 1206 or 47 uF 6.3/10 V part, or simply one more 10 uF, is better.

(a) Mostly already documented (partial). (b) Affects the ordered boards, but only as an unmeasured risk; hand rework would be soldering one more cap across +5V/GND, only worth doing if the bench check shows ringing.

Corrected statement: The 5 V buck has 4 x 10 uF (40 uF nominal, est. 25-30 uF effective) plus ~3 uF of 1 uF caps, versus TI's 47 uF example remark for a 1 MHz / 5.5 uH design; the datasheet does not make this a requirement at 2.3 MHz / 10 uH. Severity low. Fix: on the first board scope the 5 V rail with a 0.2-2 A load step (check ringing/phase margin), and, if desired, add one 22 uF 1206 X5R 10 V or a 47 uF cap.
