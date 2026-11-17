# P14 - CAN, USB, microSD (TCAN1042V x2, CAN termination, USB-C + USBLC6-2SC6, microSD socket)

STATUS: complete (2026-11-16).

## Summary
1. TCAN1042VDRQ1 (U10, U106) pin-by-pin correct: 1 TXD, 2 GND, 3 VCC=+5V, 4 RXD, 5 VIO=+3V3, 6 CANL, 7 CANH, 8 STB=GND (normal mode). VERIFIED (TI SLLSES9C p.4 pin table; pcb_pads.csv).
2. Both transceivers share CAN_H/CAN_L (nets J2.27/28, U10, U106; +J5.19/20 on current motherboards); single 120 ohm (R1) in series with a 0 ohm link R6 on the motherboard. Termination must stay (an unterminated recessive-to-dominant decay is slow); stubs are 3-4 cm. No error.
3. TCAN1042VDRQ1 live stock is 207 (JLC), extended part, $0.60@30. A pin-compatible, cheaper, deeply stocked alternate: NXP TJA1042T/3/1J (C132227, 62k stock, $0.31@30, $0.26@100, extended). Same SO8 pinout incl. VIO on 5 and STB on 8 (NXP TJA1042 Rev.12 Table 4); VIO 2.8-5.5 V, VCC 4.5-5.5 V, CANH/CANL +-58 V, Tvj -40..150 C; ESD spec is IEC 8 kV on bus pins (TI: 16 kV HBM).
4. USB-C (USB4105-GF-A): CC1 (A5) and CC2 (B5) each have own 5.1k (R2, R3) to GND; A6/B6 both USB_DP, A7/B7 both USB_DM, VBUS A4/A9/B4/B9 joined, GND A1/A12/B1/B12, shield S1 GND, SBU A8/B8 unconnected. Pad positions in pcb_pads.csv match the GCT footprint order (A1 B12 A4 B9 B8 A5 B7 A6 A7 B6 A8 B5 B4 A9 B1 A12). VERIFIED.
5. USBLC6-2SC6 (SOT-23-6): pins 1 and 6 (I/O1) = USB_DP, 3 and 4 (I/O2) = USB_DM, 2 GND, 5 VBUS: matches ST pinout. VERIFIED (datasheet p.1 diagram; pcb_pads.csv U4).
6. USB VBUS: USB_VBUS goes J4 -> JD2.32 -> daughterboard D10 (B5819W, pad 1 cathode on +5V, pad 2 anode on USB_VBUS): correct direction, USB can only feed +5V, +5V rail cannot push into VBUS (reverse biased). No VBUS sense wire to the MCU (PA9 unconnected) and rusEFI F4 board.h defines BOARD_OTG_NOVBUSSENS TRUE, so rusEFI does not need it. VERIFIED.
7. microSD J4 (Molex 47219-2001): contact numbering 1 DAT2, 2 CD/DAT3 (=CS), 3 CMD (=MOSI), 4 VDD, 5 CLK, 6 VSS, 7 DAT0 (=MISO), 8 DAT1 against nets: 2=SD_CS, 3=SD_MOSI, 4=+3V3, 5=SD_SCK, 6=GND, 7=SD_MISO, 1/8 pulled up: all correct; G1-G4 on GND. Footprint matches the Molex drawing (pitch 1.10, pad 0.80x1.50, G pads 1.45x2.00, 13.75 x 8.30 span, 2.60 / 2.38 offsets; computed from pcb_pads.csv). VERIFIED. No card-detect pins on this socket.
8. Nothing found wrong in scope; the useful findings are supply/alternate ones.

## 1. Identity and live stock (VERIFIED: tools/lcsc.py 2026-11-16, kb/parts_manifest.md)
| Board | Ref | BOM value | LCSC | Real MPN | Pkg | JLC lib | stock | $@30 | $@100 |
|---|---|---|---|---|---|---|---|---|---|
| cur_db, ord_db | U10, U106 | TCAN1042VDRQ1 | C485806 | TCAN1042VDRQ1 (TI) | SOIC-8 | ext | 207 (today) | 0.5957 | 0.5155 |
| cur_db | J4 | microSD | C164170 | 472192001 (Molex) | SMD hinged | ext | 1788 | 0.5859 | 0.5188 |
| cur_db, ord_db | D10 | B5819W | C8598 | B5819W SL (JSCJ) | SOD-123 | basic | 731k | 0.0256 | 0.0256 |
| all mb | J4 | USB4105-GF-A | C3020560 | GCT | SMD 16P | ext | 16.7k | 0.7331 | 0.6366 |
| all mb | U4 | USBLC6-2SC6 | C7519 | ST | SOT-23-6L | ext | 34.8k | ~0.12 | 0.0789 at high qty |
| all mb | R2,R3 | 5.1k | C23186 | UNI-ROYAL | 0603 | basic | 19M | 0.0015 | |
| all mb | R1 | 120 | C22787 | UNI-ROYAL | 0603 | basic | 2.4M | 0.002 | |
| all mb | R6 | 0R | C21189 | UNI-ROYAL | 0603 | basic | 17M | 0.0021 | |

## 2. TCAN1042V digest (datasheet datasheets/C485806_TCAN1042VDRQ1.pdf = TI SLLSES9C, genuine TI)
- Abs max: VCC, VIO -0.3..7 V; CANH/CANL +-58 V (non-H); logic <= VIO+0.3; Tj -55..150 C. HBM bus pins +-16 kV, others +-6 kV.
- Pins SOIC-8 (V variant): 1 TXD, 2 GND, 3 VCC, 4 RXD, 5 VIO, 6 CANL, 7 CANH, 8 STB (active-high standby; low = normal).
- Decoupling in design: U10 C67 (+5V 100n) and C56 (+3V3 100n) at ~4 mm; U106 C122 (+5V) and C118 (+3V3) at ~3-4 mm. OK.

