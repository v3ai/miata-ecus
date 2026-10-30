"""Parts list + JLCPCB BOM/CPL from design.py and the routed board."""
import csv, sys, collections
import design

# every LCSC number was looked up on 2026-10-28 (scripts/mpn.json); nothing left to flag
VERIFY = set()
# JLC "basic" parts (no extended-part setup fee) among the ones used here
BASIC = {'C14663', 'C57112', 'C1588', 'C15849', 'C19666', 'C23630', 'C15850', 'C1525', 'C15195',
         'C1523', 'C21189', 'C22936', 'C23182', 'C22775', 'C21190', 'C4190', 'C23162', 'C23186',
         'C23212', 'C25804', 'C22790', 'C4216', 'C23231', 'C11702', 'C25879', 'C25900', 'C25744',
         'C25779', 'C25917', 'C17408', 'C27834', 'C46653', 'C13585', 'C1603', 'C6186', 'C8678',
         'C2286', 'C72043', 'C72041', 'C72038', 'C318884', 'C29718', 'C7512', 'C1653',
         'C25803', 'C25819', 'C23138', 'C25908', 'C25770'}

GROUPS = [
    ('MCU & support', lambda r, p: r == 'U1' or r in {'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10',
                                                       'C11', 'C12', 'C13', 'C14', 'C15', 'FB1', 'Y1', 'R1',
                                                       'SW1', 'SW2', 'J3'}),
    ('Status LEDs', lambda r, p: r in {'D1', 'D2', 'D3', 'D4', 'D5', 'R2', 'R3', 'R4', 'R5', 'R6'}),
    ('Power', lambda r, p: r in {'D6', 'D7', 'D8', 'D9', 'D10', 'R7', 'C16', 'L1', 'L2', 'C17', 'C18', 'U2',
                                 'C19', 'R8', 'C20', 'R9', 'C21', 'R10', 'C22', 'C23', 'U3', 'C24', 'C25',
                                 'U4', 'C26', 'C27', 'R11', 'R12', 'C28', 'R13', 'R14', 'C29'}),
    ('Injector / solenoid drivers', lambda r, p: r.startswith('Q') or any(v.endswith('_CTL') for v in p['pads'].values()) and p['value'] == '10k' and 'GND' in p['pads'].values()),
    ('Ignition drivers', lambda r, p: r in {'U6', 'U7', 'RN1', 'C34', 'C35'} or any('IGN' in v for v in p['pads'].values())),
    ('Relay / lamp drivers', lambda r, p: r == 'U5'),
    ('Knock input', lambda r, p: r == 'U8' or any(v.startswith('KN_') or v in ('AN_KNOCK',) for v in p['pads'].values())),
    ('VR (crank/cam) input', lambda r, p: r == 'U9' or r == 'C50' or any(v.startswith('VR') for v in p['pads'].values())),
    ('Analog / hall / switch inputs', lambda r, p: any(v.startswith(('IN_', 'AN_', 'HALL', 'SW')) for v in p['pads'].values())),
    ('CAN', lambda r, p: r in {'U10', 'C56'}),
    ('Mezzanine headers', lambda r, p: r in {'J1', 'J2'}),
    ('Mechanical', lambda r, p: r.startswith('H')),
]

DESC = {
    'STM32F407VGT6': 'MCU, Cortex-M4F 168MHz, 1MB flash, LQFP-100',
    'AUIPS2041LTR': 'Protected low-side switch, 39V clamp (inj/IACV/VVT/boost/alt)',
    'ULN2003AD': '7ch Darlington low side (relays, CEL, tach)',
    'TC4427': 'Dual 1.5A driver, 5V logic out for COP smart coils',
    'MAX9926UAEE+': 'Dual VR sensor interface, adaptive threshold',
    'LMV321IDBVR': 'Op-amp, knock sensor gain stage',
    'LMR14020': '40V 2A buck converter, 12V -> 5V',
    'TLS115B0EJ': '5V sensor supply tracker, short-to-battery protected',
    'AMS1117-3.3': '3.3V LDO',
    'SN65HVD230DR': '3.3V CAN transceiver',
    'SMCJ30A': '1500W TVS, load dump',
    'SS34': '3A 40V Schottky',
    'B5819W': '1A 40V Schottky',
    'X50328MSB2GI': '',
    '8MHz': '8MHz crystal 5032, 20pF (YXC X50328MSB2GI)',
    'Mezz_Power_Out': '1x40 2.54mm male header (power/outputs)',
    'Mezz_Signal_In': '1x40 2.54mm male header (inputs/comms)',
    'SWD': 'Tag-Connect TC2030-NL footprint, nothing to place',
    'M3': 'M3 mounting hole',
}


def group_of(p):
    for g, f in GROUPS:
        if f(p['ref'], p):
            return g
    return 'Other'


def pkg(p):
    return p['fp'].split(':')[1].split('_')[0] if p['fp'].split(':')[1].startswith(('R_', 'C_', 'L_', 'D_', 'LED_')) \
        else p['fp'].split(':')[1]


def rows():
    agg = collections.OrderedDict()
    for p in design.parts:
        key = (group_of(p), p['value'], p['fp'], p['lcsc'])
        agg.setdefault(key, []).append(p['ref'])
    out = []
    order = [g for g, _ in GROUPS] + ['Other']
    for (g, val, fp, lcsc), refs in sorted(agg.items(), key=lambda kv: (order.index(kv[0][0]), kv[0][1])):
        out.append(dict(group=g, value=val, refs=refs, fp=fp, lcsc=lcsc,
                        desc=DESC.get(val, ''), qty=len(refs)))
    return out


def jlc_bom(path):
    agg = collections.OrderedDict()
    for p in design.parts:
        if not p['lcsc']:
            continue
        agg.setdefault((p['value'], p['fp'].split(':')[1], p['lcsc']), []).append(p['ref'])
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
        for (v, fp, l), refs in agg.items():
            w.writerow([v, ','.join(refs), fp, l])


def jlc_cpl(board_path, path):
    import pcbnew
    b = pcbnew.LoadBoard(board_path)
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
        for fp in b.GetFootprints():
            r = fp.GetReference()
            if r.startswith('H') or r in ('J3', 'J102'):
                continue
            pos = fp.GetPosition()
            x = pcbnew.ToMM(pos.x) - 100.0
            y = -(pcbnew.ToMM(pos.y) - 50.0 - 60.0)     # JLC uses y-up from bottom-left
            w.writerow([r, f'{x:.3f}mm', f'{y:.3f}mm', 'Bottom' if fp.IsFlipped() else 'Top',
                        f'{fp.GetOrientationDegrees() % 360:.0f}'])


if __name__ == '__main__':
    out = sys.argv[1]
    jlc_bom(out + '/jlcpcb_bom.csv')
    if len(sys.argv) > 2:
        jlc_cpl(sys.argv[2], out + '/jlcpcb_cpl.csv')
    tot = sum(r['qty'] for r in rows())
    print(len(rows()), 'lines', tot, 'parts')
