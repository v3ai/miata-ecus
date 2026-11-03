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
VALUE_RC = {'R10': '62'}                                     # rev 0.5b, see LCSC['R0603']
# rev 0.5b: AD8628ARTZ is the 5-lead SOT-23 package (the module's footprint is named TSOT-23-5; the pads are identical)
FP_OVERRIDE = {'U5': 'Package_TO_SOT_SMD:SOT-23-5',
               # rev 0.6: STM32F103C8T6 instead of the module's STM32F042K6T6 (see U2_PADS)
               'U2': 'Package_QFP:LQFP-48_7x7mm_P0.5mm'}
LCSC = {   # from the module's rev C JLC BOM
    'R0402': {'10': 'C25077', '100k': 'C25741', '10k': 'C25744', '1k': 'C11702', '22k': 'C25768',
              '27k': 'C25771', '3.3k': 'C25890', '47': 'C25118', '47k': 'C25792', '6.8k': 'C25917',
              '68k': 'C36871'},
    # rev 0.5b: R110 (module R10, pump current sense) 62 ohm 1% (C23222): the 61.9 ohm part ran out at JLC, and 62 is
    # 0.16 % off, inside its 1 % tolerance
    'R0603': {'61.9': 'C23092', '62': 'C23222', '62k': 'C23221'},
    # 33n: X7R instead of the module's Y5V C1585; rev 0.5b: YAGEO CC0402KRX7R9BB333 (50 V), the FH part ran out at JLC
    'C0402': {'100n': 'C1525', '1u': 'C52923', '33n': 'C106862'},
    'C0603': {'4.7u': 'C19666'},
}
PARTS_LCSC = {'U1': 'C50282', 'U2': 'C8734', 'U3': 'C36658', 'U5': 'C29309', 'Q1': 'C2649436',
              'D1': 'C2286', 'D2': 'C12624', 'D3': 'C2288'}
VALUE = {'U1': 'MCP6004', 'U2': 'STM32F103C8T6', 'U3': 'REF3033', 'U5': 'AD8628', 'Q1': 'VND14NV04',
         'D1': 'RED', 'D2': 'GREEN', 'D3': 'BLUE', 'J2': 'SWD (WBO)'}
DESC = {'U1': 'wideband: quad op-amp (virtual ground, pump driver, Nernst sense/buffer)',
        'U2': 'wideband controller MCU (rusEFI wideband firmware, board port firmware/wideband/miata_f1)',
        'U3': 'wideband: 3.3 V ADC/analog reference', 'U5': 'wideband: pump current sense amp',
        'Q1': 'wideband: LSU heater low side (protected)', 'D1': 'wideband: heater',
        'D2': 'wideband: status', 'D3': 'wideband: status',
        'J2': 'Tag-Connect TC2030-NL footprint, wideband MCU SWD (fallback; normally flashed by the ECU)'}

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


