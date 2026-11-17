# C031 verdict: partly

Checked: evidence/*/pcb_footprints.csv and pcb_pads.csv (J1), repo/README.md l.175-176, repo/research/pinouts_9605.md l.29,123, kb/boards/B13 notes.
- ORDERED 1999-2000 board (ord_mb9900) fits TE 176122-6, the 64-pos stock part (68 pads, J1 x span 111.4 mm). It does NOT carry a 76P header, so the "76 vs 64 window" problem does not apply to it. The 76P (178780-1, 80 pads incl. mounts, span 123.3 mm) is on CURRENT cur_mb9900 and on 1996-97 (ordered and current).
- 1996-97: 76P is what Hellen NA8-96 ships (pinouts_9605.md l.29); fit is plausible, not proven.
- Case variants (929, Australian, 89661-32590) are forum posts quoted in B13 notes; unverified hearsay but plausible.
- Repo already says 1996-2005 outlines/holes are placeholders (review brief s6; README table "provisional (NA outline)") and README l.176 notes the 64P/76P difference; VERIFICATION.md l.1113 says "fit-check a real plug first".
## Corrected statement
Case height/holes for 1996-2005 are unmeasured (already documented). The 76P-in-64P-window risk applies to current 1996-97/1999-2000 boards (and ordered 1996-97), not to the ordered 1999-2000 board, which uses the stock 64P. Ordered 1999-2000 board risk is only case height/holes (placeholder NA outline).
## Fix
Measure one real case per generation; fit-check a plug against 76P before moving 1999-2000 to it. Low value as news.
