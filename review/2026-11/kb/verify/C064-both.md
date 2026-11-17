# C064 verification: Vane AFM output level conflict between manuals
Verdict: partly (fact true as a notes-level observation, consequence overstated; low value).
Checked:
- kb/research/R16 line 28-29 and R17 lines 73,110 do record 3.8/3.3 V (1990) vs <1 / 1-2 V (1994-96). I did not re-read the manual images; the repo-level fact is only as good as that transcription. 1994-97 Miatas also use a vane meter (VERIFICATION.md:117), and R17 mislabels it "hot-wire MAF" from rusEFI wording, which is a likely source of the apparent conflict (different measuring condition/terminal).
- Board input: IN_AUX3 -> R43 5.6k series -> AN_AUX3 with R44 10k, C43 10n, BAT54WS clamp D26 (evidence/ord_db and cur_db pcb_nets.txt, footprints). Divider 10/15.6 = 0.64, so 5 V full range gives 3.2 V at the MCU; any polarity or level between 0 and 5 V (even 12 V via clamp) is safe. Hardware is polarity-agnostic.
- Firmware: AUX3 is only mapped as MAF/AFM input; the NA presets are MAP-based (PIN-8993-A line 62), so the VAF signal is unused by default. A level conflict affects at most a future VAF-calibration, not any ordered-board function.
- Documentation: not in VERIFICATION.md/README/INSTALL (grep for 3.8 V found nothing). Only in audit notes. So not documented by repo, but it is not a board defect.
- Ordered boards: input circuit identical on ord_db (rev 0.9); no rework needed.
Corrected statement: Manuals give differing VAF voltages (unresolved transcription/measurement question), but the input divider/clamp accepts either, and firmware does not use it; no board error. Severity low/info.
Fix: none for hardware; optionally one measurement on a car before writing any VAF-based firmware.
