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
| Speeduino NA6 PNP v1.3 | two VNLD5090 (dual), four channels | the driver's own clamp (ST: 41 to 52 V for this family). No clamp parts outside it; the diodes on that sheet feed the indicator lights | one driver channel for the two injectors ([below](#how-the-others-fire-the-paired-injectors-2026-11-15)) |
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
this; all others must have their wiring harness repinned at the ECU". DIYAutoTune's page for the same cars agrees:
"'93 California spec models also use 4Y and 4Z for injector outputs" (its adapter's names for 2Y and 2Z), and "The
California spec versions in 1993 (and the 1994-1997 European market 1.6 cars) had sequential injection". On such a
car this board's PAIR jumper setting would leave injectors 3 and 4 without a pulse. INSTALL.md has a check for it.
Not confirmed from a wiring diagram.

## How the others fire the paired injectors (2026-11-15)

Asked: on a 1990-93 car's stock wiring (injectors 1 and 3 on one ECU wire, 2 and 4 on the other), how many drivers
work each wire, and how often does it open?

| ECU | Drivers on each paired wire | Openings of each wire per engine cycle | Read from |
|---|---|---|---|
| rusEFI Hellen NA6, and FOME on the same board | one. Its four outputs go to four pins (3U, 3V, 3Y, 3Z in its naming); the stock harness has wires on the first two | two. Batch mode fires each output again with the cylinder 360° away, "to support 'two-wire batch' mode" | the firmware's 1.6 preset, board file and connector map |
| Speeduino NA6 PNP v1.3 | one VNLD5090 channel per pin (2U, 2V, 2Y, 2Z) | two. Its own base tune: layout "Paired", 2 squirts, alternating. In the firmware: "Default is 1 squirt per revolution" | board file (pads traced), base tune, firmware |
| MegaSquirt from DIYAutoTune / AMP EFI (DIYPNP, MSPNP2) | one: INJ1 to 2U, INJ2 to 2V | settable. "2 squirts, alternating" is one (the two drivers take turns); simultaneous is two. The base map's setting could not be read | DIYAutoTune's 1990-93 page; MegaSquirt forum |
| ME221 / ME442 | one: "2U Injector 1 (&3 <1993)" | not stated. The guide calls the fuelling mode "usually 'Fully Seq'", which on this wiring would be one | install guide |
| Link MX5X | one per pin (Injection 1 to 4 on 2U, 2V, 2Y, 2Z) | not found | pinout |

- **Nobody puts two drivers on one wire.** Every board read drives each paired wire from a single output. This
  board's PAIR jumpers, which add a second driver, are its own (from motherboard rev 0.6, to halve each driver's
  current).
- **The open designs open each wire once per revolution**, twice per cycle. Speeduino's stated reason: without
  knowing the stroke "you cannot have less than 2 squirts". The Miata's cam sensor gives the stroke, so that reason
  does not bind here.
- **MegaSquirt's own advice is once per cycle:** "for port injection, 2 squirts/alternating is generally the way to
  go", and more squirts "eat into the injection time with the extra open times" (Bernard Fife, 2006). A poster in
  another thread prefers once per revolution for batch fire. Both are in use.
- **None of them has clamp parts outside the driver**, so none has this board's question of which of two clamps
  takes the energy, and none publishes a temperature estimate.

For this board, as it stood when this was written: its 1989-93 setting (two drivers per wire, two openings per
cycle) matched the open designs in how often the wire opens and nobody in the two drivers. One driver per wire with
one opening per cycle (VERIFICATION.md, "Clamp TVS: what JLCPCB stocks") is MegaSquirt's "2 squirts, alternating" on
the same wiring.

**Decided (owner, 2026-11-15): copy the open designs.** A stock-wired 1989-93 car now has one driver on each
injector wire (no shunts on JP1 and JP2 of the 1989-95 motherboard) and keeps batch firing. For this board that is
the hottest of the arrangements compared, because its clamp parts, not the driver chips, take the turn-off energy:
the numbers are in VERIFICATION.md, "1989-93: one driver per injector wire".

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
- Firing of the paired injectors: rusEFI `firmware/config/engines/mazda/mazda_miata_1_6.cpp`,
  `firmware/config/boards/hellen/hellenMiataNA6/` and `firmware/controllers/engine_cycle/fuel_schedule.cpp`
  (commit 1374bd0); FOME `firmware/controllers/engine_cycle/fuel_schedule.cpp` and
  `firmware/config/boards/hellen/hellen64_miataNA6_94/` in https://github.com/FOME-Tech/fome-fw (e628773, 2026-11-14);
  Speeduino `speeduino/fuel_calcs.cpp` in https://github.com/speeduino/speeduino (5d217bf, 2026-11-06) and
  `Mazda/NA6 PNP base tune.msq` in https://github.com/speeduino/Tunes (99b2a62, 2025-03-03);
  DIYAutoTune's 1990-93 Miata page: https://www.diyautotune.com/?p=95448 ;
  ME221 quick start: https://motorsport-electronics.co.uk/wp-content/uploads/2023/09/ME221_MX5_8995-Quick-Start-.pdf ;
  Link pinout: https://cdn.shopify.com/s/files/1/0811/8022/9941/files/G4x_MX5Link_MX5NAX_Wiring_Pinout.pdf ;
  MegaSquirt forum: https://microsquirt.com/viewtopic.php?p=137124 , https://microsquirt.com/viewtopic.php?p=125250 ,
  https://grassrootsmotorsports.com/forum/grm/injector-pairing-for-batch-fire-injection-in-megas/34018/page1/
