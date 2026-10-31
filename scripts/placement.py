"""Placement for the 125 x 60 mm daughterboard (mm, board origin top-left, y down).

Floor plan
  top edge    J1: power in, 7 relay outs, 4 ign outs, 8 smart low-side outs
  top band    ULN2003 | 2x TC4427 | 8x NCV8406A (each directly under its header pin)
  left        power supply (TVS, reverse diode, 5V buck, 5V sensor tracker, 3.3V LDO)
  centre      STM32F407 + decoupling + crystal
  right       SWD, BOOT/RESET buttons, status LEDs, USB/CAN
  bottom band one conditioning column per J2 pin (series R, then R/C pair to GND)
  bottom edge J2: sensor inputs, VR, comms, SWD
"""
import design

BOARD_W, BOARD_H = 125.0, 60.0
PLACE = {}


def hx(n):
    """x of header pin n (both headers share the same x grid)"""
    return 13.0 + (n - 1) * 2.54


def put(ref, x, y, rot=0):
    PLACE[ref] = (round(x, 4), round(y, 4), rot)


def part(ref):
    return next(p for p in design.parts if p['ref'] == ref)


def find(a, b=None, value=None):
    """2-pin part between nets a and b; returns (ref, pad1_is_a)"""
    for p in design.parts:
        nets = list(p['pads'].values())
        if len(p['pads']) != 2:
            continue
        if b is None:
            ok = a in nets
        else:
            ok = set(nets) == {a, b}
        if ok and (value is None or p['value'] == value):
            return p['ref'], p['pads']['1'] == a
    raise KeyError((a, b, value))


def vert(ref_flag, x, y, first_on_bottom=True):
    """vertical 2-pin part; puts net 'a' (from find) at the bottom if requested"""
    ref, pad1_is_a = ref_flag
    a_bottom = first_on_bottom
    rot = 90 if (pad1_is_a == a_bottom) else 270     # rot 90 -> pad1 at +y (bottom)
    put(ref, x, y, rot)


def horiz(ref_flag, x, y, a_left=True):
    ref, pad1_is_a = ref_flag
    rot = 0 if (pad1_is_a == a_left) else 180
    put(ref, x, y, rot)


# --- headers & holes --------------------------------------------------------
put('J1', hx(1), 2.75, 90)
put('J2', hx(1), 57.25, 90)
for i, (x, y) in enumerate([(4.5, 4.5), (120.5, 4.5), (4.5, 55.5), (120.5, 55.5)]):
    put(f'H{1+i}', x, y)

# --- MCU ----------------------------------------------------------------------
MX, MY = 61.0, 32.0
put('U1', MX, MY, 0)
# decoupling: one 100n per VDD pin, at the package corners / gaps
put('C1', 53.2, 22.0, 0)        # pin 99/100 (top-left)
put('C2', 51.2, 25.2, 0)        # pin 10/11, top-left corner
put('C3', 50.4, 35.2, 0)        # pin 19/20 (left)
put('C4', 73.8, 36.4, 0)        # 3rd bottom-edge decoupler, right of the corner (planes via vias)
put('C5', 70.4, 38.9, 0)        # pin 49/50 (bottom-right corner)
put('C6', 70.6, 22.6, 0)        # pin 74/75 (top-right corner)
put('C7', 73.4, 25.0, 90)       # bulk 4.7u (rev 0.5: below the shifter's input path)
put('C8', 49.8, 23.6, 0)        # bulk 4.7u
put('C9', 70.4, 40.6, 0)        # VCAP1 (pin 49)
put('C10', 71.4, 25.4, 90)      # VCAP2 (pin 73), clear of the USB/SWD exits (pin 73)
put('FB1', 45.0, 36.3, 0)       # VDDA ferrite
put('C11', 45.0, 39.1, 0)
put('C12', 45.0, 37.7, 0)
# crystal left of PH0/PH1 (pins 12/13)
put('Y1', 44.6, 32.4, 90)
put('C13', 41.2, 30.6, 0)
put('C14', 41.2, 34.2, 0)
# reset/boot
put('R1', 114.0, 36.0, 0)       # BOOT0 pull-down, by the BOOT button (rev 0.5: off the shifter's input path)
put('C15', 41.8, 37.4, 0)       # NRST cap
put('SW1', 119.5, 37.6, 0)      # BOOT   (right edge, under the LED column)
put('SW2', 119.5, 45.4, 0)      # RESET
put('J3', 79.4, 33.0, 0)        # Tag-Connect SWD, right of the MCU (rev 0.5: its old spot holds U11)
# LEDs: neat column at the right edge
for i, (r, d) in enumerate([('R2', 'D1'), ('R3', 'D2'), ('R4', 'D3'), ('R5', 'D4'), ('R6', 'D5')]):
    y = 20.0 + i * 3.0
    put(r, 116.6, y, 0)
    put(d, 119.6, y, 180)       # cathode (pad1) on the right -> GND

