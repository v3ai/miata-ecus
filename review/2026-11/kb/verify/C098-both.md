# C098 verdict: partly (wiki quote true; applicability to this board's hole unverified)
Checked: work/B13.../web/mre_na48.html lines 220-226 say one hole (J27) of the NA case needs 3 M4 washers (recessed thread, stock heat sink). True as quoted, and "washers may be included with your kit".
repo/INSTALL.md step 4 says use stock screws in six M4 holes; no mention of washers or recessed hole (grep: none in INSTALL/VERIFICATION/README). Kit/additional-parts list has no washers.
Not verified: that one of this repo's six holes (H1-H6, ord_mb8993 footprints) sits at the recessed J27 location; the wiki fact is about the MRE board's hole and the case, which is the same NA case, but hole coordinates were not compared with a case or MRE KiCad file. Also the wiki gives no dimensions beyond "3 M4 washers".
(a) Not documented by repo, so news. (b) Affects ordered boards only as an assembly/kit item, no rework of the PCB. Severity low-medium (doc/kit).
Fix: add a caution to INSTALL step 4 (one hole has a recessed thread; stack washers or a spacer until the board sits flat, check on the real case), add 3 M4 washers to the kit.
