# C162 verdict: unverifiable (arithmetic right, inputs are guesses)
Checked: work/R21-jlcpcb-cost-model/model.py line 9: db6 {10:70,50:250}, db4 {10:36,50:130}. (70-36)/10=3.4 and (250-130)/50=2.4, so the arithmetic matches. The inputs are the audit's own estimates (its notes say +-40%, quote "recollection", one JLC 6L 100x100 anchor "from $35.1" and a 2023 blog price per m2). No real JLCPCB quote was obtained, so the saving is not verified.
ENIG on 6L: audit notes cite the JLC capabilities page; plausible, not rechecked.
(a) Partly known: VERIFICATION.md documents the 4L->6L move (rev 0.10) as a routing decision, not a cost one. (b) Ordered boards (rev 0.9 daughterboard) are already 4L, so nothing to rework. Only the current rev 0.10 is affected. (c) Not a recommendation of change; the saving is unquoted.
Corrected statement: 6L vs 4L is probably a few dollars per board (about 1% of the $399 price), but the figure is an unquoted estimate.
Fix: get a real JLCPCB quote for both stackups at 125x76 mm before citing a number; none needed otherwise.
