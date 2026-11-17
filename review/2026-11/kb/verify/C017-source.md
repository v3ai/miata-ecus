# C017 source verification: verdict PARTLY (true facts, but already documented; "invented" is wrong)

Checked:
- repo/firmware/board/miata_nb_tune.cpp:51-66: rows for 116, 135, 158, 185, 220 kPa are all 80 at every RPM. TRUE. Row 99 kPa ends 65-77.
- The file says (line 6, 27, 139) the tables are "copied from rusEFI mazda_miata_vvt.cpp, unchanged". ext/rusefi/.../mazda_miata_vvt.cpp:87 holds the same table (TS2C export 2017). So the flat 80 is upstream rusEFI's fill, not invented by this project.
- STFT: miata_board.cpp:173-174 maxAdd 10, maxRemove 5 in power region. TRUE.
- 1.6 table reuse: miata_board.cpp includes mazda_miata_1_6.h; the 1994-97 years use it. F02.10 was only "inferred" by its audit; VE values were not measured against anything.
- Already documented: repo/firmware/README.md:108-111 ("1994-97 run a fuel table made on a 1.6 ... NB table above about 100 kPa is a flat 80 %... turbo car needs a tuner before full throttle", STFT limits at :101-104); VERIFICATION.md:719-720 "Not checked, can't be without a car".
- Ordered boards: firmware is flashed, not board hardware, so no rework; it applies to any ordered unit running the shipped tune.

Corrected statement: NB VE above 116 kPa is a flat 80 (rusEFI upstream filler, copied unchanged); 1994-97 use the 1.6 rusEFI table. Both limitations are already disclosed in firmware/README.md and VERIFICATION.md. Not news; severity for a naturally aspirated Miata is low; relevant only to boosted cars, which the README says need a tuner. The "high" severity and "invented" wording are overstated.
Fix: optional: raise the boost-region lambda target / add TunerStudio notice; stock NA cars are unaffected.
