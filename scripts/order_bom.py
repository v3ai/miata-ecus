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
    'mb': {'JD1', 'JD2', 'J2', 'J3', 'J5', 'J6', 'JP1', 'U2'},  # sockets, Micro-Fit, AUX, IAT jumper header, MAP
}
# footprints with nothing to fit (Tag-Connect SWD pads: the cable presses on)
PADS_ONLY = {'daughter': {'J3', 'J102'}, 'mb': set()}
WHY = {
    ('daughter', 'J1'): 'Bottom side. Solder while plugged into a motherboard\'s sockets so they come out straight',
    ('mb', 'U2'): 'Lies flat, marking side up, leads bent 90 deg down, held by 2 x M3 screws',
}
# parts that aren't on the board's parts list at all, per motherboard
MB_EXTRA = [
    # item, qty, mfr, mpn, lcsc, notes
    ('Jumper shunt, 2.54 mm', 1, 'BOOMELE', '2.54 shunt, open top', 'C5305',
     'For JP1 (IAT source): EXT = board IAT connector J3, STOCK = harness sensor'),
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
# 1989-93 manual cars: the stock throttle "sensor" is only an idle / full-throttle switch. The conversion to a real
# 0-5 V sensor wired to the board's J6 (rev 0.10). Bought per car; listed in the 1989-93 self-order BOM and in the
# whole-build list. (item, qty, mfr, mpn, lcsc, required, notes)
TPS_REQ = 'Manual cars'
YEAR_CAR = {'mb_na6': [
    ('Throttle position sensor, 0-5 V potentiometer, 3 pins', 1, 'Bosch', '0 280 122 001', '', TPS_REQ,
     'Same part as BMW 13 63 1 721 456; the sensor the NA6 adapter plates below are made for. 86 deg usable travel, '
     '2 kOhm track, -40 to +130 C. Pins 1 and 2 are the ends of the track (5 V and ground, about 2 kOhm between them '
     'at any throttle), pin 3 the wiper (signal): check with an ohmmeter before wiring. Replaces the stock idle switch'),
    ('TPS adapter plate for the NA6 throttle body (buy)', 1, 'Flyin\' Miata', 'TPS upgrade kit 07-360XX, no-TPS option', '',
     TPS_REQ, 'Bolts to the side of the 1990-93 manual throttle body and carries the Bosch / BMW sensor. Either this or '
     'the printed plate below. Not with an NB intake manifold'),
    ('TPS adapter plate for the NA6 throttle body (3D print)', 1, '', 'Thingiverse 4476762 or Printables 619337', '',
     'Optional', 'Instead of the bought plate: Skuzzle\'s "Mazda MX5 - BMW TPS adapter" (Thingiverse 4476762), or its '
     'thicker remix "BMW tps adaptor maximum beef" (Printables 619337). Print in ASA (PLA and PETG soften in the engine '
     'bay); check the licence on the model page'),
    ('Screw, M4, with nut (sensor to printed plate)', 2, '', 'M4 screw + M4 nut, length to suit the plate', '', 'Optional',
     'Printed plate only'),
    ('Screw, M4, with wide (fender) washer (printed plate to throttle body)', 2, '', 'M4 screw + M4 fender washer, length to suit', '',
     'Optional', 'Printed plate only: the wide washers spread the load on the plastic'),
    ('TPS plug, Bosch Junior Timer 3-pin, with terminals', 1, 'Bosch', '1 237 000 039', '', TPS_REQ,
     'Mates with the Bosch 0 280 122 001. Buy it as a kit with its terminals (e.g. EFI Hardware C03F-0002): loose '
     'terminals often don\'t fit the housing'),
    ('Shielded cable, 3 x 22 AWG with drain, 105 C or better', 3, '', 'M27500-22SB3T23 (or equivalent), metres', '', TPS_REQ,
     'J6 to the sensor: about 3 m from the ECU in the passenger footwell through the firewall to the throttle body; '
     'measure your route. Shield drain to J6 pin 4 only (open at the sensor end). Office cable rated 60 C is not '
     'good enough under the hood. Three twisted 22 AWG TXL wires in loom also work (leave pin 4 empty)'),
    ('Micro-Fit 3.0 receptacle, 1x4', 1, 'Molex', '43645-0400', '', TPS_REQ,
     'Mates with J6: 1 = 5 V, 2 = TPS signal, 3 = sensor ground, 4 = shield drain'),
    ('Micro-Fit 3.0 female crimp terminal, 20-24 AWG (TPS lead)', 4, 'Molex', '43030-0007', '', TPS_REQ,
     'For the J6 receptacle; buy spares'),
    ('Convoluted loom, 6 mm (1/4 in), split', 2, '', '6 mm split loom, metres', '', 'Optional',
     'Engine-bay run of the TPS lead; tie it to the engine harness, away from the exhaust and the coil leads'),
]}
URLS = {
    'TPS upgrade kit 07-360XX, no-TPS option': 'https://flyinmiata.com/products/tps-upgrade',
    'Thingiverse 4476762 or Printables 619337': 'https://www.thingiverse.com/thing:4476762',
    '1 237 000 039': 'https://www.efihardware.com/products/388/connector-TPS-Module-3-pin-plug-Bosch',
}
COLS = ['Line', 'Item', 'Quantity', 'Designator', 'Manufacturer', 'Manufacture Part Number', 'LCSC Part Number',
        'Required', 'Find it', 'Notes']


def is_jlc(kind, p):
    return bool(p['lcsc']) and p['ref'] not in HAND[kind] and not p.get('dnp')


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
    ('O2 sensor weld bung, M18 x 1.5', 1, '', 'M18 x 1.5 weld bung', '', 'Yes', 'Unless the exhaust has a spare port'),
    ('Micro-Fit 3.0 receptacle, 2x3', 1, 'Molex', '43025-0600', '', 'Yes', 'Mates with J2 (LSU 4.9)'),
    ('Micro-Fit 3.0 female crimp terminal, 20-24 AWG', 8, 'Molex', '43030-0007', '', 'Yes', '6 for the LSU lead, 2 for the IAT lead; buy spares'),
    ('LSU 4.9 extension lead or sensor-side connector', 1, '', 'LSU 4.9 pigtail', '', 'Yes', 'Wire it to the 43025-0600 at the board end'),
    ('Vacuum hose, MAP barb to intake manifold', 1, '', 'vacuum hose to fit the MPX5700AP barb', '', 'Yes', ''),
    ('Micro-Fit 3.0 receptacle, 1x2', 1, 'Molex', '43645-0200', '', 'Optional', 'Mates with J3, only with an external IAT (JP1 on EXT)'),
    ('IAT sensor, M12 x 1.5 open element', 1, '', 'open-element air temperature sensor', '', 'Optional', 'Only with JP1 on EXT; on STOCK the car\'s own sensor is used'),
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
