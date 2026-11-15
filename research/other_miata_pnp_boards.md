# What other Miata plug-in ECUs do (2026-11-15)

Asked: for the choices still open on rev 0.10 (processor temperature grade, where the 1989-93 injector turn-off
heat goes, the wideband lead), what do other plug-in ECUs for these cars do?

Read for this: the design files of the open-hardware boards (parts lists and schematics from their GitHub
repositories), and the makers' own pages and manuals for the closed ones. Where a figure comes from a sibling
part's datasheet, or a maker says nothing, the table says so. Nothing here was measured.

## Processor and temperature rating

| ECU | Processor | Temperature the maker states |
|---|---|---|
| rusEFI Hellen64, 1990-95 | STM32F407ZGT6 (parts list) | none |
| rusEFI Hellen72, 2001-05 | STM32F407IGT6 (parts list) | none |
| rusEFI uaEFI (universal) | STM32F429VIT6 on its processor module (parts list) | none |
| Speeduino NA6 PNP v1.3 | Arduino Mega 2560 plugged onto the board | none |
| Link G4X plug-ins (MX5X and others) | "150 MHz" engine processor | inside the ECU −10 to 85 °C, ambient −30 to 90 °C |
| ME221 / ME442 | "120 MHz 32-bit" | −20 to 85 °C |
| AMP EFI (the former DIYAutoTune MSPNP) | MS3Pro-based | none found |

- Every STM32 in the open designs is the suffix-6 part: −40 to 85 °C ambient, 105 °C junction. That is the grade
  this board's STM32F407VGT6 has. Nobody found uses the 105 °C / 125 °C suffix-7 grade.
- The two makers that state a figure stop at 85 °C inside the case.
- What ECUs see in a cabin, from one forum thread with logged internal temperatures: about 52 °C after half an
  hour at 25 °C outside; a trainer gives 65 °C as a typical maximum and calls 77 °C (170 °F) too hot. That is one
  thread, not a survey, but it is the range the model's "air around the board" should be read against.

## Injector drivers and the turn-off energy

| ECU | Injector drivers | Where the coil's turn-off energy goes | Two injectors on one wire (1990-93 harness) |
|---|---|---|---|
| Speeduino NA6 PNP v1.3 | two VNLD5090 (dual), four channels | the driver's own clamp (ST: 41 to 52 V for this family). No clamp parts outside it; the diodes on that sheet feed the indicator lights | its page does not say (the 1.6 harness joins the injectors in pairs) |
| rusEFI Hellen (output module 0.3) | AUIPS2041L in SOT-223 | the driver's own clamp (63 to 75 V on the sibling AUIPS2051L; the 2041's own sheet was not read). Freewheel diodes only on the general-purpose outputs | the part is listed at 1.4 A, less than two 12 to 16 Ω injectors draw; the uaEFI page says its board "was designed for one injector per driver" |
| ME221 / ME442, 1989-95 | not published | not published | one output per pair before 1993 ("Injector 1 (&3 <1993)"); high-impedance injectors only |
| AMP EFI, 1990-93 | four channels, high-impedance | not published | sequential needs the harness "repinned at the ECU", except the 1993 California cars |

- **Nobody adds clamp parts outside the driver, and nobody moves the energy off the board.** Every design found lets
  the driver chip's own clamp absorb it. That is what this board did up to rev 0.9. Rev 0.10's diode and 16 V TVS per
  injector is already more than any of them does.
- **Where the 1990-93 pairing is addressed, the answer is in the car:** split the two paired wires and run one
  injector per output. A rusEFI board seller's advice in a 1991 build thread: "I do recommend going sequential fuel
  right away"; the owner cut injectors 3 and 4 off the splice and ran them to spare ECU pins. AMP's instructions
  repin at the ECU.
- This board's 1989-95 motherboard already has that path: JP1 and JP2 on SEQ, injector 3 to pin 2Y and injector 4 to
  pin 2Z (manual cars only: 2Z is the A/T control unit on automatics). With that done a 1989-93 car heats the board
  like a 1994-2005 car.
- Both the Speeduino board and ST's datasheet for that driver family put a resistor in series with each driver input
  (1 kΩ). It supports the finding that the ordered rev 0.9 boards need their input resistors fitted.
- No maker publishes a temperature estimate for the board, and a search turned up no reports of a Miata plug-in ECU
  overheating in the footwell. Absence of reports is weak evidence; it is not a thermal analysis.

## Wideband sensor

