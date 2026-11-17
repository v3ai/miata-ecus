# C044 verdict: partly (numbers true; "disagree" is not a defect; already documented; firmware only)

Checked myself:
- rusEFI table (repo/firmware/ext/rusefi/.../mazda_miata_vvt.cpp, lines 135-155): 99.5 kPa row = 28 at 4144/4884 rpm, 30 at 6787, 31 at 8000; 157.7 kPa row = 24 at 6787, 25 at 8000. Matches the claim. Copied unchanged in repo/firmware/board/miata_nb_tune.cpp (line 159).
- Speeduino NB8B PNP msq advTable1: 96 kPa row = 11 deg at 4700-5200, 9 deg at 7200. Matches.
- But NB8B is a generic, very conservative Speeduino base tune (8 deg at 100 kPa high rpm); a stock NB 1.8 at WOT does not run 9-11 deg, so the 18 deg "disagreement" says the Speeduino file is a safe placeholder, not that rusEFI's NA load rows are wrong. The 28 deg at 99.5 kPa row is the naturally aspirated WOT region; it is not a boost problem.
- Boost rows (158 kPa, 24-25 deg at 6800-8000 rpm) are plausibly aggressive for 91 octane at about 8.7 psi (typical pump-gas boost tunes pull to the high teens/low 20s). This rests on forum rules of thumb, not a measurement; "unsafe" is unproven. Those rows only matter on a car with a turbo/supercharger, which the stock car lacks.
- Already documented: repo/README.md line 85 ("base tune is a starting point... nobody has tuned them under boost"), INSTALL.md line 327-328 ("first drives: light throttle only... nobody has tuned it under boost"), firmware base-tune link. Not in review brief s6 explicitly, but the repo warns the same thing.
- Ordered boards: hardware unaffected. It is a firmware/tune table, changeable by reflash, no rework by hand.

Corrected statement: rusEFI's NB ignition table (used unchanged) has about 24-25 deg at 158 kPa/6800-8000 rpm, which is likely aggressive for 91 octane boost; the repo already says the tune is untested under boost. The Speeduino comparison is of little value (generic conservative tune).
Fix: optional, cap the table above ~120 kPa to ~15-18 deg in the shipped tune; low effort, firmware only. Wording already exists.
