# R11 Tuning software workflow (TunerStudio, rusEFI tuner/console, logs), first connection to finished tune

Date of research: 2026-11-16. Tags: VERIFIED = read today in a primary page/file; INFERRED = reasoning shown; UNVERIFIED = memory/forum/search-summary only.
Note: rusEFI wiki pages were read through page summaries except `book.pdf`, which I downloaded and read in full text. Treat summary-only items as VERIFIED-by-summary (medium confidence) where marked "(wf)".

## Summary (10 lines)
1. rusEFI now ships its own free Windows app, "rusEFI tuner" (the old Java console, renamed), with tune editor, Burn, firmware update, .mlg log viewer, engine sniffer, gauges. TunerStudio is officially an "optional professional/advanced alternative". (book.pdf p.3-7, wiki Console (wf)). It is Windows-only per the wiki; Linux only for CAN/firmware update.
2. TunerStudio: free edition vs registered. EFI Analytics store today: TunerStudio MS (registered) USD 69.95 (sale, normal 79.95), MS Ultra USD 99.95 (sale, normal 129.95/129.90), MegaLogViewer HD 49.95 (sale from 69.95), MegaLogViewer MS 34.95, TS Dash Pro 39.99, Shadow Dash MS (Android) 14.99. VE Analyze Live (autotune) needs registered TS; Ultra adds Trim Table Analyze, integrated log viewer. (https://www.efianalytics.com/register/browseProducts.jsp, VERIFIED, saved work/.../efi_products.html; sale prices as shown 2026-11-16).
3. **Custom-board ini problem**: rusEFI "Detect" downloads the .ini from rusEFI's online archive, which official boards populate from CI (needs FTP secrets, `firmware/tunerstudio/upload_ini.sh`). This board is a custom build; the repo CI makes the .ini as an artifact. And `EFI_EMBED_INI_MSD` is FALSE by default on stm32f4ems and the board does not override it, so the ECU does not present the .ini as a USB drive. Result (INFERRED): a customer cannot get the matching .ini by pressing Detect; the seller must publish bundle + .ini and instruct manual selection. See findings.
4. LTFT (long-term fuel trim, learns into a table, optional "apply to VE") exists in the pinned rusEFI and is ON by default for stm32f4ems; the board does not disable it (VERIFIED by grep). FOME shallow clone has no LTFT code. Repo docs mention only short-term trim.
5. Autotune on rusEFI: works through standard TS VE Analyze Live (needs lambda in a TS-readable channel; FOME changelog shows lambda-table/AFR-mode fixes and MegaLogViewer VE-analyze channel fixes, i.e. it works but has been fragile). No quantitative rusEFI-specific success reports found (UNVERIFIED; only generic "60-80 % of ideal" opinion from a competitor's forum post).
6. Wireless: rusEFI Bluetooth is classic SPP via an external JDY-33/HC-05 on a TTL UART; iPhone cannot connect (wf). This board exposes no free TTL UART on J5 (USART3 is the wideband link), so wireless = USB or a CAN-to-WiFi bridge on J5 pins 19/20 (INFERRED).
7. FOME is ahead in documentation structure (HT guides), console bundle with drivers, per-day SD log folders (unreleased), WiFi boards (Atlas), 4 wideband channels; rusEFI is ahead in LTFT, new own tuner app, rusEFI Online tune library. Hardware is compatible today, warned to diverge.
8. Competitors' tuning software is free (Link PCLink, ECUMaster, MaxxECU MTune; Haltech NSP downloadable; MSE MEITE free) and includes wizards/base maps/autotune; a buyer pays only for hardware. rusEFI+TS autotune costs USD 70 extra.
9. Guided first-start proposal at the end.

## 1. Stage-by-stage

Legend per stage: time / skill (INFERRED from procedure length unless sourced) / typical mistakes / what the vendor can pre-do / FOME vs rusEFI.

### 1.1 Install software, drivers, ports
- rusEFI: Windows installer `rusEFI_Universal_Updater.exe` installs "rusEFI tuner"; "installing the Windows application does not update ECU firmware"; the installer uses snapshot firmware; for Release/LTS use the downloaded bundle; bundle needs "Install Drivers" (Virtual COM Port + DFU) and Java (bundle helps install it) (book.pdf p.3-4, VERIFIED).
- TunerStudio downloads (https://www.tunerstudio.com/index.php/downloads, wf): Windows 8/10/11 exe (TS MS 3.3.01), macOS .dmg (TS 3.1.06, 10.7+), Linux tar.gz (3.3.01, run .sh). Bundled Java not stated. Shadow Dash Android v1.6.10 dated 09/25/2018 (old; store page says not compatible with many Android 16 devices).
- Linux: add user to `uucp` (Arch) / `dialout` (Debian/Ubuntu, INFERRED from search result, not rusEFI page); stop ModemManager or udev `ID_MM_DEVICE_IGNORE` rule (https://wiki.rusefi.com/Linux-Connectivity, wf). macOS: rusEFI wiki says nothing (wf); TS has a Mac build, version lags (3.1.06 vs 3.3.01).
- Windows port: pick the COM port; usually two ports appear, higher number is the TS one; the other is text console; baud irrelevant for USB; "Test Port" (Tunerstudio-Connectivity, wf). Known Windows driver trap: old "STM device in DFU mode" driver gives DRIVER ERROR (HOWTO-Update-Firmware, wf); FOME: "ConfigManagerErrorCode=28" fix via silent_st_drivers (FOME Flashing Software Notes, VERIFIED, own download).
- Time 15-45 min, skill low-moderate; mistakes: wrong COM port (console vs TS), Windows driver, Linux dialout/ModemManager, firewall for Java. Vendor can: ship a one-page "install" with the bundle zip, signed driver, VID/PID so udev rule can be given. VID/PID is generic ST (inherited) unless changed: UNVERIFIED.

### 1.2 Project creation and matching .ini to firmware signature
- TS: Create New Project -> Detect (auto-download of official .ini over USB/serial/Bluetooth) or Browse to .ini from the bundle; "board should also present itself as a USB storage device containing the .ini ... most foolproof" (book.pdf p.7-8, VERIFIED). Mismatch fix: use .ini from same bundle as the firmware; forum: update both (https://www.rusefi.com/forum/viewtopic.php?p=40543 via search, UNVERIFIED).
- Board facts: `EFI_EMBED_INI_MSD FALSE` (repo/firmware/ext/rusefi/firmware/config/stm32f4ems/efifeatures.h:406-407, VERIFIED); no override in board.mk/prepend.txt (grep, VERIFIED). `upload_ini.sh` needs FTP secrets that only rusEFI's CI has (VERIFIED). So Detect on this custom build most likely fails to find an archived .ini (INFERRED, medium; not tested on hardware).
- FOME: after update, TS prompts "Update ECU Definition"; manual .ini from bundle; FOME ECUs show ZIP with ini on a USB device (FOME HT-Set-Up, VERIFIED) and has built-in ini storage (changelog line 253 for F7), Atlas WiFi can download the ini matching installed firmware (changelog line 57).
- Time 5 min if done right; typical mistake: stale project after firmware update (signature mismatch), choosing master .ini; vendor can: put the exact .ini in release zip named with firmware version, embed ini (MSD or on SD card), or ship a pre-made TS project folder.

### 1.3 Firmware update methods
- rusEFI: console "Update ECU firmware" (OpenBLT over USB-serial where the board has it; auto-DFU where supported); manual DFU "recovery"; ST-Link last resort; SD-card not covered (HOWTO-Update-Firmware wf). Warns firmware Oct 2025-Jan 2026 was reported fragile with poor power during updates; "keep my tune" not guaranteed. Linux works with 64-bit Java.
- Board: first flash DFU (hold BOOT tap RESET), later OpenBLT through console (repo firmware/README.md:38-43, claim; `USE_OPENBLT=yes` meta-info.env VERIFIED). Never run on hardware.
- FOME: console recommended; bundle has drivers/ and console/ dirs; after update must click preset button in Popular vehicles (not the reset one) (FOME HT-Updating-The-Firmware, VERIFIED). F7 dual-bank mass-erase caveat (not our F4).
- Time 10 min; mistakes: updating with TS open, unplug before green success, wrong bundle channel (snapshot vs LTS), losing tune, **using the Windows "Universal Updater" on a non-catalogue board** (UNVERIFIED whether it refuses; risk flagged in findings).
- Vendor: one signed bundle per release, a "backup tune first" step, a recovery guide with photos of BOOT/RESET.

### 1.4 Initial settings
FOME HT-Set-Up lists what a user must enter: displacement, cylinders, firing order, fuel algorithm, trigger type/offset, outputs (pump, fan, tach, check engine), injector size, dead times, VE table, CLT/IAT corrections (VERIFIED). This product pre-loads all of these per year via Popular Vehicles buttons (repo firmware/README.md:88-112) - a real UX advantage (claims, unchecked on hardware). Remaining user inputs: injector size if non-stock, IAT sensor curve, wideband flash step, TS project. Mistake: wrong NB2 year button (2001-02 vs 2003-05) which cuts fuel/spark (README claim). Time 20 min, skill low if buttons work.

### 1.5 Sensor calibration
- Throttle: Tools > Calibrate TPS: Get Current closed/full, then Burn (book.pdf p.12; FOME same). MAP: custom linear 0.2 V at 0 kPa to 4.7 V at 700 kPa preset by board. Expect ~100 kPa key-on; CLT/IAT read ambient; VBATT within 0.5 V of meter (INSTALL.md:320). Mistake: calibrating with throttle plate not at stop; unburned values; not stopping engine before Burn (rusEFI does not write flash while engine running, book.pdf p.5 FAQ).
- Time 10 min. Vendor can pre-fill all except TPS closed/WOT (could be a button/wizard).

### 1.6 Trigger setup and timing verification with a light
- rusEFI procedure: disable fuel (injection enabled=false; remove injector fuses), Timing Mode fixed at known mark, plugs out, timing light on cyl 1, adjust Setup>Trigger>Trigger Angle Advance until the light agrees, back to dynamic (book.pdf p.23-25, VERIFIED). First check pattern with Engine Sniffer (rusEFI tuner) or Tooth Logger (TS) with fuel and ignition off; cranking RPM 150-300 (rusEFI) / 150-400 (FOME).
- Repo INSTALL step 4 locks timing at 10 deg and uses the same; NOTE the repo does not say to disable fuel/pull injector fuses for this test whereas rusEFI says "DISABLE FUEL ... FIRE DANGER" (INSTALL.md:322-326 vs book.pdf p.23). Finding.
- Time 30-60 min; skill moderate; mistakes: reading the wrong mark, fuel left on, timing mode not restored to dynamic (risk of fixed 10 deg forever). Vendor: Miata CAS is a fixed fixture: pre-set Trigger Angle Advance should land within a few degrees; a TS dialog "verify timing" lockout button with auto-revert on power cycle would remove the "forgot to unlock" mistake (INFERRED proposal).

### 1.7 Output bench tests
- TS: Controller > Bench Test & Commands; test fuel pump, each injector, each spark, fan, CEL; fire extinguisher; use fuel-safe setup (book.pdf p.12; FOME HT-First-Start). Wiki Bench-Testing referenced.
- Risk: board drives 4 injector outputs with year-dependent JP shunts; bench test of "injector 3/4" on 1989-95 does nothing visible (repo README). Vendor can supply a one-page table "test button -> what should click" per year.
- Time 20 min.

### 1.8 First start, idle
- rusEFI: engine must crank well; cranking mode below 500 rpm; separate cranking fuel/advance; if idle bad use Idle > manual idle slider, aim 800-1200 rpm, rough-tune idle cells by +-20% on a 3x3 block, "1200 RPM and AFR 10.5 works" for first run (book.pdf p.26-28). Idle wiki: base open loop, warm-up correction, cranking air curve, optional closed-loop PID; mistakes: closed loop not engaging because TPS/RPM thresholds, hunting with small dead zone (wiki Idle-Control, wf).
- Time 1-3 h first start incl. troubleshooting (INFERRED); skill moderate-high without base tune; with a good year base tune lower.
- Vendor pre-config: whole base tune already (README). Weak points repo states itself (1994-97 table from a 1.6; NB table flat 80 % above 100 kPa).
- FOME: same flow, plus Idle VE table and Idle ignition table and "Advanced idle" docs (nav list, VERIFIED) which the rusEFI 2025 wiki lacks as separate pages (rusEFI idle page mentions not).

### 1.9 VE tuning, manual and autotune
- Manual: warm engine, adjust VE against wideband; hill pull in high gear for WOT; rusEFI guide suggests 11.5-12.5 AFR at full load; work idle first, then wall wetting, then cold start (book.pdf p.28-31).
- Autotune: "Requires a registered version of TunerStudio" (book.pdf p.31, VERIFIED). Registered TS MS USD 69.95 today. Set Target AFR table (14 all cells is "good enough" to start), drive, TS adjusts cells. rusEFI wiki also admits no dyno needed for lambda-based but peak power needs dyno.
- Quality: no rusEFI-specific outcome data found (UNVERIFIED). Generic: autotune gets a base, still needs manual cleanup (forum, UNVERIFIED). FOME changelog: "Fix autotune while TS project is in AFR mode - corrections now made properly for target AFR table values" (line 234) and "Log channels to make MegaLogViewer VE Analyze work" (line 244) (VERIFIED in file, own clone): both firmwares depend on TS; FOME fixed AFR/lambda-mode bugs in its ini, rusEFI status unknown.
- Closed-loop alternative: rusEFI STFT/LTFT can do much of what autotune does for free (see 1.14). INFERRED.
- Time: 3-10 drive hours over several sessions (INFERRED, no source); skill moderate. Vendor: shipping a per-year Target AFR/lambda table and WOT enrichment tables (already: lambda 1.0 cruise, 0.90 at 100 kPa, 0.80 at 175 kPa per README).

### 1.10 Ignition tuning without a dyno
- rusEFI: guess a table, then "adjust for max power and if possible tune with a knock sensor; if knock, back off 2-4 deg" (book.pdf p.30). Realistic dyno-less approach (INFERRED, practitioner standard): keep the stock Miata map conservative, tune only idle and cruise MBT by feel, stay under knock; no way to find MBT without torque feedback. Stock-engine Miata with rusEFI's NA/NB table is usually adequate (UNVERIFIED).
- Vendor: ship conservative table with timing reduced above 100 kPa (already, README:94).

### 1.11 Cold start and warm-up over several mornings
- rusEFI guide only says: tune wall wetting then cold temperature enrichment (book.pdf p.31 stub); tool exists: `firmware/tunerstudio/WueAnalyze.ini` in rusEFI repo (VERIFIED path) i.e. TS "WUE Analyze" style. Practical: warm engine first (use stock ECU to warm engine, book.pdf p.11), then log 3-5 cold mornings at differing temperatures, adjust WUE/CLT cranking multipliers (INFERRED).
- Time: 3-5 sessions (INFERRED). Skill: moderate. Mistakes: tuning cold start on a day only 15 C; not logging; over-rich washes oil (book.pdf p.28). Vendor can pre-fill; this is where the base tune from other cars needs the most local fix.

### 1.12 Acceleration enrichment
- rusEFI: TPS-based and wall-wetting; doc page Acceleration_Compensation (listed in search results; not read). FOME: pages "Acceleration compensation", "Wall Wetting", "TPS based" under Fuel (nav, VERIFIED). Typical mistakes: wall-wetting parameters tuned before VE correct; dead-time errors. Time 1-2 sessions.

### 1.13 Closed-loop and long-term trim
- Repo: STFT enabled by default, +-10 % idle/cruise, +10/-5 % under load, only when warm and wideband present (README:103-106).
- rusEFI pinned source: LTFT module `long_term_fuel_trim.cpp/.h` (VERIFIED), default `EFI_LTFT_CONTROL TRUE` in stm32f4ems efifeatures.h:57; board prepend.txt does not disable; TS dialog text: "Gathering Data", "Apply Correction", time constants, Max add/remove, deadband; commands `ltft_reset`, `ltft_apply_to_ve`; saved as own flash record. LTFT can "apply to VE", i.e. replaces manual correction pass. Not documented in the repo; not tested on board; flash write cadence unknown (wear: INFERRED low).
- FOME: shallow clone grep for "ltft|long term" in controllers/ini/changelog: no hits (VERIFIED absent in clone of 2026-11-16), it has 4 fuel trim banks and Closed Loop Fuel page.
- Time: automatic over hours of driving; skill: low. Mistake: leaving LTFT learning with a leaking exhaust / sensor not warm, learning a wrong cell.

### 1.14 Boost and VVT
- Boost: rusEFI page steps (output, frequency 0-3000 Hz, open loop table, closed loop PID, min RPM/TPS/MAP inhibit, failsafe duty) (wf). "Overboost protection on Smart ECU page is proposed, not current". Board: NB base tune VE flat 80 % above 100 kPa, no boost tune exists, README says turbo needs a tuner. FOME: Boost control + Boost cut with new 4x4 table (changelog), nav has VVT PID, On/Off VVT, VVT target tables.
- VVT: the 2001-05 button loads rusEFI's VVT target table and PID (README). Time for a stock engine: 0 (preset); skill high if retuned.

### 1.15 Knock setup
- rusEFI Miata guide (mirror): NA6 example knock freq ~7.3 kHz (second harmonic 14.6 kHz), build threshold curve from a low-load full-rpm log; stock NB knock sensor present; Bosch KS4-P suggested (https://*.wiki-7d7.pages.dev mirror, UNVERIFIED mirror). Software knock "in Proteus first" forum (UNVERIFIED). Board: software knock on PA3 ADC3 via on-board amp (knock_config.h, VERIFIED); the "knock amp clips above ~284 mV" is a repo-known limitation. 1990-97 cars have no sensor, "add your own" on J5 pin 6.
- Practical: knock tuning without a dyno/headphones is unsafe; the safest vendor choice is to leave knock retard as detection/log only (INFERRED).

### 1.16 Logging to SD and reading logs
- rusEFI SD logging: microSD, 50 ms (20 Hz) default, ~20 MB/h (~50 h/GB); enable in TS "SD Card Logger"; USB-power order decides mode (car powered first = logging; USB first = card reader); cannot log and read at once; `past-codes.csv` (Logging-Guide, wf). FOME: 20 Hz < ~100 MB/h, 50 Hz bigger; Normal vs Trigger mode; unreleased: logs in YYYY/MM/DD folders if RTC set, all output channels logged (changelog, VERIFIED). Note the two sources disagree on size per hour (20 vs ~100 MB/h) maybe because FOME logs all channels now; trust file sizes measured in person (not done).
- Reading: rusEFI tuner built-in log viewer opens .mlg/.msl; MegaLogViewer MS USD 34.95 / HD 49.95 (note: MegaLogViewer HD includes "auto tune from your log files"); TS Ultra integrates viewer.
- TS logging: Ctrl+L start, triggered logging expressions, 100 Hz recommended (FOME Data Logging page, VERIFIED). A forum claim that free TS logs only 15 Hz is ~6 years old (UNVERIFIED).
- **Board relevance**: microSD socket rated -20..+85 C (documented); the USB-vs-vehicle power-order behaviour matters for a glovebox USB cable (INSTALL.md:163 suggests leaving USB plugged in permanently, which, per Logging-Guide, would put the ECU in card-reader mode if USB powers first - INFERRED conflict; flagged).

### 1.17 Sharing tunes for remote help
- rusEFI Online (https://wiki.rusefi.com/Online, wf): anyone downloads without account; upload needs rusEFI forum login; stores .msq; no privacy statement. Support: share tune + log + firmware version; screenshots insufficient (book.pdf p.5). Remote tuning guide exists (not read). Practical: .msq + .mlg to a tuner; TS licence file-sharing no issue. Mistake: sharing .msq with a different .ini version; vendor can add a "Collect support bundle" step.

### 1.18 Dashboards, CAN, Bluetooth, mobile
- Dashboards: TS free allows one dashboard theme (book.pdf p.9); designer needs registered. rusEFI tuner has its own gauge editor (wf). TS Dash Pro USD 39.99 for RPi dashes.
- Bluetooth: rusEFI classic SPP, JDY-33 default on TTL UART, init with `bluetooth_jdy`; iOS cannot; "link is slow", CAN-to-WiFi is the faster option (Bluetooth wiki, wf). This board: the only UART exposed is the wideband link (INFERRED from README; J5 pin map shows CAN, no TTL), so a Bluetooth stick cannot be plugged to a TTL port; USB-OTG from a phone untested.
- Mobile: MSDroid wiki says gauge values and tables not working (page stale, wf); Shadow Dash MS USD 14.99, v1.6.10 2018 (EFI Analytics, VERIFIED).
- FOME Atlas boards have WiFi with log download; this board has none.

## 2. Other ecosystems (two lines each; hardware price not compared here)
- Link (PCLink): free Windows-only download, versions per ECU generation, ~800 pages help, logging with XY/histogram, "QuickTune"/auto-tune on G4X listed by a retailer; Miata plug-in G4X US retail listings USD 1,595 (reach.dog listing, 2026; search summary, UNVERIFIED date). Firmware update inside PCLink (UNVERIFIED).
- Haltech (NSP): setup wizard builds a base map for Nexus plug-in ECUs, Quick-Tune records lambda corrections to cells, undo/redo; Haltech Connect app (Android/iOS) for Nexus only, not Elite (support.haltech.com, hpacademy via search).
- ECUMaster (EMU Black): "completely free software client with all functions unlocked; updates free" (catalogue 2024-25); V3 Software Guide (Nov 2025) has Wizard and Autotune chapters; Windows installer.
- MaxxECU (MTune): free updates; release 1.160 dated 2026-04-21 mentions local autotune from logfile, WiFi/Bluetooth comms; Windows .msi; free-ness stated on MaxxECU site ("all systems come with MTune").
- Motorsport Electronics: ME221 (entry, Miata NA/NB) and ME442 (adds on-board wideband, closed-loop boost/lambda/VVT, SD logging); software MEITE described as free (spec sheets via search; no official download page found).
Implication: all competitors ship free software with wizard/autotune; the open-source stack asks the owner to buy TS registered (USD 69.95) for equivalent autotune, unless rusEFI tuner or LTFT meets the need.

## 3. FOME vs rusEFI today (summary table)
| Item | rusEFI | FOME | source |
|---|---|---|---|
| Own tuner app | rusEFI tuner (Windows, ex-console), TS optional | FOME console (flasher, debug), TS the main tool | book.pdf; FOME wiki |
| Guided docs | Quick Start / Get Running PnP; first-start page | HT-Set-Up, HT-First-Start, HT-Updating, per-feature pages | wikis |
| LTFT | yes, default on | none found | grep |
| Windows driver trouble | handled "Install Drivers" | silent_st_drivers + OpenBLT no driver (since 2312) | FOME flashing notes |
| SD log | 20 MB/h at 20 Hz (wiki) | full channel parity, date folders (unreleased) | wiki; changelog |
| Online tune library | rusEFI Online (needs forum login) | none found | wiki |
| Wifi boards | via can2wifi adapter | Atlas WiFi built in | changelog |
| Idle docs | 1 page | Idle VE, idle ignition table, advanced idle | wiki nav |
| Project posture | official hardware list | "compatibility may change" | fome-fw README |
Both run this board only via the custom-board build; the repo pins rusEFI 1374bd0.

## 4. Implications for this project
(goal numbers per review brief section 1)
1. (Goal 4, UX) The TS .ini does not come with the ECU and Detect will likely not find it: publish the .ini beside every firmware release with the firmware version in its name, add a step in INSTALL.md ("Create project -> Browse -> pick the .ini from the downloaded zip"); consider `EFI_EMBED_INI_MSD TRUE` in board config (flash cost to check) or putting the ini on the SD card. Evidence: efifeatures.h:406, book.pdf p.8, upload_ini.sh. Confidence medium (not tested on hardware).
2. (Goal 4) INSTALL.md first-start step 4 should tell the user to disable fuel / pull injector fuses before the cranking timing check (rusEFI says fire danger), and to restore Timing Mode to dynamic; the doc currently says only "Lock the timing" (INSTALL.md:322-326 vs book.pdf p.23). Confidence high.
3. (Goal 4) LTFT is compiled in by default and unmentioned. Either document it ("Gathering data / Apply correction" off by default?) or disable with `#define EFI_LTFT_CONTROL FALSE` in prepend.txt. Needs the owner to check default config states of the learning switches (not read). Confidence medium.
4. (Goal 4) INSTALL.md:163 suggests leaving a USB-C cable plugged in for tuning; rusEFI/FOME SD logging switches to card-reader mode when USB powers the ECU first (Logging-Guide wf; FOME Data Logging page VERIFIED). Document power-up order or note logging only works when the key powers it first. Confidence medium.
5. (Goals 1, 4) Wireless: no free TTL UART on J5 for the standard Bluetooth module; offer a CAN-to-WiFi/Bluetooth bridge note or add UART pins on J5 in a future motherboard/daughterboard revision. Confidence medium (J5 map read only via README).
6. (Goal 4) Wideband flash step "Flash on-board wideband" is a mandatory first step with no equivalent at competitors; verify it works on Windows before shipping, and consider flashing the F103 at assembly (vendor pre-configuration), removing one customer step. Confidence medium.
7. (Goal 4) Ship units with the main firmware pre-flashed (DFU needs BOOT/RESET buttons, driver risk) and the wideband pre-flashed; this removes stage 1.3 for most customers. Confidence high as logic.
8. (Goal 4) Guided first start: see section 5.
9. (Goal 4, packaging) Include in the box a card: tuning software links, .ini note, safety (fire, injector fuses), SD card order, support-bundle checklist (tune+log+firmware version, from book.pdf p.5).
10. (Goal 4) Update path: warn that Windows "Universal Updater"/snapshot channel is for official boards; this custom board must use the bundle's console (UNVERIFIED that Updater refuses unknown boards).

## 5. Proposal: guided first-start procedure for this product
Principle: every step has a pass/fail check the user can see on the TunerStudio/rusEFI tuner screen, and no step needs the engine to run until step 8. Estimated 2-3 h (INFERRED).
1. Before the car (desk, USB power): A. install rusEFI tuner (Windows) or TS + MLV; B. open the bundle zip; create TS project with the .ini named in the zip; the connected firmware signature matches (screen shows firmware name); C. press the year button (the NB2 year warning: 2001-02 vs 2003-05); D. press "Flash on-board wideband" (or pre-flashed: confirm version shown); E. burn, save .msq as "factory". Pass: sensors read ambient, MAP ~100 kPa (key on only; USB power alone back-feeds ~4 V, documented).
1. Car, key on, engine off: connect USB; check CLT/IAT/VBATT/MAP/TPS, calibrate TPS, burn (engine stopped). Pass: values plausible; no red LED. Proposed: a TS dialog "Pre-start checklist" ticking each.
2. Bench outputs: pump, each injector (do injectors click in the right order: 1-3-4-2), spark per coil (with a plug grounded), fan, CEL. On 1989-93 note paired injector behavior. Pass: tick sheet printed per year. Fire extinguisher.
3. Trigger check with fuel and ignition disabled: crank 5 s, Engine Sniffer/Tooth Logger shows the CAS pattern, RPM 150-300. Pass: stable sync, RPM within range. Fail: stop, support bundle.
4. Timing check: injection disabled and injector fuses pulled; fixed 10 deg; plugs out; light on cyl 1; adjust Trigger Angle Advance until 10; restore dynamic; burn; (proposed firmware: fixed-timing mode auto-reverts at ECU power-cycle). Pass: light reads 10 +-1 at crank, then dynamic confirmed in TS.
5. Re-enable fuel, restore fuses, plugs in. Prime pump (key on/off x3), check fuel pressure and leaks.
6. First start, warm engine preferably (use stock ECU to warm, rusEFI advice): crank max 10 s with 30 s rests; watch RPM and lambda; abort on fuel smell, knocking, or lambda <0.7 for >10 s (rusEFI says AFR 10.5 is OK for idle at first; FOME stop list). If it won't start after 3 tries: capture log + tune.
7. Idle: closed-loop idle on stock IAC? (not read) otherwise manual idle slider to 800-1200; allow warm-up to 80 C; lambda from wideband within 0.85-1.15 (STFT limit +-10 %). Pass: stable idle for 5 min, no CEL.
8. Test drive with SD card (key powers first), light throttle only; log 30 min; share log. Closed loop engaged (STFT within 10 %).
9. Over next mornings: cold start log at temperatures; adjust WUE and cranking multipliers; 3-5 sessions; save a tune each time.
10. Later: LTFT gathering (if enabled), VE Analyze (needs registered TS) or manual; turbo cars: tuner before boost.
Possible automation (vendor/firmware): (a) a "Pre-start" TS menu that runs the checks and displays pass/fail; (b) one-click "fuel and ignition off for trigger test" with auto-revert at power cycle; (c) "Verify timing" button with auto-revert; (d) per-year printed card of bench-test expected results; (e) support bundle zip button.

## Sources actually read
- kb/research/files/11/rusefi_book.pdf and .txt (https://wiki.rusefi.com/book.pdf, full read of pp.3-32) 
- https://www.efianalytics.com/register/browseProducts.jsp (saved work/R11-tuning-software-workflow/efi_products.html); license page, TS downloads (page fetch)
- rusEFI wiki (page fetch): Console, HOWTO-Update-Firmware, Logging-Guide, Tunerstudio-Connectivity, Online, MSDroid, Boost-Control, Idle-Control, Linux-Connectivity, Bluetooth
- FOME wiki pages saved in work/R11-tuning-software-workflow/fome/*.txt (HT-First-Start-Safely, HT-Updating-The-Firmware, HT-Set-Up, Flashing-Software-Notes, Data-Logging) and nav list from https://wiki.fome.tech/
- FOME repo shallow clone work/R11-tuning-software-workflow/fome/fome-fw (CHANGELOG.md)
- repo files: INSTALL.md, README.md, firmware/README.md, firmware/board/*, ext/rusefi efifeatures.h, long_term_fuel_trim.*, storage.cpp, tunerstudio.template.ini, upload_ini.sh
- Search summaries only (UNVERIFIED depth): Link, Haltech, ECUMaster, MaxxECU, MSE, rusEFI knock mirror, autotune forum threads

## Not checked
- Any behaviour on real hardware (no board exists); Detect on the custom firmware; Universal Updater refusal on custom boards.
- rusEFI wiki pages Knock, Closed-Loop, Acceleration Compensation, Cranking, Remote Tuning, Bench-Testing, and TS Autotune table size limits of the free edition.
- Actual hours for tuning stages (no source found; all INFERRED).
- Link/Haltech/ECUMaster/MaxxECU/MSE feature details read from vendor pages only partly; prices of those ECUs not verified.
- Whether the repo's CI really publishes the .ini inside the bundle (README claims); LTFT default switch states.
