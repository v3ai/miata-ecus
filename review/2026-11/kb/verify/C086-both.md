# C086 verification: F407 DFU entry vs slow 8 MHz crystal

Verdict: partly (real risk class, the cited facts are accurate, but nothing shows this design is affected).

Checked:
- Hellen-one issue 79 (GitHub API): comment quotes "the bootloader waits 800us for the clock to start ... our clock is locking in ~900us"; the failing boards were Hellen 144/176-pin F407 (H64a/b); the fix tried was a different oscillator, and the F407 Discovery oscillator on the same PCB worked. Hellen NB2 issue 5: 176-pin F407 fails, 100-pin Discovery F407 and F427/F429 pass. rusefi issue 4847: auto-reboot after DFU differs by batch for the same F407ZGT6 part number (a separate matter, after-flash leave/reset).
- The "800 us" figure is an informal Hellen developer comment, not an ST document. "Moved to 20 MHz" is not in the issues I read.
- This project: both ord_db and cur_db use Y1 = C115962 (YXC X50328MSB2GI, 8 MHz, 20 pF, 80 ohm ESR) with 33 pF C0G loads (VERIFICATION.md:220), on a 100-pin F407VGT6. That is the same kind of 8 MHz fundamental crystal as the F407 Discovery that worked, but with 33 pF loads and 80 ohm ESR (slower start-up than a low-ESR 8 pF crystal). Start-up time was never measured and the repo has no mention of the 800 us / issue 79 (grep of VERIFICATION.md, README, research).
- The design has a BOOT0 button, BOOT1 pulled low (R72, H3) and reset button, so hardware DFU entry exists; software DFU (reboot_dfu) is the exposed path.

Corrected statement: A 2021 rusEFI/Hellen issue showed STM32F407 boards whose HSE start-up (~900 us per developer) exceeded the ROM bootloader's reported ~800 us limit, making software-requested DFU loop back to the app; it was seen on 144/176-pin Hellen boards and not on a Discovery. This board uses an 8 MHz 20 pF/80 ohm crystal with 33 pF loads, so the same failure is possible but unconfirmed. Medium is high for an unmeasured risk; low-medium fits.

Ordered boards: applies to ordered rev 0.9 daughterboard (same Y1 C115962), but can only be fixed by swapping the crystal or the caps by hand. Better action is to test first: HSE start-up on a scope and software DFU on the first board, with the BOOT0 button as fallback (hardware DFU is not affected the same way unless the reset loop occurs, which in issue 79 also hit the PROG-button path).
Already documented: no.

Fix: on first board power-up, test software and button DFU 5+ times; scope OSC_OUT start-up; if slow, reduce loads toward ~20-24 pF (C0G) or substitute a lower-ESR crystal.
