# C023 source check
Verdict: PARTLY.
Checked:
- repo/INSTALL.md lines 322-326 (First start): step 3 "Crank... engine starts" comes BEFORE step 4 base-timing check; no mention of disabling fuel / injector fuses / plugs / fire danger. TRUE.
- repo/firmware/README.md items 111-112 and 249-251 (step 11): timing check documented, "Always: check base timing before first drive"; restore to dynamic IS stated ("Then set Timing Mode back to dynamic"; INSTALL says "Unlock it again"). So R11.02's "does not warn fixed timing must be restored" is FALSE.
- rusefi_book.txt 821-889: rusEFI procedure = disable injection, remove injector fuses, remove plugs, fire extinguisher, fixed timing, crank with fuel off, adjust Trigger Angle Advance, restore fuses. TRUE (a tutorial for setting trigger offset on engines whose offset is unknown; here the offset is preset by Miata presets).
- "No Miata preset sets globalTriggerAngleOffset": not verified by me (pinned rusefi path not found at expected glob); F02.07 itself is "inferred". The "incumbent MSPnP" part is third-party-manual based, not re-checked.
- Not in VERIFICATION.md as an open item (grep found no timing-light item), but the check itself is documented, so only the safety wording is news.
Ordered boards: no hardware effect; docs/firmware only, applies to the ordered boards' first start equally.
Corrected statement: INSTALL.md/firmware README do instruct a timing-light check (and restoring dynamic timing), but INSTALL orders it after the first start, and neither document includes rusEFI's disable-fuel/pull-injector-fuses/pull-plugs fire-safety steps. Real severity: low-medium (doc).
Fix: in INSTALL step 4 add: do the check before first start with injection disabled/injector fuses out (rusEFI book p.23-24), then restore. Optional firmware default fixed timing is a design choice, not an error.
