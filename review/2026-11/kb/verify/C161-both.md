# C161 verdict: partly (true but already documented, not an error, low value)
Checked: ext/hellen-one/modules/ign8/0.2/ign8-BOM.csv = U460 SN74LVC4245A + 8x 10R, nothing else (confirms Hellen ign8). Project BOM (evidence/cur_db/sch_bom_grouped.csv): ign path adds U13 74HCT04, Q16-Q19 ZXMS6004FF, D31-D34 B5819W, R144-R147 3.3k; plus U11/U12 LVC4245 level shifters, Q1-Q8 VND7NV04, Q9-Q15 ZXMS6004FF. Same ZXMS/B5819/LVC4245/74HCT04/TC4427 present in evidence/ord_db BOM, so the ordered boards have them too (not a rework item).
Documented: repo/VERIFICATION.md H1 (line ~208, 5 V gates via LVC4245 deliberately for AUIPS2041 4.0-5.5 V input spec) and rows ~569-570 (protected ignition fixed deliberately). Not news.
Not verified: Speeduino TC4424A+2.4k and Hellen injector 3.3 V gating, "about a dozen parts" (actual count is larger, ~20 incl. outputs).
Corrected statement: the project deliberately adds protection and 5 V gating beyond Hellen/Speeduino; documented design choices with stated rationale, not an error or free removal.
Fix: none needed; optional cost-down only by dropping protection, which is a design tradeoff.
