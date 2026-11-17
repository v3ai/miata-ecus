# C001 source verification: CONFIRMED
- Ordered and current fab BOM: R110 value 62, 1206, LCSC C25341 (repo/ordered-boards/2026-11/daughterboard/fab/miata-ecu-daughterboard-rev0.9_jlcpcb_bom.csv; evidence/ord_db and cur_db BOMs).
- R110 pads: pin1 LSU_RT, pin2 LSU_IP (evidence/ord_db/pcb_pads.csv:501-502).
- tools/lcsc.py C25341: JLC and LCSC both "1206W4F620LT5E ... 620mOhm, +/-800ppm". Uniroyal datasheet (datasheets/txt/C25341*, sec 2.4.3): 11th code L = 10^-3, so 620 x 10^-3 = 0.62 ohm.
- tools/lcsc.py C17971: 1206W4F620JT5E, 62 ohm, 1 %, 100 ppm, Extended, stock 123k, $0.0053 at qty 1 (J = 10^-1).
- Source: repo/scripts/wideband.py:153 (R10 -> C25341) and design.py:64 LCSC_R1206['62']. wideband.py:33 comment shows rev 0.5b moved to 0603 C23222, but the 1206 mapping still uses C25341 (the shipped BOM is 1206).
- Not documented: grep of repo/VERIFICATION.md for C25341/C17971 finds nothing. Not an open item.
- Affects ORDERED boards: yes (ord_db rev 0.9 BOM has C25341).
Correct statement as written. Impact: pump-current sense about 100x too small, so lambda reads near 1 (arithmetic from 0.62 vs 62 ohm; not measured). I did not re-derive the firmware gain.
Fix: hand-replace R110 on ordered boards with 62 ohm 1 % 1206 (C17971) or 61.9 ohm; change LCSC_R1206['62'] and wideband.py:153 to C17971; add script check of LCSC resistance vs value.
