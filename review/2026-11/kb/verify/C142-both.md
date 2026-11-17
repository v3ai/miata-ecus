# C142 verdict: confirmed (doc/process issue, low practical weight)
- repo/scripts/bom.py:7 says every LCSC number was looked up 2026-10-28 (scripts/mpn.json) and nothing is left to flag; VERIFY = set().
- Checked: none of the 14 listed codes is a key in mpn.json (135 entries). Each is used in design.py or wideband.py (e.g. design.py:64 R1206 map, :275 C95063, :339 C155605).
- C25341 (R110, 62 ohm intended) is live-looked-up in kb/parts_manifest.md:90 as 1206W4F620LT5E = 0.62 ohm. So the gap hides a real wrong part. It is a separate finding; mpn.json is only read by order_bom.py (self-order BOM), not a checker.
- "44 unused" not reproduced exactly (my crude regex gave 27, noisy); count is approximate.
- Not documented in VERIFICATION.md/review brief (grep). Not hardware: affects no ordered board by itself.
Fix: make bom.py fail on any LCSC code absent from mpn.json or whose MPN/value disagrees with the parts manifest.
