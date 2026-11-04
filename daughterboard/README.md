# Miata ECU — daughterboard rev 0.9 (routed, unverified)

125 × 76 mm, **4 layers**. All SMD parts are on top; the two 1×40 2.54 mm male headers are mounted on the
**bottom side** (plastic under the board, pins pointing down) so the board plugs straight into female
headers on the year-specific motherboard. J1 on the top edge carries power and outputs, J2 on the
bottom edge carries inputs, comms and the LSU 4.9 wideband sensor.

## What changed in rev 0.9
Layout only; the circuit is rev 0.8's.
- **J1 back on the top edge, J2 on the bottom edge**, as up to rev 0.7, with the four mounting holes in the corners.
  The 16 mm strip of output drivers that rev 0.8 put above J1 now sits just below it: each VND7NV04 (Q1-Q8) stands
  with its tab up against its own J1 pin and its leads facing the level shifters, and the relay switches, the
  ignition diodes and pull-down switches and their resistors are mirrored the same way. Everything else keeps its
  rev 0.8 place and copper.
- **Drain copper** per driver: @AREA@, joined by @VIAS@ thermal vias (most in the tab pad; order them filled and
  capped). Estimated junction to ambient @RTH@ °C/W (rev 0.8: 48).
- **On the motherboards** the daughterboard sits 16 mm lower, centred top to bottom (42 mm from the top edge, as up to
  rev 0.7): J1 and the upper standoffs are at their rev 0.7 places, J2, the lower standoffs and the AUX header 16 mm
  lower. A rev 0.9 daughterboard needs a motherboard of rev 0.9 (1989-95) or 0.7 (1996-2005).
- **Re-routed incrementally:** the rev 0.8 copper was kept everywhere except the nets of the moved parts
  (`route_eco.py`), which `route.py` routed again; four connections were finished by hand (`hand_route_all.py`).
  DRC: 0 unconnected, 0 clearance errors.

