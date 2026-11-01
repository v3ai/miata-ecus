"""
Miata ECU daughterboard - single source of truth for parts and connectivity.

Every part: ref, value, footprint (lib:name), LCSC number, {pad: net}.
Placement lives in place.py, routing in route.py.
"""

FP = {
    'R0603': 'Resistor_SMD:R_0603_1608Metric',
    'R0805': 'Resistor_SMD:R_0805_2012Metric',
    'R0402': 'Resistor_SMD:R_0402_1005Metric',
    'C0402': 'Capacitor_SMD:C_0402_1005Metric',
    'C0603': 'Capacitor_SMD:C_0603_1608Metric',
    'C0805': 'Capacitor_SMD:C_0805_2012Metric',
    'C1206': 'Capacitor_SMD:C_1206_3216Metric',
    'RN4':   'Resistor_SMD:R_Array_Convex_4x0603',
    'LED':   'LED_SMD:LED_0603_1608Metric',
    'FB':    'Inductor_SMD:L_0603_1608Metric',
    'SOD123': 'Diode_SMD:D_SOD-123',
    'SOD323': 'Diode_SMD:D_SOD-323',
    'TSSOP24': 'Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm',
    'F1206': 'Fuse:Fuse_1206_3216Metric',
    'SMA':   'Diode_SMD:D_SMA',
    'SMC':   'Diode_SMD:D_SMC',
    'SOT223': 'Package_TO_SOT_SMD:SOT-223',
    'SOT223T2': 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
    'SOT235': 'Package_TO_SOT_SMD:SOT-23-5',
    'SOIC8': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
    'SOT23': 'Package_TO_SOT_SMD:SOT-23',
    'SOIC8EP': 'Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm',
    'DSO8EP': 'Package_SO:Infineon_PG-DSO-8-27_3.9x4.9mm_EP2.65x3mm',
    'SOIC16': 'Package_SO:SOIC-16_3.9x9.9mm_P1.27mm',
    'QSOP16': 'Package_SO:QSOP-16_3.9x4.9mm_P0.635mm',
    'LQFP100': 'Package_QFP:LQFP-100_14x14mm_P0.5mm',
    'XTAL':  'Crystal:Crystal_SMD_5032-2Pin_5.0x3.2mm',
    'L1210': 'Inductor_SMD:L_1210_3225Metric',
    'L5050': 'Inductor_SMD:L_Sunlord_MWSA0503S',
    'L7066': 'Inductor_SMD:L_Sunlord_MWSA0603S',
    'BTN':   'Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A',
    'HDR40': 'Connector_PinHeader_2.54mm:PinHeader_1x40_P2.54mm_Vertical',
    'TAG':   'Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical',
    'MH':    'MountingHole:MountingHole_3.2mm_M3',
}

# value -> LCSC for passives (all JLC parts proven in rusEFI hellen-one BOMs
# unless marked otherwise in the BOM notes)
LCSC_R0603 = {'0': 'C21189', '1': 'C22936', '47': 'C23182', '100': 'C22775', '330': 'C23138',
              '1k': 'C21190', '2.2k': 'C4190', '2.7k': 'C13167', '4.7k': 'C23162',
              '5.1k': 'C23186', '5.6k': 'C23189', '6.8k': 'C23212', '10k': 'C25804',
              '12k': 'C22790', '33k': 'C4216', '47k': 'C25819', '68k': 'C23231',
              '100k': 'C25803'}
LCSC_R0402 = {'6.8k': 'C25917', '1k': 'C11702', '2.2k': 'C25879', '2.7k': 'C25885', '4.7k': 'C25900',
              '5.6k': 'C25908', '10k': 'C25744', '33k': 'C25779', '100k': 'C25741', '1M': 'C26083'}
LCSC_C0402 = {'1u': 'C52923', '1n': 'C1523', '10n': 'C15195', '100n': 'C1525'}
LCSC_R0805 = {'5.1k': 'C27834', '100': 'C17408'}
LCSC_C0603 = {'22p': 'C1653', '33p': 'C1663', '220p': 'C1603', '1n': 'C1588', '10n': 'C57112',
              '100n': 'C14663', '1u': 'C15849', '2.2u': 'C23630', '4.7u': 'C19666'}
