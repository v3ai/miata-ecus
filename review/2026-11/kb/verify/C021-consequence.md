# C021 consequence check: US duty on JLCPCB assemblies
Verdict: partly (true as a budget fact; severity overstated; the "35 percent" and the classification rest on an image and on inference).

Checked
- The JLC FAQ page text in kb/research/files/R21-jlcpcb-cost-model/ (us-tariff-policy-faq, updated 2026-10-29) says: individuals ship DDP; the "35%-90%" rates are flat averages, "we will not refund or charge the difference"; total rate "about 35%~92.5%". It also says PCBA are intermediate goods, so the exempt electronics HS codes do not apply. The per-line table (PCB 35 / SMT 35 / stencil 90) is only in the Tariff-us.png image. I did not re-read it, but the audit's note says it did, and the text is consistent with it.
- Not in review brief section 6 or repo/VERIFICATION.md (grep: duty/customs/tariff only match injector duty cycle). So it is news.
- HS 8537.10.91.60 at 2.7% under CBP ruling N275130 is VERIFIED per R26 (not re-fetched). Whether 8537.10.91 is on the legacy Section 301 25% list is UNVERIFIED. The 12.5% forced-labour duty (FR 2026-15181) is cited. The 40% and 55% figures are inference.
- Arithmetic: $72.5 goods value per set at q=10 x 35% = $25.4. That is about 6% of the $399 price, and about 8% at q=5 ($32). Not critical.

Consequence
- Cost and margin only. No circuit or firmware effect.
- JLC's flat rate means the actual rate does not matter if JLC is the importer of record on DDP. The budget number is 35% of the JLC-invoiced PCB+SMT value. The 40% and 55% scenarios only matter if the owner switches to CPT.
- The "buy THT parts locally" lever is real, but whether JLC applies the 35% to component lines is unverified (R21 says so). The MAP saving of about $10 per set is therefore unconfirmed.
- The suggested fix "budget at least 15% duty" is too low. The only verified number is 35%, so budget 35% (as R21 itself says). "Plan formal entry with a broker" is unnecessary at this size. DDP through JLC is mandatory for an individual, and a company can pick CPT. Cheaper fix: a one-line budget entry plus one question to JLC support (does the 35% apply to parts lines?).

Ordered boards: the current order is already placed. Duty is a landed-cost issue on the shipment, and the rework logic does not apply. Duty on those boards is about 35% of their invoice, payable at checkout or on a later payment link.

Corrected statement: JLC pre-collects a flat 35% (image table, PCB and SMT; stencil 90%) on US DDP orders with no true-up. De minimis is gone. Planning cost is about $25-32 per set at q=5-10 (6-8% of the $399 price). The independent 40% and 55% scenarios and the 8537.10 classification are inferred, not verified.
Severity: medium.
