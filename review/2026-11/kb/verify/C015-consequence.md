# C015 consequence check
Verdict: partly. Stock facts true (tools/lcsc.py today: C46641168 JLC 57, LCSC 55, extended, single source; C960026 194k, $0.11@1, $0.0887@50, same 1812, 2A hold/4A trip/30V/40A, 20/100 mohm; C18198342 62k, $0.0838@50). F2 (9900) / F2,F3 (0105) use C46641168 in ord_mb9900/ord_mb0105 BOMs.
Consequence: 57 pcs = 57 boards of 9900 or 28 of 0105. Not an error in the ordered boards; a prototype/small-batch order is covered. Only a volume run (>28 0105 boards) or stock drift to ~0 before the order is assembled blocks it. Parts are also ~$0.007/board, so the swap is cost-neutral. Severity: low/medium (supply risk, not a defect), not high.
Fix: swap to C960026 in the next release (same footprint, no layout change; both extended so no fee change). For the ordered boards: nothing needed unless JLC reports shortage at assembly; then substitute C960026 as a drop-in by JLC engineer note.
Not documented as an open item in VERIFICATION.md (grep found nothing relevant).