LCSC_C0805 = {'10u': 'C15850', '1n': 'C46653'}
LCSC_C1206 = {'10u/50V': 'C13585'}

parts = []   # list of dicts


def add(ref, value, fp, lcsc, pads, desc='', dnp=False):
    # dnp: footprint on the board, part not assembled by JLC (listed as optional in the self-order BOM)
    parts.append(dict(ref=ref, value=value, fp=FP[fp], lcsc=lcsc, pads=pads, desc=desc, dnp=dnp))


def R(ref, value, a, b, size='0603'):
    tbl = {'0603': LCSC_R0603, '0805': LCSC_R0805, '0402': LCSC_R0402}[size]
    add(ref, value, 'R' + size, tbl[value], {'1': a, '2': b})


def C(ref, value, a, b, size='0603'):
    tbl = {'0603': LCSC_C0603, '0805': LCSC_C0805, '1206': LCSC_C1206, '0402': LCSC_C0402}[size]
    add(ref, value, 'C' + size, tbl[value], {'1': a, '2': b})


# ---------------------------------------------------------------------------
# Headers.  J1 = top edge (power + outputs), J2 = bottom edge (inputs + comms)
# ---------------------------------------------------------------------------
J1 = {1: 'VBAT_IN', 2: 'VBAT_IN', 3: 'VIGN_IN', 4: 'GND', 5: 'GND',
      6: 'OUT_FP', 7: 'OUT_MAINRLY', 8: 'OUT_AC', 9: 'OUT_FAN', 10: 'OUT_CEL',
      11: 'OUT_TACH', 12: 'OUT_LS7', 13: 'GND',
      14: 'OUT_IGN1', 15: 'OUT_IGN2', 16: 'OUT_IGN3', 17: 'OUT_IGN4', 18: 'GND'}
HS_OUT = ['INJ1', 'INJ2', 'INJ3', 'INJ4', 'IACV', 'VVT', 'BOOST', 'ALT']
for i, name in enumerate(HS_OUT):
    p = 19 + 3 * i
    J1[p] = 'OUT_' + name
for p in range(19, 41):
    J1.setdefault(p, 'GND')

J2 = {1: 'V5_SENS', 2: 'GND', 3: 'IN_KNOCK', 4: 'IN_TPS', 5: 'IN_MAP', 6: 'IN_CLT',
      7: 'IN_IAT', 8: 'IN_AFR', 9: 'IN_AUX1', 10: 'IN_AUX2', 11: 'IN_AUX3', 12: 'GND',
      13: 'IN_HALL1', 14: 'IN_HALL2', 15: 'IN_SW1', 16: 'IN_SW2', 17: 'IN_SW3', 18: 'GND',
      19: 'VR2_N', 20: 'VR2_P', 21: 'VR1_P', 22: 'VR1_N', 23: 'GND',
      24: 'UART_TX', 25: 'UART_RX', 26: 'GND', 27: 'CAN_L', 28: 'CAN_H', 29: 'GND',
      30: 'USB_DM', 31: 'USB_DP', 32: 'USB_VBUS',
      # on-board wideband (rev 0.2): pins 33-40 sit straight under the controller block.
      # LSU 4.9: UN = Nernst cell, RT = trim/IA, VM = virtual ground, IP = pump current.
      # Heater: H- is switched low side; HTR_GND is the heater current return, kept off the
      # daughterboard ground plane (the motherboard ties it to GND).
      33: 'LSU_UN', 34: 'LSU_RT', 35: 'LSU_VM', 36: 'LSU_IP',
      37: 'LSU_HTR_N', 38: 'LSU_HTR_N', 39: 'HTR_GND', 40: 'HTR_GND'}

add('J1', 'Mezz_Power_Out', 'HDR40', 'C2977586', {str(k): v for k, v in J1.items()},
    '1x40 2.54mm male, to motherboard (top edge)')
add('J2', 'Mezz_Signal_In', 'HDR40', 'C2977586', {str(k): v for k, v in J2.items()},
    '1x40 2.54mm male, to motherboard (bottom edge)')