# Rev 0.6: the wideband MCU is an STM32F103C8T6 (LQFP-48): the STM32F042 is scarce at JLCPCB/LCSC. The module's
# analog front end is unchanged; the pins are chosen so each group faces its parts with U102 at 90 deg (ESR drives
# and LEDs left, heater / battery sense / pump right, CAN and the programming UART up, analog and the crystal down).
# firmware/wideband/miata_f1/io/io_pins.h and board.h carry the same map. PA9/PA10 (USART1) are the ROM
# bootloader's serial port for the programming link from the main MCU; net names are from the main MCU's side.
U2_PADS = {
    '1': '+3V3',                          # VBAT
    '5': 'WB_OSC_IN', '6': 'WB_OSC_OUT',  # PD0 / PD1: 8 MHz crystal Y101
    '7': 'WB_NRST', '8': 'GND', '9': 'WB_VDDA',
    '10': 'WB_UN_SENSE',                  # PA0 ADC_IN0
    # PA1 (pin 11): rev 0.7 no connection. The module wires it to LSU_VM but never samples it; a VM wire shorted to
    # battery then put about 2 A into it through nothing at all
    '12': 'WB_IP_SENSE',                  # PA2 ADC_IN2
    '13': 'WB_VM',                        # PA3 ADC_IN3
    '16': 'WB_IP_DAC',                    # PA6 TIM3_CH1
    '18': 'WB_VBAT_DIV',                  # PB0 ADC_IN8
    '20': 'WB_BOOT1',                     # PB2 / BOOT1: R135 to GND, so BOOT0 high starts the ROM bootloader
    '21': 'WB_HTR_PWM',                   # PB10 TIM2_CH3 (partial remap 2)
    '23': 'GND', '24': '+3V3',
    '30': 'WB_PROG_RX', '31': 'WB_PROG_TX',   # PA9 USART1_TX / PA10 USART1_RX
    '32': 'WB_CAN_RX', '33': 'WB_CAN_TX',     # PA11 / PA12
    '34': 'WB_SWDIO', '35': 'GND', '36': '+3V3', '37': 'WB_SWCLK',
    '41': 'WB_ESR_42', '42': 'WB_ESR_ADV', '43': 'WB_ESR_49',   # PB5 / PB6 / PB7
    '44': 'WB_BOOT0',
    '45': 'WB_LED_B', '46': 'WB_LED_G',   # PB8 / PB9
    '47': 'GND', '48': '+3V3',
}


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
        lib = FP_OVERRIDE.get(r, f['lib'])
        if r[0] in 'RC' and r[:2] not in ('CS',):
            size = '0402' if '0402' in lib else '0603'
            val = VALUE_RC.get(r, f['value'])
            lc = LCSC[r[0] + size][val]
        else:
            val = VALUE.get(r, f['value']); lc = PARTS_LCSC.get(r, '')
        pads = {}
        for num, pl in f['pads'].items():
            if num:
                pads[num] = net(pl[0][2])
        if r == 'U2':
            pads = {str(n): U2_PADS.get(str(n), '') for n in range(1, 49)}
        if r == 'U1':
            # rev 0.7: the Nernst buffer's input (pin 10) through R137 (10k) instead of straight from the LSU_UN wire,
            # so a UN wire shorted to battery puts (14.4 - 3.6) / 10k = 1.1 mA into the MCP6004's input diodes (2 mA
            # max) instead of the full short. The buffer input is CMOS (pA), so the 10k costs nothing at DC or at the
            # ESR frequency.
            pads['10'] = 'WB_UN_IN'
        # rev 0.8, LSU wires shorted to battery: the parts in the pump and virtual-ground paths take a fault current,
        # so they are 1206 (0.25 W); a resettable fuse (F2) sits in the VM wire, whose path (R109, 10 ohm) would
        # otherwise pass about 1 A. Clamp diodes (D40/D41) take the current off the op-amp outputs into +3V3, where the
        # shunt clamp (U15/Q20) holds the rail.
        if r in ('R8', 'R9', 'R10'):
            lib = 'Resistor_SMD:R_1206_3216Metric'
            lc = {'R8': 'C17969', 'R9': 'C17903', 'R10': 'C25341'}[r]
        if r in ('R9', 'C4', 'R3'):          # sensor side of R109 is now the node behind the fuse
            pads = {k: ('WB_VMS' if v == 'LSU_VM' else v) for k, v in pads.items()}
        out.append(dict(ref=ref(r), value=val, fp=lib, lcsc=lc, pads=pads, desc=DESC.get(r, 'wideband'),
                        mod_ref=r, side=f['side']))
    # CAN transceiver for the controller, same bus as the main MCU
    # rev 0.8: TCAN1042V-Q1 (5 V supply, 3.3 V VIO, +-58 V bus fault protection), as the main MCU's U10
    out.append(dict(ref='U106', value='TCAN1042VDRQ1', fp='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', lcsc='C485806',
                    pads={'1': 'WB_CAN_TX', '2': 'GND', '3': '+5V', '4': 'WB_CAN_RX', '5': '+3V3', '6': 'CAN_L',
                          '7': 'CAN_H', '8': 'GND'}, desc='wideband CAN transceiver (shared CAN bus)', side='F'))
    out.append(dict(ref='C122', value='100n', fp='Capacitor_SMD:C_0402_1005Metric', lcsc='C1525',
                    pads={'1': '+5V', '2': 'GND'}, desc='U106 VCC decoupling', side='F'))
    out.append(dict(ref='C118', value='100n', fp='Capacitor_SMD:C_0402_1005Metric', lcsc='C1525',
                    pads={'1': '+3V3', '2': 'GND'}, desc='U106 decoupling', side='F'))
    # rev 0.6, for the STM32F103: its own 8 MHz crystal (keeps CAN in spec over temperature; same part as the main
    # MCU's Y1, 33 pF loads for its 20 pF), BOOT1 pull-down, and decoupling for its third VDD pin
    out.append(dict(ref='Y101', value='8MHz', fp='Crystal:Crystal_SMD_5032-2Pin_5.0x3.2mm', lcsc='C115962',
                    pads={'1': 'WB_OSC_IN', '2': 'WB_OSC_OUT'}, desc='wideband MCU crystal', side='F'))
    out.append(dict(ref='C119', value='33p', fp='Capacitor_SMD:C_0402_1005Metric', lcsc='C1562',
                    pads={'1': 'WB_OSC_IN', '2': 'GND'}, desc='Y101 load', side='F'))
    out.append(dict(ref='C120', value='33p', fp='Capacitor_SMD:C_0402_1005Metric', lcsc='C1562',
                    pads={'1': 'WB_OSC_OUT', '2': 'GND'}, desc='Y101 load', side='F'))
    out.append(dict(ref='R135', value='10k', fp='Resistor_SMD:R_0402_1005Metric', lcsc='C25744',
                    pads={'1': 'WB_BOOT1', '2': 'GND'}, desc='wideband MCU BOOT1 pull-down', side='F'))
    out.append(dict(ref='C121', value='100n', fp='Capacitor_SMD:C_0402_1005Metric', lcsc='C1525',
                    pads={'1': '+3V3', '2': 'GND'}, desc='U102 VDD decoupling', side='F'))
    # rev 0.7: Schottky from VDDA (REF3033) to VDD (+3V3). With the low-dropout U4, VDD no longer lags VDDA at power-up;
    # this covers the other direction: at key-off and in a brown-out the +3V3 rail (0.15 A load) collapses while VDDA
    # (about 1 uF, a light load) lingers, up to 0.8 V above VDD. ST allows 0.3 V; the diode holds it to its forward drop.
    out.append(dict(ref='D30', value='BAT54WS', fp='Diode_SMD:D_SOD-323', lcsc='C124205',
                    pads={'1': '+3V3', '2': 'WB_VDDA'}, desc='F103 VDDA-to-VDD clamp (Diodes BAT54WS-7-F)', side='F'))
    # rev 0.8: 22k (was 10k): 0.9 mA into the buffer input in a 24 V jump start with the UN wire shorted (2 mA max)
    out.append(dict(ref='R137', value='22k', fp='Resistor_SMD:R_0402_1005Metric', lcsc='C25768',
                    pads={'1': 'LSU_UN', '2': 'WB_UN_IN'}, desc='Nernst buffer input series resistor (LSU_UN short protection)',
                    side='F'))
    out.append(dict(ref='F2', value='nSMD010', fp='Fuse:Fuse_1206_3216Metric', lcsc='C70065',
                    pads={'1': 'LSU_VM', '2': 'WB_VMS'},
                    desc='PTC 0.1 A hold / 0.25 A trip, 60 V, 1.6 ohm: LSU VM wire (TECHFUSE nSMD010)', side='F'))
    out.append(dict(ref='D40', value='B5819W', fp='Diode_SMD:D_SOD-123', lcsc='C8598',
                    pads={'1': '+3V3', '2': 'WB_PUMP'}, desc='pump drive clamp to +3V3', side='F'))
    out.append(dict(ref='D41', value='B5819W', fp='Diode_SMD:D_SOD-123', lcsc='C8598',
                    pads={'1': '+3V3', '2': 'WB_VM'}, desc='virtual-ground drive clamp to +3V3', side='F'))
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
