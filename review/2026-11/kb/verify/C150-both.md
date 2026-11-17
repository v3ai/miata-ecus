# C150 verdict: partly (conclusion sound, details loose, nothing actionable)
Checked: work/R10-processor-choices/dl/jlc_search_f103_alts_2052.txt (live JLC data), kb/parts_manifest.md:98, repo/firmware/board/wideband_uart_flash.cpp:51,268, VERIFICATION.md:312-361.
- ST C8734: $1.4611..$0.9326, stock 191k, preferred. True. Repo already says F103 is only emulated (VERIFICATION.md:356).
- Top-tier clone prices: CH32 C2687451 $0.69, APM32 C393540 $0.78, CKS32 C556576 $0.87 (stock 421, true), GD32 C77994 $1.04 (dearer than ST), FCM32 C3151837 $0.45 (stock 819). Savings are therefore 0.06-0.24 for APM/CKS/CH, 0.48 for FCM (omitted from the "at most 0.35" figure), negative for GD32. At smaller quantities the gap is similar. Still a few tenths per board on a $399 product.
- Flasher accepts only product ID 0x410 (line 268); the emulation models ST, not clones. Clone behaviour claims (GD I2C failure, CKS DP ID, CH32 serial 0xFF) come from web sources I did not re-check: unverified.
- Not news: no change to the design is proposed; the repo already uses genuine ST. Affects ordered boards: no (BOM keeps C8734; only matters if JLC substitutes, which is a process choice).
Corrected statement: Clone F103C8 parts at JLC save about $0.06-0.48 each vs ST $0.93@1000+ (GD32 costs more); clone compatibility with the ROM-bootloader flasher and ADC/CAN is untested. Keep C8734.
Fix: none needed; optionally note "no substitution" on the JLC order.