# ---------------------------------------------------------------------------
# MCU  STM32F407VGT6 (1MB flash - required by rusEFI F4 builds)
# ---------------------------------------------------------------------------
mcu = {
    # supplies
    '6': '+3V3', '11': '+3V3', '19': '+3V3', '28': '+3V3', '50': '+3V3', '75': '+3V3', '100': '+3V3',
    '10': 'GND', '27': 'GND', '74': 'GND', '99': 'GND', '20': 'GND',
    '21': '+3V3A', '22': '+3V3A',
    '49': 'VCAP1', '73': 'VCAP2',
    '12': 'HSE_IN', '13': 'HSE_OUT', '14': 'NRST', '94': 'BOOT0',
    # relay/lamp outputs from the top of the left edge (ULN2003 sits up-left). PC13/PC14 run through the backup
    # power switch, which can supply 3 mA in total; the two ULN2003 inputs draw at most ~0.72 mA each at 3.3 V
    # ((3.3 - 2 Vbe) / 2.7k), so 1.45 mA together, and relays need no speed (ST's limit there is 2 MHz).
    '1': 'LS7_CTL', '2': 'TACH_CTL', '3': 'CEL_CTL', '4': 'FAN_CTL', '5': 'AC_CTL',
    '7': 'MAINRLY_CTL', '8': 'FP_CTL',
    # rev 0.5: PB2 is BOOT1; pulled low so ST's DFU bootloader starts reliably (BOOT0 = 1, BOOT1 = 0)
    '37': 'BOOT1',
    # rev 0.5: low-side driver enable (PA8, active low, pulled up to +5V: drivers off until firmware enables).
    # On the right edge, so it reaches U11's ~OE from below instead of adding a ninth line to the top-edge bundle.
    '67': 'DRV_EN_N',
    # ignition + smart low sides from the top edge, ordered left->right like the driver row
    '98': 'IGN1_CTL', '97': 'IGN2_CTL', '96': 'IGN3_CTL', '95': 'IGN4_CTL',
    '93': 'INJ1_CTL', '92': 'INJ2_CTL', '91': 'INJ3_CTL', '90': 'INJ4_CTL',
    '89': 'IACV_CTL', '88': 'VVT_CTL', '87': 'BOOST_CTL', '86': 'ALT_CTL',
    # analog: all nine sensor inputs on the bottom edge in J2 column order, knock on
    # PA3 (ADC3_IN3); battery/ignition sense on the left edge next to their divider
    '26': 'AN_KNOCK', '29': 'AN_TPS', '30': 'AN_MAP', '31': 'AN_CLT', '32': 'AN_IAT',
    '33': 'AN_AFR', '34': 'AN_AUX1', '35': 'AN_AUX2', '36': 'AN_AUX3',
    '24': 'AN_VBATT', '25': 'AN_VIGN',
    # digital inputs (bottom edge)
    '38': 'HALL1', '39': 'HALL2', '40': 'SW1', '41': 'SW2', '42': 'SW3',
    '43': 'VR2_OUT', '44': 'VR1_OUT',
    # comms (right edge)
    '51': 'CAN_RX', '52': 'CAN_TX',            # CAN2 PB12/PB13
    '63': 'UART_TX', '64': 'UART_RX',          # USART6 PC6/PC7
    '59': 'LED_RUN', '60': 'LED_COMM', '61': 'LED_WARN', '62': 'LED_ERR',  # PD12-15
    # wideband MCU programming link (rev 0.4): USART3 on PD8/PD9 to the F042's ROM-bootloader USART1
    # (PA10/PA9), PD10 drives its BOOT0 (10k pull-down stays), PD11 (open drain) its NRST
    '55': 'WB_PROG_TX', '56': 'WB_PROG_RX', '57': 'WB_BOOT0', '58': 'WB_NRST',
    '70': 'USB_DM', '71': 'USB_DP',            # OTG_FS PA11/PA12
    '72': 'SWDIO', '76': 'SWCLK',              # PA13/PA14
}
add('U1', 'STM32F407VGT6', 'LQFP100', 'C12345', mcu, 'MCU, 168MHz Cortex-M4F, 1MB flash')

for i in range(6):
    C(f'C{1+i}', '100n', '+3V3', 'GND', '0402' if i == 3 else '0603')   # one per VDD pin
