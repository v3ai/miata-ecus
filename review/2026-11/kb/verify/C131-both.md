# C131 verdict: partly true, already documented (not news)
The facts are plausible (sourced from MegaSquirt MSPNP manuals, not rechecked by me). But the repo already covers them.
- repo/INSTALL.md section 7 (lines ~296-311): GM open-element IAT on an adapter for the AFM plug (1990-93), the two wires at the plug (1994-97), the stock IAT plug (1999-2005), and the TunerStudio curve entry. It links the MiataSource and Speedy EFI adapters.
- repo/INSTALL.md section 5 (lines 258-270): MAP hose routing through the washer-bottle plug or the grommet, the cruise-control tee, and the parts list (4 mm barbed tee, hose at line 114).
- The "verify the board's IAT input handles GM sensors" item is already in VERIFICATION.md ("GM-type CLT/IAT option", line ~581).
Ordered boards: the IAT is on the harness signal on all boards (the dedicated IAT plug was removed after rev 0.11/0.7); the issue is install documentation, not hardware, and nothing needs hand rework.
Fix: none. At most, add the "tee and hose in the kit" suggestion (a kit decision).
