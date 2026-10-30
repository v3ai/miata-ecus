import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import design, bom

out = sys.argv[1]
wb = Workbook()
F = 'Arial'
hdr_font = Font(name=F, bold=True, color='FFFFFF')
hdr_fill = PatternFill('solid', fgColor='1F3A5F')
grp_fill = PatternFill('solid', fgColor='DCE6F1')
warn_fill = PatternFill('solid', fgColor='FFF2CC')
thin = Side(style='thin', color='BFBFBF')

# --- Parts list --------------------------------------------------------------
ws = wb.active
ws.title = 'Parts List'
import json as _json, os as _os
MPN = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'mpn.json')))
cols = ['Group', 'Qty', 'Value', 'Description', 'Designators', 'Footprint', 'LCSC #', 'JLC type', 'Notes', 'Manufacturer', 'MPN']
ws.append(cols)
for c in range(1, len(cols) + 1):
    cell = ws.cell(1, c)
    cell.font, cell.fill = hdr_font, hdr_fill
    cell.alignment = Alignment(vertical='center')
r = 2
last_group = None
first_data = r
for row in bom.rows():
    if row['group'] != last_group:
        ws.cell(r, 1, row['group']).font = Font(name=F, bold=True)
        for c in range(1, len(cols) + 1):
            ws.cell(r, c).fill = grp_fill
        r += 1
        last_group = row['group']
    lc = row['lcsc']
    jtype = '' if not lc else ('Basic' if lc in bom.BASIC else 'Extended')
    note = ''
    if lc in bom.VERIFY:
        note = 'LCSC # not cross-checked: confirm value/package before ordering'
    if not lc:
        note = 'Not assembled'
    vals = [row['group'], row['qty'], row['value'], row['desc'], ', '.join(row['refs']),
            row['fp'].split(':')[1], lc, jtype, note, MPN.get(lc, {}).get('mfr') or '', MPN.get(lc, {}).get('mpn') or '']
    for c, v in enumerate(vals, 1):
        cell = ws.cell(r, c, v)
        cell.font = Font(name=F)
        cell.border = Border(bottom=thin)
        cell.alignment = Alignment(vertical='top', wrap_text=(c in (4, 5, 9)))
        if note.startswith('LCSC'):
            cell.fill = warn_fill
    r += 1
last = r - 1
r += 1
ws.cell(r, 1, 'Total placements').font = Font(name=F, bold=True)
ws.cell(r, 2, f'=SUMIF(H{first_data}:H{last},"Basic",B{first_data}:B{last})+SUMIF(H{first_data}:H{last},"Extended",B{first_data}:B{last})').font = Font(name=F, bold=True)
r += 1
ws.cell(r, 1, 'Unique extended parts').font = Font(name=F, bold=True)
ws.cell(r, 2, f'=COUNTIF(H{first_data}:H{last},"Extended")').font = Font(name=F, bold=True)
ws.cell(r, 3, 'JLC charges a one-time loading fee per unique extended part').font = Font(name=F, italic=True, color='666666')
r += 2
ws.cell(r, 1, 'All LCSC numbers were checked against LCSC/JLCPCB listings on 2026-10-28 (manufacturer + MPN columns). Check stock at order time.').font = Font(name=F, italic=True)
widths = [26, 6, 16, 44, 40, 34, 11, 10, 34, 18, 24]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = 'A2'

# --- Header pinout --------------------------------------------------------------
ws2 = wb.create_sheet('Header Pinout')
ws2.append(['Pin', 'J1 (top edge) net', 'J1 function', 'J2 (bottom edge) net', 'J2 function'])
for c in range(1, 6):
    ws2.cell(1, c).font, ws2.cell(1, c).fill = hdr_font, hdr_fill