C('C7', '4.7u', '+3V3', 'GND')
C('C8', '4.7u', '+3V3', 'GND')
C('C9', '2.2u', 'VCAP1', 'GND')
C('C10', '2.2u', 'VCAP2', 'GND')
add('FB1', 'BLM18PG221', 'FB', 'C80165', {'1': '+3V3', '2': '+3V3A'}, 'VDDA ferrite')
C('C11', '1u', '+3V3A', 'GND')
C('C12', '100n', '+3V3A', 'GND')
add('Y1', '8MHz', 'XTAL', 'C115962', {'1': 'HSE_IN', '2': 'HSE_OUT'}, 'X50328MSB2GI 20pF')
# rev 0.5: 33 pF load caps for the 20 pF crystal (C = 2 x (CL - ~4 pF pin + stray), AN2867)
C('C13', '33p', 'HSE_IN', 'GND')
C('C14', '33p', 'HSE_OUT', 'GND')
R('R1', '10k', 'BOOT0', 'GND')
C('C15', '100n', 'NRST', 'GND')
add('SW1', 'BOOT', 'BTN', 'C318884', {'1': '+3V3', '2': 'BOOT0'}, 'hold at power-up for DFU')
add('SW2', 'RESET', 'BTN', 'C318884', {'1': 'NRST', '2': 'GND'})
add('J3', 'SWD', 'TAG', '', {'1': '+3V3', '2': 'SWDIO', '3': 'NRST', '4': 'SWCLK', '5': 'GND', '6': ''},
    'Tag-Connect TC2030-NL footprint (no part placed)')

# status LEDs (rev 0.5b: Hubei KENTO KT-0603 series, which JLC stocks; the Everlight parts ran out)
for i, (net, col, lc) in enumerate([('LED_RUN', 'GREEN', 'C12624'), ('LED_COMM', 'BLUE', 'C2288'),
                                    ('LED_WARN', 'YELLOW', 'C2287'), ('LED_ERR', 'RED', 'C2286')]):
    R(f'R{2+i}', '1k', net, f'{net}_A')
    add(f'D{1+i}', col, 'LED', lc, {'1': 'GND', '2': f'{net}_A'})   # pad1 = K
R('R6', '1k', '+3V3', 'PWR_LED_A')
add('D5', 'GREEN', 'LED', 'C12624', {'1': 'GND', '2': 'PWR_LED_A'}, 'power LED')

# ---------------------------------------------------------------------------
# Power (topology copied from rusEFI hellen-one power_12and5V)
# ---------------------------------------------------------------------------
add('D6', 'SMCJ30A', 'SMC', 'C224048', {'1': 'VBAT_IN', '2': 'GND'}, 'load dump TVS')
add('D7', 'SS34', 'SMA', 'C8678', {'1': '+12V_IN', '2': 'VBAT_IN'}, 'reverse battery')
add('D8', 'B5819W', 'SOD123', 'C8598', {'1': '+12V_IN', '2': 'VIGN_IN'}, 'wake on ignition')
# rev 0.5: resettable fuse on the logic supply (an internal fault no longer waits on the car's 15-30 A fuse;
# same part and position as Hellen's power-12V module), then a TVS that also clamps the ignition-wake path and fast
# spikes for the buck. SMAJ33A: 36.7 V minimum breakdown, above a 35 V (suppressed) load dump, so it never has to
# soak up a 400 ms dump through F1 (D6 on the input does that, as in Hellen's design).
# rev 0.5b: TECHFUSE nSMD050-33V (same 0.5 A hold / 1 A trip / 100 A, 1206; rated 33 V instead of 24 V, so a
# tripped fuse during an overvoltage stays inside its rating). The SMD1206P050TF/24 ran out at JLC.
add('F1', 'nSMD050-33V', 'F1206', 'C70077', {'1': '+12V_IN', '2': '+12V'},
    'PTC 0.5 A hold / 1 A trip, 33 V: logic supply fuse')
