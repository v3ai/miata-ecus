# C133 verify: stock-function matrix per year
Verdict: partly (documentation suggestion, not a defect; already mostly covered)
- The claim describes the incumbent MS-PnP's coverage (from vendor images in files/R04, not re-checked here), not this project. It is a UX/docs suggestion with no design fact to refute.
- repo/README.md lines 30-82 already has a "By year" table (injection, VVT, knock, alternator, main relay, O2 heater, TPS) plus a limitations list: VICS wired but not set up (l.103), automatics untested (l.104), no EGR/purge/VTCS, 1990-93 fuel pump and TPS caveats. INSTALL.md has per-year pin tables.
- Missing: a single works / does not work / needs jumper matrix per stock function (idle, fans, A/C, clutch, tach, pump, CEL), and the website does not carry one (not checked in depth).
- Ordered boards: not affected; documentation only.
Corrected statement: README has a partial per-year table and a limitations list; a full per-function matrix is still absent. Low-effort doc improvement, severity low.
Fix: extend the README "By year" table with rows for idle, fans, A/C, clutch, tach, pump, CEL, and copy it to the product page.
