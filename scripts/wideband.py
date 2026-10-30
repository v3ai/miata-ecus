"""On-board wideband controller: the FOME / rusEFI open-source wideband module (MIT,
github.com/mck1117/wideband, hardware/board_module rev C). This file maps the module's parts and
nets onto the daughterboard. Rev 0.2 transplanted the module's own layout (placement() / copper()
below, wb_build.py); rev 0.3 places and routes it in the board's own style instead (wb_clean.py).

Refs: module ref + 100 (module R1 -> R101, U2 -> U102 ...), so the block reads straight
against the FOME schematic. Removed from the module: its two 1x8 headers (J1/J3; their
signals now run to the daughter header / CAN bus), its 3.3 V LDO U9 (runs from the
daughter +3V3 plane) and its power LED (D4/R18). Added: U106 + C118, a CAN transceiver on
the shared CAN bus (rusEFI talks to the controller over CAN, exactly as to the module).

Placement: the module is rotated -90 deg (clockwise) so its sensor-side header row faces
J2 and lands exactly above J2 pins 33-40.
"""
import math
import wb_module

M = wb_module.load()
MCX, MCY = 95.504, 83.566           # module centre: between its two header columns
ROT = -90                           # clockwise on screen
CX, CY = 103.17, 39.3               # block centre on the daughterboard

DROP = {'J1', 'J3', 'U9', 'D4', 'R18'}
LCSC = {   # from the module's rev C JLC BOM
    'R0402': {'10': 'C25077', '100k': 'C25741', '10k': 'C25744', '1k': 'C11702', '22k': 'C25768',
              '27k': 'C25771', '3.3k': 'C25890', '47': 'C25118', '47k': 'C25792', '6.8k': 'C25917',
              '68k': 'C36871'},
    'R0603': {'61.9': 'C23092', '62k': 'C23221'},
    'C0402': {'100n': 'C1525', '1u': 'C52923', '33n': 'C285077'},   # 33n: X7R instead of the module's Y5V C1585
    'C0603': {'4.7u': 'C19666'},
}
PARTS_LCSC = {'U1': 'C50282', 'U2': 'C69216', 'U3': 'C36658', 'U5': 'C29309', 'Q1': 'C2649436',
              'D1': 'C2286', 'D2': 'C12624', 'D3': 'C2288'}
VALUE = {'U1': 'MCP6004', 'U2': 'STM32F042K6T6', 'U3': 'REF3033', 'U5': 'AD8628', 'Q1': 'VND14NV04',
         'D1': 'RED', 'D2': 'GREEN', 'D3': 'BLUE', 'J2': 'SWD (WBO)'}
DESC = {'U1': 'wideband: quad op-amp (virtual ground, pump driver, Nernst sense/buffer)',
        'U2': 'wideband controller MCU (FOME/rusEFI wideband firmware)',
        'U3': 'wideband: 3.3 V ADC/analog reference', 'U5': 'wideband: pump current sense amp',
        'Q1': 'wideband: LSU heater low side (protected)', 'D1': 'wideband: heater',
        'D2': 'wideband: status', 'D3': 'wideband: status',
        'J2': 'Tag-Connect TC2030-NL footprint, wideband MCU SWD (first flash; then CAN bootloader)'}

NETMAP = {
    '/LSU_Ip': 'LSU_IP', '/LSU_Vm': 'LSU_VM', '/LSU_Rtrim': 'LSU_RT', '/LSU_Un': 'LSU_UN',
    'Net-(J1-Pin_3)': 'LSU_HTR_N', 'Net-(J1-Pin_1)': 'HTR_GND',
    '+5V': '+5V', 'GND': 'GND', '+3V3': '+3V3', 'VDDA': 'WB_VDDA',
    '/CAN_RX': 'WB_CAN_RX', '/CAN_TX': 'WB_CAN_TX', '/VBatt_Sense': 'VBAT_IN',
    '/SWDIO': 'WB_SWDIO', '/SWCLK': 'WB_SWCLK', '/nRESET': 'WB_NRST', '/Boot0': 'WB_BOOT0',
    '/Ip_sense': 'WB_IP_SENSE', '/Vm': 'WB_VM', '/Un_sense': 'WB_UN_SENSE', '/LSU_Un_sense': 'WB_UN_BUF',
    '/Ip_dac': 'WB_IP_DAC', '/heater_pwm': 'WB_HTR_PWM', '/LED_GREEN': 'WB_LED_G', '/LED_BLUE': 'WB_LED_B',
    '/Nernst_esr_drive_42': 'WB_ESR_42', '/Nernst_esr_drive_49': 'WB_ESR_49', '/Nernst_esr_drive_adv': 'WB_ESR_ADV',
    'Net-(U2-PB0)': 'WB_VBAT_DIV', 'Net-(Q1-G)': 'WB_HTR_G', 'Net-(D1-A)': 'WB_LED_H',
    'Net-(D2-K)': 'WB_LED_GK', 'Net-(D3-K)': 'WB_LED_BK', 'Net-(C2-Pad2)': 'WB_ESR', 'Net-(C3-Pad1)': 'WB_PUMP',
    'Net-(U1A--)': 'WB_PUMP_N', 'Net-(U1A-+)': 'WB_PUMP_P', 'Net-(U1B--)': 'WB_UN_N', 'Net-(U1B-+)': 'WB_UN_P',
    'Net-(U1D-+)': 'WB_VM_REF', 'Net-(U5--)': 'WB_IS_N', 'Net-(U5-+)': 'WB_IS_P', 'Net-(R17-Pad1)': 'WB_IS_OUT',
    '/SEL_1': '', '/SEL_2': '', 'Net-(D4-A)': '',
}


