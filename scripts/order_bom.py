"""Split each board's parts into what JLCPCB assembles and what you order and fit yourself.

JLCPCB gets the SMD parts plus the USB-C receptacle (0.5 mm pitch, hard by hand). Every through-hole part is left
to you: it saves Standard-PCBA through-hole fees and bottom-side assembly, and all of them are easy joints. The
self-order BOM also carries the parts no assembler can fit (harness header, shunt, standoffs, screws) and the
not-fitted options, marked optional. Its Quantity / Manufacture Part Number / Manufacturer / LCSC Part Number
columns are what LCSC's BOM upload tool reads.
"""
import csv, json, os, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
MPN = json.load(open(os.path.join(HERE, 'mpn.json')))

# parts that have an LCSC number but that you fit yourself (left out of the JLC BOM and CPL)
HAND = {
    'daughter': {'J1', 'J2'},                                   # 1x40 pin headers, bottom side
    'mb': {'JD1', 'JD2', 'J2', 'J3', 'J5', 'U2'},               # sockets, Micro-Fit, add-on header, MAP (and every JPn)
}
# hand-fitted parts the board's parts list names without an LCSC number: value or footprint fragment ->
# (item, manufacturer, part number, required)
NAMED = {
    'AEM 30-3427': ('Wideband sensor header, Micro-Fit 3.0, 2x4, right angle (assumed to take AEM harness 30-3427)',
                    'Molex', '0430450800', 'Yes'),
    'AUX 2x10': ('Box header, 2x10, 2.54 mm, vertical (add-on header; takes a 20-way ribbon cable plug)',
                 'On Shore Technology', '302-S201', 'Optional'),
    'PinHeader_1x02': ('Pin header, male, 1x2, 2.54mm, through-hole, vertical', 'Sullins', 'PRPC002SAAN-RC', 'Optional'),
    'R_2512': ('Resistor 1k, 2512, 1 W', 'Yageo', 'RC2512JK-071KL', 'Optional'),
}
# footprints with nothing to fit (Tag-Connect SWD pads: the cable presses on)
PADS_ONLY = {'daughter': {'J3', 'J102'}, 'mb': set()}
WHY = {
    ('daughter', 'J1'): 'Bottom side. Solder while plugged into a motherboard\'s sockets so they come out straight',
    ('mb', 'U2'): 'Lies flat, marking side up, leads bent 90 deg down, held by 2 x M3 screws',
}
# parts that aren't on the board's parts list at all, per motherboard
MB_EXTRA = [
    # item, qty, mfr, mpn, lcsc, notes     (jumper shunts are added per board, one for each jumper header it has)
    ('Screw, M3 x 6, pan head', 8, '', 'M3 x 6 pan head', '', 'Two per daughterboard standoff (HD1-HD4)'),
    ('Screw, M3 x 10, pan head', 2, '', 'M3 x 10 pan head', '', 'MAP sensor (U2) hold-down'),
    ('Nut, M3', 2, '', 'M3 hex nut', '', 'MAP sensor (U2) hold-down'),
]
# harness headers: manufacturer part numbers for the J1 footprints
HARNESS = {
    'TE 174917-6': ('TE Connectivity', '174917-6', 'Not available from TE: salvage from a stock NA ECU or buy a clone'),
    'TE 178780-1': ('TE Connectivity', '178780-1', 'Alternates 174915-6, 3-178780-6'),
    'TE 176122-6': ('TE Connectivity', '176122-6', 'Alternate 4-174518-7'),
    'TE 353830-5': ('TE Connectivity', '353830-5', 'Alternate 1123038-2'),
}
# 1989-93 manual cars: the stock throttle "sensor" is a two-contact switch. The conversion to a real 0-5 V sensor that
# plugs into the stock switch plug, with the motherboard's R28 / R30 links (rev 0.11). Bought per car; listed in the
# 1989-93 self-order BOM and in the whole-build list. (item, qty, mfr, mpn, lcsc, required, notes)
TPS_REQ = 'Manual cars'
YEAR_CAR = {'mb_na6': [
    ('Throttle position sensor, Kia, 3-pin Mazda-style plug', 1, 'Kia', '0K01118911', '', TPS_REQ,
     'Also sold as 0K24718911, 0K30A18911 or aftermarket TH291 / 5S5504 / TPS4185 (rusEFI wiki list). Plugs into the '
     'car\'s stock throttle switch plug: 1N gives it 5 V (fit R28), 2D is its ground, 2L its signal (move R29 to R30). '
     'Before fitting R28, check with an ohmmeter which sensor pins are the track ends (constant resistance between them '
     'at any throttle) and that they meet the 1N and 2D wires; the third pin, the wiper, must meet 2L. If the reading '
     'falls as the throttle opens, TunerStudio\'s calibration handles it'),
    ('TPS mount for the NA6 throttle body (3D print)', 1, '', 'Thingiverse 3414132', '', TPS_REQ,
     '"Mazda NA6 Miata variable TPS mount": holds the Kia sensor on the throttle shaft in place of the stock switch. '
     'Print in ASA (PLA and PETG soften in the engine bay); check the licence on the model page'),
    ('TPS upgrade kit with sensor (instead of the two rows above)', 1, 'Flyin\' Miata', 'TPS upgrade kit 07-360XX, with TPS', '',
     'Optional', 'Bought alternative: adapter plate plus an OEM or BMW sensor; Flyin\' Miata says it plugs into the stock '
     'harness. Check that it comes with the lead for the stock plug. Not with an NB intake manifold'),
]}
URLS = {
    '30-3427': 'https://www.aemelectronics.com/products/dashes_and_gauges/aem_performance_gauges/gauge_accessories/parts/30-3427',
    '0K01118911': 'https://wiki.rusefi.com/Legacy-Miata-NA-48-pin-board-for-MRE',
    'Thingiverse 3414132': 'https://www.thingiverse.com/thing:3414132',
    'TPS upgrade kit 07-360XX, with TPS': 'https://flyinmiata.com/products/tps-upgrade',
}
COLS = ['Line', 'Item', 'Quantity', 'Designator', 'Manufacturer', 'Manufacture Part Number', 'LCSC Part Number',
        'Required', 'Find it', 'Notes']


