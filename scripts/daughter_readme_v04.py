"""Rev 0.4 README for the daughterboard release: the rev 0.3 README plus this revision's change (the wideband
MCU is programmed through the main MCU, so both flash over the one USB-C port).
usage: daughter_readme_v04.py <rev 0.3 README> <release dir>"""
import sys, re, collections
src, rel = sys.argv[1], sys.argv[2]
t = open(src).read()
drc = open(rel + '/fab/drc_report.txt').read()
cnt = collections.Counter(re.findall(r'^\[(\w+)\]', drc, re.M))


def rep(a, b):
    global t
    assert a in t, a[:70]
    t = t.replace(a, b)


rep('# Miata ECU — daughterboard rev 0.3 (routed, unverified)', '# Miata ECU — daughterboard rev 0.4 (routed, unverified)')
rep('## What changed in rev 0.3', '''## What changed in rev 0.4
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
    2. rusEFI then flashes the wideband, either from an image it carries or by passing a PC programmer
       (STM32CubeProgrammer / `stm32flash`) through its USB serial port.
    3. After that, rusEFI keeps PD10 low and PD11 released, and the wideband runs normally on CAN.
  - **Firmware:** the link is hardware only. The rusEFI side (bootloader client or pass-through) belongs in this
    board's rusEFI port, which hasn't been written yet.
  - **Fallback:** the J102 Tag-Connect SWD pads stay as a fallback.

## What changed in rev 0.3''')
rep('''- **Wideband:** in TunerStudio, enable the rusEFI CAN wideband. The controller answers at index 0, the default.
  - First flash: program the FOME wideband firmware (`f0_module` target) through the J102 Tag-Connect pads on the bottom side.
  - After that, rusEFI can update it over CAN.''',
    '''- **Wideband:** in TunerStudio, enable the rusEFI CAN wideband. The controller answers at index 0, the default.
  - Flashing goes through the main MCU: USART3 on PD8 (TX) / PD9 (RX) to the F042's ROM bootloader, PD10 = its BOOT0,
    PD11 = its reset (open drain). In normal running, keep PD10 low and PD11 released.
  - The firmware is the FOME wideband `f0_module` build. Fallback: SWD through the J102 Tag-Connect pads on the bottom side.''')
rep('6. **Wideband first flash.** Plan on a Tag-Connect TC2030-NL cable (or pogo pins) for the one-time SWD flash of U102.',
    '6. **Wideband first flash.** It goes through the main MCU (rev 0.4), so no extra cable is needed once this board\'s rusEFI '
    'port has the programming feature. Until then, a Tag-Connect TC2030-NL cable on J102 does it.')
m = re.search(r'- \*\*DRC \(KiCad 7\):\*\*.*?(?=\n## )', t, re.S)
t = t[:m.start()] + (f'''- **DRC (KiCad 7):** 0 clearance errors, {cnt.get('unconnected_items', 0)} unconnected items. Warnings remaining:
  - Silkscreen overlaps ({cnt.get('silk_overlap', 0)}) and silkscreen clipped by a pad opening ({cnt.get('silk_over_copper', 0)}): cosmetic, in the main part of the board.
  - Courtyard overlaps ({cnt.get('courtyards_overlap', 0)}) on tightly packed passives in the main part of the board. The copper clearances still pass.
  - "Library not in configuration" notes from running headless.
''') + t[m.end():]
assert 'clearance' not in cnt, 'clearance errors in DRC: fix before release'
open(rel + '/README.md', 'w').write(t)
print('wrote', rel + '/README.md', dict(cnt))