| ECU | Controller | How the sensor connects |
|---|---|---|
| Speeduino NA6 PNP | none on board | any outside controller's 0-5 V output, on the stock oxygen-sensor wire |
| Link MX5X | none on board | outside controller on an analog input |
| rusEFI Hellen64 | on board (LSU 4.9) | the owner wires the sensor to a connector on the board and brings 12 V to the heater |
| rusEFI uaEFI | on board (LSU 4.9) | its own connector on the board |
| ME221 / ME442 | on board (LSU 4.9) | the maker's own lead ("WBO2 kit") on a six-way connector |
| AMP EFI | optional, on board | the maker's own 6 ft cable with an LSU 4.9, plugged into the ECU |

- Nobody uses AEM's harness. Makers with a controller on the board sell their own lead; the open boards leave the
  lead to the owner.
- Using AEM's ready-made harness (30-3427) is this project's own choice. It saves making a lead, at the cost of
  depending on a part documented for another product. The connector is now identified from AEM's instructions and
  matches a photograph of the plug (VERIFICATION.md, motherboards rev 0.13 / 0.9).

## What this means for the open choices

1. **Processor grade.** The 85 °C part is what everyone uses, and 85 °C inside the case is where the commercial
   units stop. Keeping the STM32F407VGT6 is in line with all of them. The model's thin spot remains one combination:
   a 1989-93 car on the stock paired wiring, with high-inductance injectors, held at high rpm in a hot cabin.
2. **Clamps on the 1989-95 motherboard.** Nobody does this. The usual fix for the same cars is the sequential
   conversion, which this motherboard already supports, and which removes the extra heat at its source.
3. **Wideband lead.** Keeping AEM's harness is defensible; the alternative others take is to supply their own lead.

## Decisions (2026-11-15)

The owner's, on the three choices above:

1. **Processor:** the standard STM32F407VGT6 stays.
2. **1989-95 motherboard:** no clamp parts. 1990-93 cars used at sustained high rpm are converted to one wire per
   injector; the steps are in [INSTALL.md](../INSTALL.md#one-wire-per-injector-on-a-199093-car-optional).
3. **Wideband lead:** AEM's harness (30-3427) stays.

One thing in AMP's 1990-93 instructions bears on the install guide: "'93 California models are already set up for
this; all others must have their wiring harness repinned at the ECU". If a 1993 California car has one wire per
injector, this board's PAIR jumper setting would leave injectors 3 and 4 without a pulse. INSTALL.md now has a
check for it. Not confirmed from a wiring diagram.

## Sources

- rusEFI Hellen64 NA6: `bom_replace_hellen64_NA6_94-d.csv` in https://github.com/rusefi/hellen-miata-NA6
- rusEFI Hellen72 NB2: `bom_replace_hellen72_NB2-f.csv` in https://github.com/rusefi/hellen-miata-NB2
- rusEFI building blocks (output 0.3, wbo 0.3, mega-mcu100 0.3 parts lists): https://github.com/andreika-git/hellen-one (commit 5076e80, 2026-10-30)
- rusEFI uaEFI: https://wiki.rusefi.com/uaEFI
- rusEFI 1991 Miata build thread: https://rusefi.com/forum/viewtopic.php?p=41337
- Speeduino NA6 PNP v1.3 schematic: `PNPs/Miata NA6/Latest` in https://github.com/speeduino/Hardware (commit ee6a924, 2026-04-04); board notes: https://gitea.interbiznw.com/speeduino/wiki.js/src/branch/master/boards/MX5_PNP.md
- ST VNL5090 family datasheet: https://www.st.com.cn/resource/en/datasheet/vnl5090n3-e.pdf
- Infineon AUIPS2051L datasheet (sibling of the AUIPS2041L): https://www.mouser.com/datasheet/2/196/international%20rectifier_auips2051-1168736.pdf ; AUIPS2041L listing: https://www.digikey.de/en/products/detail/infineon-technologies/AUIPS2041L/3455087
- Link G4X plug-in specifications: https://linkecu.com/documentation/G4X%20PlugIn%20ECU%20Specifications.pdf ; MX5X: https://nzperformance.co.nz/products/mx5x
- ME221 specifications: https://merchandising.demon-tweeks.com/DT/product-images/manuals-instructions-guides/atp_me221-ecu-specs-may23.pdf ; ME221 / ME442 1989-95 install guide: https://sps-motorsportshop.com/media/pdf/25/1a/70/ME221_ME442-MX58995-Install-Guide.pdf
- AMP EFI 1990-93 product page: https://www.diyautotune.com/product/mspnp2-mm9093/ ; installation: https://ampenginemanagement.com/blogs/mspnp-pro-documentation/pro-mm9093-installation
- ECU temperatures in use: https://hpacademy.com/forum/off-topic-discussion/show/ecu-temperature-2