# --- power ---------------------------------------------------------------------
put('D6', 14.6, 9.4, 0)         # TVS, pad1 (VBAT_IN) left
put('D7', 13.8, 14.4, 180)      # SS34, K(+12V) right? pad1=K -> rot180 puts pad1 right
put('D8', 22.0, 8.6, 180)       # VIGN -> +12V
put('R7', 20.4, 13.4, 0)
put('C16', 24.4, 13.4, 0)       # rev 0.5: 1206, 50 V
put('F1', 24.6, 16.2, 0)        # rev 0.5: logic supply PTC, then the TVS below it
put('D12', 25.7, 19.15, 0)
put('C59', 33.2, 19.0, 90)      # rev 0.5: third buck output cap
put('L1', 7.2, 19.4, 90)
put('C17', 4.4, 25.0, 90)
put('C18', 7.4, 25.0, 90)
put('U2', 14.2, 24.4, 0)        # LMR14020
put('C19', 14.2, 20.4, 0)       # boot cap
put('R8', 10.6, 29.2, 90)       # RT
put('C20', 17.6, 29.2, 90)      # SS
put('D9', 20.1, 20.4, 90)       # catch diode
put('L2', 25.45, 25.5, 270)     # 10uH, 7 x 6.6 mm (rev 0.5): on end between D9/FB and the output caps
put('R9', 20.3, 27.0, 180)      # FB top
put('C21', 20.3, 28.6, 180)
put('R10', 20.3, 30.2, 0)       # FB bottom
put('C22', 30.0, 22.6, 90)
put('C23', 30.0, 26.2, 90)
put('D10', 90.3, 52.2, 90)      # USB VBUS -> 5V, next to its J2 pin
put('U3', 13.0, 34.6, 0)        # TLS115 sensor 5V
put('C24', 7.4, 32.0, 90)
put('C25', 7.4, 37.0, 90)
put('U4', 34.6, 30.4, 90)        # AMS1117 3.3V (tab up)
put('C26', 31.0, 36.6, 90)
put('C27', 40.2, 26.0, 90)
# battery / ignition sense: 2x3 block in the gap between the AUX3 and HALL1 columns
# (J2 pin 12 is GND right below it); the ADC lines hop under the analog lanes on B.Cu
for k, (r_in, r_gnd, c_f) in enumerate([('R11', 'R12', 'C28'), ('R13', 'R14', 'C29')]):
    x = 40.1 + 1.8 * k            # room for a shared GND via between the two columns
    put(r_in, x, 47.2, 270)       # input on top, node below
    put(r_gnd, x, 49.1, 270)      # node on top, GND below
    put(c_f, x, 51.0, 270)

# --- top band: drivers ------------------------------------------------------------
put('U5', 32.17, 11.0, 90)      # ULN2003, outputs facing J1
put('U6', 46.655, 14.6, 90)     # TC4427 #1 -> IGN1/2 (OUT_A/OUT_B line up with pins 14/15)
put('U7', 51.735, 14.6, 90)     # TC4427 #2 -> IGN3/4
for k, n in enumerate(['IGN1', 'IGN2', 'IGN3', 'IGN4']):
    r = find(n + '_DRV', 'OUT_' + n)
    vert(r, hx(14 + k), 6.6, first_on_bottom=True)
put('D11', 39.2, 19.3, 0)       # rev 0.5: ULN2003 COM clamp TVS (SMA)
put('C34', 47.29, 9.6, 90)
put('C35', 52.37, 9.6, 90)
put('RN1', 48.2, 20.6, 90)
for i, n in enumerate(design.HS_OUT):
    x = hx(19 + 3 * i)
    put(f'Q{1+i}', x, 10.0, 90)                 # tab (drain) up to the header pin
    r = find(n + '_IN', 'GND')
    # pull-down beside the IN-pin lane; INJ4's and IACV's step aside for the level shifter
    rx, ry = {'INJ4': (73.6, 16.4)}.get(n, (x - 3.4, 16.6))
    vert(r, rx, ry, first_on_bottom=False)
# rev 0.5: 3.3 V -> 5 V level shifter for the low-side inputs, under Q4. Standing on end (rot 180): the MCU-side
# column (B, INJ1 at the top ... ALT, then the enable) faces left, into the bundle from the MCU's top edge, in the
# order the lines leave it; the driver-side column (A) faces right, toward Q5-Q8 (Q1-Q4 go back over the top)
put('U11', 80.0, 21.6, 180)     # B column starts below the Q2-Q4 pull-downs
put('C57', 85.0, 25.6, 0)       # VCCA (pin 1, bottom right)
put('C58', 75.9, 27.2, 0)       # VCCB (pins 23/24, bottom left)
put('R71', 78.4, 27.2, 0)       # enable pull-up (pin 22)

# --- bottom band: conditioning columns ----------------------------------------------
Y_SER, Y_PAIR, Y_PULL = 54.0, 51.6, 55.62


