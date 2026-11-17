# C034 verify: SOT-23 CPL +180 vs community -90
Verdict: partly (unverifiable on the key point: which rotation JLC's model actually needs).
Checked:
- repo/scripts/order_bom.py JLC_ROT: `^(T?SOT-23)` -> +180, comment "seen on SOT-23 and SOT-23-5; SOT-23-6 assumed". VERIFICATION.md ~288-293 documents the same, and review brief s.6 says JLC rotations for new parts were never checked. So not news.
- Community table (matthewlai JLCKicadTools, ^SOT-23 = -90): could not fetch (all raw URLs 404). Bouni's current table also not retrievable. It is old, secondary, and its convention (KiCad version, sign) is not shown to match this CPL. A 90 deg difference between tables of different conventions does not show the repo is wrong; the repo value is a direct primary observation of JLC's preview (rev 0.5). Hellen reference CPLs in ext/ could not be used (their pcb files carry no usable refs).
- Applies equally to ordered rev 0.9 (same JLC_ROT) and current: yes, ordered boards affected, if wrong; BAT54S/A diodes (D15-18, D35-37) would be mis-oriented.
Corrected statement: The repo's SOT-23 +180 rests on one JLC preview observation; an old secondary table disagrees (-90). Which is right is not settled by anything checkable offline. Risk is real but already disclosed; severity low-medium. The 7 SOT-23 diodes were in a preview (rev 0.5); the SOT-23-6 USBLC6 (B05.01) is the genuinely unverified entry.
Fix: check D15-18, D35-37 and U4 in JLC's placement preview/ DFM step for the ordered boards before assembly is confirmed (free).
