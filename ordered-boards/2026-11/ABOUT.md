# Boards ordered in November 2026

This folder is a frozen copy of the design as it was ordered, so it stays usable after the main design moves on.
Nothing in here is edited again. The same state is the git tag `ordered-2026-11` (commit `4f34615`); the tag also has
the build scripts, the 3D viewer and the shop drafts, which are not copied here.

| Board | Folder | Revision | Harness header |
|---|---|---|---|
| Daughterboard (all years) | `daughterboard/` | 0.9 | – |
| 1989–93 motherboard | `motherboards/1989-93/` | 0.11 | TE 174917-6, 48 pins |
| 1994–95 motherboard | `motherboards/1994-95/` | 0.9 | TE 174917-6, 48 pins |
| 1996–97 motherboard | `motherboards/1996-97/` | 0.7 | TE 178780-1, 76 pins |
| 1999–2000 motherboard | `motherboards/1999-2000/` | 0.7 | TE 176122-6, 64 pins |
| 2001–05 motherboard | `motherboards/2001-05/` | 0.7 | TE 353830-5, 72 pins |

## What is here

- `daughterboard/`, `motherboards/`: KiCad files, Gerbers, BOM and placement files, schematics, each board's README.
- `README.md`: what these boards can and can't do. `INSTALL.md`: fitting one to a car, with labelled pictures.
- `VERIFICATION.md`: every check that was run and what is still open. No board had been built or tested when this
  copy was made.
- `additional-parts/`: the parts to buy besides the boards.
- `firmware/`: the rusEFI board files for these boards. Build this firmware for them, not a later one: later board
  revisions change the pin map. (`git checkout ordered-2026-11` gives the complete tree to build from.)

## Known points on these boards

- **Tachometer, 1989–95:** the firmware drives the tach wire (2I), but on a stock car the igniter drives the
  tachometer and that wire is the igniter's signal into the ECU. With the stock igniter, switch the tach output off
  in TunerStudio. It is only wanted after a coil-on-plug conversion with the igniter removed.
- **Add-on fuse:** the AUX header's 12 V pin holds 0.5 A. A boost valve takes most of that.
- **Sequential injection on 1989–93** needs solder links (R23–R26), described in that board's README.
- **Flex fuel, nitrous arming:** AUX pins 12 and 13 can serve as inputs with a firmware setting; not bench-checked.
- No CAN on a connector, no microSD.

These boards and later revisions use the same two 40-pin board-to-board connectors, but later motherboards may expect
daughterboard functions these do not have. Pair the boards in this folder with each other.
