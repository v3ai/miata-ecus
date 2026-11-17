# C110 verification: own enclosure option / printed shell lacks EMI shield
Verdict: PARTLY (qualitative points true; all dollar figures are unquoted estimates; mostly known to the repo; not an ordered-board issue)

Checked:
- clusters.json C110 and medplus.jsonl R28.02/R24.07/R24.08: every one is verification "inferred", R24.07 confidence low; the authors say "no quote".
- Cost basis is not about this product: SendCutSend price is for a 9x6.6 in plate benchmark, Hammond 1455T2201 $42.25 is an aggregator price, the MJF rate is a UK vendor (JLC3DP rate not found). I did not re-quote; the $8-35 range is unsupported.
- Repo already documents the root problems: README line 91 ("stock case has to be cut" for wideband, USB-C, MAP hose, ribbon) and line 253 (1996-2005 case geometry is a placeholder); review brief s6 lists the placeholder outline and the 1989-93 hot case. So the "case-outline placeholder risk" half is not news. The business idea (sell own enclosure, keep customer ECU intact) is new but is a product decision, not an error.
- "Plastic gives no shield / poor heat path" is generic physics; true for unfilled plastic. Stock-case-as-heat-path evidence rests on one rusEFI wiki note (not re-read). The fix (metal lid, thermal pad) is reasonable but unquantified; no thermal data in the repo shows the stock case is needed.
- Ordered boards: no. This is a packaging option for future units; nothing to rework by hand. The ordered boards use the NA outline and stock case regardless.

Corrected statement: Offering an own enclosure (printed or bent aluminium) would avoid cutting customers' stock ECU cases and sidestep the 96-05 case-geometry placeholder, but a plain printed shell loses the stock aluminium case's shielding and heat spreading, so use a metal shell or lid on the hot 1989-93 variant. Cost per unit is unquoted ($12-35 is a guess); get JLC3DP/JLCCNC quotes before relying on any number.
Severity: low (option/idea, no defect). 
Fix: get real quotes at 10 and 100 units; measure stock cases first; if printed, add aluminium lid + thermal pad over drivers/regulator.
