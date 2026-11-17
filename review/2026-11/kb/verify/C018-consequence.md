# C018 consequence check
Verdict: partly (true, but a non-finding about the design).
Checked: kb/research/R10-processor-choices.md lines 9-15, 30-35, 61-65, 104 (rusEFI readme, AT32 port is F435/F437, issue #8396 open, GD32 0 hits); kb/parts_manifest.md U1 lines 11/233 (ord_db and cur_db both use genuine STM32F407VGT6, 126 pcs at JLC, 5.05/3.34 USD).
Consequence: no board uses a clone, so nothing is broken and ordered boards are unaffected (they already carry the ST part). Saving is ~0.6-1.0 USD of a ~399 USD product (~0.2%), far less than one failed unit. Real risks of clones (APM32 NVIC bits 3 vs 4, flash programming, ADC cal, same ID 0x413) confirm "do not ship". Severity high is overstated: it is an info-level "do not do" note; the actual issue is that ST stock at JLC is only 126 pcs (supply risk), which is the thing to watch.
Not in review brief sec 6 as far as seen; research file already documents it.
Fix: none needed; keep ST part, buy MCU stock ahead / consign from franchised distributor.
