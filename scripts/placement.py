"""Placement for the 125 x 76 mm daughterboard (mm, board origin top-left, y down).

Rev 0.9: J1 back on the top edge and the driver strip moved below it (see the end of this file); the rest unchanged.

Rev 0.8: the board grew a 16 mm strip above J1 (over empty motherboard space under the harness header on every year).
Everything below J1 keeps its rev 0.7 coordinates in this file ("the old frame": J1 at y 2.75); the strip is at
negative y in that frame, and every position is shifted down by DY at the end, so the board origin stays top-left.

Floor plan
  top strip   8x VND7NV04 (DPAK) over their J1 pins; relay switches (ZXMS6004) over J1 6-12; ignition source
              diodes and pull-down switches over J1 14-17
  top edge    J1: power in, 7 relay outs, 4 ign outs, 8 smart low-side outs
  top band    relay level shifter | 2x TC4427 + inverter | low-side level shifter, sensor 5 V tracker, +3V3 clamp
  left        power supply (TVS, reverse diode, 5V buck, 5V sensor tracker, 3.3V LDO)
  centre      STM32F407 + decoupling + crystal
  right       SWD, BOOT/RESET buttons, status LEDs, USB/CAN
  bottom band one conditioning column per J2 pin (series R, then R/C pair to GND)
  bottom edge J2: sensor inputs, VR, comms, SWD
"""
import design

DY = 16.0                      # rev 0.8: height of the strip above J1
BOARD_W, BOARD_H = 125.0, 60.0 + DY
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

# --- top strip (rev 0.8, old-frame y < 0) and top band: drivers ---------------------------------------------
# Low-side drivers: DPAK, leads up (IN right, source left), tab straight down onto its J1 pin. tab_copper.py pours
# each drain on F.Cu, In2.Cu and B.Cu over a 6.9 mm wide column with thermal vias.
Q_Y = -6.0
for i, n in enumerate(design.HS_OUT):
    x = hx(19 + 3 * i)
    put(f'Q{1+i}', x, Q_Y, 270)
    r = find(n + '_IN', 'GND')
    # pull-down right of the IN lead, above the tab gap the IN line comes up through
    vert(r, x + 3.81, -13.9, first_on_bottom=False)   # top pad 0.85 mm from the board edge
# relay / lamp / tach switches over J1 6-12, staggered (SOT-23 at 2.54 mm pitch), drain down to the pin
for i, n in enumerate(design.RELAYS):
    put(f'Q{9 + i}', hx(6 + i), -3.0 if i % 2 == 0 else -7.4, 270)
put('RN2', 29.5, -12.4, 0)
put('RN3', 37.1, -12.4, 0)
# ignition: source diode straight over each J1 pin (cathode down), pull-down switch above, staggered
for i, n in enumerate(design.IGN):
    put(f'D{31 + i}', hx(14 + i), -3.4, 90)
    put(f'Q{16 + i}', hx(14 + i), -8.6 if i % 2 == 0 else -12.6, 270)
# relay level shifter where the ULN2003 was: A port (gates) along the top facing the strip, B port (MCU) below
put('U12', 36.5, 13.2, 270)
put('C64', 41.4, 11.0, 90)
put('C65', 41.4, 18.2, 90)
put('U6', 46.655, 14.6, 90)     # TC4427 #1 -> IGN1/2 (OUT_A/OUT_B line up with pins 14/15)
put('U7', 51.735, 14.6, 90)     # TC4427 #2 -> IGN3/4
for k, n in enumerate(design.IGN):
    r = find(n + '_DRV', n + '_SRC')
    vert(r, hx(14 + k), 6.9, first_on_bottom=True)
put('C34', 47.29, 10.0, 90)
put('C35', 52.37, 10.0, 90)
put('RN1', 48.2, 20.6, 90)
# rev 0.5: 3.3 V -> 5 V level shifter for the low-side inputs. Standing on end (rot 180): the MCU-side column (B, INJ1 at
# the top ... ALT, then the enable) faces left, into the bundle from the MCU's top edge, in the order the lines leave
# it; the driver-side column (A) faces right, toward the strip
put('U11', 80.0, 21.6, 180)
put('C57', 85.0, 25.6, 0)       # VCCA (pin 1, bottom right)
put('C58', 75.9, 27.2, 0)       # VCCB (pins 23/24, bottom left)
put('R71', 78.4, 27.2, 0)       # enable pull-up (pin 22)
# rev 0.8: harness sensor 5 V tracker and the +3V3 shunt clamp in the band the SOT-223 drivers used to fill
put('U14', 62.0, 9.0, 0)
put('C61', 62.0, 13.4, 0)
put('C62', 66.4, 9.0, 90)
put('Q20', 100.6, 9.6, 0)
put('U15', 94.4, 9.4, 90)
put('R141', 94.4, 13.0, 0)
put('R142', 91.0, 8.0, 90)
put('R143', 91.0, 11.2, 90)
put('C63', 98.0, 14.0, 0)      # 100 uF bulk on +3V3 (1206), beside Q20's emitter
put('C68', 96.6, 15.9, 0)      # second 100 uF bulk on +3V3 (1206), below C63

