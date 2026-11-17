# R10 - Processor choices (STM32F407VGT6 main MCU, STM32F103C8T6 wideband MCU)

Date of research: 2026-11-15/16. Tags: VERIFIED (read today in a primary source or live tool), INFERRED, UNVERIFIED.
Raw JLC/LCSC listings: `work/R10-processor-choices/dl/` (jlc_search_*.txt, jlc_extra_search.txt, jlc_tiers.txt). Release listing: `dl/rusefi_rel.json`, NA6 bundle `dl/na6/na6.zip`.
No ST site page could be fetched (st.com timed out from this machine for curl and page fetch); Mouser, DigiKey.com, Future, Newark denied or timed out. See "Not checked".

## Summary (10 lines)
1. VERIFIED: JLC stock of the genuine STM32F407VGT6 (C12345) is thin: 126 pcs on 2026-11-15, 72 pcs on 2026-11-16; extended (not basic) part; USD 5.05 @1, 3.57 @100, 3.34 @1000. LCSC shows only 22. A run of 100+ boards would exceed JLC stock.
2. VERIFIED: pin-compatible parts have far more JLC stock and are cheaper: GD32F407VGT6 C115906 20,600 pcs, USD 4.04/2.97(@90)/2.80(@1080); AT32F407VGT7 C528446 1,254 pcs; APM32F407VGT6 C2990873 1,107 pcs.
3. VERIFIED: rusEFI does NOT officially support any of these clones. Its boards readme lists F4 and F7 as "most supported", H7 alpha, AT32 "experimental/abandoned" (the AT32 port is for F435/F437, not F407). An open rusEFI issue (#8396) says the current 407-discovery build hard-faults on APM32F407 since the ChibiOS 21->22 upgrade. No rusEFI report of a working GD32F407 was found.
4. VERIFIED: a current rusEFI F407 image is 640,368 bytes (hellenNA6 2026-11-16 release, includes bootloader?: not checked) and this project's build is 669 kB. STM32F407VET6 (512 kB) therefore cannot hold it; rusEFI's own VET6 build script is a legacy 450K special case with reduced features.
5. VERIFIED/secondary: ST page for F407VGT6 shows Active, 10-year longevity from 2026-01-01 (read via search-engine extraction of st.com, two queries; the page itself would not load for me). Distributor lead times are long (DigiKey SG 52 weeks, Newark 32 weeks quoted by aggregator).
6. Best second source for the main MCU if ST stock runs out: buy genuine F407VGT6 from franchised distributors (TME/Newark have stock) or LCSC global; the GD32F407VGT6/APM32 route needs a firmware port and hardware validation (USB, flash, interrupts), do not ship it unvalidated.
7. Wideband: genuine STM32F103C8T6 is basic-preferred? (JLC says "EXTENDED (PREFERRED)") with 191,011 pcs at USD 1.46/1.01(@250)/0.93(@1000); the upstream F042K6 is effectively unavailable at JLC (1 pc LQFP-32, 56 pcs QFN-32). F103C8 is the right choice. rusEFI wideband repo has an F1 port (f1_rev2/rev3/dual), so the F103 is upstream-supported hardware (not the F042 only).
8. Clones of F103C8 at JLC save only USD 0.15-0.35 each and carry documented behavioural differences (GD32F103 failed an I2C bench test; clocks/flash timing differ; CKS/APM32 ROM bootloader copies ST's). The repo's flasher expects the F103 ROM bootloader (ID 0x410): clones need testing. Not worth it.
9. Crystals: F407 USB needs the HSE (datasheet), so Y1 stays. The wideband F103 could run from HSI like upstream f1_rev3 (HSI +-2.5% worst case over temperature): removing Y101 saves about USD 0.15-0.30 but adds CAN timing risk and a firmware change.
10. Eliminating the second processor is not practical: no in-tree LSU driver in rusEFI (CJ125 only in changelog), it would need new firmware for heater PID and Ip control.

## 1. Main processor: availability and price (JLC/LCSC live lookups 2026-11-15/16, USD)
| Part | LCSC code | JLC stock (11-16) | Price @1 / mid / top tier | Source |
|---|---|---|---|---|
| STM32F407VGT6 (ST) | C12345 | 72 (126 on 11-15); LCSC 22 | 5.05 / 3.57 @100 / 3.34 @1000 | tools/lcsc.py, VERIFIED |
| STM32F407VGT6TR | C919362 | 0 | 8.71..6.48 | VERIFIED |
| STM32F407VET6 (512 kB) | C28730 | 68 | 4.64 / 3.48 @90 / 3.29 @1080 | VERIFIED |
| STM32F405RGT6 (LQFP64) | C15742 | 24 | 6.44 / 4.63 @100 | VERIFIED |
| STM32F405VGT6 (LQFP100) | C56621 | 1,100 | 7.61..5.37 | VERIFIED |
| STM32F427VGT6 | C117815 | 2,585 | 9.01 / 6.01 @100 | VERIFIED |
| STM32F429VGT6 | C95448 | 33 | 30.40..28.13 | VERIFIED |
| STM32F407ZGT6 (LQFP144) | C19156 | 374 | 6.26..4.52 | VERIFIED |
| GD32F407VGT6 | C115906 | 20,600 | 4.04 / 2.97 @90 / 2.80 @1080 | VERIFIED |
| GD32F407VET6 | C108421 | 13,882 | 3.92..2.66 | VERIFIED |
| GD32F405VGT6 | C2688747 | 48 | 4.96..3.03 | VERIFIED |
| AT32F407VGT7 (105C, 1 MB, 240 MHz) | C528446 | 1,254 | 3.97 / 2.59 @90 / 2.34 @900 | VERIFIED |
| APM32F407VGT6 (Geehy) | C2990873 | 1,107 | 4.43 / 2.89 @90 / 2.61 @900 | VERIFIED |
| APM32F407VET6 | C3029187 | 477 | 4.19..2.47 | VERIFIED |
| HK32F407VGT7 | C52204722 | 383 | 4.33..2.70 | VERIFIED (not researched further) |
| CKS32F407VET6 | C5185731 | 39 | 4.89..2.82 | VERIFIED |
| N32G457VEL7 (Nations) | C2932364 | 821 | 2.43..1.43 | VERIFIED, not pin-compatible assumed (unchecked) |

Notes
- All are "extended" parts at JLC (extra per-part-type fee, see R21). INFERRED: the JLC stock of C12345 fell from 126 to 72 in one day, so a single 100-board order could empty it; JLC may then show "out of stock" and require consigned parts.
- GD32F407VGT6: JLC's attribute says 512KB, GigaDevice's own product page says 1024K bytes flash, 192K SRAM, 168 MHz, USB FS+HS OTG, 2xCAN 2.0B, -40..85 C (https://www.gigadevice.com/product/mcu/mcus-product-selector/gd32f407vgt6, VERIFIED). JLC listing is wrong or mislabeled. Vdd min per JLC is 2.6 V (vs ST 1.8 V); the board runs 3.3 V, so OK (INFERRED).
- STM32F42x: F427VGT6 is software-family-compatible with F407 but costs about 2x; pin compatibility of LQFP100 not verified (ST application note DM00123028 could not be downloaded): UNVERIFIED. rusEFI has F429 boards (f429-discovery, bundle in release), so firmware exists (VERIFIED in release asset list); it would be a different build target.
- Distributor snapshots (all UNVERIFIED unless stated; sites partly blocked):
  - DigiKey Singapore page (VERIFIED by page fetch 11-16): STM32F407VGT6, stock 1,124, status Active, lead time 52 weeks, prices in SGD: 1 = 21.48, 10 = 16.89, 90 = 14.57, 450 = 13.58 (SGD, not USD).
  - TME (VERIFIED by page fetch 11-16): 1,162 in stock, USD 9.97 @1, 8.70 @90, trays of 90.
  - Findchips aggregator (page fetch, undated): Newark 5,997 pcs, USD 6.01-10.06 range; Win Source 49,400 pcs (broker, USD 4.29-5.51: brokers are a counterfeit risk); ST direct 18 pcs.
  - Search extraction (UNVERIFIED): Newark lead time 32 weeks, USD 9.25 @100; Arrow 52 weeks; Future 52+ weeks; DigiKey tape-and-reel 30 weeks.
  - Mouser (page denied) UNVERIFIED: only an aggregator figure for the -TR code, USD ~8.2 @100.
  - So: at distributors the genuine part costs USD 7-10 at 100, i.e. JLC/LCSC's USD 3.57 @100 is the cheapest by about 2x. Distributor price is the practical fall-back cost, USD 8-9.
- Longevity: ST product page (st.com/en/microcontrollers-microprocessors/stm32f407vg.html) status Active, longevity 10 years starting 2026-01-01 (INFERRED end about 2036). I could not load the page; the statement was returned by two independent search queries quoting the page, and a third-party page quotes the same start date for the F407ZGT6. Treat as secondary: re-check on the ST page before relying. ST's rule: commitment is reviewed annually; community staff answers say it holds until early notification (secondary, community.st.com). A 2021 PTN on STM32F407VGT6J concerns the MicroEJ variant, not the standard part (secondary).
- STM32F103C8: ST community says F103 family is in the 10-year program; the F103CBT6 start date quoted as Jan 2022 (UNVERIFIED, secondary).

## 2. Flash size: can F407VET6 (512 kB) work?
- VERIFIED: rusEFI latest release (tag 2026-11-16) bundle `rusefi_bundle_hellenNA6_autoupdate.zip` contains `rusefi_development_2026-11-16_hellenNA6_...bin` of 640,368 bytes and `rusefi.hex` 1,801,249 bytes (hex text). Source: https://github.com/rusefi/rusefi/releases (API dl/rusefi_rel.json; zip inspected with python zipfile).
- VERIFIED: this repo's own offline compile links to 669 kB (repo/VERIFICATION.md:714) and "77 KB spare" under the 1 MB limit (VERIFICATION.md:102).
- VERIFIED: rusEFI's VET6 build scripts (repo/firmware/ext/rusefi/firmware/config/boards/STM32F407VET6_Mini.bat) comment "this board has only 512K flash ... 'len = 450K'" and disable internal-flash storage and RTC: a legacy reduced build.
- INFERRED: 640-669 kB > 512 kB, so VET6 cannot run the current firmware; the cheaper VET6 (JLC USD 3.29@1080) is no saving. Also GD32F407VET6/APM32F407VET6/CKS32F407VET6 are out for the same reason. Only 1 MB (xG) parts qualify.

## 3. rusEFI / FOME official processor statements
- VERIFIED: repo/firmware/ext/rusefi/firmware/config/boards/readme.md (pinned commit): "most supported platforms are stm32f4 and stm32f7; alpha version support stm32h7; experimental/abandoned support kinetis; ... cypress; ... AT32 MCUs."
- VERIFIED: the code tree contains an AT32F4 port (hw_layer/ports/at32/at32f4, rusefi.mk ARCH_AT32F4) with device IDs for AT32F435/437 only (at32_common.cpp: AT32F435ZMT7 etc.), boards at_start_f435 and m74_9. Release notes of 2026-11-11 mention "AT32 GPT for fast ADC", so AT32F435 work is active in Nov 2026 (VERIFIED via release page). No AT32F407 target. AT32F403A/407 and F435/437 are not compatible (Artery migration guide MG0018, per search extraction, UNVERIFIED).
- VERIFIED: rusEFI forum thread (rusefi.com/forum/viewtopic.php?p=47209): m74.9 uses AT32F435ZMT7; "Artery has some pin differences from STM32"; port started May 2023 as a separate effort; RAM setting issues; progress to CAN/UDS by Nov 2023.
- VERIFIED: GitHub issue rusefi/rusefi#8396 (open, 2025-08-04), "ChibiOS upgrade makes apm32f407 Hardfault": "Load latest 407 discovery onto apm32 ... Board does not get detected over usb ... see hardfault ... pre-chibios discovery loads fine ... subtle memory alignment differences in apm32 and stm32". Author motivation: "Some places in the world can't get real stm32 locally". No fix recorded (comments 0).
- VERIFIED: GitHub issue search in rusefi/rusefi for "GD32" gives 0 results; "APM32" 1.
- FOME: not separately checked beyond ext/ (see R02). UNVERIFIED that FOME supports other than STM32 F4/F7/H7.
- Forum (UNVERIFIED, older): F7 is the most capable well-supported; H7 "more or less unsupported" (rusefi.com/forum/viewtopic.php?p=48666, 49619).

## 4. Clone experience reports for F407-class parts
| Part | Evidence | Tag |
|---|---|---|
| APM32F407 | EEVblog thread (2022-2025): USB FS, ETH, SD, UART worked; interrupt priority bits 3 vs 4 (8 vs 16 levels per Geehy FAE) made FreeRTOS code crash/lose frames; factory ADC calibration data missing; internal temp sensor wrong; bootloader flash self-test failed (flash programming differs); HASH absent; device ID 0x413 same as STM32F407, so software cannot tell them apart. https://www.eevblog.com/forum/microcontrollers/geehy-apm32f407-as-st32f407-replacement-does-anyone-use/ | VERIFIED as report; forum |
| APM32F407 + rusEFI | issue #8396 above: hard fault, USB not enumerating after ChibiOS 22 | VERIFIED |
| GD32F407VGT6 | same thread: one user says its "USB differs from STM" (single post); Olimex says GD32-E407 board ran their STM32 test software unchanged (olimex forum, not tested on all interfaces) | forum, UNVERIFIED |
| GD32 general | Flash is separate die with zero-wait-state cache at high clocks (vendor-style blogs), I2C bench failures on GD32F103 (blaatschaap.be) | UNVERIFIED/secondary |
| AT32F407 | Only vendor library; not a rusEFI target; Cortex-M4F 240 MHz; 105 C grade | VERIFIED listing, no firmware evidence |
- INFERRED: rusEFI exercises USB (console and TunerStudio), many timers, ADC with DMA, CAN, SPI flash/SD and internal flash for settings, so every difference listed above applies; a clone is a firmware port plus a validation project, not a BOM swap.

## 5. Wideband processor
| Part | LCSC | JLC stock | Price @1 / @250 or mid / @1000 | Notes |
|---|---|---|---|---|
| STM32F103C8T6 (ST) | C8734 | 191,011 | 1.46 / 1.01 / 0.93 | JLC "EXTENDED (PREFERRED)" (VERIFIED, lcsc.py) |
| APM32F103C8T6 | C393540 | 5,673 | 1.24 / 0.85 / 0.78 | 96 MHz; ROM bootloader a copy of ST's per blaatschaap (secondary); I2C bench passed there |
| GD32F103C8T6 | C77994 | 16,141 | 1.62 / 1.12 / 1.04 | LOWER JLC price advantage none; 108 MHz; own bootloader; failed I2C bench in blaatschaap test |
| CKS32F103C8T6 | C556576 | 421 | 1.55 / 0.98 / 0.87 | SW-DP IDCODE 0x2BA01477 vs 0x1BA01477 on genuine (arXiv 2008.09710, per search extraction) |
| CH32F103C8T6 | C2687451 | 3,392 | 1.19 / 0.76 / 0.69 | serial number reads all 0xFF, second USB block; not a Cortex-M3 ID clone |
| STM32F042K6T6 (upstream module part, LQFP-32) | C69216 | 1 | 4.05 / 2.75 / 2.53 | VERIFIED: practically unavailable at JLC |
| STM32F042K6U6TR (UFQFPN-32 5x5) | C2053439 | 56 | 4.11 / 3.10@100 / 2.92 | |
| STM32F042F6P6 (TSSOP-20) | C2969989 | 2,149 | 1.78..1.02 | other pin count; would need layout change |
- VERIFIED: ext/wideband-rusefi/hardware/board_module/export/rev C/CPL-wideband_controller.csv: upstream module uses STM32F042K6Tx LQFP-32. The repo's note (scripts/daughter_readme_v05.py:19) that the F042K6 was scarce is confirmed: 1 piece LQFP, 56 QFN.
- VERIFIED: rusEFI's wideband repo (ext/wideband-rusefi/firmware/boards) has F1 ports: f1_rev2, f1_rev3, f1_dual (comment: "Both single-channel and dual-channel F103 boards live at rusefi-hardware"). The F103 is thus an upstream-supported part, not just this project's idea. ST says F042 is Active, lead time 13 weeks on DigiKey and PCI 16085 (humidity cards, 2026-02-09) only (search extraction, UNVERIFIED).
- Price/supply verdict: genuine F103C8T6 is clearly the safest (191k stock, preferred, USD 0.93-1.46) and about USD 1.5 cheaper than F042K6 at 100 pcs. Clones save USD 0.15-0.35 each (INFERRED from table) but have documented clock/timing/bootloader differences and potential relabeled-part risk; with the ROM-bootloader flasher (VERIFICATION.md:351 models F103 medium-density ID 0x410) the clones are untested.
- Clone-detection facts (secondary): genuine F103C8 always reports 64 kB in flash-size register; CKS/CS32 may report 128 kB; ID 0x410 genuine (community.st.com threads, UNVERIFIED).
- Elimination of the second MCU: VERIFIED no in-tree LSU/CJ125 driver in the pinned rusEFI (grep: only CHANGELOG.md and generated ini mentions); the wideband firmware is a separate project (heater PID, Nernst/pump control) with a 26 kB image (repo/firmware/wideband/miata_wbo_f103.bin, 26,348 bytes). Running it on the F407 would require a port into rusEFI's scheduler plus ADC channels and timers; INFERRED saving about USD 1.0 + LQFP + passives, with large firmware and safety risk (heater control must survive a main-MCU crash). Alternative: buy a CJ125 IC (C22419808, LQFP-32, 2,400 pcs, USD 9.66..6.95) is more expensive: not a saving.

## 6. Crystals versus internal oscillators
- Main F407: VERIFIED STM32F407 datasheet (datasheets/txt/C12345_STM32F407VGT6.txt:1893) "The USB OTG full-speed controller requires a dedicated 48 MHz clock that is generated by a PLL connected to the HSE oscillator." HSI accuracy VERIFIED Table 34 (line 6242): +-1% at 25 C, +-4% -10..85 C, -8/+4.5% -40..105 C. USB full speed needs 48 MHz +-0.25% (USB 2.0 spec, from memory, UNVERIFIED), so HSI cannot do USB; CAN also needs a good clock. Keep Y1.
- Wideband F103: VERIFIED datasheet Table 24 (C8734 txt lines 3068-3082): HSI factory-calibrated -1.1/+1.8% at 25 C, -1.5/+2.2% at -10..85 C, -2/+2.5% at -40..105 C. VERIFIED upstream ext/wideband-rusefi/firmware/boards/f1_rev3/mcuconf.h:41-50: HSE disabled, PLL from HSI x12 (48 MHz) and board.h "NOTE: HSE not fitted". So upstream ships F1 wideband modules on HSI including CAN. This project's miata_f1/mcuconf.h:43-52 adds an 8 MHz crystal "to keep CAN bit timing in spec over temperature". Crystal Y101 C115962 costs USD 0.246 @1/0.126 @1000 (kb/parts_manifest.md:18) plus two caps; removing it would match upstream. CAN tolerance (CAN spec: about 0.5% oscillator tolerance for robust operation at 500 kbit/s with typical sample point; 1.58% theoretical max) is an INFERRED/UNVERIFIED statement; with +-2.5% HSI worst-case the wideband would be out of spec at the extremes but the main ECU's CAN is crystal-accurate and upstream has fielded it. Verdict: keeping the crystal is the conservative choice; savings only about USD 0.20-0.30 per unit.
- Main-MCU 32 kHz LSE is already off (repo firmware/board/mcuconf.h comment).

## 7. Recommendation table
| Role | Primary | Backup 1 | Backup 2 | Risk notes |
|---|---|---|---|---|
| Main MCU | STM32F407VGT6 (ST, 1 MB) | Same part from franchised stock (TME/Newark/DigiKey: USD 7-10 @100, lead 30-52 weeks quoted, UNVERIFIED), buy ahead 6-12 months | STM32F405VGT6 (C56621, 1,100 pcs, USD 5.4-7.6): no OTG-HS/ETH/DCMI; F405 uses same die family; rusEFI's F4 builds target F407 config, F405 firmware compatibility not tested here: UNVERIFIED. STM32F427VGT6 (C117815, 2,585 pcs, USD 6-9): pin compatibility UNVERIFIED | VET6 too small. Clones GD32F407VGT6/APM32F407VGT6/AT32F407VGT7: cheaper and in stock but no rusEFI support and a known APM32 hard-fault issue: only after a validation port |
| Wideband MCU | STM32F103C8T6 C8734 | Same, other distributors | APM32F103C8T6 C393540 only after flashing/ADC/CAN test | F042K6 effectively unavailable; do not go back |
| Main crystal | 8 MHz HSE, Y1 | | | USB needs it |
| Wideband crystal | keep Y101 | remove to follow upstream only after CAN test over temperature | | USD 0.2-0.3 |

### Second-source plan when the main MCU is out of stock at JLC
1. Pre-buy: 12 months of genuine F407VGT6 (about 100 pcs/year => USD 400-900 from franchised distributors) and use JLC "consigned/customer-supplied parts" for assembly (R21 owns the JLC mechanics).
2. Keep an LQFP-100 footprint-identical, 1 MB, 3.3 V alternative evaluated on a bench board first: APM32F407VGT6 and GD32F407VGT6 first, AT32F407VGT7 last (different peripheral set, 240 MHz, 105 C). Test list: USB enumeration (HSE 8 MHz to 48 MHz PLL), OpenBLT bootloader flashing and settings flash write, 2x CAN, ADC with DMA and temperature, timers/trigger input capture, interrupt priority count (8 vs 16 levels), SPI (SD card), RTC off. Run the rusEFI unit tests and an engine-simulator bench.
3. Contribute the chip ID/NVIC priority-bit fix upstream and keep a clearly labeled separate firmware build, so the customer's TunerStudio does not offer the wrong binary.
4. Do not ship clone-populated boards as the default; mark any such variant in the product page.

## Implications for this project
1. Stock risk of U1 at JLC (VERIFIED 72 pcs, falling): plan the first production lot around real stock, or buy U1 separately; JLC could reject large lots. Boards: daughterboard. Confidence high.
2. VET6 is not a viable cost-down (VERIFIED 640-669 kB vs 512 kB). Confidence high.
3. A clone MCU saves USD 0.5-1.0 at 100 (C115906 GD32 USD 2.97@90 vs ST 3.57@100) but would put the product on an unsupported firmware path (rusEFI issue #8396). Not recommended for the first build; JLC price gap is small relative to a USD 399 product. Confidence high.
4. Wideband F103C8T6 is the right call: stock 191k, USD 0.93-1.46; F042K6 at JLC 1 pc. Docs: keep the repo note. Confidence high.
5. Documentation: state that the board is for genuine 1 MB F407VGT6 only; add "second-source plan" to README/INSTALL support section.
6. Optional saving: remove Y101 and 2 caps from the wideband (USD 0.2-0.3, 3 parts) at the cost of CAN timing margin; keep it unless the CAN is tested over -40..85 C. Confidence medium.
7. Wideband MCU elimination: not recommended. Confidence medium.

## Sources actually read
- tools/lcsc.py live lookups 2026-11-15/16 (dl/*.txt).
- datasheets/txt/C12345_STM32F407VGT6.txt (lines 1893, 6230-6250), C8734_STM32F103C8T6.txt (lines 3068-3082).
- repo/firmware/ext/rusefi/firmware/config/boards/readme.md, STM32F407VET6_Mini.bat, hw_layer/ports/at32/*, rusefi.mk.
- ext/wideband-rusefi/firmware/boards/{f0_module,f1_rev3}/mcuconf.h, board.h; hardware/board_module CPL.
- repo/firmware/wideband/miata_f1/{mcuconf.h,board.h}, repo/firmware/README.md, repo/VERIFICATION.md.
- https://github.com/rusefi/rusefi/releases (+ API json, hellenNA6 autoupdate zip), https://api.github.com/repos/rusefi/rusefi/issues/8396 and issue searches.
- https://rusefi.com/forum/viewtopic.php?p=47209 (m74.9 AT32F435).
- https://www.gigadevice.com/product/mcu/mcus-product-selector/gd32f407vgt6.
- https://www.eevblog.com/forum/microcontrollers/geehy-apm32f407-as-st32f407-replacement-does-anyone-use/
- https://www.blaatschaap.be/identifying-32f103-clones/ ; cnx-software APM32F103 article.
- DigiKey SG and TME product pages (page fetch); findchips search page; web-search extractions for ST longevity, Newark/Arrow/Future quotes.

## Not checked
- ST product pages (st.com unreachable): longevity icons for F407VGT6/F103C8T6/F042K6 are secondary only.
- Mouser, DigiKey.com, Arrow, Farnell pages (denied); unit prices at 1/100/1000 at large distributors are therefore only partly verified.
- Whether the 640 kB NA6 bin includes the OpenBLT bootloader; FOME sources and its processor statements.
- GD32F407 / APM32F407 user-manual differences (wait states, ADC, USB), errata; clone chip-ID values of F103 clones against the ROM bootloader (0x410) not measured.
- STM32F427 pin compatibility with the project's pin map; F405 firmware compatibility.
- Counterfeit incidence at JLC/LCSC for F407/F103.
