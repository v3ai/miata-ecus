# Miata ECU — daughterboard rev 0.5 (routed, unverified)

125 × 60 mm, **4 layers**. All SMD parts are on top; the two 1×40 2.54 mm male headers are mounted on the
**bottom side** (plastic under the board, pins pointing down) so the board plugs straight into female
headers on the year-specific motherboard. J1 on the top edge carries power and outputs, J2 on the
bottom edge carries inputs, comms and the LSU 4.9 wideband sensor.

## What changed in rev 0.5
The fixes from the verification review (`VERIFICATION.md` in the repository root). Existing designators are unchanged;
new parts have new numbers.
- **5 V drive for the low-side drivers.** The AUIPS2041 input, current limit and shutdown are specified at 4-5.5 V,
  and rev 0.4 drove them at 3.3 V.
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
  - C16 is now 10 µF / 50 V, D9 is a 60 V SS36, and C59 adds buck output capacitance.
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
| `fab/jlcpcb_bom.csv`, `fab/jlcpcb_cpl.csv` | JLC assembly BOM and placement file |
| `miata_ecu_daughterboard_parts.xlsx` | Parts list by function, J1/J2 pinout, MCU pin map |
| `../scripts/` (repo top level) | The design source: `design.py` (parts + netlist), `placement.py`, `build_pcb.py`, `route.py`, `wideband.py` (the wideband circuit, mapped from the FOME module in `wideband_ref/` under its MIT licence), `wb_clean.py` (its rev 0.3 placement and heater copper; `wb_preview.py` draws a placement preview), `wb_build.py` (the rev 0.2 transplant, kept for reference), `daughter_finish.py` |

The schematic and the board are both generated from `scripts/design.py`. The schematic's exported
netlist was checked pad-by-pad against the board's netlist (754 pads, 0 differences), and every
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

## Stack-up and rules
- **Layers:** F.Cu signal / In1.Cu solid GND / In2.Cu solid +3V3 / B.Cu signal. GND pours are on both outer layers.
- **Tracks:** 0.2 mm signal track with 0.15 mm clearance. Power tracks are 0.4–1.0 mm (injector and solenoid outputs 0.8 mm).
- **Vias:** 0.6 mm with a 0.3 mm drill. All of this is standard JLC 4-layer capability.
- **Ground and 3.3 V connections:** every GND and +3V3 SMD pad drops to its plane through its own via.
  - The MCU supply pins go inward to vias under the package.
  - About 330 GND stitching vias sit on a 3 mm grid.
- **DRC (KiCad 7):** 0 clearance errors, 0 unconnected items. Warnings remaining:
  - Silkscreen overlaps (19) and silkscreen clipped by a pad opening (5): cosmetic.
  - Courtyard overlaps (12) on tightly packed passives. The copper clearances still pass.
  - "Library not in configuration" notes from running headless.

## Circuit summary (topologies follow rusEFI hellen-one modules)
| Block | Parts |
|---|---|
| MCU | STM32F407VGT6 (1 MB flash, rusEFI F4 target), 8 MHz crystal, 4 status LEDs, BOOT/RESET buttons, Tag-Connect TC2030 SWD pads |
| Power | SMCJ30A load-dump TVS → SS34 reverse diode (and B5819W ignition wake) → 0.5 A PTC → SMAJ33A TVS → LMR14020 5 V buck. TLS115 protected 5 V sensor supply. AMS1117 3.3 V. USB VBUS can power it on the bench. |
| Injectors / IACV / VVT / boost / alternator | 8× AUIPS2041L protected low-sides driven at 5 V by an SN74LVC4245A. Its output enable (PA8) is pulled off until the firmware runs; pull-downs on both sides |
| Relays, CEL, tach, spare | ULN2003 (7 ch), flyback clamp to an SMAJ33A TVS (not +12V) |
| Ignition (COP / smart coils) | 2× TC4427, 5 V push-pull through 100 Ω, pulled down at the inputs |
| Crank / cam | MAX9926 dual VR (two 5.1k resistors per leg, 1 nF differential) |
| Sensors | 8× 0–5 V inputs with a 5.6k/10k divider and 10 nF. CLT and IAT have 2.7k pull-ups to sensor 5 V. |
| Knock | LMV321 AC-coupled gain stage (≈5.7×), biased at 1.65 V |
| Digital inputs | 2 hall (1k pull-up, 4.7k series, clamped to 3.3 V), 3 switch inputs (12 V → 33k/10k) |
| Comms | SN65HVD230 CAN, USB FS, USART6 |
| Wideband (LSU 4.9) | FOME/rusEFI controller: STM32F042 running the FOME wideband firmware, MCP6004 (virtual ground, pump driver, Nernst sense and buffer), AD8628 pump-current sense, REF3033 reference, VND14NV04 protected heater low side, SN65HVD230 on the shared CAN bus |

## rusEFI board-config notes
- **Analog inputs:** divider ratio 1.56 on the eight sensor inputs. The battery and ignition dividers are (33k + 6.8k)/6.8k = 5.85.
- **Knock:** PA3 (ADC3_IN3).
- **CAN:** CAN2 on PB12 (RX) and PB13 (TX).
- **UART:** USART6 on PC6 and PC7.
- **USB:** PA11 / PA12.
- **Crank/cam:** VR1 (crank) on PE13, VR2 (cam) on PE12. The MAX9926 output is inverted, which is why the + and − legs are swapped on J2.
- **Low-side enable:** PA8, open drain, low = enabled (the board firmware handles it).
- **Pin map:** the full pin map is in the spreadsheet's "MCU Pin Map" tab.
- **Wideband:** in TunerStudio, enable the rusEFI CAN wideband. The controller answers at index 0, the default.
  - Flashing goes through the main MCU: USART3 on PD8 (TX) / PD9 (RX) to the F042's ROM bootloader, PD10 = its BOOT0,
    PD11 = its reset (open drain). In normal running, keep PD10 low and PD11 released.
  - The firmware is the FOME wideband `f0_module` build. Fallback: SWD through the J102 Tag-Connect pads on the bottom side.

## Before ordering
1. **LCSC numbers.** Every number was looked up against LCSC/JLCPCB in rev 0.2, and three wrong ones were fixed. Still check stock for the extended parts when you order.
2. **Part rotations.** Check every rotation in JLC's assembly preview. JLC's footprint orientation differs from KiCad's for some packages (SOT-223, SOIC, QSOP).
3. **Ignition outputs.** The 10 nF caps from the hellen ignition outputs were left off to keep the column tidy. If you want them back, add them on the motherboard next to the coil connector.
4. **Headers on the bottom.** J1/J2 are listed as `Bottom` in the CPL. If you let JLC fit them, that is
   bottom-side assembly and adds cost. They are cheap to hand-solder, and you can square them up against
   the motherboard's female headers while the solder sets. If you do that, delete J1/J2 from the BOM.
5. **Schematic and layout review.** No person has reviewed the schematic yet. The wideband *circuit* is the proven FOME design, but since rev 0.3 its *layout* is new to this board, so it no longer inherits the module's proven layout. Bring up the wideband on the first boards before relying on it (heater control, pump current, and lambda reading against a known sensor).
6. **Wideband first flash.** It goes through the main MCU (rev 0.4), so no extra cable is needed: the board's rusEFI firmware has the programming feature (`wbo_uart_flash`). A Tag-Connect TC2030-NL cable on J102 is the fallback.