def is_jlc(kind, p):
    hand = p['ref'] in HAND[kind] or (kind == 'mb' and p['ref'].startswith('JP'))
    return bool(p['lcsc']) and not hand and not p.get('dnp')


def find_url(lcsc, mpn, mfr=''):
    if mpn in URLS:
        return URLS[mpn]
    if lcsc:
        return f'https://www.lcsc.com/product-detail/{lcsc}.html'
    if mpn and mfr:                                             # a real part number; generic hardware gets no link
        return 'https://www.digikey.com/en/products/result?keywords=' + urllib.parse.quote(mpn)
    return ''


def self_rows(kind, parts):
    """Rows of the self-order BOM for one board: (item, qty, refs, mfr, mpn, lcsc, required, notes)."""
    rows, agg = [], {}
    for p in parts:
        r = p['ref']
        if is_jlc(kind, p) or (r.startswith('H') and not r.startswith('HD')) or r in PADS_ONLY[kind]:
            continue                                            # assembled, or a case mounting hole
        if p.get('dnp'):                                        # footprint left empty: optional
            m = MPN.get(p['lcsc'], {})
            a = agg.setdefault(('dnp', p['lcsc']), dict(item=m.get('desc') or p['value'], refs=[], mfr=m.get('mfr', ''),
                                                        mpn=m.get('mpn', '') or p['value'], lcsc=p['lcsc'],
                                                        req='Optional', notes=''))
            a['refs'].append(r)
            # each option keeps its own note (R20-R22 and R27 share a part but not a purpose)
            a['notes'] = (a['notes'] + '; ' if a['notes'] else '') + f"{r}: {p['desc']}"
        elif p['lcsc']:                                         # through-hole part you fit yourself
            m = MPN.get(p['lcsc'], {})
            key = (p['lcsc'],)
            note = WHY.get((kind, r)) or ''
            agg.setdefault(key, dict(item=m.get('desc') or p['value'], refs=[], mfr=m.get('mfr', ''),
                                     mpn=m.get('mpn', ''), lcsc=p['lcsc'], req='Yes', notes=note))['refs'].append(r)
        elif r.startswith('HD'):                                # daughterboard standoffs
            agg.setdefault(('standoff',), dict(item='Standoff, M3 x 11 mm, hex, female-female', refs=[], mfr='',
                                               mpn='M3 x 11 F-F hex standoff', lcsc='', req='Yes',
                                               notes='Daughterboard above the motherboard (8.5 mm sockets + 2.5 mm header plastic)')
                           )['refs'].append(r)
        elif p['value'] in HARNESS:
            mfr, mpn, note = HARNESS[p['value']]
            agg[(p['value'],)] = dict(item=f'Harness header {p["value"]}', refs=[r], mfr=mfr, mpn=mpn, lcsc='',
                                      req='Yes', notes=note)
        elif p['value'] in NAMED or any(k in p['fp'] for k in NAMED):
            item, mfr, mpn, req = NAMED.get(p['value']) or next(v for k, v in NAMED.items() if k in p['fp'])
            a = agg.setdefault(('named', item), dict(item=item, refs=[], mfr=mfr, mpn=mpn, lcsc='', req=req, notes=''))
            a['refs'].append(r)
            a['notes'] = (a['notes'] + '; ' if a['notes'] else '') + f"{r}: {p['desc'].replace('NOT FITTED: ', '')}"
        else:                                                   # not-fitted options
            lc = 'C23162' if p['value'] == '4.7k' else ('C17477' if p['value'] == '0R' else '')
            m = MPN.get(lc, {})
            key = ('opt', p['value'], p['fp'])
            a = agg.setdefault(key, dict(item=m.get('desc') or p['value'], refs=[], mfr=m.get('mfr', ''),
                                         mpn=m.get('mpn', ''), lcsc=lc, req='Optional', notes=''))
            a['refs'].append(r)
            # each option keeps its own note (R20-R22 and R27 share a part but not a purpose)
            a['notes'] = (a['notes'] + '; ' if a['notes'] else '') + f"{r}: {p['desc'].replace('NOT FITTED: ', '')}"
    for v in agg.values():
        rows.append((v['item'], len(v['refs']), ','.join(v['refs']), v['mfr'], v['mpn'], v['lcsc'], v['req'], v['notes']))
    if kind == 'mb':
        n_jp = sum(1 for p in parts if p['ref'].startswith('JP'))
        if n_jp:
            m = MPN.get('C5305', {})
            rows.append(('Jumper shunt, 2.54 mm', n_jp, '', m.get('mfr', 'BOOMELE'), m.get('mpn', '2.54 shunt, open top'),
                         'C5305', 'Yes', 'One per jumper header; which position each goes on is in the README\'s jumper table'))
        for item, q, mfr, mpn, lcsc, notes in MB_EXTRA:
            m = MPN.get(lcsc, {})
            rows.append((item, q, '', m.get('mfr', mfr), m.get('mpn', mpn), lcsc, 'Yes', notes))
    rows.sort(key=lambda t: (t[6] != 'Yes', not t[0].startswith('Harness'), t[5] == '', t[0]))
    return rows


