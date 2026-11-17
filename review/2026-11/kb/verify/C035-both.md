# C035 verdict: partly (true, but small and dominated by the sensor's own tolerance)
Checked:
- Datasheet C435835_LDL1117S33R.txt:195-199: VOUT accuracy +-2 % at 25 C, +-3 % over -40..125 C. True.
- Evidence ord_db pcb_nets.txt: IN_CLT/IN_IAT pull-ups R33/R36 go to V5_EXT, and the MAP sensor is on V5_SENS, so they follow +5V. ADC reference is +3V3A (FB1 from +3V3), so the rails are independent. True.
- firmware miata_board.cpp:31 adcVcc=3.3 fixed; MPX5700AP curve assumes Vout = 5 V x (...). No VREFINT or 5 V compensation. True. (The shipped and ordered miata_board.cpp differ; the claim is not affected.)
- Arithmetic: r = (V5/5)/(V3/3.3). With 5 V +-2.4 % and 3V3 +-3 %, worst r is +-5.4 %, so about +-5.4 kPa at 100 kPa and +-11 kPa at 200 kPa. The claimed +-7 / +-13 kPa matches the +-6.7 % worst corner (+-3.7 % on 5 V) from P07.02, not the 4.88-5.12 V figure. Typical about half. The ordering of magnitude is right; the exact numbers are corner-dependent.
- Context: MPX5700AP's own span tolerance is +-2.5 % of span (about +-17.5 kPa), larger than this effect. Not news about the sensor itself.
Already documented? Partly. VERIFICATION.md:692 documents MAP +-2.5 % accuracy and the MPX4250AP option, but the ratiometric / rail-independence mismatch is not mentioned. Key-on baro correction partly absorbs the MAP offset.
Ordered boards: yes, it applies equally (same topology); only firmware calibration or hand-rework with a wire to a spare ADC pin can address it. Not worth rework.
Corrected statement: ADC reference (3V3 LDO, +-3 %) and sensor 5 V (+-2.4..3.7 %) are independent; worst-case gain error is +-5.4..6.7 %, typical under 2-3 %, i.e. about +-5..7 kPa MAP at 100 kPa and a few K on CLT/IAT. Smaller than MPX5700AP's own tolerance. Low-medium.
Fix: bench-calibrate MAP gain/offset (baro at key-on); optionally a 10k/10k divider from V5_EXT to a spare ADC input in a future revision. Alternatively pull CLT/IAT to +3V3 (requires re-deriving bias resistors).
