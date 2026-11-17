# C008 consequence check
Verdict: partly. The facts are true. The severity "high" is overstated, and the finding is already documented.
- Ordered db rev 0.9 has no series resistor between U11 (SN74LVC4245) and Q1-Q8 (VND7NV04) inputs. This matches kb/findings B03.02 and B18.04 (delta_db). ST datasheet (datasheets/txt C155605) Table 2: RIN MIN 150 ohm, IIN +-20 mA.
- Consequence: U11 drives 5 V, below VINCL of 6-8 V. IIN is about 0.1 mA, and the 15 mA Igf fault sink is within U11's 24 mA. Normal switching cannot reach 20 mA. The risk is limited to out-of-range events (ESD, transients, rail excursion) and edge rates faster than ST characterised. ST states no mechanism. The uaEFI field failures (R01.04) are second-hand and I did not verify them.
- Already documented: repo/VERIFICATION.md line 64 and open item A1 (line 746: "applies to the ordered rev 0.9 boards"). Not news.
- Affects the ordered boards: yes. Current rev 0.10 has R152-R159.
- Fix: 8 hand rework sites on DPAK inputs (cut track and bridge with 220 ohm 0402/0603). It is delicate, but it works. A cheaper option is to accept the risk, scope gate and drain at bring-up, and fit the resistors only if the first-power tests show a problem. The B18.04 view of medium severity is right.
