# C029 source check: verdict PARTLY
Checked: repo/website/products/products.json (all 5 "You add" rows): "A Bosch LSU 4.9 sensor ... and its lead, a vacuum hose, your stock ECU case". Literally true that the storefront omits IAT, TPS (1989-93 manual; the body text does mention adding a sensor, but not the cost/part), TunerStudio, tune.
Repo does document IAT (INSTALL.md s7, README "Air temperature sensor") and TPS kit (README ~206-230), so for the repo it is not news; storefront-only gap.
TunerStudio: RE Ultra shows 99.99 sale / 129.90 regular on efianalytics browse page (search today; product page shows a 9,999.99 placeholder). Whether registration is required is not shown to be mandatory (free Lite exists; claim that auto-tune needs it not verified by me).
The "530-620 USD" total is not derived anywhere: R05.03 is "inferred", medium confidence (LSU 119.20 from ECUMaster kit, IAT GBP 12-20, TS 50-80 secondary). 399+119+~15+(0..100) = about 533-633; plausible range but unsourced arithmetic, and TS cost is optional.
Not affecting ordered boards (website/UX only). Competitor MM9697 $1,199.99 inclusions not rechecked.
Corrected: Storefront lists only LSU sensor+lead, hose, case; IAT (needed if AFM/airbox removed), TPS for 1989-93 manual, optional TunerStudio licence (~$100) and tune are not priced. Rough all-in is about $530-630 if TS bought; ~$530 without.
Fix: add "Cost to a running car" block / optional starter kit on product pages. Severity medium (ux), not high.
