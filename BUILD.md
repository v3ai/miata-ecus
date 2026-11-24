# Building the boards yourself

For people who order the bare or JLCPCB-assembled boards and finish them at home. If you bought an assembled unit,
skip this page: it arrives flashed and tested, and you go straight to [INSTALL.md](INSTALL.md).

> **Read this first.** No board has been built or run yet. Every step below is written from the design files and
> the firmware notes, and nobody has done it on this hardware. Steps marked **unchecked** are the ones to expect
> corrections to. Until a first board has been built, the supported path is an assembled unit.

What to order and where: [ORDERING.md](ORDERING.md). The firmware: [firmware/README.md](firmware/README.md).

**The steps, in order:**
1. [Solder the daughterboard to the motherboard](#1-solder-the-daughterboard-to-the-motherboard)
2. [Fit the through-hole parts](#2-fit-the-through-hole-parts)
3. [Visual and continuity checks](#3-visual-and-continuity-checks)
4. [Power up over USB (bench check)](#4-power-up-over-usb-bench-check)
5. [First flash over USB (DFU mode)](#5-first-flash-over-usb-dfu-mode)
6. [Flash the on-board wideband](#6-flash-the-on-board-wideband)
7. [Pick your year](#7-pick-your-year)

Then go to [INSTALL.md](INSTALL.md).

## What you need

- A daughterboard and your year's motherboard, both assembled by JLCPCB (the SMD parts and the USB-C socket).
- The hand-fitted parts from the motherboard's `fab/*_self_order_bom.csv`: the harness header, the MAP sensor with its
  two M3 × 16 screws and nylon-insert nuts, the wideband sensor header J2, and the add-on header J5 if you want it. They are all on the
  [parts page](additional-parts/shopping_list.html).
- On the 1989-95 board, the two option-jumper headers (JP5, JP6) and their shunts.
- A soldering iron, flux, solder, and a multimeter. For reflow: a hot plate, an oven or hot air, and solder paste.
- A USB-C cable and a laptop with the [rusEFI console](https://rusefi.com) or STM32CubeProgrammer or
  `dfu-util`, and [TunerStudio](https://www.tunerstudio.com/).
- The firmware `.bin` file ([firmware/README.md](firmware/README.md#getting-the-firmware)).

## 1. Solder the daughterboard to the motherboard

The daughterboard (rev 0.13 on) is a castellated module: its J1 / J2 pins are 80 plated half-holes along its two long
edges, and it is soldered flat onto the motherboard's two rows of lands, JD1 and JD2. There are no sockets, standoffs
or screws. An earlier, socketed daughterboard does not fit these motherboards. **Unchecked:** no module has been
soldered down yet.

Do this before fitting the through-hole parts (harness header, MAP sensor, wideband and add-on headers), so nothing
stands in the way of the lands or the heat.

1. **Before it goes down:** the wideband controller's SWD pads (J102) are on the module's underside and will be
   covered. They are only a fallback (the controller is programmed through the main processor), so this matters only
   if that programming route has failed you on an earlier board.
2. **Lands:** a motherboard assembled by JLCPCB usually arrives with the lands tinned, because its paste stencil
   covers them though nothing is placed there. Clean them and flux them. For reflow on bare lands, add solder paste:
   a thin, even line along each row, or a stencil.
3. **Place the module** with J1 (its edge with the processor) over JD1, the row nearest the harness header. The
   silkscreen marks the module's corners. Each half-hole sits on the middle of its land; the lands reach 1.8 mm out
   past the module's edge.
4. **Solder, one of two ways:**
   - **Reflow** on a hot plate, in an oven or with hot air across the whole module, to a normal profile for the paste.
     The daughterboard's own parts go through a second reflow; they are all on its top side, face up, so they stay
     put. Parts that have been out of their dry packing a long time may need baking first (their moisture ratings
     are on LCSC's pages).
   - **Soldering iron:** tack two diagonally opposite corner pins, check every half-hole is over its land, then solder
     each pin: the tip on the land just outside the edge, solder fed into the half-hole until it fills it.
5. **Check every joint:** a concave fillet from the land up into each half-hole, and no bridge to its neighbours.

The module comes off again only with every joint molten at once (hot plate or hot air): it is not a part to swap at
the roadside.

## 2. Fit the through-hole parts

From the motherboard's self-order list, in this order:

1. **Harness header** (J1): TE 174917-6 on the 1989-95 board, TE 178780-1 on 1996-97 and 1999-2000, TE 353830-5 on
   2001-05. Check the housing against the board's footprint before soldering.
2. **MAP sensor** (U2, MPX5700AP): it lies flat, marking side up, leads bent 90 degrees down, the single barb
   pointing toward the middle of the board, held by two M3 × 16 pan-head screws put in from under the board, with
   nylon-insert nuts on top of the sensor. The heads go underneath because there is little room between the board
   and the case floor. The mounting holes go through the whole 8 mm body, so shorter screws (the 10 mm ones listed
   before 2026-11-23) do not reach the nut. Bend the leads so the body lies flat before you solder them, then tighten
   the nuts only until the body is snug: it is plastic. The barb's position on the footprint was taken from a photo: check it against your part.
3. **Wideband header J2** (JST S08B-PUDSS-1). Its pin map, with the AEM harness's wire colours, is in
   [INSTALL.md](INSTALL.md#header-pin-maps) and printed beside the header.
4. **Add-on header J5**, if you will use it (a 2x10 box header; the silkscreen names its pins). Pin map: [INSTALL.md](INSTALL.md#header-pin-maps).
5. **1989-95 board:** the option-jumper headers JP5 and JP6, if not already fitted. Leave the shunts for
   [INSTALL.md](INSTALL.md#1-set-up-on-the-desk). The year links (R38-R42) come fitted by JLCPCB for the version you
   ordered: check them against [the table](INSTALL.md#header-pin-maps).
6. **1989-93 manual cars with a throttle position sensor kit:** fit R28 and move R29 to R30 now, if you will fit the
   kit ([README](README.md#throttle-position-sensor-198993-manual-cars)).

## 3. Visual and continuity checks

Unpowered, under a loupe or magnifier, then with a meter:

1. Look at the processor's and the injector drivers' joints, and the diodes' bands against the silkscreen.
2. Every castellated joint: a fillet, no bridge between neighbouring pins on either row.
3. Meter, the board unpowered, on the motherboard's land rows (JD1 = the module's J1, JD2 = its J2; pin 1 of each is the left end, by the JD1 / JD2 label):
   JD1 pins 4 and 5 read as ground, and there is no short between neighbouring pins along both rows, especially from
   12 V (JD1 pins 1 and 2) to ground.

## 4. Power up over USB (bench check)

1. Plug in USB-C, with nothing else connected. The **PWR** light (green) comes on, and **ERR** (red) stays off. The lights are named on the daughterboard from rev 0.14: RUN (green), COMM (blue), WARN (yellow), ERR (red), PWR (green).
2. The board shows up as a USB device. If it does not, go back to the continuity checks.
3. When you test the wideband itself, power the board from 12 V, not from USB alone.

## 5. First flash over USB (DFU mode)

A blank board has no firmware. Put the main processor in ST's DFU mode:

1. Hold **BOOT** (SW1 on the daughterboard; the name is printed beside it).
2. Tap **RESET** (SW2).
3. Release BOOT.
4. Flash the `.bin` at **0x08000000** with the rusEFI console from the bundle, STM32CubeProgrammer, or

   ```
   dfu-util -a 0 -s 0x08000000:leave -D rusefi_miata-ecu.bin
   ```

Details, and the later updates (no buttons: the rusEFI console's update button, through the OpenBLT bootloader), are in
[firmware/README.md, Flashing the main MCU (USB-C)](firmware/README.md#flashing-the-main-mcu-usb-c).

## 6. Flash the on-board wideband

With the engine off (on the bench), open TunerStudio, connect, and press **Flash on-board wideband** under Popular
Vehicles. It takes about 15 seconds. In the rusEFI console, `wbo_uart_flash` does the same and `wbo_uart_status`
reports the result. Details: [firmware/README.md](firmware/README.md#flashing-the-on-board-wideband).

Check that TunerStudio shows the wideband on CAN before you fit the sensor in an exhaust.

## 7. Pick your year

In TunerStudio, press **your year** under Popular Vehicles. 2001-02 and 2003-05 are separate buttons. This loads that
year's settings and its [base tune](firmware/README.md#base-tune). A blank board starts with the 1989-93 settings.

Optional: put a microSD card in the daughterboard's socket (lift the lid, lay the card in, close and slide it shut).
rusEFI logs to it; a card is not needed to run.

Now check the year links and set the jumpers (1989-95), and fit the unit to the car: [INSTALL.md](INSTALL.md).
