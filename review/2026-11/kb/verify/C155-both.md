# C155 verdict: confirmed (low, recommendation)
Checked: evidence/cur_mb8995 and cur_mb9697 pcb_nets.txt: OUT_IGN3 = J5.1+JD1.16, OUT_IGN4 = J5.2+JD1.17, OUT_BOOST = D5.2, J5.3, JD1.37 (+JP6.3 on 1989-95 only). No harness cavity on 96+ boards; on 89-95 boost reaches 2O only via JP6 pos 3 (default shunt 1-2 = AFM). repo/scripts/mb_na6.py:121,154.
Daughterboard: IGN3/4 = U7 (TC4427), Q18/Q19 (ZXMS6004 $0.60), R17/R18, R146/R147, D33/D34, C35; boost = Q7 VND7NV04 ($2.68, manifest) + R25, R158. Prices match manifest; the exact $2.03 / $2.69 sums not recomputed but plausible.
Documented: VERIFICATION.md:131 ("IGN3/IGN4 stay idle"), :921 (add-on header offers spare outputs, boost valve). Facts known; the removal saving (~$4.7) is not stated there.
Ordered boards: no (cur_db only; claim is a cost option, not an error).
Corrected statement: as stated, with caveat that J5 AUX header is a documented, advertised feature (boost valve, COP on 3/4), so removal is a product decision, not a free removal. Saving ~$4.7/unit parts only, before assembly fees.
Fix: feature-tier decision; optional DNP of Q7/Q18/Q19 group via BOM variant rather than removing the circuits.
