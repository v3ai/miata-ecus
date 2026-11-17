# C080 verdict: partly (low-medium, firmware only)
Checked:
- repo/firmware/wideband/miata_f1/mcuconf.h:225 STM32_WDG_USE_IWDG FALSE, halconf.h:194 HAL_USE_WDG FALSE; identical in upstream ext/wideband-mck1117 (f1_dual, f1_rev3). No watchdog: TRUE, same as upstream.
- ext/wideband-mck1117/firmware/heater_control.cpp:60-80: HeaterAllow::Unknown (no CAN command seen since boot, can.cpp:59) falls back to battery voltage (>9.5 V for 0.5 s) and starts heating. TRUE, but this is deliberate upstream standalone behaviour, not a repo bug. Preheat is still 2 V (condensation phase) for 5 s, then 7 V ramp. It only triggers if the ECU never sends any wideband CAN message; once the ECU sends NotAllowed the heater stays in preheat.
- Hang scenario (timer PWM keeps running while CPU hangs, heater stays at last duty) is plausible by design but not demonstrated; no test or datasheet figure checked beyond that. "Full battery voltage" is the worst case only if duty was high at hang time.
- Not documented in repo VERIFICATION.md/README (grep for watchdog/IWDG/auto-start: none) so it is news.
- Ordered boards: hardware identical (F103 + R126 pull-down on WB_HTR_PWM, evidence/ord_db pcb_nets). Fix is firmware only (flash over SWD/bootloader); no rework needed.
Corrected statement: Wideband F103 firmware (as upstream) has IWDG disabled and heats autonomously from battery voltage if no CAN allow/deny message ever arrives; both are inherited upstream design choices with firmware-only fixes. Severity low-medium.
Fix: enable IWDG (STM32_WDG_USE_IWDG TRUE, HAL_USE_WDG TRUE) and kick it from the heater loop; optionally build with a no-CAN-no-heat option for in-car use where the ECU always sends allow.