# --- bottom band: conditioning columns ----------------------------------------------
Y_SER, Y_PAIR, Y_PULL = 54.0, 51.6, 55.62


def column(pin, series, pair=(), pull=None, y_ser=Y_SER, y_pull=Y_PULL, pull_dx=0.0):
    x = round(hx(pin) * 4) / 4          # snap to the 0.25 mm routing grid so the
                                        # node line fits between the R/C pair
    vert(series, x, y_ser, first_on_bottom=True)
    offs = [0.0] if len(pair) == 1 else [-0.6, 0.6]
    for o, pr in zip(offs, pair):
        vert(pr, x + o, Y_PAIR, first_on_bottom=True)
    if pull:
        horiz(pull, round((x + 1.27 + pull_dx) * 4) / 4, y_pull, a_left=False)
    return x


# rev 0.7: the analog series resistors and the CLT/IAT bias resistors are 0603. The series row moves up 0.2 mm and the
# bias resistors down to 55.75 so the two clear each other; IAT's bias resistor steps 0.35 mm right of CLT's.
# Each analog column's clamp (BAT54WS, SOD-323, cathode up) stands 0.75 mm right of the node line, above the pair.
CLAMP_Y = 48.9
for k, (pin, n) in enumerate([(4, 'TPS'), (5, 'MAP'), (6, 'CLT'), (7, 'IAT'), (8, 'AFR'), (9, 'AUX1'),
                              (10, 'AUX2'), (11, 'AUX3')]):
    pull = find('V5_EXT', 'IN_' + n) if n in ('CLT', 'IAT') else None
    if pull:
        pull = (pull[0], not pull[1])        # 'a' = IN net
    x = column(pin, find('IN_' + n, 'AN_' + n),
               (find('AN_' + n, 'GND', '10k'), find('AN_' + n, 'GND', '10n')), pull,
               y_ser=53.8, y_pull=55.75, pull_dx=0.35 if n == 'IAT' else 0.0)
    # AUX3's stands left of its lane: the +12V feed to the battery-sense divider runs up its right side
    # (AUX2's and AUX3's face each other: 0.6 mm off their lines so the two bodies clear)
    put(f'D{19 + k}', x + {'AUX2': 0.6, 'AUX3': -0.6}.get(n, 0.75), CLAMP_Y, 270)   # pad 1 (cathode, +3V3) up
# rev 0.7: the hall pull-ups are 0603, standing between the columns (two lying 0603s don't fit side by side on the
# 2.54 mm pitch), harness end down
for k, (pin, n) in enumerate([(13, 'HALL1'), (14, 'HALL2')]):
    pull = find(f'V5_H{k + 1}', 'IN_' + n)
    x = column(pin, find('IN_' + n, n), (find(n, 'GND'),))
    vert((pull[0], not pull[1]), x + 1.27, 55.2, first_on_bottom=True)
# rev 0.7: switch input clamps (1N4148WS). SW1's and SW2's stand between the series resistors, anode (the switch
# node) up next to the R/C pair, cathode down to a plane via; SW3's gap is taken by the VR2 conditioner (R75/R78),
# so its clamp lies below the VR parts, above J2's GND pin, anode left towards the series resistor's top
for k, (pin, n) in enumerate([(15, 'SW1'), (16, 'SW2'), (17, 'SW3')]):
    x = column(pin, find('IN_' + n, n), (find(n, 'GND', '10k'), find(n, 'GND', '10n')))
put('D27', 49.7, 53.9, 90)
put('D28', 52.2, 53.9, 90)
put('D29', 56.0, 55.2, 180)

# knock: series resistor (rev 0.7) and coupling cap in its column, amp in the bottom-left corner
vert(find('IN_KNOCK', 'KN_IN'), hx(3), 55.4, first_on_bottom=True)
vert(find('KN_IN', 'KN_P'), hx(3), 52.9, first_on_bottom=True)
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

# VR: LM2903 (rev 0.5b) under the right half of the MCU, legs in their header columns. VR2 on the left (comparator A,
# pins 1-3), VR1 on the right (comparator B, pins 5-7); each input's BAT54S clamp and bias resistors sit beside it.
put('U9', 67.0, 46.3, 0)
put('D15', 69.25, 50.8, 0)       # VR1_INP clamp
put('D16', 73.15, 50.8, 0)       # VR1_INN clamp
for i, ref in enumerate(('R73', 'R74', 'R77', 'R79', 'R80', 'C60')):   # VR1 bias, hysteresis, VR_BIAS divider
    put(ref, 68.2 + 1.15 * i, 54.0, 90)