def write_self_bom(kind, parts, path, module=None):
    rows = self_rows(kind, parts)
    car = [(item, q, '', mfr, mpn, lcsc, req, notes) for item, q, mfr, mpn, lcsc, req, notes in YEAR_CAR.get(module, [])]
    # board parts first (fitted, then optional), then this year's in-car parts (needed, then optional)
    rows = ([r for r in rows if r[6] == 'Yes'] + [r for r in rows if r[6] != 'Yes'] +
            [r for r in car if r[6] != 'Optional'] + [r for r in car if r[6] == 'Optional'])
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for i, (item, q, refs, mfr, mpn, lcsc, req, notes) in enumerate(rows, 1):
            w.writerow([i, item, q, refs, mfr, mpn, lcsc, req, find_url(lcsc, mpn, mfr), notes])
    return rows


# one set per car you install in (not on any board)
CAR = [
    ('Wideband sensor, Bosch LSU 4.9', 1, 'Bosch', '0 258 017 025', '', 'Yes', 'The board runs it directly'),
    ('O2 sensor weld bung, M18 x 1.5', 1, '', 'M18 x 1.5 weld bung', '', 'Optional', 'Only to keep the stock oxygen sensor as well: the LSU 4.9 screws into the stock front sensor\'s hole (same M18 x 1.5 thread)'),
    ('Wideband sensor harness, AEM X-Series', 1, 'AEM', '30-3427', '', 'Yes',
     'From the sensor to J2. That its plug fits J2 (Micro-Fit 3.0, 2x4) is assumed: check before the first use'),
    ('Silicone vacuum hose, 3-4 mm (1/8-5/32 in) inside diameter, 3 m', 1, '', '4 mm ID silicone vacuum hose', '', 'Yes', 'MAP sensor barb to the intake manifold. 1994-97 need most of it (ECU behind the seat). See INSTALL.md, MAP hose'),
    ('Barbed vacuum tee, 4 mm (5/32 in)', 1, '', '4 mm barbed tee', '', 'Optional', 'Needed when the manifold port already has a hose on it: cars with cruise control (1990-95) and every 1996-97. Not needed on a free capped nipple'),
    ('Air temperature sensor, open element (GM type), with an adapter for the stock sensor plug', 1, '',
     'open-element air temperature sensor', '', 'Optional',
     'Only once the airflow meter or the stock airbox is gone: it goes on the stock sensor\'s plug (INSTALL.md, Air temperature)'),
    ('Ribbon cable with a 2x10 IDC socket, 2.54 mm', 1, '', '20-way IDC ribbon cable', '', 'Optional',
     'For the add-on header J5 (boost valve, flex fuel, nitrous, CAN, coil 3 and 4, knock)'),
    ('microSD card', 1, '', 'microSD card, FAT32 formatted', '', 'Optional', 'For rusEFI\'s on-board logging (rev 0.10 daughterboard)'),
]