def column(pin, series, pair=(), pull=None):
    x = round(hx(pin) * 4) / 4          # snap to the 0.25 mm routing grid so the
                                        # node line fits between the R/C pair
    vert(series, x, Y_SER, first_on_bottom=True)
    offs = [0.0] if len(pair) == 1 else [-0.6, 0.6]
    for o, pr in zip(offs, pair):
        vert(pr, x + o, Y_PAIR, first_on_bottom=True)
    if pull:
        horiz(pull, round((x + 1.27) * 4) / 4, Y_PULL, a_left=False)


for pin, n in [(4, 'TPS'), (5, 'MAP'), (6, 'CLT'), (7, 'IAT'), (8, 'AFR'), (9, 'AUX1'),
               (10, 'AUX2'), (11, 'AUX3')]:
    pull = find('V5_SENS', 'IN_' + n) if n in ('CLT', 'IAT') else None
    if pull:
        pull = (pull[0], not pull[1])        # 'a' = IN net
    column(pin, find('IN_' + n, 'AN_' + n),
           (find('AN_' + n, 'GND', '10k'), find('AN_' + n, 'GND', '10n')), pull)
for pin, n in [(13, 'HALL1'), (14, 'HALL2')]:
    pull = find('V5_SENS', 'IN_' + n)
    column(pin, find('IN_' + n, n), (find(n, 'GND'),), (pull[0], not pull[1]))
for pin, n in [(15, 'SW1'), (16, 'SW2'), (17, 'SW3')]:
    column(pin, find('IN_' + n, n), (find(n, 'GND', '10k'), find(n, 'GND', '10n')))

# knock: series cap in its column, amp in the bottom-left corner
vert(find('IN_KNOCK', 'KN_P'), hx(3), 53.6, first_on_bottom=True)
put('U8', 12.0, 45.0, 0)
put(find('KN_P', 'KN_BIAS')[0], 15.6, 47.6, 0)
put(find('+3V3', 'KN_BIAS')[0], 8.0, 41.8, 0)
put(find('KN_BIAS', 'GND', '100k')[0], 8.0, 43.4, 0)
put(find('KN_BIAS', 'GND', '1u')[0], 8.0, 45.0, 0)
put(find('KN_OUT', 'KN_N')[0], 12.0, 41.6, 0)
put(find('KN_N', 'KN_BIAS')[0], 8.0, 46.8, 0)
put(find('KN_OUT', 'AN_KNOCK')[0], 15.6, 42.6, 0)
put(find('AN_KNOCK', 'GND')[0], 15.6, 44.4, 0)
put('C47', 12.0, 48.6, 0)       # LMV321 decoupling
# rev 0.5: hall input clamps (below the analog lanes) and the BOOT1 pull-down
put('D13', 43.48, 48.3, 270)    # straight above each hall column's filter cap, anode down
put('D14', 46.02, 48.3, 270)
put('R72', 59.7, 44.6, 90)      # in the wedge between AN_AUX3's lane and HALL1's escape

# VR: MAX9926 under the right half of the MCU, legs in their header columns
put('U9', 67.6, 46.3, 270)
for pin, n, inner in [(19, 'VR2_N', 'VR2_A'), (20, 'VR2_P', 'VR2_B'),
                      (21, 'VR1_P', 'VR1_B'), (22, 'VR1_N', 'VR1_A')]:
    x = hx(pin)
    vert(find(n, inner), x, 54.45, first_on_bottom=True)
    tgt = {'VR2_A': 'VR2_INP', 'VR2_B': 'VR2_INN', 'VR1_B': 'VR1_INN', 'VR1_A': 'VR1_INP'}[inner]
    vert(find(inner, tgt), x, 51.4, first_on_bottom=True)
vert(find('VR2_INP', 'VR2_INN'), 61.2, 46.6, first_on_bottom=True)
vert(find('VR1_INP', 'VR1_INN'), 71.8, 47.0, first_on_bottom=True)
put(find('+3V3', 'VR1_OUT')[0], 74.4, 43.4, 0)
put(find('+3V3', 'VR2_OUT')[0], 74.4, 45.0, 0)
put('C50', 74.4, 48.4, 0)       # MAX9926 VCC

# CAN transceiver above its header pins (CANL/CANH face J2)
put('U10', (hx(27) + hx(28)) / 2, 48.6, 270)
put('C56', 84.6, 46.0, 90)

# --- wideband controller block (FOME module layout, rotated so its sensor-side header row
# lands on J2 pins 33-40) + its CAN transceiver above the block's CAN pins ---------------
import wideband, wb_clean
if wb_clean.ENABLED:            # rev 0.3: block laid out in the board's own style (wb_clean.py)
    PLACE.update(wb_clean.PLACE)
else:                           # rev 0.2: the FOME module layout, transplanted
    for _r, (_x, _y, _rot, _side) in wideband.placement().items():
        PLACE[_r] = (_x, _y, _rot, _side)
    put('U106', 95.5, 22.3, 180)    # D/R pins face the block's CAN ports, CANH/CANL face left
    put('C118', 100.3, 22.3, 90)

for p in design.parts:
    if p['ref'] not in PLACE:
        print('not placed:', p['ref'])