add('D12', 'SMAJ33A', 'SMA', 'C223988', {'1': '+12V', '2': 'GND'}, 'TVS on the fused logic supply (Littelfuse)')
R('R7', '1', '+12V', 'DAMP')
C('C16', '10u/50V', 'DAMP', 'GND', '1206')   # rev 0.5: 50 V part (was 4.7u 16 V)
# rev 0.5b: FH CMI322513U2R2KT (500 mA, 0.3 ohm; the buck draws about 0.15 A at 12 V). The Taiyo Yuden
# LBC3225T2R2MR ran out at JLC.
add('L1', '2.2uH', 'L1210', 'C70960', {'1': '+12V', '2': '+12V_F'}, 'input filter (FH CMI322513U2R2KT, 500 mA, 0.3 ohm)')
C('C17', '10u/50V', '+12V_F', 'GND', '1206')
C('C18', '10u/50V', '+12V_F', 'GND', '1206')
add('U2', 'LMR14020', 'SOIC8EP', 'C187824',
    {'1': 'BUCK_BOOT', '2': '+12V_F', '3': '+12V_F', '4': 'BUCK_RT', '5': 'BUCK_FB',
     '6': 'BUCK_SS', '7': 'GND', '8': 'BUCK_SW', '9': 'GND'}, '40V 2A buck -> 5V')
C('C19', '100n', 'BUCK_BOOT', 'BUCK_SW')
R('R8', '10k', 'BUCK_RT', 'GND')
C('C20', '10n', 'BUCK_SS', 'GND')
add('D9', 'B360A', 'SMA', 'C94193', {'1': 'BUCK_SW', '2': 'GND'}, 'catch diode, 60 V 3 A SMA (rev 0.5; Diodes B360A-13-F since 0.5b)')
# rev 0.5: Isat 5.5 A, above the LMR14020's 3.8 A maximum current limit (the 5x5 mm MWSA0503S saturated at 3.5 A)
add('L2', '10uH', 'L7066', 'C132141', {'1': 'BUCK_SW', '2': '+5V'}, 'buck inductor, Sunlord MWSA0603S-100MT')
R('R9', '68k', '+5V', 'BUCK_FB')
C('C21', '220p', '+5V', 'BUCK_FB')
R('R10', '12k', 'BUCK_FB', 'GND')
C('C22', '10u', '+5V', 'GND', '0805')
C('C23', '10u', '+5V', 'GND', '0805')
C('C59', '10u', '+5V', 'GND', '0805')   # rev 0.5: third output cap (about 30 uF effective, TI example 47 uF)
add('D10', 'B5819W', 'SOD123', 'C8598', {'1': '+5V', '2': 'USB_VBUS'}, 'bench power from USB')
# protected 5V sensor supply, tracks +5V
add('U3', 'TLS115B0EJ', 'DSO8EP', 'C3743696',
    {'1': 'V5_SENS', '2': '', '3': 'GND', '4': '', '5': '+5V', '6': '', '7': '+12V', '8': '+12V', '9': 'GND'},
    'sensor 5V tracker, short-to-battery protected')
C('C24', '1u', '+12V', 'GND')
C('C25', '1u', 'V5_SENS', 'GND')
# 3.3V
add('U4', 'AMS1117-3.3', 'SOT223T2', 'C6186', {'1': 'GND', '2': '+3V3', '3': '+5V'})
C('C26', '10u', '+5V', 'GND', '0805')
C('C27', '10u', '+3V3', 'GND', '0805')
# supply sensing
R('R11', '33k', '+12V', 'AN_VBATT', '0402')
R('R12', '6.8k', 'AN_VBATT', 'GND', '0402')
C('C28', '100n', 'AN_VBATT', 'GND', '0402')
R('R13', '33k', 'VIGN_IN', 'AN_VIGN', '0402')
R('R14', '6.8k', 'AN_VIGN', 'GND', '0402')
C('C29', '100n', 'AN_VIGN', 'GND', '0402')

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------
# 7x relay/lamp/tach low side: ULN2003. Rev 0.5: COM goes to a TVS (SMAJ33A, 36.7-40.6 V breakdown) instead of
# +12V. Relay kick-back still clamps (about 41 V worst case, under the ULN's 50 V), a battery-fed relay coil (2003-05
# main relay) can no longer back-feed the ECU through the clamp diodes with the key off, and a 35 V load dump on the
# relay and lamp feeds doesn't reach the breakdown (a small zener here would conduct and could fail short, which
# would switch every relay on).
uln = {'8': 'GND', '9': 'ULN_COM'}
for i, n in enumerate(['FP', 'MAINRLY', 'AC', 'FAN', 'CEL', 'TACH', 'LS7']):
    uln[str(1 + i)] = n + '_CTL'
    uln[str(16 - i)] = 'OUT_' + n
