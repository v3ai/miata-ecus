# C138 verdict: partly (true mechanism, overstated consequence)
Checked:
- repo/INSTALL.md:163 does say "Leave a USB-C cable plugged in and run it to the glovebox or centre console". INSTALL.md:128 and README.md:54 advertise microSD logging. Neither mentions power order. grep of VERIFICATION.md and review brief found no mention, so it is not documented.
- FOME doc (work/R11.../Basic-Features_Data-Logging.txt): "SD card logger works only when the ECU is powered without a USB connection (or if usb is connected a few seconds after the car has been started)". Matches the claim.
- Pinned rusEFI repo/firmware/ext/rusefi/firmware/hw_layer/mmc_card.cpp ~1120-1130: if engineConfiguration->alwaysWriteSdCard then SD_MODE_ECU; else if usbConnected then SD_MODE_PC. So a mitigation exists: the alwaysWriteSdCard setting.
- Board: USB_VBUS net goes to D10.2 and J2.32 (evidence/ord_db/pcb_nets.txt), so USB VBUS is diode-ORed into power. A bare cable with nothing at the far end has no VBUS, so it does not trigger PC mode.
Corrected statement: the logging conflict is real. It only occurs if the far end of the cable is a host that supplies VBUS at key-on (a laptop that is already on, or a phone or charger). A cable left dangling is harmless. The advice to leave it run to the console is fine for tuning. It needs one line about SD logging: unplug before starting the car, or plug in only after the engine runs, or set alwaysWriteSdCard (the card then cannot be read over USB).
Severity: low (docs only). Ordered boards: not a hardware issue, no rework (ordered=false is right). Not already documented.
Fix: add a note to INSTALL.md section 3 or the logging section; verify alwaysWriteSdCard behaviour on the first board.
