# C115 verdict: partly (facts true, saving overstated and trivial; not news; ordered boards unaffected)

Checked
- Live JLC 2026-11 (tools/lcsc.py): NCV8406ASTT3G C459816 SOT-223 extended, stock 4875, $0.4468 at 100. VND7NV04TR-E C155605 extended, stock 2391, $1.8164 at 100 ($1.66 at 1000). Delta $1.37 per channel: true. E-L9826TR C155567 $1.7313 at 30, stock 951: true.
- Datasheet NCV8406A.txt: VDSS 60 V, EAS 110 mJ, RthJA 100 C/W (min pad), Ilim 5.0/7.0/9.5 A: matches. JLC lists Rds 185 mohm typ. The 210 mohm at 25 C figure was not rechecked.
- L9826 datasheet: current limit and thermal shutdown only on outputs 1 and 2 (Ilim 0.5-1.1 A): matches.
- Repo: Q1-Q8 are VND7NV04 on cur_db (parts_manifest line 56). NCV8406A was the rev 0.9/0.7 part and was replaced for thermal reasons (VERIFICATION.md lines 267, 510, 567).

Corrections
- The saving is 4 x $1.37 = about $5.5 per board only if Q5-Q8 are the four 1 A channels. It adds a second extended-part line (NCV8406A) and a new SOT-223 footprint. VND7NV04 stays on Q1-Q4. JLC charges the extended-part fee once per unique part per order, so the saving per unit is smaller on small runs.
- Hot dissipation of about 0.5 W at 1 A is arithmetic from 445-520 mohm hot: correct (I x I x R). The 1 A valve currents are from the repo's own docs (VERIFICATION.md line 1149), not measured.
- The VND7NV04 gives 6 A current limit and 200 mJ clamp. The NCV8406A is weaker in Rds, and it already failed the repo's own thermal test on injectors. For 1 A loads it is plausible, but this is untested.
- The L9826 part is "not recommended" by its own finding (about $1.7 saving, loses per-channel limiting, needs SPI firmware). Not worth acting on.

(a) Not in review brief section 6 or the open items as a cost idea, but the history (NCV8406A replaced by VND7NV04) is documented, so the drivers' trade-off is known.
(b) Ordered boards: no. The ordered rev 0.9 daughterboard already carries NCV8406A, so the finding is a design-respin idea for rev 0.10 only.
(c) Premises true (prices, specs). Benefit real but small (about $5.5 per board, less the extended-fee and footprint/respin cost), and it trades away current-limit margin and thermal headroom with no bench data.

Fix: none needed now; optional rev 0.11 cost item after the bench measures actual idle/VVT/boost/alternator currents and driver temperatures.