add('U5', 'ULN2003AD', 'SOIC16', 'C7512', uln, '7ch 500mA low side for relays/CEL/tach')
add('D11', 'SMAJ33A', 'SMA', 'C223988', {'1': 'ULN_COM', '2': 'GND'}, 'TVS: ULN2003 flyback clamp (Littelfuse)')

# 4x ignition logic outputs (smart coils / COP): TC4427 at 5V
for u, (a, b) in zip(['U6', 'U7'], [('IGN1', 'IGN2'), ('IGN3', 'IGN4')]):
    add(u, 'TC4427', 'SOIC8', 'C20551',
        {'1': '', '2': a + '_CTL', '3': 'GND', '4': b + '_CTL', '5': b + '_DRV', '6': '+5V',
         '7': a + '_DRV', '8': ''}, '1.5A dual driver for coil-on-plug logic inputs')
rn = 15
cn = 34
ign_pd = {}
for i, n in enumerate(['IGN1', 'IGN2', 'IGN3', 'IGN4']):
    ign_pd[str(1 + i)] = n + '_CTL'
    ign_pd[str(8 - i)] = 'GND'
    R(f'R{rn}', '100', n + '_DRV', 'OUT_' + n, '0805'); rn += 1
add('RN1', '4x10k', 'RN4', 'C29718', ign_pd, 'ignition inputs pull-down')
C(f'C{cn}', '1u', '+5V', 'GND', '0402'); cn += 1     # C34 TC4427 #1 VDD
C(f'C{cn}', '1u', '+5V', 'GND', '0402'); cn += 1     # C35 TC4427 #2 VDD

# 8x smart low side (injectors, IACV, VVT, boost, alternator). Rev 0.5b: onsemi NCV8406A (SOT-223, same pinout:
# 1 gate, 2/tab drain, 3 source; 60-70 V active clamp, 210 mOhm at 5 V, current limit and thermal shutdown,
# AEC-Q101). It replaces the AUIPS2041L (63-75 V clamp), which ran out at JLC and LCSC.
# Rev 0.5: driven at 5 V through an SN74LVC4245A (full enhancement and current limit at 5 V). Its OE is pulled up to +5V, so all eight are off (and pulled low) through reset, boot, the
# bootloader and DFU until the firmware drives DRV_EN_N low.
for i, n in enumerate(HS_OUT):
    add(f'Q{1+i}', 'NCV8406ASTT3G', 'SOT223', 'C459816',
        {'1': n + '_IN', '2': 'OUT_' + n, '3': 'GND', '4': 'OUT_' + n},
        'protected low side, 60-70 V clamp')
lvc = {'1': '+5V', '2': 'GND', '11': 'GND', '12': 'GND', '13': 'GND', '22': 'DRV_EN_N', '23': '+3V3', '24': '+3V3'}
for i, n in enumerate(HS_OUT):           # DIR low: B (3.3 V, MCU) -> A (5 V, drivers); A7/B7 = INJ1 ... A0/B0 = ALT
    lvc[str(10 - i)] = n + '_IN'
    lvc[str(14 + i)] = n + '_CTL'
add('U11', 'SN74LVC4245APWR', 'TSSOP24', 'C7859', lvc, '8-bit 3.3 V -> 5 V level shifter for the low-side inputs')
# driver-side pull-downs keep the outputs off while the shifter is disabled
for i, n in enumerate(HS_OUT):
    R(f'R{rn}', '10k', n + '_IN', 'GND'); rn += 1

# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------
# analog 0-5V -> 0-3.2V (div 1.56). CLT/IAT get 2.7k bias to sensor 5V.
for n in ['TPS', 'MAP', 'CLT', 'IAT', 'AFR', 'AUX1', 'AUX2', 'AUX3']:
    R(f'R{rn}', '5.6k', 'IN_' + n, 'AN_' + n, '0402'); rn += 1
    R(f'R{rn}', '10k', 'AN_' + n, 'GND', '0402'); rn += 1
    C(f'C{cn}', '10n', 'AN_' + n, 'GND', '0402'); cn += 1
    if n in ('CLT', 'IAT'):
        R(f'R{rn}', '2.7k', 'V5_SENS', 'IN_' + n, '0402'); rn += 1