# programming link from the main MCU (rev 0.4): the F042's USART1 (PA9 TX, PA10 RX; unused by the FOME
# firmware) is its ROM bootloader's serial port. Net names are from the main MCU's side.
PROG = {'19': 'WB_PROG_RX', '20': 'WB_PROG_TX'}


def net(n):
    if not n or n.startswith('unconnected'):
        return ''
    return NETMAP[n]


def ref(r):
    k = ''.join(c for c in r if c.isalpha()); n = int(''.join(c for c in r if c.isdigit()))
    return f'{k}{n + 100}'


def xy(x, y):
    """module coords -> daughterboard coords (mm, board origin)"""
    dx, dy = x - MCX, y - MCY
    a = math.radians(ROT)          # screen-CCW angle; y down => rotate by -a in math terms
    X = dx * math.cos(a) + dy * math.sin(a)
    Y = -dx * math.sin(a) + dy * math.cos(a)
    return (round(CX + X, 4), round(CY + Y, 4))


def norm(a):
    a = (a + 180) % 360 - 180
    return 180.0 if a == -180 else a


def parts():
    """design-style part dicts (pads keyed by pad number, '' pads skipped)"""
    out = []
    for r, f in sorted(M['fps'].items()):
        if r in DROP:
            continue
        lib = f['lib']
        if r[0] in 'RC' and r[:2] not in ('CS',):
            size = '0402' if '0402' in lib else '0603'
            val = f['value']
            lc = LCSC[r[0] + size][val]
        else:
            val = VALUE.get(r, f['value']); lc = PARTS_LCSC.get(r, '')
        pads = {}
        for num, pl in f['pads'].items():
            if num:
                pads[num] = net(pl[0][2])
        if r == 'U2':
            pads.update(PROG)
        out.append(dict(ref=ref(r), value=val, fp=lib, lcsc=lc, pads=pads, desc=DESC.get(r, 'wideband'),
                        mod_ref=r, side=f['side']))
    # CAN transceiver for the controller, same bus as the main MCU
    out.append(dict(ref='U106', value='SN65HVD230DR', fp='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', lcsc='C12084',
                    pads={'1': 'WB_CAN_TX', '2': 'GND', '3': '+3V3', '4': 'WB_CAN_RX', '5': '', '6': 'CAN_L',
                          '7': 'CAN_H', '8': 'GND'}, desc='wideband CAN transceiver (shared CAN bus)', side='F'))
    out.append(dict(ref='C118', value='100n', fp='Capacitor_SMD:C_0402_1005Metric', lcsc='C1525',
                    pads={'1': '+3V3', '2': 'GND'}, desc='U106 decoupling', side='F'))
    return out


def placement():
    P = {}
    for r, f in M['fps'].items():
        if r in DROP:
            continue
        x, y = xy(f['x'], f['y'])
        P[ref(r)] = (x, y, norm(f['rot'] + ROT), f['side'])
    return P


# header pins of the module -> ports on the block edge
# sensor side (module J1) lands on J2 pins 40..33; power side (module J3) faces up
def ports():
    out = []
    for side, mref in (('S', 'J1'), ('P', 'J3')):
        for num, pl in M['fps'][mref]['pads'].items():
            x, y, n = pl[0][:3]
            out.append(dict(side=side, num=int(num), at=xy(x, y), mnet=n, net=net(n)))
    return out


def copper():
    """module tracks / vias / zones, mapped (dropped parts' copper removed later as dangling)"""
    segs = [dict(a=xy(*s['a']), b=xy(*s['b']), w=s['w'], layer=s['layer'], net=net(s['net'])) for s in M['segs']]
    vias = [dict(at=xy(*v['at']), size=v['size'], drill=v['drill'], net=net(v['net'])) for v in M['vias']]
    zones = [dict(net=net(z['net']), layer=z['layer'], poly=[xy(*p) for p in z['poly']])
             for z in M['zones'] if z['layer'][0] == 'F.Cu']
    return segs, vias, zones


if __name__ == '__main__':
    for p in ports():
        print(p)
    for p in parts():
        print(p['ref'], p['value'], p['lcsc'], p['pads'])
