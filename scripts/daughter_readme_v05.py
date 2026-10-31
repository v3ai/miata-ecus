"""Rev 0.5 README for the daughterboard release: the rev 0.4 README plus this revision's changes (the fixes from the
verification review, VERIFICATION.md).
usage: daughter_readme_v05.py <rev 0.4 README> <release dir> <netlist pads checked>"""
import sys, re, collections
src, rel, npads = sys.argv[1], sys.argv[2], sys.argv[3]
t = open(src).read()
drc = open(rel + '/fab/drc_report.txt').read()
cnt = collections.Counter(re.findall(r'^\[(\w+)\]', drc, re.M))


def rep(a, b):
    global t
    assert a in t, a[:70]
    t = t.replace(a, b)


rep('# Miata ECU — daughterboard rev 0.4 (routed, unverified)', '# Miata ECU — daughterboard rev 0.5 (routed, unverified)')
rep('## What changed in rev 0.4', '''## What changed in rev 0.5
The fixes from the verification review (`VERIFICATION.md` in the repository root). Existing designators are unchanged;
new parts have new numbers.
- **Parts JLCPCB stocks (rev 0.5b).** JLCPCB's BOM check found ten lines short of stock. All replacements fit the same
  footprints (no re-route); details in `VERIFICATION.md`.
  - Q1-Q8: onsemi **NCV8406A** (SOT-223, same pinout, 60-70 V active clamp, current limit and thermal shutdown)
    instead of the AUIPS2041L.
  - F1: TECHFUSE nSMD050-33V (33 V rating). D11/D12: Littelfuse SMAJ33A. L1: FH CMI322513U2R2KT.
    Status LEDs: Hubei KENTO KT-0603 G/B/Y. C103: YAGEO 33 nF 50 V. R110: 62 Ω (was 61.9 Ω, inside its 1 % tolerance).
  - U9 (MAX9926, spare VR inputs no Miata uses) is not fitted; its footprint stays.
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
  - C16 is now 10 µF / 50 V, D9 is a 60 V SS36, and C59 adds buck output capacitance.
- **Crank/cam input clamps.** D13/D14 (1N4148WS) clamp PE7/PE8 to +3V3. These 5 V-tolerant pins have no clamp of
  their own, so a crank/cam wire shorted to battery would otherwise destroy them.
- **Buck inductor L2** is now a Sunlord MWSA0603S-100MT (7 × 6.6 mm, 5.5 A saturation), above the LMR14020's
  3.8 A maximum current limit. The old 5 × 5 mm part saturated at 3.5 A.
- **Crystal load caps** C13/C14 are 33 pF (were 22 pF) to match the 20 pF crystal.
- The Tag-Connect SWD pads J3 moved right of the MCU to make room for U11.

## What changed in rev 0.4''')
rep('| Power | SMCJ30A load-dump TVS → SS34 reverse diode → LMR14020 5 V buck. TLS115 protected 5 V sensor supply. AMS1117 3.3 V. Ignition can wake the ECU (B5819W). USB VBUS can power it on the bench. |',
    '| Power | SMCJ30A load-dump TVS → SS34 reverse diode (and B5819W ignition wake) → 0.5 A PTC → SMAJ33A TVS → LMR14020 5 V buck. TLS115 protected 5 V sensor supply. AMS1117 3.3 V. USB VBUS can power it on the bench. |')
rep('| Injectors / IACV / VVT / boost / alternator | 8× AUIPS2041L protected low-sides with 10k pull-downs (outputs stay off while the MCU is in reset) |',
    '| Injectors / IACV / VVT / boost / alternator | 8× NCV8406A protected low-sides driven at 5 V by an SN74LVC4245A. Its output enable (PA8) is pulled off until the firmware runs; pull-downs on both sides |')
rep('| Relays, CEL, tach, spare | ULN2003 (7 ch), flyback to +12V |', '| Relays, CEL, tach, spare | ULN2003 (7 ch), flyback clamp to an SMAJ33A TVS (not +12V) |')
rep('| Digital inputs | 2 hall (1k pull-up), 3 switch inputs (12 V → 33k/10k) |',
    '| Digital inputs | 2 hall (1k pull-up, 4.7k series, clamped to 3.3 V), 3 switch inputs (12 V → 33k/10k) |')
rep('- **Pin map:** the full pin map is in the spreadsheet\'s "MCU Pin Map" tab.',
    '- **Low-side enable:** PA8, open drain, low = enabled (the board firmware handles it).\n'
    '- **Pin map:** the full pin map is in the spreadsheet\'s "MCU Pin Map" tab.')
rep('| `fab/jlcpcb_bom.csv`, `fab/jlcpcb_cpl.csv` | JLC assembly BOM and placement file |',
    '| `fab/jlcpcb_bom.csv`, `fab/jlcpcb_cpl.csv` | JLC assembly BOM and placement file: every part except the two bottom-side 1×40 headers |\n| `fab/self_order_bom.csv` | What you order and fit yourself: the J1/J2 1×40 pin headers |')
rep("4. **Headers on the bottom.** J1/J2 are listed as `Bottom` in the CPL. If you let JLC fit them, that is\n   bottom-side assembly and adds cost. They are cheap to hand-solder, and you can square them up against\n   the motherboard's female headers while the solder sets. If you do that, delete J1/J2 from the BOM.",
    "4. **Headers on the bottom.** J1/J2 are not in the JLC BOM or CPL (they'd need bottom-side assembly). They're in\n   `fab/self_order_bom.csv`: hand-solder them, squared up against a motherboard's female sockets while the solder\n   sets.")
t = re.sub(r'netlist was checked pad-by-pad against the board\'s netlist \(\d+ pads, 0 differences\)',
           f"netlist was checked pad-by-pad against the board's netlist ({npads} pads, 0 differences)", t)
m = re.search(r'- \*\*DRC \(KiCad 7\):\*\*.*?(?=\n## )', t, re.S)
t = t[:m.start()] + (f'''- **DRC (KiCad 7):** 0 clearance errors, {cnt.get('unconnected_items', 0)} unconnected items. Warnings remaining:
  - Silkscreen overlaps ({cnt.get('silk_overlap', 0)}) and silkscreen clipped by a pad opening ({cnt.get('silk_over_copper', 0)}): cosmetic.
  - Courtyard overlaps ({cnt.get('courtyards_overlap', 0)}) on tightly packed passives. The copper clearances still pass.
  - "Library not in configuration" notes from running headless.
''') + t[m.end():]
assert 'clearance' not in cnt and cnt.get('unconnected_items', 0) == 0, ('fix before release', dict(cnt))
open(rel + '/README.md', 'w').write(t)
print('wrote', rel + '/README.md', dict(cnt))