# knock: AC coupled, biased to 1.65V, gain 5.7
C(f'C{cn}', '100n', 'IN_KNOCK', 'KN_P'); cn += 1
R(f'R{rn}', '100k', 'KN_P', 'KN_BIAS'); rn += 1
R(f'R{rn}', '100k', '+3V3', 'KN_BIAS'); rn += 1
R(f'R{rn}', '100k', 'KN_BIAS', 'GND'); rn += 1
C(f'C{cn}', '1u', 'KN_BIAS', 'GND'); cn += 1
R(f'R{rn}', '47k', 'KN_OUT', 'KN_N'); rn += 1
R(f'R{rn}', '10k', 'KN_N', 'KN_BIAS'); rn += 1
R(f'R{rn}', '330', 'KN_OUT', 'AN_KNOCK'); rn += 1
C(f'C{cn}', '10n', 'AN_KNOCK', 'GND'); cn += 1
C(f'C{cn}', '100n', '+3V3', 'GND'); cn += 1
add('U8', 'LMV321IDBVR', 'SOT235', 'C7972',
    {'1': 'KN_P', '2': 'GND', '3': 'KN_N', '4': 'KN_OUT', '5': '+3V3'}, 'knock amp')

# VR (spare inputs; no Miata year uses a VR sensor). Rev 0.5b: LM2903 dual comparator, made by TI, onsemi, ST, Diodes,
# UMW and others, instead of the single-source MAX9926 (out of stock everywhere). Per channel: the harness legs go through
# 2 x 5.1k to the comparator inputs, 1 nF across them, a BAT54S on each input to GND and +5V (holds them at -0.3..5.3 V;
# the LM2903 inputs take up to 36 V and down to -0.3 V), 100k from each input to VBIAS (1.65 V), and 1M from the
# open-collector output back to IN+ for about 30 mV of hysteresis. Output high when harness - is above harness +
# (the MAX9926's polarity), 10k pull-up to +3V3 into PE13/PE12. See firmware/tools/circuit_sim.py section H.
# comparator A (pins 1-3) takes VR2 and B (5-7) VR1, so each channel's pins face its own header columns
add('U9', 'LM2903DR', 'SOIC8', 'C7549',
    {'1': 'VR2_OUT', '2': 'VR2_INN', '3': 'VR2_INP', '4': 'GND',
     '5': 'VR1_INP', '6': 'VR1_INN', '7': 'VR1_OUT', '8': '+5V'}, 'dual comparator: VR conditioner (spare VR inputs)')
for ref, node in (('D15', 'VR1_INP'), ('D16', 'VR1_INN'), ('D17', 'VR2_INP'), ('D18', 'VR2_INN')):
    # BAT54S: pad 1 anode of the lower diode (GND), pad 2 cathode of the upper diode (+5V), pad 3 the input
    add(ref, 'BAT54S', 'SOT23', 'C19726', {'1': 'GND', '2': '+5V', '3': node}, f'VR input clamp ({node})')
for ref, a_, b_ in (('R73', 'VR1_INP', 'VR_BIAS'), ('R74', 'VR1_INN', 'VR_BIAS'),
                    ('R75', 'VR2_INP', 'VR_BIAS'), ('R76', 'VR2_INN', 'VR_BIAS')):
    R(ref, '100k', a_, b_, '0402')
R('R77', '1M', 'VR1_OUT', 'VR1_INP', '0402')    # hysteresis
R('R78', '1M', 'VR2_OUT', 'VR2_INP', '0402')
R('R79', '10k', '+3V3', 'VR_BIAS', '0402')
R('R80', '10k', 'VR_BIAS', 'GND', '0402')
C('C60', '100n', 'VR_BIAS', 'GND', '0402')
# outputs are inverted, so harness + goes to IN-
for ch in ['1', '2']:
    R(f'R{rn}', '5.1k', f'VR{ch}_N', f'VR{ch}_A', '0805'); rn += 1
    R(f'R{rn}', '5.1k', f'VR{ch}_A', f'VR{ch}_INP', '0805'); rn += 1
    R(f'R{rn}', '5.1k', f'VR{ch}_P', f'VR{ch}_B', '0805'); rn += 1
    R(f'R{rn}', '5.1k', f'VR{ch}_B', f'VR{ch}_INN', '0805'); rn += 1
    C(f'C{cn}', '1n', f'VR{ch}_INP', f'VR{ch}_INN', '0805'); cn += 1
    R(f'R{rn}', '10k', '+3V3', f'VR{ch}_OUT'); rn += 1
