# C081 verdict: partly (price true; electrical equivalence only partly checked)
Checked:
- BOM (evidence/cur_db and ord_db sch_bom_grouped.csv:30): D19-D26,D30,D38,D39 = 11x BAT54WS C124205 on both ordered and current daughterboard.
- Live prices (tools/lcsc.py today): C124205 $0.0937@50, $0.0843@150, $0.0768@500. C7502694 (HJC, extended+preferred) $0.0127@1, $0.0107@500, stock 46.8k. C3040452 (Fuxinsemi) $0.0128@1, $0.0103@500, stock 73k. 7-9x confirmed. Saving 11 x ~(0.094-0.012) = ~$0.9/board at qty 50, ~$0.75 at qty 500. All three are Extended, so no basic/extended fee change.
- Nets: D19-D26 clamp AN_ nodes (incl. AN_VBATT, AN_VIGN) to +3V3; D30 is WB_VDDA to +3V3. Fix text's "VBATT/VIGN clamps" = D38/D39: correct.
- Both clone datasheets list VRRM 30 V, IFSM 600 mA; HJC Tj 125 C (Diodes 150 C). LCSC lists IR 2 uA for both.
Not verified: the 3x hot-leakage claim (curve read from graph by the originating audit; I did not re-read it). Fuxinsemi pin polarity unconfirmed.
Already documented: no (VERIFICATION.md only records the BAT54WS leakage CHECK, line ~526, not clones). Not news-breaking; small saving.
Ordered boards: affected only as a rework option (not worth hand-swapping 11 diodes); matters for next revision.
Corrected statement: BAT54WS-7-F could be replaced by C7502694/C3040452 for about $0.75-0.9/board; electrical equivalence at 25 C per datasheet, hot leakage unverified (possibly ~3x worse), and Tj max 125 C vs 150 C. Medium severity is overstated: low.
Fix: next rev use clones for sensor clamps D19-D26 after confirming polarity/leakage curves; keep Diodes for D38/D39 (VBATT/VIGN) and D30 if desired.
