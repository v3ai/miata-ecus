# C061 verdict: confirmed (true, low severity as a risk; not news in substance)
Checked:
- FSM 1994 wiring p.10 (work/PIN-9495-A-design-outward/m94_wiring.pdf, rendered): fan relay K104 coil fed BLK/WHT from ENGINE fuse 15A (run/start), coil ground BLK/GRN to PCM B1-01 (1L) and the DLC. No thermoswitch in the drawn circuit. VERIFIED.
- Board: ord_mb9495 pcb_nets.txt:35 OUT_FAN -> J1.1L / JD1.9. VERIFIED.
- rusEFI mazda_miata_1_6.cpp:282-285 NA94 preset: fan 100/96, fan2 95/91. VERIFIED. Repo miata_board.cpp:325-327 applies setMazdaMiataNA94() for the 94-95 preset, so these are the shipped defaults. Stock thresholds not found; "100 C is late" is opinion.
Not shown: that the stock ECU turns on lower; consequence "overheats" only if the user disables/misconfigures fan, so risk is conditional.
Documented? INSTALL.md only lists JP3 FAN2 and the fan as a feature; no explicit "ECU is sole fan control, verify in tune" warning found. Not in review brief sec 6. Mild news.
Ordered boards: yes (same wiring; firmware-level mitigation only, no rework needed). Fix: documentation plus a default on-temperature around 95 C and a fan-on test at first start; consider fail-on when CLT sensor faults (rusEFI has fan-on behaviour on bad CLT? unchecked).