C(f'C{cn}', '100n', '+5V', 'GND'); cn += 1

# Hall (open collector): 1k pull-up to sensor 5V, 4.7k series, 1n filter
for n in ['HALL1', 'HALL2']:
    R(f'R{rn}', '4.7k', 'IN_' + n, n, '0402'); rn += 1
    R(f'R{rn}', '1k', 'V5_SENS', 'IN_' + n, '0402'); rn += 1
    C(f'C{cn}', '1n', n, 'GND', '0402'); cn += 1
# rev 0.5: clamp diodes to +3V3 (PE7/PE8 are 5 V-tolerant pins with no clamp of their own; a crank/cam wire
# shorted to battery would otherwise put ~14 V on them). 4.7k limits the clamp current to ~2 mA.
add('D13', '1N4148WS', 'SOD323', 'C2128', {'1': '+3V3', '2': 'HALL1'}, 'HALL1 clamp to +3V3')
add('D14', '1N4148WS', 'SOD323', 'C2128', {'1': '+3V3', '2': 'HALL2'}, 'HALL2 clamp to +3V3')

# 12V switch inputs: 33k/10k divider, 10n filter
for n in ['SW1', 'SW2', 'SW3']:
    R(f'R{rn}', '33k', 'IN_' + n, n, '0402'); rn += 1
    R(f'R{rn}', '10k', n, 'GND', '0402'); rn += 1
    C(f'C{cn}', '10n', n, 'GND', '0402'); cn += 1

# CAN (3.3V transceiver; termination lives on the motherboard)
add('U10', 'SN65HVD230DR', 'SOIC8', 'C12084',
    {'1': 'CAN_TX', '2': 'GND', '3': '+3V3', '4': 'CAN_RX', '5': '', '6': 'CAN_L', '7': 'CAN_H', '8': 'GND'})
C(f'C{cn}', '100n', '+3V3', 'GND'); cn += 1

# rev 0.5 additions (refs above the rev 0.4 range, so no existing designator changes)
C('C57', '100n', '+5V', 'GND', '0402')        # U11 VCCA
C('C58', '100n', '+3V3', 'GND', '0402')       # U11 VCCB
R('R71', '10k', '+5V', 'DRV_EN_N', '0402')    # drivers disabled until the firmware pulls DRV_EN_N low
R('R72', '10k', 'BOOT1', 'GND', '0402')       # PB2 / BOOT1 low
# The MCU-side control lines have no pull-downs (no room between the MCU and U11). While U11 is disabled its
# outputs are high-impedance and R19-R26 hold the drivers off, so a floating MCU pin does nothing. Once enabled,
# the board firmware parks every control pin rusEFI isn't using as an input with pull-down (rusEFI's own
# "unused" state is a pull-UP, which would switch the driver on).

# mounting holes
for i in range(4):
    add(f'H{1+i}', 'M3', 'MH', '', {})

# on-board wideband controller (FOME / rusEFI module circuit: see wideband.py; layout: wb_clean.py)
import wideband as _wb
for _p in _wb.parts():
    parts.append(dict(ref=_p['ref'], value=_p['value'], fp=_p['fp'], lcsc=_p['lcsc'], pads=_p['pads'],
                      desc=_p['desc']))


def nets():
    s = set()
    for p in parts:
        s.update(v for v in p['pads'].values() if v)
    return sorted(s)


if __name__ == '__main__':
    import collections
    print(len(parts), 'parts', len(nets()), 'nets')
    cnt = collections.Counter()
    for p in parts:
        for v in p['pads'].values():
            if v:
                cnt[v] += 1
    single = [n for n, c in cnt.items() if c == 1]
    print('single-pad nets:', single)
