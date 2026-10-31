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
    'mb': {'JD1', 'JD2', 'J2', 'J3', 'J5', 'JP1', 'U2'},        # sockets, Micro-Fit, AUX, IAT jumper header, MAP
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
COLS = ['Line', 'Item', 'Quantity', 'Designator', 'Manufacturer', 'Manufacture Part Number', 'LCSC Part Number',
        'Required', 'Find it', 'Notes']


def is_jlc(kind, p):
    return bool(p['lcsc']) and p['ref'] not in HAND[kind]


def find_url(lcsc, mpn, mfr=''):
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
        if p['lcsc']:                                           # through-hole part you fit yourself
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
            agg.setdefault(key, dict(item=m.get('desc') or p['value'], refs=[], mfr=m.get('mfr', ''),
                                     mpn=m.get('mpn', ''), lcsc=lc, req='Optional',
                                     notes=p['desc'].replace('NOT FITTED: ', '')))['refs'].append(r)
    for v in agg.values():
        rows.append((v['item'], len(v['refs']), ','.join(v['refs']), v['mfr'], v['mpn'], v['lcsc'], v['req'], v['notes']))
    if kind == 'mb':
        for item, q, mfr, mpn, lcsc, notes in MB_EXTRA:
            m = MPN.get(lcsc, {})
            rows.append((item, q, '', m.get('mfr', mfr), m.get('mpn', mpn), lcsc, 'Yes', notes))
    rows.sort(key=lambda t: (t[6] != 'Yes', not t[0].startswith('Harness'), t[5] == '', t[0]))
    return rows


def write_self_bom(kind, parts, path):
    rows = self_rows(kind, parts)
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
    """One ordering list for a whole build. boards: [(label, kind, parts, count)]."""
    agg = {}
    for label, kind, parts, count in boards:
        for item, q, refs, mfr, mpn, lcsc, req, notes in self_rows(kind, parts):
            k = (lcsc or mpn, req)
            a = agg.setdefault(k, dict(item=item, qty=0, mfr=mfr, mpn=mpn, lcsc=lcsc, req=req, where=[], notes=notes))
            a['qty'] += q * count
            a['where'].append(label)
    for item, q, mfr, mpn, lcsc, req, notes in CAR:
        agg[(mpn, req)] = dict(item=item, qty=q * cars, mfr=mfr, mpn=mpn, lcsc=lcsc, req=req, where=['car'], notes=notes)
    rows = sorted(agg.values(), key=lambda a: (a['req'] != 'Yes', a['where'] == ['car'], not a['item'].startswith('Harness'),
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
