# C021 source verification (PRIMARY SOURCES lens)
Verdict: PARTLY (JLC 35% prepay verified from JLC's own page; US duty stack and HS code only secondary/unverified here).

Checked
- JLC FAQ saved text (kb/research/files/R21-jlcpcb-cost-model/j_https___jlcpcb.com_help_article_us-tariff-policy-faq.txt) and Tariff-us.png (viewed): PCB 35%, SMT 35%, Stencil 90%. Section 2.2: 35-90% rates are an average, "will not refund or charge the difference". Individuals must use DDP (section 5). PCBA are treated as intermediate products. TRUE as stated.
- JLC page lists Section 301 25% and its own "122 tariff 12.5% from Jul 24 2026" (JLC's label). The claim's reinterpretation as forced-labor Section 301 (9903.05.31) rests on gingercontrol.com (secondary, line 116) plus R26's Federal Register citations; I did not re-fetch the Federal Register. De minimis suspension: only secondary text re-read (gingercontrol); the exact dates 2026-06-24/07-24 in R26.08 not re-checked.
- HS: saved USITC json (kb/research/files/R26/hts8537.json) confirms 8537.10 exists with 2.7% general for the 8537.10.9x lines. The CBP ruling N275130 and whether 8537.10.91 is on a Section 301 List 1/3 were NOT verified by anyone (R26 says so). The "about 40%" stack and "12.5%-55%" range are therefore inference. Note JLC itself charges 35%, so the stack cannot be tested.
- Not stated by JLC: whether the 35% applies to components JLC sources/fits (R21.08 premise "MAP $29 -> $10 duty" is unverified). The claim text "JLC prepays 35 percent" is slightly loose: JLC collects it from the customer in advance; the true customs bill may differ, and no true-up occurs.
- "At q=10 duty on a set about $25 (range $9-40)" is arithmetic on R21's unverified PCB estimates (R21 says PCB estimate UNVERIFIED); goods value ~$72/set. Plausible, not sourced.

(a) Already documented? No mention of duty/tariff in the review brief or repo/VERIFICATION.md (grep). It is news, though a business-cost item, not a design error.
(b) Ordered boards: not applicable; these are already ordered, only affects landed cost of the next order / selling price at $399.
(c) Recommendation: budget 15%+ is a floor; the verified planning number is JLC's 35% (flat, checkout-visible). "Buy THT parts domestically to save ~$10" depends on unverified component-duty treatment; the saving may be zero.

Corrected statement
JLCPCB pre-collects US DDP duty of 35% on PCB and SMT lines (90% stencil), flat, no true-up (verified on JLC's FAQ and rate table, 2026-10-29). Individuals must ship DDP. Independent estimate of the real stack (2.7% MFN + 25% Section 301 if listed + 12.5% forced-labor 301, de minimis gone) is about 40% but HS code listing and 232 status are unverified. Whether 35% is charged on JLC-fitted components is unknown. Severity: medium for a pricing input (about $25 per set at q=10, estimate).

Fix
Use JLC's checkout DDP line as the real number once a quote exists; get a broker/CBP view on 8537.10.91 and 301 list membership only if selling in volume; do not rely on the "buy MAP locally" saving until JLC's quote shows whether components are taxed.
