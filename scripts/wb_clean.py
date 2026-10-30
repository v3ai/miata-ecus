"""Wideband controller block, laid out in the daughterboard's own style (rev 0.3).

Same circuit and parts as the FOME / rusEFI wideband module (wideband.py: refs = module refs + 100),
but placed fresh on the board's grid instead of transplanting the module's layout: every part at 0 / 90 deg,
functional groups next to the IC pins they serve, and the board router wires it like the rest of the board.
The heater path (VND14NV04 low side to J2 37-40) is hand-planned 1 mm copper.

Floor plan (board mm, y down; J2 LSU pins 33-40 at x 94.28 .. 112.06, y 57.25):
  top      CAN transceiver U106 above the MCU's CAN pins; SWD Tag-Connect J102 underneath (B side)
  middle   U102 STM32F042 at 90 deg: analog inputs face down, ESR drives / LEDs / BOOT0 face left,
           heater PWM + battery sense face right
  bottom   analog front end (U101 quad op-amp, U105 current sense, REF3033) over J2 33-36;
           heater switch Q101 over J2 37-40
"""

ENABLED = True

# ref: (x, y, rot, side).  2-pin parts: rot 0 = pad 1 left, 180 = pad 1 right, 90 = pad 1 down, 270 = pad 1 up
PLACE = {
    # --- MCU, CAN transceiver above its CAN pins, SWD Tag-Connect on the back
    'U102': (100.5, 32.5, 90, 'F'),
    'U106': (96.0, 23.0, 90, 'F'),
    'C118': (99.4, 23.0, 90, 'F'),
    'J102': (108.5, 23.0, 0, 'B'),
    'C113': (103.3, 25.9, 90, 'F'),
    'C110': (105.6, 25.9, 90, 'F'),
    # under the MCU's bottom row: +3V3 / NRST / VDDA decoupling
    'C112': (97.3, 39.6, 270, 'F'),
    'C116': (98.8, 39.9, 270, 'F'),
    'C109': (100.9, 39.6, 270, 'F'),
    # left column: ESR drive resistors, BOOT0 pull-down; status LEDs further left
    'R116': (93.6, 30.3, 0, 'F'),
    'R119': (93.6, 31.3, 0, 'F'),
    'R106': (93.6, 33.7, 0, 'F'),
    'R129': (93.6, 35.0, 0, 'F'),
    'D103': (89.6, 30.4, 0, 'F'), 'R113': (86.9, 30.4, 0, 'F'),
    'D102': (89.6, 32.2, 0, 'F'), 'R130': (86.9, 32.2, 0, 'F'),
    # right column: battery sense divider, heater PWM pull-down and heater LED
    'R120': (107.4, 29.2, 180, 'F'),
    'R121': (107.4, 30.4, 0, 'F'),
    'C106': (107.4, 31.6, 0, 'F'),
    'R126': (107.4, 33.0, 180, 'F'),
    'R127': (107.4, 34.2, 180, 'F'), 'D101': (110.1, 34.2, 180, 'F'),
    # --- analog: 3.3 V reference (left), quad op-amp, current-sense amp (right)
    'U103': (90.4, 41.4, 90, 'F'),
    'C108': (88.2, 41.4, 90, 'F'), 'C117': (87.0, 41.4, 90, 'F'),
    'C107': (92.6, 41.4, 270, 'F'),
    'U101': (96.0, 46.6, 180, 'F'),
    # U101 left side (pins 8-14: UN_BUF, LSU_UN, GND, VM_REF, VM)
    'R114': (90.6, 44.6, 180, 'F'),
    'R101': (90.6, 45.8, 180, 'F'), 'R102': (90.6, 47.0, 0, 'F'), 'C101': (90.6, 48.2, 0, 'F'),
    # U101 right side (pins 7..1 top to bottom: UN_SENSE, UN_N, UN_P, +3V3, PUMP_P, PUMP_N, PUMP).
    # Feedback parts stand vertically across the two pins they join (R107: pins 7-6, R133 + C103: pins 2-1);
    # the middle pins run straight out to R105 / R104 (UN_P) and R132 / R134 (PUMP_P).
    'R107': (100.35, 44.82, 90, 'F'),
    'R133': (100.35, 48.33, 90, 'F'), 'C103': (101.45, 48.33, 90, 'F'),
    'C105': (98.0, 42.1, 0, 'F'),       # U101 +3V3 decoupling, in the open row above it
    'R105': (104.0, 45.95, 0, 'F'), 'R104': (104.0, 44.75, 180, 'F'),
    'R132': (104.0, 47.25, 0, 'F'), 'R134': (104.0, 48.45, 180, 'F'),
    'R103': (101.4, 43.2, 180, 'F'),
    'R131': (104.0, 49.65, 180, 'F'),
    # current-sense amp right of the MCU; output filter R124 / C111 at the MCU's Ip-sense pin
    'U105': (109.0, 39.0, 0, 'F'),
    'R124': (105.6, 38.3, 180, 'F'), 'C111': (104.0, 39.5, 270, 'F'),
    'R117': (109.0, 36.4, 0, 'F'),
    'R115': (107.0, 41.6, 180, 'F'),
    'C114': (112.0, 38.05, 0, 'F'),
    # between U101 and J2 33-36: LSU-side parts over their sensor pins
    'C102': (94.28, 53.4, 90, 'F'),
    'R108': (97.0, 51.6, 90, 'F'),
    'R109': (99.4, 51.4, 90, 'F'), 'C104': (100.6, 51.4, 90, 'F'),
    'R110': (99.4, 54.4, 0, 'F'),
    'R111': (102.4, 51.6, 90, 'F'), 'R112': (103.6, 51.6, 90, 'F'),
    # --- heater switch over J2 37-40: leads down, source straight onto pin 40, gate resistor beside the gate
    'Q101': (109.78, 47.5, 90, 'F'),
    'R125': (105.2, 52.6, 180, 'F'),
}
PLACE = {k: v for k, v in PLACE.items() if v}

# Heater path, 1 mm, hand-planned (net, layer, width, points). The drain leaves the tab straight down between
# the gate and source leads and jogs under the gate onto J2 38; the source lead sits right over J2 40.
# J2 37/38 and 39/40 are paired on the bottom layer.
HEATER = [
    ('LSU_HTR_N', 'F', 1.0, [(109.78, 48.5), (109.78, 53.9), (108.28, 55.4), (106.98, 55.4), (106.98, 57.25)]),
    ('LSU_HTR_N', 'B', 1.0, [(104.44, 57.25), (106.98, 57.25)]),
    ('HTR_GND', 'F', 1.0, [(112.06, 52.6), (112.06, 57.25)]),
    ('HTR_GND', 'B', 1.0, [(109.52, 57.25), (112.06, 57.25)]),
]
# thin taps onto wide nets: (ref, pad) -> width
TAPS = {('R120', '1'): 0.25}       # battery sense divider on the 1 mm VBAT_IN net
# LED function labels on the silkscreen: ref -> (text, dx, dy) from the LED centre (dx > 0: left-aligned text)
LED_LABELS = {'D101': ('HTR', 1.8, 0.0), 'D102': ('OK', 0.0, 1.5), 'D103': ('ACT', 0.0, -1.5)}
# reference text positions (board mm, angle) where the footprint default would sit on copper or another label
REF_POS = {'U102': (100.5, 32.5, 0), 'U105': (110.0, 41.5, 0), 'U103': (90.4, 38.9, 90)}