put('D17', 56.6, 47.4, 0)        # VR2_INP clamp
put('D18', 52.6, 47.4, 0)        # VR2_INN clamp
put('R75', 55.4, 50.6, 90)       # VR2_INP bias
put('R76', 56.9, 50.6, 90)       # VR2_INN bias
put('R78', 55.4, 53.3, 90)       # VR2 hysteresis
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
put('C50', 71.8, 43.4, 90)      # LM2903 VCC, next to pin 8

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

# rev 0.8 protection parts, at free spots found next to the parts they serve (old frame: y - DY)
put('U13', 42.9, 37.65 - DY, 0)
put('D35', 41.4, 69.9 - DY, 90)        # hall pull-up diodes, common anode
put('D38', 36.15, 62.75 - DY, 0)       # AN_VBATT clamp (clear of the analog fan lanes)
put('R139', 76.25, 52.1 - DY, 90)       # UART TX series
put('C67', 79.75, 60.6 - DY, 180)      # U10 VCC
put('C122', 96.7, 43.0 - DY, 0)        # U106 VCC
put('F2', 103.75, 70.45 - DY, 0)       # LSU VM wire PTC
put('D41', 93.6, 66.1 - DY, 0)         # Vm drive clamp
put('C66', 45.65, 34.8 - DY, 180)      # U13
put('R140', 74.8, 45.45 - DY, 0)      # UART RX series
put('D40', 99.55, 57.65 - DY, 180)     # pump drive clamp
put('D39', 42.15, 57.9 - DY, 0)        # AN_VIGN clamp (clear of the analog fan lanes)
put('D36', 74.0, 50.5 - DY, 0)       # UART TX clamp
put('D37', 74.0, 47.5 - DY, 0)        # UART RX clamp

put('R144', 45.9, 15.7 - DY, 0)   # ignition output pull-down
put('R145', 50.2, 15.85 - DY, 180)   # ignition output pull-down
put('R146', 54.5, 15.85 - DY, 0)   # ignition output pull-down
put('R147', 53.55, 8.2 - DY, 90)   # ignition output pull-down
# rev 0.8: shift the whole old frame down by the strip's height
for _r, _v in list(PLACE.items()):
    PLACE[_r] = (_v[0], round(_v[1] + DY, 4)) + tuple(_v[2:])

# rev 0.9: J1 and the top holes back at the top edge (their rev 0.7 places), and the driver strip below J1 instead of
# above it: every strip part is reflected about the middle of the 16 mm band (y -> STRIP_FLIP - y) and turned 180 deg,
# so each DPAK's tab still faces its own J1 pin, now from below, and its leads face the level shifters. Everything else
# keeps its rev 0.8 place.
STRIP_FLIP = 21.5               # rev 0.8 strip y 0..16 -> rev 0.9 y 5.5..21.5; J1 18.75 -> 2.75
J1_Y, J2_Y = 2.75, 57.25 + DY
HOLES = [(4.5, 4.5), (120.5, 4.5), (4.5, 55.5 + DY), (120.5, 55.5 + DY)]
STRIP = [r for r, v in PLACE.items() if v[1] < 16.5 and not r.startswith('H') and r != 'J1']
for _r in STRIP:
    _v = PLACE[_r]
    PLACE[_r] = (_v[0], round(STRIP_FLIP - _v[1], 4), (_v[2] + 180) % 360) + tuple(_v[3:])
put('J1', hx(1), J1_Y, 90)
for i, (x, y) in enumerate(HOLES):
    put(f'H{1+i}', x, y)

# rev 0.9: nudges to JLCPCB's recommended part-to-part spacing (scripts/jlc_spacing.py), mm, applied on the routed
# board with scripts/nudge_part.py and recorded here so a rebuild places the parts the same way
NUDGE = {
    'R144': (-0.12, 0.0),
    'R146': (0.12, 0.0),
    'F2': (0.07, 0.0),
    'RN1': (0.12, 0.0),
    'U13': (-0.05, 0.0),
    'C67': (0.0, -0.16),
    'C5': (0.0, 0.24),
    'C2': (0.0, -0.22),
    'C35': (0.0, -0.03),
    'C66': (0.0, -0.03),
    'C34': (0.0, -0.03),
    'D30': (0.0, 0.47),
    'U106': (0.0, -0.5),
    'C122': (0.0, -0.25),
    'C118': (0.0, -0.5),
}
for _r, (_dx, _dy) in NUDGE.items():
    _v = PLACE[_r]
    PLACE[_r] = (round(_v[0] + _dx, 4), round(_v[1] + _dy, 4)) + tuple(_v[2:])

# rev 0.10 (final frame): microSD socket in the free area right of Q20, card slot toward the right board edge
put('J4', 113.0, 28.0, 270)
put('C69', 103.4, 26.0, 90)
put('C70', 103.4, 30.0, 90)
put('R150', 103.4, 33.0, 0)
put('R151', 107.0, 35.6, 0)

for p in design.parts:
    if p['ref'] not in PLACE:
        print('not placed:', p['ref'])
