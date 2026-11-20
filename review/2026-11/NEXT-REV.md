# Next board revision: change list

Read 2026-11-17 against current `main` (d7d0d35). Current design: daughterboard rev 0.10 (6 layers); motherboards
1989-95 rev 0.13, 1996-97 / 1999-2000 / 2001-05 rev 0.9. Paths are relative to the repo. The ordered prototypes in
`ordered-boards/2026-11/` are out of scope.

Owner decisions this list is built on:
1. **IAT:** every year uses a GM-type air-temperature sensor in the engine bay, on the car's own IAT wires (pushed
   into the stock plug's cavities or spliced). The kit carries the sensor, its connector, pins and wire.
2. **No via in any SMD pad, on any board.** Re-routing is acceptable.

Marks: **C** checked against the files today; **M** needs a measurement on a car or the bench first.

Line numbers refer to `main` at d7d0d35, before the work. Section 8 is the state of the work on the `no-via-in-pad`
branch.

---

## 1. No via in any SMD pad

### How many vias land in a pad today (C)

Exact pad polygons; via 0.6 mm ring, 0.3 mm drill. `scripts/jlc_fab_check.py` now runs this check on every release.

| Board | Vias | Touching an SMD pad | Nudge within 0.5 / 1.0 / 1.5 mm | No room within 1.5 mm |
|---|---|---|---|---|
| Daughterboard rev 0.10 | 1,349 | **539** (207 in the eight DPAK tabs, 332 in small pads) | 209 / 278 / 306 of 332 | **26** (34 at 0.2 mm clearance) |
| 1989-95 rev 0.13 | 1,179 | **20** | 10 / 15 / 17 | 3: D5.1, F1.1, D4.2 |
| 1996-97 rev 0.9 | 1,136 | **15** | 10 / 14 / 14 | 1: D5.1 |
| 1999-2000 rev 0.9 | 1,128 | **14** | 8 / 12 / 12 | 2: D5.1, F1.1 |
| 2001-05 rev 0.9 | 1,093 | **19** | 13 / 19 / 19 | 0 |

- No via touches a through-hole pad. No SMD pad is on an inner layer. A further 27 daughterboard vias sit within
  0.1 mm of a pad edge without touching it; treat those as violations too (solder wick, mask web).
- Daughterboard nets: GND 192, +3V3 65, the eight injector/output drains about 26 each.
- **Daughterboard spots that need a local re-route, not a nudge** (board mm):
  - **MCU and analog corner:** C39.2, R36.1, R70.2, R72.2, R104.1, R111.1, R131.1, U1.21, C59.2.
  - **J1/J2 strip:** U6.2, U6.6, RN1.2, RN2.3.
  - **Reference and CAN:** U9.2/3/7 (these go away if the VR block is left off), U106.6, U105.2.
  - **Regulators:** the U3 exposed pad, U8.2.
  - **Clamps:** D48.2, D6.2, Q20.3, D36.1, D37.1.
  - **microSD:** J4.7.
