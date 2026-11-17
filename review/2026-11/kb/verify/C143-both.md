# C143 verdict: confirmed (trivial, low)
- mb_na8.py:57 calls base.build_parts(HARNESS, paired_injectors=False, ...); mb_na6.py:189 `def build_parts(harness=None, idle_pullup=True, tps_links=True)` has no such arg -> TypeError if run. 
- No importer: grep finds mb_na8 only in mb_make.sh:22 (file copy list). mb_export.py uses importlib on argv, but nothing passes mb_na8. trigger_select defined only in mb_common.py:138, no caller found in grep.
- Current/ordered 94-95 generator is mb_y9495.py (exists); mb_na8 is a stale legacy module (header/CHANGES stop at rev 0.9, still HARN_IAT/JP1).
- (b) Does not affect ordered hardware: ordered-boards/2026-11 holds the frozen KiCad outputs; dead script cannot alter them. Regeneration caveat is only about scripts.
- (a) Not checked in VERIFICATION.md beyond a grep for mb_na8 (no hit seen); minor housekeeping, not news of any consequence.
Fix: delete mb_na8.py (and from mb_make.sh list) and unused trigger_select.