def write_order_all(boards, daughters, cars, path):
    """One ordering list for a whole build. boards: [(label, kind, parts, count[, module])]; a module's YEAR_CAR parts
    are counted once per car."""
    agg = {}
    for label, kind, parts, count, *mod in boards:
        for item, q, mfr, mpn, lcsc, req, notes in YEAR_CAR.get(mod[0] if mod else None, []):
            agg[(mpn, req, label)] = dict(item=item, qty=q * cars, mfr=mfr, mpn=mpn, lcsc=lcsc, req=req,
                                          where=[f'{label} car'], notes=notes)
        for item, q, refs, mfr, mpn, lcsc, req, notes in self_rows(kind, parts):
            k = (lcsc or mpn, req)
            a = agg.setdefault(k, dict(item=item, qty=0, mfr=mfr, mpn=mpn, lcsc=lcsc, req=req, where=[], notes=notes))
            a['qty'] += q * count
            a['where'].append(label)
    for item, q, mfr, mpn, lcsc, req, notes in CAR:
        agg[(mpn, req)] = dict(item=item, qty=q * cars, mfr=mfr, mpn=mpn, lcsc=lcsc, req=req, where=['car'], notes=notes)
    rows = sorted(agg.values(), key=lambda a: (a['req'] != 'Yes', a['req'] == 'Optional', a['where'][-1].endswith('car'),
                                               not a['item'].startswith('Harness'),
                                               a['lcsc'] == '', a['item']))
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Line', 'Item', 'Quantity', 'For', 'Manufacturer', 'Manufacture Part Number', 'LCSC Part Number',
                    'Required', 'Find it', 'Notes'])
        for i, a in enumerate(rows, 1):
            where = 'every motherboard' if len(a['where']) == 5 and 'daughterboard' not in a['where'] else ', '.join(a['where'])
            w.writerow([i, a['item'], a['qty'], where, a['mfr'], a['mpn'], a['lcsc'], a['req'],
                        find_url(a['lcsc'], a['mpn'], a['mfr']), a['notes']])
    return rows


# ---- JLC placement file -------------------------------------------------------------------------------------------
# JLC reads the CPL in the gerbers' own coordinates: KiCad X, and Y negated (gerbers are y-up), with no offset.
# Rotation: JLC's part models don't all share KiCad's zero orientation. These offsets come from JLC's placement
# preview of the rev 0.5 daughterboard (pin 1 of JLC's model against the board's pin-1 pad), October 2026.
# Footprints not listed matched with no offset (chip R/C/L, SMA/SMC/SOD diodes, LEDs, crystal, buttons).
import re
JLC_ROT = [
    (r'^SOT-223', 180),                 # seen: 3 pins / tab swapped
    (r'^TO-252', 180),                  # seen
    (r'^(T?SOT-23)', 180),              # seen on SOT-23 and SOT-23-5; SOT-23-6 assumed the same
    (r'^(SOIC|Infineon_PG-DSO)', 270),  # seen on SOIC-8 and SOIC-16
    (r'^(TSSOP|LQFP)', 270),            # seen on LQFP-32; TSSOP rows/columns seen swapped
    (r'^R_Array_Convex', 90),           # seen
]


def jlc_rotation(fp_name, kicad_deg):
    for pat, off in JLC_ROT:
        if re.match(pat, fp_name):
            return (kicad_deg + off) % 360
    return kicad_deg % 360


# Centre: JLC places its part model's centre on Mid X/Y. Where a KiCad footprint's origin is not the centre of its
# pads, the CPL gives the pad centre instead (offset in the footprint's own frame, mm, KiCad y down).
# USB4105: KiCad's origin sits 1.14 mm in front of the pad field (toward the board edge); JLC's preview of the rev 0.9
# motherboard showed the connector that far forward, its contacts short of the pads.
JLC_OFFSET = [
    (r'^USB_C_GCT_USB4105', (0.0, -1.14)),
]


def jlc_offset(fp_name):
    for pat, off in JLC_OFFSET:
        if re.match(pat, fp_name):
            return off
    return (0.0, 0.0)


def cpl_row(fp):
    """Designator, Mid X, Mid Y, Layer, Rotation for one footprint (pcbnew FOOTPRINT)."""
    import math
    import pcbnew
    pos = fp.GetPosition()
    name = fp.GetFPIDAsString().split(':')[-1]
    ox, oy = jlc_offset(name)
    a = math.radians(-fp.GetOrientationDegrees())          # KiCad rotates counter-clockwise on a y-down board
    x = pcbnew.ToMM(pos.x) + ox * math.cos(a) - oy * math.sin(a)
    y = pcbnew.ToMM(pos.y) + ox * math.sin(a) + oy * math.cos(a)
    return [fp.GetReference(), f'{x:.3f}mm', f'{-y:.3f}mm',
            'Bottom' if fp.IsFlipped() else 'Top', f'{jlc_rotation(name, fp.GetOrientationDegrees()):.0f}']
