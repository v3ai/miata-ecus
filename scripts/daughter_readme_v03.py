"""Rev 0.3 README for the daughterboard release, from the rev 0.2 README plus this revision's changes.
usage: daughter_readme_v03.py <rev 0.2 README> <release dir>"""
import sys, re, collections
src, rel = sys.argv[1], sys.argv[2]
t = open(src).read()
drc = open(rel + '/fab/drc_report.txt').read()
cnt = collections.Counter(re.findall(r'^\[(\w+)\]', drc, re.M))

t = t.replace('# Miata ECU — daughterboard rev 0.2 (routed, unverified)', '# Miata ECU — daughterboard rev 0.3 (routed, unverified)')
new = '''## What changed in rev 0.3
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

'''
t = t.replace('## What changed in rev 0.2', new + '## What changed in rev 0.2')
t = t.replace('`wideband.py` + `wb_build.py` (the transplanted wideband block, source layout in `wideband_ref/` under its MIT licence)',
              '`wideband.py` (the wideband circuit, mapped from the FOME module in `wideband_ref/` under its MIT licence), '
              '`wb_clean.py` (its rev 0.3 placement and heater copper; `wb_preview.py` draws a placement preview), '
              '`wb_build.py` (the rev 0.2 transplant, kept for reference)')
t = t.replace('''Rebuild: `python3 build_pcb.py daughter.kicad_pcb && python3 route.py daughter.kicad_pcb routed.kicad_pcb`,
then `flip_headers.py` and `daughter_finish.py`,
and `python3 gen_sch2.py <outdir> miata_ecu_daughter` (wired schematic), then `check_sch_netlist.py` on the
exported netlist and `link_board.py` to relink footprints and net names.''',
              '''Rebuild: `scripts/daughter_make.sh <workdir>` (build, route, header flip, finishing, DRC), then
`scripts/daughter_release.sh <workdir>/finished.kicad_pcb <outdir>` (wired schematic, schematic-vs-design netlist
check, board relinked to the schematic, DRC, JLC files, PDF, parts workbook, renders).''')
m = re.search(r'- \*\*DRC \(KiCad 7\):\*\*.*?(?=\n## )', t, re.S)
drc_txt = (f'''- **DRC (KiCad 7):** 0 clearance errors, {cnt.get('unconnected_items', 0)} unconnected items. Warnings remaining:
  - Silkscreen overlaps ({cnt.get('silk_overlap', 0)}) and silkscreen clipped by a pad opening ({cnt.get('silk_over_copper', 0)}): cosmetic, in the main part of the board.
  - Courtyard overlaps ({cnt.get('courtyards_overlap', 0)}) on tightly packed passives in the main part of the board. The copper clearances still pass.
  - "Library not in configuration" notes from running headless.
''')
t = t[:m.start()] + drc_txt + t[m.end():]
t = t.replace('5. **Schematic review.** No person has reviewed the schematic yet. The wideband block is a copy of a proven design; the rest is still unreviewed.',
              '5. **Schematic and layout review.** No person has reviewed the schematic yet. The wideband *circuit* is the proven FOME '
              'design, but since rev 0.3 its *layout* is new to this board, so it no longer inherits the module\'s proven layout. '
              'Bring up the wideband on the first boards before relying on it (heater control, pump current, and lambda reading against a known sensor).')
open(rel + '/README.md', 'w').write(t)
print('wrote', rel + '/README.md', dict(cnt))