FUNC = {
    'VBAT_IN': '12V from main relay (feeds ECU + flyback)', 'VIGN_IN': 'Switched ignition (wakes ECU, sensed)',
    'GND': 'Ground', 'OUT_FP': 'Fuel pump relay (low side)', 'OUT_MAINRLY': 'Main relay coil (low side)',
    'OUT_AC': 'A/C clutch relay (low side)', 'OUT_FAN': 'Radiator fan relay (low side)',
    'OUT_CEL': 'Check engine lamp (low side)', 'OUT_TACH': 'Tach output (open collector)',
    'OUT_LS7': 'Spare low side 500mA', 'OUT_IGN1': 'Coil 1, 5V logic (COP / igniter)',
    'OUT_IGN2': 'Coil 2, 5V logic', 'OUT_IGN3': 'Coil 3, 5V logic', 'OUT_IGN4': 'Coil 4, 5V logic',
    'OUT_INJ1': 'Injector 1 (low side, protected)', 'OUT_INJ2': 'Injector 2', 'OUT_INJ3': 'Injector 3',
    'OUT_INJ4': 'Injector 4', 'OUT_IACV': 'Idle air valve (PWM)', 'OUT_VVT': 'VVT oil control valve (PWM, NB2)',
    'OUT_BOOST': 'Boost control solenoid (PWM)', 'OUT_ALT': 'Alternator field control (NB2)',
    'V5_SENS': 'Protected 5V sensor supply', 'IN_KNOCK': 'Knock sensor', 'IN_TPS': 'Throttle position 0-5V',
    'IN_MAP': 'MAP sensor 0-5V (MPX5700AP on motherboard)', 'IN_CLT': 'Coolant temp (2.7k pull-up on board)',
    'IN_IAT': 'Intake air temp (2.7k pull-up on board)', 'IN_AFR': 'Wideband analog out 0-5V',
    'IN_AUX1': 'Spare analog 0-5V', 'IN_AUX2': 'Spare analog 0-5V', 'IN_AUX3': 'Spare analog 0-5V',
    'IN_HALL1': 'Hall input (1k pull-up to 5V), e.g. NB2 cam', 'IN_HALL2': 'Hall input, e.g. VSS',
    'IN_SW1': 'Switch input 0-12V (A/C request)', 'IN_SW2': 'Switch input 0-12V (clutch/neutral)',
    'IN_SW3': 'Switch input 0-12V (PS pressure)', 'VR2_N': 'VR #2 (cam) -', 'VR2_P': 'VR #2 (cam) +',
    'VR1_P': 'VR #1 (crank) +', 'VR1_N': 'VR #1 (crank) -', 'UART_TX': 'USART3 TX (3.3V, Bluetooth etc.)',
    'UART_RX': 'USART3 RX', 'CAN_L': 'CAN low (wideband controller, dash)', 'CAN_H': 'CAN high',
    'USB_DM': 'USB D- to motherboard USB-C', 'USB_DP': 'USB D+', 'USB_VBUS': 'USB 5V (bench power/flashing)',
    'SWDIO': 'SWD data', 'SWCLK': 'SWD clock', 'NRST': 'MCU reset', 'BOOT0': 'DFU boot select',
    '+3V3': '3.3V out (low current)', '+5V': '5V out (low current)',
}
for pin in range(1, 41):
    a, b = design.J1[pin], design.J2[pin]
    ws2.append([pin, a, FUNC.get(a, ''), b, FUNC.get(b, '')])
for row in ws2.iter_rows(min_row=2):
    for c in row:
        c.font = Font(name=F)
for i, w in enumerate([6, 16, 40, 16, 44], 1):
    ws2.column_dimensions[get_column_letter(i)].width = w
ws2.freeze_panes = 'A2'

# --- MCU pin map -------------------------------------------------------------------
ws3 = wb.create_sheet('MCU Pin Map')
ws3.append(['LQFP pin', 'Port', 'Net', 'Use'])
for c in range(1, 5):
    ws3.cell(1, c).font, ws3.cell(1, c).fill = hdr_font, hdr_fill
import re
sym = {}
import os
for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stm32f407v_lqfp100_pins.txt')).read().split():
    n, nm = line.split(':', 1)
    sym[n] = nm
u1 = next(p for p in design.parts if p['ref'] == 'U1')['pads']
for n in sorted(u1, key=int):
    net = u1[n]
    port = sym.get(n, '')
    if net in ('+3V3', 'GND', '+3V3A', 'VCAP1', 'VCAP2'):
        continue
    ws3.append([int(n), port, net, FUNC.get(net, '')])
for row in ws3.iter_rows(min_row=2):
    for c in row:
        c.font = Font(name=F)
for i, w in enumerate([9, 9, 16, 40], 1):
    ws3.column_dimensions[get_column_letter(i)].width = w
wb.save(out)
print('saved', out)