## 3. Usage audit
### U10 (daughterboard, cur and ord identical nets)
| Pad | Net | Datasheet | OK |
|---|---|---|---|
| 1 | CAN_TX (U1.52) | TXD | OK |
| 2 | GND | GND | OK |
| 3 | +5V | VCC | OK |
| 4 | CAN_RX (U1.51) | RXD | OK |
| 5 | +3V3 | VIO | OK |
| 6 | CAN_L | CANL | OK |
| 7 | CAN_H | CANH | OK |
| 8 | GND | STB low = normal | OK |
U106 identical with WB_CAN_TX/RX (U102.33 / U102.32). Footprint SOIC-8_3.9x4.9mm_P1.27mm, standard (pads 1.95x0.6 at 1.27 pitch, span 4.95 centre rows - matches generic SOIC-8).
### Stress
CAN pins +-58 V covers 24 V jump start, reverse battery on a harness short, and suppressed load dump (35 V); only reachable via J5 pins on cur_mb (ord boards have no J5 CAN; bus stays on-board). No TVS on J5 CAN: relies on 16 kV HBM; acceptable for an add-on header (INFERRED). Power: ~70 mA dominant max, 92 K/W (NXP) / similar: negligible.
### CAN bus topology
Net CAN_H = J2.28, U10.7, U106.7 (+J5.19, R1.1); CAN_H length 32 mm F.Cu + 4 mm In3 + 3.9 mm B.Cu, CAN_L similar (pcb_net_routing.csv). 120 ohm only at the motherboard end (R1+R6 0R in series = a cuttable link). External device on J5 brings its own termination -> ~60 ohm. Fine at 500 kbit/s. Could one transceiver be saved? Only by moving the F407<->F103 wideband link to non-CAN (UART/open-drain wired-AND) which needs firmware changes in the wideband code; saves ~$0.6 + 2 caps; rusEFI wideband protocol is CAN (INFERRED), so not recommended.
### USB path
J4 (USB4105) -> U4 (placed on the same board edge, ~1.8 mm away) -> JD2.30/31 -> daughterboard J2.30/31 -> U1.70/71 (PA11/PA12) directly, no series resistors (OK for STM32 FS). Skew DM 58.5 mm vs DP 62.8 mm on 2 layers, no impedance control: acceptable for 12 Mbit/s (INFERRED). USBLC6 traces: both I/O pairs pass through the part per its recommended layout (netlist shows I/O1 pins 1&6 on DP, I/O2 pins 3&4 on DM).
VBUS 0.3 mm track; D10 1 A part for <= 500 mA host current.
Footprint USB_C_GCT_USB4105_16P custom (ecu_mb): pad order matches GCT drawing (image crop work/P14-can-usb-sd/usb4105_layout_pins.png).
### microSD
Supply C69 100n + C70 10u (+3V3) within ~9 mm; 47k pull-ups on CS, MISO, MOSI, DAT1, DAT2 (SD spec 10-100k): OK. SCK has no pull-up (normal). SPI2 PB10/PB14/PB15 -> U1 pins 47/53/54 and CS PD13 pin 60: LQFP100 pin functions match STM32F407 (SPI2_SCK on PB10 AF5 is valid) (INFERRED from memory of F407 AF table, UNVERIFIED against ST datasheet). rusEFI supports USB MSD of the card only if HAL_USE_USB_MSD is built (mmc_card.cpp:402/609), so "card appears as a drive" must be checked in the project's firmware build.
UX: hinged socket under a closed stock case means card changes require opening the case; the design relies on MSD over USB. Socket rated -20..85 C (documented already).

## 4. Cost / alternates
- TJA1042T/3/1J (C132227): saves ~$0.28/unit at 30 pcs x2 = ~$0.57 per board, stock 62k vs 207. Differences: ESD spec form, Tvj to 150 C, SPLIT-less /3 variant has VIO. Needs no layout change. Other TJA1042T/3 clones (Tudi C55098871) not read.
- USBLC6: clones (UMW C2687116 $0.048) save <$0.1; datasheets not read; not recommended.
- No removal possible: R1 needed (termination), R6 0R only a cut-link (could be replaced by direct trace, saves $0.002), D10 needed for USB-only bench power.

## Sources actually read
the review brief; evidence/cur_db, cur_mb8995/9697/9900, ord_mb8993/9495/9697/9900, ord_db pcb_nets/pads/footprints/routing; datasheets/txt/C485806 (pp.4-6), C7519 (pin diagram), C3020560 (pin table), C164170 Molex drawing image (pdfpages p110); NXP TJA1042 datasheet (work/P14-can-usb-sd/dl/tja1042.pdf, Table 4/6); repo/scripts/design.py lines 110-166, 242, 509-524; rusEFI stm32f4 board.h; tools/lcsc.py searches.

## Not checked
Layer-image review (thermal/loop area) of CAN/USB routing; USB4105 land pattern dimensions beyond pad order; Molex 47219 temperature rating from product spec; USBLC6 abs-max table in detail; whether the daughterboard +5V can cope with USB inrush; ESD behaviour of USB shield vs stock case; STM32 AF table; TCAN1044V alternates (datasheet download failed).
