# C159 verdict: partly (low-value negative finding; conclusion stands, details off)
Checked live 2026-11-16 (tools/lcsc.py): VND14NV04TR-E C2649436 = $1.36 @100, extended, stock 1897 (true).
VND7NV04TR-E C155605 = $1.82 @100 ($1.66 is the @1000 tier), so it is MORE expensive: the conclusion "not cheaper" holds.
"About 6 A limiting, not adequate" is wrong: VND7NV04 datasheet (datasheets/txt/C155605*) Ilim = 6 min / 9 typ / 12 max A, VND14NV04 = 12/18/24 A.
Cold LSU heater peak ~12-14 V / 2.5 ohm = ~5-6 A, so VND7 is marginal, not clearly inadequate; irrelevant as it costs more.
"No cheaper equivalent" is overstated: VNN3NV04PTR-E C443999 (ST OMNIFET, SOT-223, extended, stock 1288) is $0.87 @100 (saves ~$0.49); different footprint, datasheet not in pack, current limit unread (likely lower than needed for cold-heater inrush). Other searched ST parts (VND5N07, VND10N06, VNP10N07) cost more.
Plain-MOSFET saving figure (~$1.2) is unchecked; same-sentence admits datasheet unread.
(a) Not documented in VERIFICATION.md as such, but not news and no action. (b) Affects ordered boards: no (cost only; ordered boards use same part, nothing to rework).
Fix: none; keep VND14NV04. Optional: evaluate VNN3NV04P Ilim vs heater inrush for ~$0.5/unit, needs new footprint.