- **Motherboards:** the 1989-95 board has 3 such spots, 1996-97 one and 1999-2000 two (the table's last column).
  All are D5 (SMA), fuse F1 (2920) or the SMC clamp D4; the rest are wideband-block 0603s, USB-C J4, U4, D1/D2, D3/D4.
  2001-05 needs nudges only.

### Thermal cost (model, uncalibrated)

- **Driver tabs:** removing all 207 tab vias moves Q1 at 0.55 W from 72 to 74 °C above air. Removing every via
  within 3 mm of a tab gives 75 °C.
- **Regulators:** removing the vias under U2/U3/U4/U14/Q20 adds 0-1 °C each.
- **Conclusion:** the rule is thermally safe in the model. Confirm with the thermal-camera run from the old Step 2.
- **Ring the tabs:** about 20 vias around each driver tab replace the ones inside it.

### Generator changes (C, `scripts/`)

| Where | Today | Change |
|---|---|---|
| `route.py:162-166` `via_ok`; pad load `:183-210`; `static_vexcl` `:227` | A via may land on its own net's pads | Build a keep-out from every SMD pad polygon grown by via radius + 0.1 mm. OR it into the via exclusion and the static map, so it survives the rebuilds at `:557`/`:564` and covers the A* layer change (`:454`, `:543-549`) |
| `route.py:660-742` `gnd_stitch` | Target cells include the pad itself | With the keep-out, its 0.3 mm stub becomes the dog-bone. Allow a larger search radius for boxed-in pads |
| `route.py:744-762` `thermal_and_stitch` | Vias at the centre of every GND pad of 4 mm² or more (source of the motherboard D3/D4 vias, called from `mb_route.py:310`) | Ring of vias outside the pad, or drop it |
| `finish_route.py:374-395` `via_in_pad`, caller `:411`; A* `vok` `:267-312` | Puts vias in GND/+3V3 pads by design | Delete both; add the keep-out to `vok` |
| `tab_copper.py:8-10, :84, :138-148` | `_clear` exempts the driver's own tab; `(in_tab or not near_tab)` | `not near_tab` only; drop the `own` exemption |
| `clamp_copper.py:9, :52-80, :96-115` | "Well inside its own pad" branch admits vias into SMC pads | Remove it; reject anything within via radius + 0.1 mm of any pad, by polygon |
| `mb_tvs_copper.py:30-50, :100-105` | Keeps vias out of pads, by bounding box | Use the pad polygon |
| `hand_route.py:89-90` `nopad` | Forbids vias only near target pads | Extend to all SMD pads |
| `route_eco.py:88-117` | Keeps existing vias | Drop any via touching a pad before re-routing |
| `via_hole_gap.py:12-30`, `mb_cleanup.py:20-37`, `daughter_finish.py:75, :119` | Delete stitch vias that break hole spacing | Also delete vias in pads, then re-run `gnd_stitch` |
| `nudge_part.py` | Drags vias with the part | Re-run the check after any nudge |
| `route.py:810` (writer) | — | Assert no via in pad as a last safety net |

**Build check:** add `bad += via_in_pad(b)` to `jlc_fab_check.py` before `return layers, min_edge, bad` (about
line 100). It must skip pads with no copper layer, or the DPAK paste-helper pads give false hits. (Done on the branch.)

`daughter_release.sh:25` and `mb_release.sh:27` pipe the check through `| head -6`, which throws away its exit status.
Add `set -o pipefail` or drop the `head`, otherwise a failing check still releases.

### Text to change (C)

- **`daughterboard/README.md`:**
  - `:53-54`: thermal vias "most in the tab pad; order them filled and capped".
  - `:71-76`: "Order the board with the vias epoxy-filled and capped".
  - `:311-314`: fill "which the vias in the DPAK tabs and in the clamp TVS pads rely on", "every GND and +3V3 SMD pad
    drops to its plane through its own via", MCU supply vias under the package.
  - `:371`: Before-ordering item 9, "Filled vias".
  - `:38-41` and `:370`: temperatures, re-run after the change.
- **`VERIFICATION.md`:**
  - Via counts at `:57`, `:532`, `:567` and `:607`.
  - `:854-855`: the finisher gives every GND and +3V3 pad a via.
  - Temperature figures at `:794-832`.
- **Temperature figures in `README.md`:232-244, `INSTALL.md`:187-191 and `firmware/README.md`:76-77.** Re-quote
  them from the re-run model.
- **Script comments:** `tab_copper.py:8-10, :84`, `clamp_copper.py:9`, `finish_route.py:374-376`.
- **Order note:** "Via covering: tented. No vias in SMD pads; epoxy fill not required."

### A decision this reopens

With no via in a pad, the 6-layer board no longer needs JLCPCB's free fill. That was one of the arguments for
staying on 6 layers. Re-check the 4-layer price, previously about $2-3 per board saved, before committing the re-route
to 6 layers.

---

## 2. IAT: a GM sensor on the car's own IAT wires

### Correction to the plan (C)

- **1990-97: the sensor goes into the airflow-meter plug.** The stock sensor is built into the 1990-93 vane AFM and
  the 1994-97 hot-wire MAF.
- **1999-2000: it goes on the separate airbox IAT plug, not the MAF plug.** The stock sensor is a separate two-wire
  sensor in the air filter box, on plug B1-30 (2000 wiring diagram; `motherboards/1999-2000/README.md:60`;
  `INSTALL.md:250`). The MAF plug carries only ground, signal and 12 V.
- **2001-05: also a separate IAT, to confirm.** The 2005 manual's pin table puts the IAT on its own cavity, 4N, with
  analogue ground 4O. Whether it sits in the MAF body or the airbox was not confirmed; check one car.

### Per year (ring each wire out to the ECU cavity: colours and plug letters vary)

| Years | Plug the GM sensor uses | IAT signal (ECU cavity) | Sensor ground (ECU cavity) | Fuel pump with the meter unplugged |
|---|---|---|---|---|
| 1990-93 | AFM plug: terminal G (THA), terminal C (E2) | 2P, R/G | 2D, B/LG | **Stops.** The pump contact is in the AFM. The ECU now switches the pump on 2O (section 7) |
| 1994-95 | MAF plug, terminal D / C | 2P, R/B | 2D, B/L | ECU already switches it (2T) |
| 1996-97 | MAF plug | 3K, R/B | 3O, B/L (inferred from 94-95) | ECU already switches it (1U) |
| 1999-2000 | Airbox IAT plug B1-30 | 2B, P/L | 3F, B/R | Not affected: MAF stays or goes independently (3N) |
| 2001-05 | IAT sensor plug (location to confirm) | 4N | 4O | Not affected (2M) |

### Board hardware: no change required (C)

- **Keep the conditioning as it is:** 2.7 k pull-up to 5 V, 5.6 k / 10 k divider, 10 nF, the clamp. microRusEFI
  also uses 2.7 k; 4.7 k would squash the hot end.
- **Pin voltage with the GM sensor (Delphi 25036751 table):**

  | Air temperature | Pin voltage |
  |---|---|
  | -20 °C | 2.53 V |
  | 20 °C | 1.64 V |
  | 60 °C | 0.61 V |
  | 100 °C | 0.19 V |
  | 120 °C | 0.11 V |

  Resolution is 0.03-0.06 °C per count when cold and 0.3 °C per count at 120 °C. An open sensor reads 2.73 V; a short
  reads 0 V.
- **No IAT header or jumper exists on any current board,** so nothing has to be removed. (JP1 on the 1989-95 board is
  the INJ3 jumper; the daughterboard's J3 is the Tag-Connect.)
- **1990-93 fuel pump:**
  - The board already drives 2T (`OUT_FP`, PC14; `motherboards/1989-95/README.md:87`), but the 1990-93 harness has no
    wire there.
  - Decided: the pump relay goes on 2O instead (section 7). Make it a bring-up test.

### Firmware (C)

- **Make the GM curve the default.** In `miataAfterTuneDefaults` (`firmware/board/miata_board.cpp`, about :345-349),
  add `setAtSensor(&engineConfiguration->iat, -20, 28146, 40, 1443, 100, 175.3)`.
  - Fit error at most 0.1 °C from -20 to 120 °C.
  - It must run after the presets that load the Mazda curve (rusEFI `mazda_miata_1_6.cpp:115`; the board's NB common
    code at `miata_board.cpp:252`).
  - Do not put it in the config-override hook, which would wipe a user's edits.
- **Why a new curve is needed:** left on the Mazda curve, the GM sensor reads -28 / 12 / 54 / 98 °C at a true
  -20 / 20 / 60 / 100 °C.
- **Keep the bias settings:** `bias_resistor` 2301.6 Ω and the 4.262 V supply (`miata_pins.h:76`) are the Thevenin
  equivalent of the 2.7 k pull-up and the divider. Do not enter 2700.
- **Update the tests and simulators:** `firmware/board/tests/test_miata_ecus.cpp` (about :600), `firmware/sim/run_ecu.py`,
  and `firmware/tools/circuit_sim_full.py` (its NTC table has only the Mazda curve).
- **Remove stale JP1 / J3 / "M12 sensor" text:**
  - `firmware/board/miata_pins.h:63`
  - `firmware/README.md:146-148`
  - `connectors/daughterboard.yaml:169-170` (the TunerStudio label "IAT ... (JP1)")
  - `circuit_sim_full.py:1091`
  - `board_checks.py:339, 532, 566-570, 646` and its jp1 arguments
  - `mb_route.py:75, 251` (`HARN_IAT`)
  - the legacy `mb_na8.py`
- **Bench check:** an unplugged MAF input (AUX3) reads about 0 V. rusEFI should raise no fault, but run it once.

### Kit parts (prices read 2026-11-17)

| Item | Part | Source | Price |
|---|---|---|---|
| GM open-element IAT, 3/8-18 NPT, with connector and pins | IAT-wConn | DIYAutoTune | $19.99 (sensor alone $15.99) |
| Or: mating housing, Metri-Pack 150.2 2-way (the Delphi datasheet's named mate) | 12162197 | crimpsupply.com | $6.65; $5.32 at 50 |
| Female terminals for that housing, 20-18 ga | 12124075 | crimpsupply.com | $10.70 per 10; $8.58 per 10 at 25 packs |
| Male pins to push into the Mazda plug | in DIYAutoTune's IAT kit, "for common AFM connectors" | DIYAutoTune | Fit in Mazda cavities **unknown (M)** |
| 2-conductor 20 AWG TXL twisted pair, about 2 m | — | Thunderstruck EV | about $0.50 per ft (search snippet, not read) |
| Heat-shrink butt splices, 22-18 (splice option) | 3M MH18BCK | Waytek | $0.65 at 20; $0.52 at 100 (out of stock, 26-day lead) |
| Optional mount: 3/8 NPT aluminium weld bung | — | AMP EFI / DIYAutoTune | $9.49 / $12.99 |
| Ready-made alternative, 1990-93 only | AFM-to-IAT harness, 4 ft | MiataSource | $45 |

- **Per kit:** about $25-27 (sensor with connector, about 2 m of wire, two pins, two splices). That is about $35-40
  with a weld bung.
- **Not found:**
  - a rubber push-in grommet source;
  - a seal or position lock for the 150.2 pull-to-seat housing, which is unsealed.
- **Not in the kit:** the 150.2 crimp tool, Crimp Supply 12039500 at $240.87. It is a bench cost, not a kit cost.

### Docs that become wrong (C)

- **`INSTALL.md`:**
  - `:3`: says 1990-2005; the boards cover 1989.
  - `:106-117`: "What you need" gains the IAT kit.
  - `:170-181`: delete "keep the airflow meter plugged in, simplest first install". On 1990-93 the pump now runs
    from 2O, with a link in the AFM plug.
  - `:242-243` and `:250-252`: "the stock IAT keeps working" is no longer true.
  - `:297-312`: rewrite section 7 as a per-year procedure built on the table above. Drop the adapter rows and the
    sources at `:391-392`. Say the GM curve is preloaded.
  - `:356`: drop the AFM-plugged-in troubleshooting branch.
- **Warning to add:** never leave the stock sensor connected in parallel with the GM sensor.
- **`README.md`:**
  - `:206-211`: the air-temperature section.
  - `:39-40` and `:97-99`: the F/P wire is now standard on 1990-93.
- **Motherboard READMEs:** the IN_IAT rows. 1989-95 at `:75, 83, 104` (JP6 text at `:82, 144`); 1996-97 at
  `:61, 67, 94`; 1999-2000 at `:60, 69, 97`; 2001-05 at `:83, 90, 101`.
- **`firmware/README.md`:**
  - `:100-101`: the default curve becomes GM.
  - `:119`: AUX3 no longer carries a meter signal.
- **`VERIFICATION.md:581`:** the "GM-type IAT option" CHECK becomes the main case.
- **Store and BOMs:**
  - `website/products/make_products.py`: the `YOU_ADD` / `KIT_ADDS` lines.
  - The five `bom/*.csv` files (extra-parts section).
  - `website/README.md:9, 15`.

### Needs a car or bench (M)

1. Terminal type and size in each Mazda plug's IAT cavities, which decides whether "push the pins in" works.
2. Continuity check of the IAT and ground cavities per year, especially 1990-93 (G/C), 1996-97 (3O) and 2001-05.
3. 1990-93: the pump running from 2O through the link in the AFM plug, and that the plug's pump-contact wire is
   switched to ground (low-side compatible).
4. Where the 2001-05 IAT sensor is.

---

## 3. Daughterboard (rev 0.11)

**Must**
- **R110:** change `wideband.py:153` `'R10': 'C25341'` → `C17971`. It is still wrong on main.
  - `design.py:64` `LCSC_R1206['62']` is a dead entry (no call uses it); fix it anyway.
  - Regenerate the fab BOMs and `bom/*.csv` (line ~70).
- **LCSC value check in `bom.py`/`order_bom.py`.** `bom.py:7` currently says "nothing left to flag" with an empty
  `VERIFY`. C25341, C17971, C17936, C132227, C960026 and C56621 are all missing from `mpn.json`, so the check needs
  these entries added.
- **Placement rotations at order time:** U3/U14 (+270 via the PG-DSO rule), the microSD socket (no entry), and
  D_SMA/D_SMC/SOD (no entry). See `order_bom.py:217-224`; update its stale "rev 0.5" comment at `:211-213`.

**Should**
- **Processor:** in `design.py:169`, STM32F407VGT6 C12345 → STM32F405VGT6 C56621.
  - Also change `mpn.json`, `gen_sch.py:249` (symbol), `bom.py:37` (description) and the `design.py:124` comment.
  - `firmware/tools/board_checks.py:949, 967, 979, 998, 1104` and `check_mcu_pins.py:32-33` are keyed on the string
    `STM32F407VGT6` and will fail until renamed.
  - The firmware target is unchanged.
- **CAN transceiver:** U10 (`design.py:456`) and U106 (`wideband.py:160`) TCAN1042VDRQ1 C485806 → TJA1042T/3/1J
  C132227. `gen_sch.py:161` and about nine `board_checks.py` lines are keyed on the old value.
- **VDDA:** move C12 to the VDDA pin side with FB1 upstream (`placement.py:89-92`).
- **U4 3.3 V regulator:** more copper at the tab (`placement.py:135`). Under the new rule, that means vias around
  the tab, not under it.
- **Fix the stale VERIFICATION "for the next revision" list (`:676-690`).** Rev 0.10 already did battery sense, R120,
  CAN on AUX, CEL and the fuse change (`daughterboard/README.md:26-34`).

**Optional or after a bench check**
- **VR conditioner off by default:** `dnp=True` on U9 and about 24 parts (`design.py:409-432`). `R()` and `C()` have
  no `dnp` argument yet (`design.py:78-86`); add one. This also removes three of the via re-route spots (U9.2/3/7).
- **Injector drivers:** VND7NV04 → NCV8401B C604055 (`design.py:339`), only after the 8-channel short and thermal test.
- **R144-R147:** 3.3 k → 4.7 k C17936 (`design.py:326`). This needs a `'4.7k'` key. The 3.3 k value was chosen for
  its power rating (`design.py:322-325`), so bench it first.
- **Cheaper diodes:** BAT54WS C7502694 (`design.py:477, 526, 527`, `wideband.py:182`); D6 and D12 MDD parts
  (`design.py:202, 215`).

**Correction to the old list:** do **not** change FB1 to C14709. That part is BLM18PG121 (120 Ω), recorded as a
mismatch in `mpn.json:138-145`. The design's C80165 is correct.

**Open weaknesses not on the old list** (from the docs; decide whether rev 0.11 addresses them):
- **Wideband front end:** an IP/RT/VM wire shorted to battery destroys R108-R110 (`VERIFICATION.md:527, 573`). ESR
  also reads 27% low, so the sensor runs about 740 °C (`:514`).
- **Analog clamp diodes:** leak 26-260 mV at 85 °C. The docs said to change the type; rev 0.10 did not
  (`VERIFICATION.md:526, 688`).
- **Shunt-clamp transistor Q20:** 1.22 W against 1 W in the worst fault (`VERIFICATION.md:574`).
- **Knock amplifier:** clips above about 284 mV (`:1119`).
- **MAP divider:** loads the sensor above about 210 kPa (`:1120`).
- **Reverse battery:** the reverse-battery path through D1/D2 has no pulse rating, and the optional 1 Ω resistor is
  not fitted (`:1178-1185`).
- **SD socket:** rated -20 to +85 °C only (design audit `:22, 76`).
- **No fiducials or test points** (`daughterboard/README.md:368-369`).
- **USB-C pegs:** four DRC hole-clearance items (`VERIFICATION.md:228`).
- **Unchecked land patterns:** FXL0530 and the ZXMS6004FF pin drawing.

---

## 4. Motherboards

**Must**
- **2 A PTC:** C46641168 → C960026 in `mb_later.py:23`, for F2 on 1999-2000 (`mb_nb1.py:85`) and F2/F3 on 2001-05
  (`mb_nb2.py:95`). Also update `mpn.json:855` and the stock text in `mb_na6.py:74` and `mb_na8.py:25`.
- **The via fixes in section 1:** D5, F1 and D4 need footprint-area re-routes.

**Should**
- **Harness-header holes:** 1.1 → 1.3-1.35 mm with 1.8 mm pads, in `mk_hdr_fp.py:42`. That covers the 76-pin,
  `_NB1` and 72-pin footprints.
  - The 1989-95 48-pin footprint is not generated by that script. Its pads are 1.506 × 1.151 mm on a 1.1 mm drill,
    about 0.2 mm ring; fix it by hand.
  - Delete the unused `TE_176122-6_64P`.
- **1989-95:** widen the 0.6 mm track that carries all of pin 1B's current for 46 mm (`VERIFICATION.md:682-683`).
- **1999-2000 / 2001-05:** add a pull-up footprint on the alternator control wire 1O / 3M (`VERIFICATION.md:1108`;
  `firmware/README.md:231-241`).
- **Optional external-MAP connector,** since the MPX5700AP is not recommended for new designs (`VERIFICATION.md:1112`).
- **1996-97:** consider the 174915-6 header, as Hellen does (`VERIFICATION.md:1113`).

**After a measurement (M)**
- **Outline and holes for 1996-2005:** today they use the NA outline as a stand-in (`mb_na6.py:14-53`). The board
  height is now 161.5 mm, not the 159 mm the old list assumed; J2 is at y 149.4 and J4 at y 157.6.
- **R21 / R22 pull-ups fitted by default:** `mb_common.py:111-117`, LCSC code C23162.
- **Tach pull-up on 1996-2005:** none exists today; nets at `mb_na96.py:79`, `mb_nb1.py:65`, `mb_nb2.py:59`.
- **Heater fuse:** F1 2920L300 → L400 if warm-up trips it (`mb_common.py:40-41`).
- **VVT fuse:** F3 to a 3 A part, which needs a 2920 footprint and new spacing (`mb_later.py:23, 38-40`).
- **Wideband connector:** decide after the AEM plug test.

---

## 5. Firmware (none of this is on main yet, except where marked)

- **IAT GM curve default** (section 2).
- **Idle limits for 1989-95:** override after the preset call at `miata_board.cpp:312` / `:326`. The cause is
  upstream (`mazda_miata_1_6.cpp:146`, min 20 against a max of 20), not the board's `:223-224`, which is NB only.
- **`acSwitchMode = PI_PULLUP`:** for NA6, NA94 and 2001-05 in the year-preset function (`:301`).
- **`fan2AcMode`:** already set for NA upstream; NB only, after checking a car.
- **Protections and estimates:** `mapEstimateTable`, boost cut, lambda protection and the coolant rev limit. Set them
  in `miataBoardDefaultConfiguration` (`:159`) or `miataAfterTuneDefaults` (`:345`).
- **Dwell and voltage correction:** dwell from real coil data.
- **LTFT:** decide, and if off add `#define EFI_LTFT_CONTROL FALSE` to `prepend.txt`.
- **Wideband controller:**
  - Bump the firmware pin (`firmware/wideband/miata_wbo_f103.txt:2`) to take upstream fixes 9295698 / 91aa7c6.
  - Enable the IWDG (`miata_f1/halconf.h:194`, `mcuconf.h:225`), plus a kick in the heater loop.
  - rusEFI's "update wideband over CAN" times out on this board (`VERIFICATION.md:359-362`).
- **Already done:** tach output off on 1989-95, and the 2001-02 / 2003-05 presets.

---

## 6. What to do first

1. **Wait for the ordered boards' bring-up.** Rev 0.11 should carry its fixes. The 1990-93 pump on 2O and an IAT
   reading on a GM sensor can be tested on those boards now.
2. **On one car per generation:**
   - IAT cavities and terminal size;
   - the 2001-05 IAT location;
   - case dimensions for 1996-2005.
3. **Do the via work first.**
   - Add the keep-out, delete `via_in_pad`, ring the tabs, and add the check. Then regenerate.
   - Hand-route the about 26 daughterboard and 6 motherboard spots.
   - Run KiCad DRC; the census is computed, not DRC-checked.
   - Decide 4 versus 6 layers with a real quote.
4. **Then the part swaps in section 3/4 and the firmware in section 5.**
5. **Order a 5-board pilot of rev 0.11** before a lot of 30.

---

## 7. Web research results (2026-11-17)

### 1990-93 fuel pump without the airflow meter
- **What the other ECUs do:** all switch the pump themselves, by one of three wires.
  - **MSPNP:** drives 12 V onto the violet wire, the circuit-opening relay's "starter" coil (ECU 1C). The ST SIG fuse
    must come out.
  - **Speeduino and forum installs:** drive the relay's pump-contact wire from ECU **2O**, the airflow-meter signal
    wire, which is free once the meter is gone. The link is made at the AFM plug.
  - **This repo:** an added wire from the diagnosis box F/P terminal to 2T.
- **Nobody recommends a permanent jumper.** It runs the pump whenever the key is on and removes the stall shut-off.
- **2T has no wire on a 1990-93 harness:** not confirmed either way. The rusEFI 1994 page lists 2T as the pump relay;
  1990-93 is unconfirmed.
- **Adopted for this board (unchecked on a car):**
  - The 1989-95 motherboard already makes 2O a low-side output (JP6 = BOOST). The 1989-93 jumper setting is now JP6 on
    BOOST, and the 1989-93 year preset puts the fuel pump on that driver (`boostControlPin` unassigned).
  - The pump link and the GM sensor both happen at the AFM plug, with no wire to the diagnosis box. The F/P → 2T wire
    stays documented as the alternative (JP6 on AFM, Fuel pump pin back to FP).
  - The cost: no boost valve on 2O on those cars.
  - Check on a car that the AFM plug's pump-contact wire is grounded to run, which makes it low-side compatible.

### GM sensor on the car's wires
- **1990-93 AFM plug:** MSPNP and Speeduino both say pins **1 and 6**, either way round. That plug numbering does not
  match the manual's terminal letters, so ring it out to ECU 2P / 2D.
- **1994-97 MAF plug:** sources disagree.
  - MSPNP says the 3rd and 4th wires.
  - The colour list for a '97 plug is: 1 black/light green chassis ground, 2 black/blue sensor ground,
    3 red/black, 4 red/white, 5 white/red 12 V.
  - On that list, the 3rd and 4th wires include the meter signal, and posters warn one of them may be 5 V.
  - Measure before connecting. Red/black to ECU 2P (1994-95) or 3K (1996-97) is the IAT.
- **1999-2000 and 2001-05:** Haltech's pages say the IAT is a separate 2-pin sensor in the air filter housing on both
  NB1 and NB2. The MAF is a separate 3-pin plug. So on all NB cars the GM sensor goes on the airbox IAT plug.
- **Plug terminals:**
  - **AFM/MAF plugs:** no source found.
  - **NB airbox IAT plug:** Ballenger sells a Mazda-IAT to GM adapter, CONN-85972 at $12.99, built with 1.8 mm
    Econoseal J male blades (CONN-100005, $0.25 each). That suggests the Mazda IAT plug takes a 1.8 mm blade.
  - **GM pins:** they are 1.5 mm and would probably be loose.
  - **Recommendation:** short adapter pigtails with Mazda-fit male blades rather than pushing GM pins into the plug.
- **Self-heating on a 2.49-2.7 k pull-up:** no reports found. MSPNP uses 2.49 k with the standard GM table.

### Case dimensions, 1996-2005
- **Method check:** Hellen's old NA6 board matches our measured 1989-95 outline and holes to 0.1 mm.
- **Hellen's current NA8 (1996-97), NB1 and NB2 boards share one frame:**
  - 154 x 159 mm rounded rectangle;
  - six holes at x 5 / 149, y 5.1 / 87.1 / 153.9;
  - header pin 1 at (16.0, 21.4).
- **Our provisional 1996-2000 boards:**
  - **Outline:** the notched NA outline, 161.5 mm tall.
  - **Holes:** at x 4 / 150, y 84 / 143, which is 1 mm wider and up to 10.9 mm off in y against Hellen.
  - **Header:** 3.2 mm higher than Hellen's.
- **Hellen's frame is not the stock case.** The Hellen NB2 README lists a separate "compatible case" (89661-3T270)
  and M4 screws "for NB external case". These boards ship in their own enclosure, so their frame says nothing about
  the stock Miata case. Our outlines stay provisional; measure one stock case per generation before ordering
  1996-2005 motherboards.
- **2001-05 header:** ours is TE 353830-5, spanning 72 mm; Hellen NB2 uses TE 8-5353015-1, spanning about 124 mm.
  Hellen's board is built for its own case, so this does not show ours is wrong, but re-check the part against a real
  2001-05 ECU before ordering.

---

## 8. Progress on the via work

Status on 2026-11-18, branch `no-via-in-pad`. Every board file there has no via in or within 0.1 mm of an SMD pad,
and the boards are released as daughterboard rev 0.11 and motherboards rev 0.14 (1989-95) / 0.10 (1996-2005): fab
files, BOMs, schematics, renders, 3D viewer and pictures regenerated from them by `scripts/reexport.sh`, which
exports a finished board without touching its copper and stops on a failed check (schematic against design, KiCad
DRC errors or unconnected items, a via in a pad, a hole too close to another).

| Board | In-pad vias (incl. within 0.1 mm) | Driver-tab vias moved out of the tab pads | Moved by `via_out_of_pad.py` | Moved with rip-up | By hand | KiCad DRC after |
|---|---|---|---|---|---|---|
| Daughterboard (6 layers) | 566 | 200 (same count, in the tab copper) | 348 | 16 | 2 (R101.1, R131.1) | no errors, nothing unconnected; same warnings as rev 0.10 |
| 1989-95 | 20 | — | 19 | — | 1 (F1.1) | no errors, nothing unconnected |
| 1996-97 | 15 | — | 15 | — | — | same, plus 2 thermal-spoke warnings at USB-C J4 A12 / B1 |
| 1999-2000 | 14 | — | 12 | — | 2 (F1.1; D5.1 re-joined to F4.2) | no errors, nothing unconnected |
| 2001-05 | 19 | — | 19 | — | — | no errors, nothing unconnected |

- **How the boards were done** (scripts in `scripts/`): `via_out_of_pad.py` moves each via to the nearest legal spot
  with stubs as wide as the track they continue (0.3 mm only where nothing wider fits); `via_ripup.py` takes the ones
  with no free spot, ripping a few short segments of other nets; `finish_route.py` re-joins those nets; the last few
  were placed by hand. `jlc_fab_check.py` now fails a release with any via in a pad.
- **Stubs narrowed to 0.3 mm** (daughterboard, 26): decoupling-cap GND / +3V3 pads, the INJ4 clamp diodes D45 / D49,
  D48's VBAT_IN end and C59's +5V end. `track_current.py` on the routed board: 0 FAIL / 0 CHECK, worst rise 7.2 °C,
  as on rev 0.10.
- **KiCad version.** The routing ran under KiCad 9, which saves a format KiCad 7 cannot open. `backport_copper.py`
  wrote the tracks, vias and zone fills back into the KiCad 7 files; everything else in them is unchanged. The zone
  fills are KiCad 9's; its starved-thermal warnings on the motherboards (9 / 10 / 7 / 17) are those of a KiCad 9
  refill of the unchanged boards, except the two at J4 on 1996-97.
- **Thermal check, done:** `board_thermal.py` on rev 0.10 reproduces its published table exactly; on rev 0.11, with
  the tab vias in the copper around the tab pads, the 1989-93 cases are 1-2 °C warmer at the injector drivers and
  1 °C at the clamp TVSs, the sequential years and the processor unchanged. `VERIFICATION.md`, `README.md` and
  `INSTALL.md` quote the new figures.

Also done on the branch: the GM IAT curve as the firmware default (section 2), the 1989-93 fuel pump on 2O (section 7),
the install guide and READMEs, the kit and BOM lines, R110 C17971 and the 2 A fuse C960026.

Still open before ordering: the car checks in section 2 ("Needs a car or bench") and the 1996-2005 case
measurements.

### Rev 0.12 (branch `rev-0.12`, 2026-11-19)

Released 2026-11-20 as daughterboard rev 0.12 and motherboards rev 0.15 (1989-95) / 0.11 (1996-2005): fab files,
schematics, BOMs, renders, 3D viewer and pictures regenerated from the boards (`scripts/reexport.sh`; every board
passes its checks: schematic against design, LCSC numbers, KiCad DRC with nothing unconnected, no via in a pad).
The routing items below are not in this release.
- **Processor STM32F405VGT6** (C56621) in place of the F407: the same rusEFI build, the pins checked against ST's
  pin data for the F405, F407 and F427 (`check_mcu_pins.py`), which stay as second sources.
- **CAN transceivers TJA1042T/3** (C132227) on U10 and U106.
- **LCSC number check** (`scripts/check_lcsc.py`, in CI and `reexport.sh`): every part on every board against
  `mpn.json`, value and size included. 422 parts, no mismatch.
- **R21 / R22 fitted** (C23162): the A/C and clutch switches close to ground, and the firmware reads them active low.
- **Harness-header holes 1.3 mm** on 1996-97, 1999-2000 and 2001-05 (pads stay 1.8 mm; DRC unchanged). 2001-05's
  header was not checked against a TE drawing. The unused 64-pin footprint is gone.
- **Firmware** (section 5): idle limits for 1989-95, A/C and clutch polarity, the protections, LTFT kept as rusEFI
  ships it (documented); the wideband watchdog. Upstream wideband fixes 9295698 / 91aa7c6 were already in the pinned
  production branch. Dwell waits for the coil measurement (bring-up list).
- The leftovers of the IAT jumper are gone from the scripts, and VERIFICATION's next-revision list carries a status.

Still to do, all needing the routing pipeline (KiCad 9 route, `backport_copper.py`):
- 1989-95 header holes: its 1.51 mm pads must grow to 1.8 mm for a 1.3 mm hole, which crowds four tracks / vias near
  1A, 1H, 1O and 2B.
- C12 to the VDDA side with FB1 upstream; vias around U4's tab; the 1989-95 1B track wider; the alternator pull-up
  footprint on 1999-2000 / 2001-05, and a tach pull-up footprint on 1996-2005 (4L / 2K / 3O, not fitted until the car
  measurement says so).
- Heater fuse F1: 1.99 A hold at 60 °C against a 2.25 A cold-heater peak (VERIFICATION N5, corrected). The
  2920L400/30GR (C19078761) fits the same pads; decide after logging the heater current in a hot cabin.
- Placement rotations for U3 / U14, J4 and the newer diodes: confirm in JLCPCB's preview and on the received boards
  (`order_bom.py` lists them).
- Then another release (`reexport.sh`, renders, viewer, docs).
