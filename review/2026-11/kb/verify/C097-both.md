# C097 verdict: partly

Checked:
- TE drawing 178780 rev P10 (work/P19b-harness-header-76p-64p/dl/lcsc_C5166246.pdf, rendered): mounting block says "76x dia 1.35 +-0.10, position dia 0.2"; section views show lead 0.64. TRUE.
- Repo scripts/mk_hdr_fp.py:42 drill 1.1, pad 1.8. evidence/ord_mb9697 J1: 76 pads drill 1.1. TRUE for 1996-97.
- ord_mb9900 J1 is TE 176122-6 (64P), also drill 1.1, but the TE drawing checked is for 178780 only; no 176122 drawing was available, so TE's recommended hole for the 64P is unverified.
- Arithmetic: 0.64 sq diagonal 0.905; 1.1 - 0.905 = 0.195 diametral clearance, against 0.2 position tolerance (0.1 radial) plus fab tolerance. Marginal, not proven interference: the 0.2 tolerance is on hole position relative to datum (pegs), and the connector pin pitch error is separate and unknown. Hellen (NB1/NA6) uses the same 1.1 hole (audit measured 1.09982); I did not rebuild that check, but the audit's note is consistent. Whether Hellen boards were actually built with this footprint and the real header seats is not proven here.
- Not in review brief section 6 or VERIFICATION.md open items (grep): not documented.

Corrected statement: TE recommends 1.35 +-0.10 for 178780; the repo uses 1.1 (same as Hellen). Clearance to the 0.905 post diagonal is about 0.2 mm, equal to the position tolerance, so seating is marginal; fit untested. Applies to ordered 1996-97 (178780, TE data confirmed) and, by inference only, 1999-2000 (176122).
Ordered boards: yes (ord_mb9697, ord_mb9900). Rework: test-fit a header; if tight, open holes to 1.3 mm. (Those boards already have placeholder outlines and an unavailable header, so priority is low.) Severity: low-medium (needs a physical test; likely workable).
Fix: drill 1.3-1.35 with pad 1.8 (annulus about 0.22) on next revision; JLC accepts.