## What changed in rev 0.8
Fixes for what the rev 0.7 checks still flagged (`VERIFICATION.md`, [Rev 0.8](../VERIFICATION.md#rev-08-driver-temperature-and-protected-outputs)):
driver temperature, unprotected relay and ignition outputs, the sensor 5 V, the LSU drive wires, the CAN transceivers
and the AUX UART. Existing designators are unchanged where the part stays; new parts have new numbers.
- **Board 16 mm taller (125 × 76 mm).** The new strip along the top edge, above J1, sits over free motherboard space
  on every year (nothing on any motherboard is under it). J1, J2 and the four holes keep their places relative to each
  other, so the motherboards' sockets and standoffs don't move.
- **Low-side drivers Q1-Q8: ST VND7NV04** (DPAK, C155605) instead of the NCV8406A (SOT-223): 60 mΩ instead of 90-210,
  a 200 mJ clamp rating and 2.1 °C/W junction to case. They stand in the new strip, each with its tab down onto its
  own J1 pin, on a column of drain copper on F.Cu, In2.Cu and B.Cu (about 300 mm² per driver over the three layers)
  joined by 28-34 thermal vias, most of them inside the tab pad (`scripts/tab_copper.py`). Estimated junction to
  ambient 48 °C/W (rev 0.7: 109). Sequential injectors at 90 % duty, 7200 rpm, worst-case Rds(on): 84 °C at 60 °C
  ambient, 110 °C at 85 °C (rev 0.7: thermal shutdown). This is the "heat sink": copper and vias, no bolt-on part,
  since the board sits flat in the stock case. **Order the board with the vias epoxy-filled and capped** (JLC's
  via-in-pad process) so solder doesn't wick away from the tabs.
- **Relay, lamp and tach outputs: seven ZXMS6004FF protected low sides** (Q9-Q15, Diodes IntelliFET: current limit,
  thermal shutdown, 60 V clamp) instead of the ULN2003, driven at 5 V by a second SN74LVC4245A (U12) on the same
  enable as the other drivers, with 10k pull-downs (RN2, RN3). A relay or lamp wire shorted to battery now limits
  instead of burning a ULN channel.
- **Ignition outputs protected:** each TC4427 channel sources through its 100 Ω (now 1206) and a B5819W Schottky
  (D31-D34), and a ZXMS6004FF (Q16-Q19, gates from a 74HCT04, U13) pulls the output low. A coil wire shorted to battery
  just reverse-biases the Schottky. R144-R147 (3.3k, 1206) give the spark edge a defined fall with the pull-down off;
  3.3k keeps them inside their rating with a coil wire held at 24 V.
- **Protected harness 5 V:** a second TLS115 (U14) tracking +5V, out on J1 pin 13 (was a ground pin) to the harness's
  sensor 5 V cavities and the AUX header. The first TLS115 now feeds only the MAP sensor on the motherboard, so a
  sensor 5 V wire shorted to battery no longer takes the MAP reading or back-feeds the board. CLT/IAT bias from it;
  the hall pull-ups from it through a common-anode Schottky pair (D35), so a crank or cam wire shorted to battery
  puts nothing into its pull-up.
- **+3V3 shunt clamp:** a TL431 (U15) at 3.56 V drives a BCP53 PNP (Q20) that sinks fault current pushed into +3V3
  through the input clamps, with 2 × 100 µF bulk (C63, C68). Simulated with 1 A pushed in: 3.93 V peak for the first
  microseconds, then 3.56 V (the MCUs' absolute maximum is 4.0 V).
- **LSU drive wires:** F2 (0.1 A PTC) in the VM wire, Schottky clamps from the pump (D40) and virtual-ground (D41)
  drive nodes to +3V3, R108-R110 in 1206 and R137 22k. A short of IP, RT or VM to battery no longer reaches U101's
  outputs or the F103; the 1206 resistors take the short while it lasts (check or replace them after one).
  Firmware: VM_RESISTOR_VALUE 11.6 Ω (R109 + F2).
- **CAN: TI TCAN1042V-Q1** (U10, U106) instead of the SN65HVD230: ±58 V bus fault protection and −40 to 125 °C.
  Supplied from +5V (C67, C122), with 3.3 V I/O.
- **AUX UART:** 10k series resistors (R139, R140) and BAT54S clamps (D36, D37) on PC6/PC7.
- **Battery and ignition sense:** BAT54WS clamps D38/D39 on the dividers' ADC nodes.
- **Switch inputs: 22k/10k dividers** (was 33k): a 12 V signal at 9 V cranking now gives 2.81 V at the MCU, above ST's
  tested 2.31 V threshold. The hall series resistors R61/R63 are 0603.
- **Status LEDs:** comms and warning moved from PD13/PD14 to PC8/PC9 (PD12 run and PD15 error unchanged); the four
  adjacent PD pins left no way out for the fourth LED line. The board firmware is updated to match.
- **Re-routed incrementally** from the rev 0.7 copper (the old layout moved down 16 mm, `scripts/route_eco.py`), then
  `route.py`'s finish passes. The last connections around the wideband MCU and the LED lines were routed by hand
  (`scripts/hand_route.py`, chained by `hand_route_all.py`; a few short nets ripped up and rerouted in a better order),
  and `scripts/clean_dangling.py` removed the stubs that left. DRC: 0 unconnected, 0 clearance errors.

## What changed in rev 0.7
Fixes for the findings of the 2026-11-02 expanded circuit simulation and fault checks (`VERIFICATION.md`, findings
N1-N9). Existing designators are unchanged; new parts have new numbers.
- **U4 is an ST LDL1117S33R** (low dropout, same SOT-223 pinout) instead of the AMS1117-3.3. With about 1 V of dropout,
  the AMS1117 let the wideband MCU's VDDA (REF3033) run up to 0.95 V above its VDD while +5V rose or fell (power-up,
  key-off, crank dips; ST allows 0.3 V). The new part also keeps +3V3 up through an ISO 16750-2 level II crank, and
  is rated from -40 C.
- **D30 (BAT54WS) from the wideband MCU's VDDA to +3V3.** The low-dropout regulator alone still let VDDA lead VDD by
  about 0.8 V at key-off and in a slow brown-out, when the REF3033 holds up longer than +3V3; the Schottky caps the
  difference at about 0.25 V in every case simulated.
- **Clamps on the eight analog inputs:** D19-D26 (BAT54WS Schottky) from each AN_ node to +3V3, after the 5.6k. A
  sensor wire shorted to battery put 9.2 V on its MCU pin; now about 3.55 V, with 1.9 mA into +3V3 instead of the
  MCU. The 5.6k series and the CLT/IAT 2.7k bias resistors are now 0603. A Schottky leaks a little into the input
  when the sensor reads near 0 V, more when hot: estimated 5 mV at the sensor at 60 °C (up to about 46 mV with a
  worst-case part). Compare TPS and CLT readings with a meter on a hot day.
- **Clamps on the three 12 V switch inputs:** D27-D29 (1N4148WS) to +3V3, as on the hall inputs (a battery-fed switch
  closed during a load dump overdrove the pin). D27/D28 stand between the series resistors; D29 lies below the VR2
  parts.
- **Hall input resistors in 0603:** a crank/cam wire shorted to 14.4 V puts 88 mW into its 1k pull-up. The pull-ups
  now stand vertically beside their 4.7k series resistors to fit the larger size.
- **Knock input:** R138 (2.2k) ahead of the coupling cap C44, so a knock wire shorted to battery no longer couples a
  14 V step straight into the op-amp's input diodes.
- **Wideband sense inputs:** R137 (10k) feeds the Nernst buffer (U101 pin 10) from the LSU_UN wire, and F103 PA1 is no
  longer wired to LSU_VM (the firmware never sampled it). A UN or VM wire shorted to battery no longer reaches those
  inputs directly. The pump and virtual-ground drive paths can't take series resistance, so a short of IP, RT or VM
  to battery still damages U101 (inherited from the FOME module).
- **Injector driver copper:** OUT_INJ1-4 copper zones on both outer layers around Q1-Q4's tabs (86-90 mm² each), with
  17-21 thermal vias each. Estimated junction-to-ambient 109 °C/W instead of 130. This helps but doesn't remove the
  limit: at sustained 90 % injector duty a driver still reaches thermal shutdown at 85 °C ambient (1989-93), and on
  the sequential years, where each driver also absorbs its injector's turn-off energy, already at 60 °C near 7200 rpm.
  See VERIFICATION.md, N8.
- **Re-routed incrementally:** only the nets around the changed parts were routed again; the rest of the rev 0.6
  copper is unchanged. DRC: 0 unconnected, 0 clearance.

## What changed in rev 0.6
- **Wideband MCU: STM32F103C8T6** (U102, LQFP-48) instead of the STM32F042K6T6, which has been scarce for years and
  was down to about 100 at JLCPCB/LCSC; the F103C8T6 has over 200k there. The module's analog front end is unchanged.
  - Pins: ESR drives and LEDs face left, heater PWM / battery sense / pump PWM / BOOT1 right, CAN and the
    programming UART up, analog inputs down (`scripts/wideband.py`, U2_PADS).
  - New parts: an 8 MHz crystal Y101 with 33 pF loads C119/C120 (the same crystal as the main MCU's; keeps CAN
    timing in spec over temperature), R135 holds BOOT1 low, C121 decouples the third VDD pin.
  - Programming link unchanged: PD8/PD9 to the F103's USART1 (PA10/PA9), PD10 to BOOT0, PD11 to NRST.
  - Firmware: rusEFI's wideband controller with this board's port (`firmware/wideband/miata_f1`), carried by the
    main firmware and written with "Flash on-board wideband". rusEFI's own over-CAN wideband update is for the F042
    module and does not apply.

## What changed in rev 0.5
The fixes from the verification review (`VERIFICATION.md` in the repository root). Existing designators are unchanged;
new parts have new numbers.
- **Parts JLCPCB stocks (rev 0.5b).** JLCPCB's BOM check found ten lines short of stock. The replacements fit the
  same footprints; details in `VERIFICATION.md`.
  - Q1-Q8: onsemi **NCV8406A** (SOT-223, same pinout, 60-70 V active clamp, current limit and thermal shutdown)
    instead of the AUIPS2041L.
  - F1: TECHFUSE nSMD050-33V (33 V rating). D11/D12: Littelfuse SMAJ33A. L1: FH CMI322513U2R2KT.
    Status LEDs: Hubei KENTO KT-0603 G/B/Y. C103: YAGEO 33 nF 50 V. R110: 62 Ω (was 61.9 Ω, inside its 1 % tolerance).
  - VR inputs (spares, no Miata year uses a VR sensor): U9 is now a **LM2903** dual comparator (TI, onsemi, UMW and
    others make it) instead of the MAX9926, which is out of stock everywhere. Each input gets a BAT54S clamp to GND
    and +5V and 100k to a 1.65 V bias, and each output 1M of hysteresis (D15-D18, R73-R80, C60). The board was
    re-routed for these parts; `scripts/daughter_patch.py` adds the one track the autorouter left open (HALL1,
    through a via under the MCU) and nudges AN_AUX3 clear of the new clamps.
  - `fab/jlcpcb_cpl.csv` now uses the gerbers' own coordinates (no offset), with JLC's rotation corrections for
    SOT-223, TO-252, SOT-23, SOIC, TSSOP, LQFP and the resistor arrays, read off JLC's placement preview.
  - From the parts-availability review: D6 is now Littelfuse's SMCJ30A and D9 a Diodes B360A (both mainstream
    parts stocked at JLCPCB and US distributors; same footprints and ratings).
  - U105's footprint is named SOT-23-5 to match the AD8628ARTZ (identical pads), and SW1/SW2 share one BOM line.
- **5 V drive for the low-side drivers.** The rev 0.4 drivers (AUIPS2041) are specified at a 4-5.5 V input, and
  rev 0.4 drove them at 3.3 V.
  - U11 (SN74LVC4245A, DIR low: B → A) now drives Q1-Q8 from the MCU's control pins.
  - Its output enable is pulled up (R71), so the injectors, idle valve, VVT, boost and alternator stay off through
    reset, boot, the bootloader and DFU. The firmware enables them on **PA8** (open drain, active low) once every
    output is configured. This also covers PB3/PB4's power-up states (SWO trace, JTAG pull-up).
  - R19-R26 now pull the driver side low. The firmware parks unused control pins with the MCU's pull-downs
    (rusEFI's own idea of an unused pin is a pull-up, which would turn the driver on).
- **BOOT1 (PB2) pulled low** (R72), so ST's USB DFU bootloader starts reliably.
- **No relay back-feed.** The ULN2003's COM pin goes to an SMAJ33A TVS (D11, 36.7-40.6 V breakdown) instead of
  +12V. A battery-fed relay coil (the 2003-05 main relay) can no longer power the ECU through the clamp diodes with
  the key off. Relay kick-back clamps at 43 V at most (ULN2003 limit 50 V), and the TVS stays off through a 35 V load
  dump on the relay feeds.
- **Fused, clamped logic supply.** D7 (battery) and D8 (ignition wake) feed F1 (0.5 A PTC), then D12 (SMAJ33A) on +12V.
  - This keeps the buck under its 44 V maximum in load-dump and ISO pulse tests, and clamps the ignition path too.
    D12's breakdown sits above the 35 V load-dump clamp, so the input TVS D6 takes that energy and D12 only sees fast
    spikes.
  - An internal short trips F1 instead of waiting on the car's fuse.
  - C16 is now 10 µF / 50 V, D9 is a 60 V 3 A Schottky (Diodes B360A), and C59 adds buck output capacitance.
- **Crank/cam input clamps.** D13/D14 (1N4148WS) clamp PE7/PE8 to +3V3. These 5 V-tolerant pins have no clamp of
  their own, so a crank/cam wire shorted to battery would otherwise destroy them.
- **Buck inductor L2** is now a Sunlord MWSA0603S-100MT (7 × 6.6 mm, 5.5 A saturation), above the LMR14020's
  3.8 A maximum current limit. The old 5 × 5 mm part saturated at 3.5 A.
- **Crystal load caps** C13/C14 are 33 pF (were 22 pF) to match the 20 pF crystal.
- The Tag-Connect SWD pads J3 moved right of the MCU to make room for U11.

## What changed in rev 0.4
- **Both MCUs flash over the one USB-C port.** The main MCU now has a programming link to the wideband MCU (U102):
  | Main MCU (U1, STM32F407) | Wideband MCU (U102, STM32F042) | Job |
  |---|---|---|
  | PD8 (USART3 TX) | PA10 (USART1 RX) | data to the wideband's ROM bootloader |
  | PD9 (USART3 RX) | PA9 (USART1 TX) | data back |
  | PD10 | BOOT0 (10k pull-down kept) | high = start ST's ROM bootloader at the next reset |
  | PD11 (open drain) | NRST | reset |

  The F042's built-in ST bootloader listens on USART1 (PA9/PA10), pins the FOME firmware doesn't use. The main MCU raises
  BOOT0, pulses reset and then speaks ST's serial bootloader protocol (AN3155) to write the FOME firmware.
  - **Flow:**
    1. Flash rusEFI to the main MCU over USB-C (hold BOOT, tap RESET: ST's DFU bootloader).
    2. With the engine off, press "Flash on-board wideband" in TunerStudio (Popular Vehicles) or type
       `wbo_uart_flash` in the rusEFI console. rusEFI writes the wideband image it carries and reads it back.
    3. After that, rusEFI keeps PD10 low and PD11 released, and the wideband runs normally on CAN.
  - **Firmware:** `firmware/board/wideband_uart_flash.cpp` in the miata-ecus repository (compiles, not yet run on
    hardware).
  - **Fallback:** the J102 Tag-Connect SWD pads stay as a fallback.

## What changed in rev 0.3
- **Wideband controller laid out in this board's own style.** Rev 0.2 copied the FOME module's layout as a framed
  block (dense, mixed part angles, its own track style). Rev 0.3 keeps the identical circuit, parts, values and refs,
  but places and routes them like the rest of the board:
  - every part at 0 / 90°, in rows and columns next to the IC pins they serve;
  - the MCU (U102) at 90° so its analog pins face the analog front end, its CAN pins face the transceiver (U106,
    above it) and its heater-PWM / battery-sense pins face right;
  - the quad op-amp (U101) and its network directly above J2's LSU pins 33–36, with the op-amp feedback parts
    standing across the two pins they join; the current-sense amp (U105) right of the MCU;
  - the heater switch (Q101) over J2 37–40 with hand-planned 1 mm copper: its source lead straight onto pin 40, the
    drain from the tab between the leads onto pin 38; pins 37/38 and 39/40 are paired on the bottom layer;
  - routed by the same router as the rest of the board; the silkscreen frame and "WIDEBAND" title are gone.
- **Labels:** the block's ICs show their references like the rest of the board; the LEDs keep their HTR / OK / ACT
  labels. The BOOT / RESET switch labels moved below the switches (they overlapped the status-LED labels).
- **Bottom-side SMD pads** (the J102 Tag-Connect) now get their own plane vias from the router.

## What changed in rev 0.2
- **On-board wideband controller.** The complete FOME / rusEFI open-source wideband controller (MIT licence, github.com/mck1117/wideband, `board_module` rev C) is now on this board.
  - Its proven 4-layer layout was transplanted as a block. The parts, tracks, vias and heater pours are rotated into place, and its pad geometry was copied exactly.
  - Its stack-up matches this board: In1 GND, In2 +3V3.
  - The module's sensor-side header row lands exactly above J2 pins 33–40, so the LSU lines drop straight down into the header.
  - Changes to the module:
    - It runs from this board's +3V3 plane, so its LDO and power LED are removed.
    - The CAN ID straps are left open (rusEFI sets the index over CAN).
    - The pump-loop 33 nF cap is X7R instead of Y5V.
    - An SN65HVD230 (U106) puts it on the same CAN bus as the main MCU.
  - Refs are the module refs + 100. Module R31 is R131 here, so the block reads straight against the FOME schematic.
- **J2 pins 33–40** are now the LSU 4.9 group, listed below.
  - These pins came from SWD, BOOT0, +3V3 and +5V, which were removed from the header, and from two GND pins.
  - SWD stays on the Tag-Connect pads (J3), and BOOT/RESET are on the buttons.
- **F407 SWD pads (J3)** moved to the MCU's top-right corner. BOOT/RESET moved under the LED column.
- **LCSC fixes from a full part-number check:**
  - 2.7k 0402: C25770 was a 270k part. It is now C25885.
  - FB1: now C80165, the BLM18PG221SN1D.
  - U3: now C3743696, the TLS115B0EJ.
  - L1: now C223413, the Taiyo Yuden LBC3225T2R2MR (930 mA). The old part was a 320 mA signal inductor.

| J2 pin | Signal | | J2 pin | Signal |
|---|---|---|---|---|
| 33 | LSU_UN (Nernst cell) | | 37, 38 | LSU_HTR_N (heater low side) |
| 34 | LSU_RT (trim) | | 39, 40 | HTR_GND (heater current return; the motherboard ties it to GND) |
| 35 | LSU_VM (virtual ground) | | | |
| 36 | LSU_IP (pump current) | | | |

## Files
| Path | What |
|---|---|
| `miata_ecu_daughter.kicad_pro / .kicad_sch / .kicad_pcb` | KiCad 7.0.11 project: root schematic, board (opens in 8/9) |
| `mcu / power / outputs / inputs / connectors / wideband .kicad_sch` | Schematic sub-sheets, one per functional block |
| `miata_ecu_daughter_schematic.pdf` | All schematic pages as a PDF |
| `fab/jlcpcb_gerbers.zip` | Gerbers + drill files for JLCPCB (4-layer) |
| `fab/jlcpcb_bom.csv`, `fab/jlcpcb_cpl.csv` | JLC assembly BOM and placement file: every part except the two bottom-side 1×40 headers |
| `fab/self_order_bom.csv` | What you order and fit yourself: the J1/J2 1×40 pin headers |
| `miata_ecu_daughterboard_parts.xlsx` | Parts list by function, J1/J2 pinout, MCU pin map |
| `../scripts/` (repo top level) | The design source: `design.py` (parts + netlist), `placement.py`, `build_pcb.py`, `route.py`, `wideband.py` (the wideband circuit, mapped from the FOME module in `wideband_ref/` under its MIT licence), `wb_clean.py` (its rev 0.3 placement and heater copper; `wb_preview.py` draws a placement preview), `wb_build.py` (the rev 0.2 transplant, kept for reference), `daughter_finish.py`, `tab_copper.py` (the drivers' drain copper), `hand_route.py` / `hand_route_all.py` / `clean_dangling.py` (the rev 0.8 hand routes and cleanup) |

The schematic and the board are both generated from `scripts/design.py`. The schematic's exported
netlist was checked pad-by-pad against the board's netlist (958 pads, 0 differences), and every
footprint on the board is linked to its schematic symbol, so Update PCB from Schematic and
cross-probing work.

The schematic is drawn with real wires. Each local circuit is wired out the way you would draw it by
hand: input dividers, driver channels, the buck converter, the LDOs, the knock amp, the VR
conditioner, the crystal, reset and BOOT0, the LEDs and the decoupling banks. Every MCU supply pin is
tied to a +3V3 or GND rail. Net labels are only used where a signal leaves its block, i.e. at MCU
pins, header pins and signals going to another sheet. Global labels (flag shape) cross sheets; plain
labels stay within one sheet. Board nets carry the same names (sheet-local nets show up as e.g.
`/Power/BUCK_FB`), so Update PCB from Schematic changes nothing.

Rebuild: `scripts/daughter_make.sh <workdir>` (build, route, header flip, finishing, DRC), then
`scripts/daughter_release.sh <workdir>/finished.kicad_pcb <outdir>` (wired schematic, schematic-vs-design netlist
check, board relinked to the schematic, DRC, JLC files, PDF, parts workbook, renders).
Rev 0.8 was not routed from scratch: `route_eco.py` (with `DY=16`) carried the rev 0.7 copper over, `route.py` finished
it, then `flip_headers.py`, `daughter_finish.py`, the hand routes (`hand_route_all.py` with the open connections DRC
lists), `clean_dangling.py` and `daughter_patch.py`. A from-scratch `daughter_make.sh` run gives a different layout
that needs the same hand finishing.

## Stack-up and rules
- **Layers:** F.Cu signal / In1.Cu solid GND / In2.Cu solid +3V3 / B.Cu signal. GND pours are on both outer layers.
- **Tracks:** 0.2 mm signal track with 0.15 mm clearance. Power tracks are 0.4–1.0 mm (injector and solenoid outputs 0.8 mm).
- **Vias:** 0.6 mm with a 0.3 mm drill. All of this is standard JLC 4-layer capability.
- **Ground and 3.3 V connections:** every GND and +3V3 SMD pad drops to its plane through its own via.
  - The MCU supply pins go inward to vias under the package.
  - About 330 GND stitching vias sit on a 3 mm grid.
- **DRC (KiCad 7):** 0 clearance errors, 0 unconnected items. Warnings remaining:
  - Silkscreen overlaps (72) and silkscreen clipped by a pad opening (55): cosmetic.
  - Courtyard overlaps (97) on tightly packed passives. The copper clearances still pass, and with every courtyard
    shrunk by 0.2 mm (about the part body) nothing overlaps.
  - "Library not in configuration" notes from running headless.

## Circuit summary (topologies follow rusEFI hellen-one modules)
| Block | Parts |
|---|---|
| MCU | STM32F407VGT6 (1 MB flash, rusEFI F4 target), 8 MHz crystal, 4 status LEDs (PD12, PC8, PC9, PD15), BOOT/RESET buttons, Tag-Connect TC2030 SWD pads |
| Power | SMCJ30A load-dump TVS → SS34 reverse diode (and B5819W ignition wake) → 0.5 A PTC → SMAJ33A TVS → LMR14020 5 V buck. Two TLS115 protected 5 V supplies (MAP sensor; harness sensors on V5_EXT). LDL1117 3.3 V (low dropout), TL431 + BCP53 shunt clamp on +3V3. USB VBUS can power it on the bench. |
| Injectors / IACV / VVT / boost / alternator | 8× VND7NV04 protected low sides (DPAK, 60 mΩ) on drain copper columns with thermal vias, driven at 5 V by an SN74LVC4245A. Its output enable (PA8) is pulled off until the firmware runs; pull-downs on both sides |
| Relays, CEL, tach, spare | 7× ZXMS6004FF protected low sides (current limit, thermal shutdown, 60 V clamp) driven at 5 V by a second SN74LVC4245A on the same enable |
| Ignition (COP / smart coils) | 2× TC4427 sourcing through 100 Ω and a B5819W Schottky per channel; a ZXMS6004FF per channel (gates from a 74HCT04) pulls low, 3.3k to ground. Pulled down at the inputs |
| Crank / cam | LM2903 dual comparator for VR sensors (two 5.1k resistors per leg, 1 nF differential, BAT54S clamps, 1.65 V bias, 1M hysteresis). Spare: Miatas use hall/optical sensors on the hall inputs |
| Sensors | 8× 0–5 V inputs with a 5.6k/10k divider, 10 nF and a Schottky clamp to 3.3 V. CLT and IAT have 2.7k pull-ups to sensor 5 V. |
| Knock | 2.2k series, then an LMV321 AC-coupled gain stage (≈5.7×), biased at 1.65 V |
| Digital inputs | 2 hall (1k pull-up from V5_EXT through a Schottky, 4.7k series, clamped to 3.3 V), 3 switch inputs (12 V → 22k/10k, clamped to 3.3 V) |
| Comms | TCAN1042V-Q1 CAN, USB FS, USART6 (10k series, clamped) |
| Wideband (LSU 4.9) | FOME/rusEFI controller circuit with an STM32F103C8 (8 MHz crystal) running rusEFI's wideband firmware (board port in `firmware/wideband`), MCP6004 (virtual ground, pump driver, Nernst sense and buffer), AD8628 pump-current sense, REF3033 reference, VND14NV04 protected heater low side, TCAN1042V-Q1 on the shared CAN bus. Rev 0.8: PTC in the VM wire, Schottky clamps on the pump and virtual-ground drive |

## rusEFI board-config notes
- **Analog inputs:** divider ratio 1.56 on the eight sensor inputs. The battery and ignition dividers are (33k + 6.8k)/6.8k = 5.85.
- **Knock:** PA3 (ADC3_IN3).
- **CAN:** CAN2 on PB12 (RX) and PB13 (TX).
- **UART:** USART6 on PC6 and PC7.
- **USB:** PA11 / PA12.
- **Crank/cam:** VR1 (crank) on PE13, VR2 (cam) on PE12. The comparator output is high while the harness − leg is above the + leg, which is why the legs are swapped on J2. Wire VR sensors with both legs to the ECU (not one grounded at the engine).
- **Low-side enable:** PA8, open drain, low = enabled (the board firmware handles it).
- **Pin map:** the full pin map is in the spreadsheet's "MCU Pin Map" tab.
- **Wideband:** in TunerStudio, enable the rusEFI CAN wideband. The controller answers at index 0, the default.
  - Flashing goes through the main MCU: USART3 on PD8 (TX) / PD9 (RX) to the F103's ROM bootloader, PD10 = its BOOT0,
    PD11 = its reset (open drain); its BOOT1 is held low by R135. In normal running, keep PD10 low and PD11 released.
  - The firmware is rusEFI's wideband controller built for this board (`firmware/wideband`). Fallback: SWD through the
    J102 Tag-Connect pads on the bottom side.

## Before ordering
1. **LCSC numbers.** Every number was looked up against LCSC/JLCPCB in rev 0.2, and three wrong ones were fixed. Still check stock for the extended parts when you order.
2. **Part rotations.** Check every rotation in JLC's assembly preview. JLC's footprint orientation differs from KiCad's for some packages (SOT-223, SOIC, QSOP).
3. **Ignition outputs.** The 10 nF caps from the hellen ignition outputs were left off to keep the column tidy. If you want them back, add them on the motherboard next to the coil connector.
4. **Headers on the bottom.** J1/J2 are not in the JLC BOM or CPL (they'd need bottom-side assembly). They're in
   `fab/self_order_bom.csv`: hand-solder them, squared up against a motherboard's female sockets while the solder
   sets.
5. **Schematic and layout review.** No person has reviewed the schematic yet. The wideband *circuit* is the proven FOME design, but since rev 0.3 its *layout* is new to this board, so it no longer inherits the module's proven layout. Bring up the wideband on the first boards before relying on it (heater control, pump current, and lambda reading against a known sensor).
6. **Wideband first flash.** It goes through the main MCU (rev 0.4), so no extra cable is needed: the board's rusEFI firmware has the programming feature (`wbo_uart_flash`). A Tag-Connect TC2030-NL cable on J102 is the fallback.
7. **Parts packed tight.** The rev 0.7 and 0.8 clamps and the larger resistors sit closer to their neighbours than KiCad's
   courtyards allow (97 courtyard overlaps in the DRC report; 42 in rev 0.7); the part bodies themselves clear.
   Look at D19-D41 and the input columns in JLC's 3D preview before ordering.
8. **Injector drivers at full load.** Rev 0.8's DPAK drivers estimate 110 °C at 90 % duty, 7200 rpm and 85 °C ambient (VERIFICATION.md, Rev 0.8). The estimate rests on a copper-area model; measure a driver's temperature at full load before track use.
9. **Filled vias in the DPAK tabs.** Order the board with via-in-pad (epoxy-filled and capped vias); open vias in the tab pads would wick solder away from Q1-Q8.
10. **After an LSU wire short to battery,** check R108-R110 (1206): they take the fault so U101 doesn't, and R108 can open.
