# C099 verdict: partly
Checked: evidence/{cur_db,ord_db}/pcb_footprints.csv: no TP*/FID*/Fiducial/TestPoint footprints (true). J3 (F407 SWD, Tag-Connect TC2030) top; J102 (F103 SWD) bottom, both boards.
Not accurate: claim omits that the F103 is normally flashed via its UART bootloader from the F407 (README.md ~L200-204, VERIFICATION.md ~L192-200); J102 is documented as a fallback only. Bottom placement matters only for recovery of a bricked F103 (needs mate removal, 4 standoffs). Claim "F103 has no USB" true but irrelevant. DFU via motherboard USB-C is documented design.
Fiducials: JLC SMT assembly does not require them; low-impact. Test points: absence true, only matters for production test of a first-run handful; Tag-Connect pads are themselves test access.
Affects ordered boards: yes (same), but nothing to rework except hand-probing pads. Partly documented (J102 fallback in README).
Corrected: no TPs/fiducials (true, low-medium convenience); J102 bottom is a fallback path only, primary F103 flashing is over UART from the F407. Severity low.
Fix: optional TPs for 3V3/5V/GND/NRST on next rev.
