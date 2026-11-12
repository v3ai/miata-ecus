"""1994-1995 Miata (NA8, BP 1.8) motherboard.

Same stock case and the same 48-pin TE 174917-6 header as 1990-93 (the microRusEFI NA PnP
board fits both), so outline, holes and placement are shared with mb_na6. Only the
harness pin functions differ (rusEFI "Mazda Miata 1994" pinout; its plug 2 = 2A-2Z).
"""
import mb_na6 as base
from mb_na6 import OUTLINE, CASE_HOLES, HDR_1A, DAUGHTER, W, H, placement

NAME = 'miata_mb_9495'
TITLE = 'Miata ECU motherboard 1994-1995 (NA8)'

BASES = ['mb_na6']
CASE_NOTE = base.CASE_NOTE
HEADER_DESC = base.HEADER_DESC
CHANGES = ["Rev 0.9, for daughterboard rev 0.9: the daughterboard sits 16 mm lower, centred on the board (42 mm from the top, as up to rev 0.7), with its J1 on its top edge again: JD1 and the upper standoffs HD1/HD2 are back at their rev 0.7 places, JD2, the lower standoffs HD3/HD4, the AUX header J5 (with F4 beside it) and the parts placed against JD2 (CAN termination R1/R6, pull-up options) are 16 mm lower, and the board is routed again. Not compatible with a rev 0.8 daughterboard.", "Rev 0.8, for daughterboard rev 0.8: the harness's sensor 5 V (2K) and the AUX header pin J5-14 now come from the daughterboard's protected 5 V (V5_EXT, JD1 pin 13, which was a ground pin): a sensor 5 V wire shorted to the battery no longer back-feeds the MAP sensor and the ECU's own 5 V. The MAP sensor keeps its own supply (V5_SENS). The daughterboard outline on the silkscreen is 16 mm taller (125 x 76 mm): its new strip of output drivers overhangs the free area above JD1.",
           "Rev 0.7: LSU heater fuse F1 is a 3 A hold PTC (LUTE 2920L300/30GR, 30 V, 2920 size) instead of the 2 A 1812 part. A cold LSU 4.9 heater draws 1.6-2.3 A rms at the start of the wideband's warm-up, more than the old fuse holds once warm, so it could trip and the controller time out. No 1812 PTC holds 3 A above 8 V.",
           'Rev 0.6: freewheel diode D1 on the idle valve and D2 on the purge solenoid (2X) to its +12 V feed (the PWM turn-off energy no longer goes into the daughterboard driver); F4 resettable fuse on the AUX +12 V pin J5-15; not-fitted 12 V pull-up options R20-R22 for the VSS / A/C / clutch inputs.',
           'Rev 0.5: IAT source is now a removable jumper (JP1, 1x3 2.54 mm header + shunt) instead of the R4 / R5 0R links: shunt on EXT (default) reads the IAT connector J3, on STOCK the stock harness sensor; labelled on the silkscreen.',
           'Rev 0.4: MAP sensor is now the MPX5700AP (absolute, case 867B, one barb; LCSC C90152) instead of the MPX5700DP: new footprint with the real lozenge body and offset barb, holes on the NXP 23.11 mm spacing with 3.3 mm M3 clearance drills.',
           'Rev 0.3: first release, from the 89-93 rev 0.3 template: same case, outline, holes and 48-pin header; 94-95 pin map '
           '(rusEFI "Mazda Miata 1994" page and the Hellen NA6/94 connector map).']
VERIFY = ['The case geometry, as for 89-93: one stock case with calipers.',
          '1C (VIO): the starter (START) signal, live only while cranking (Link\'s MX5 pinout: "Start Signal"; the rusEFI 1990 page calls it ignition-on). It is only an input here (diode-isolated on the daughterboard), and the firmware does not use it as ignition sense (2026-11-12).',
          'LCSC stock for the extended parts (C124412, C127367, C587650, C3020560, C410772, C46641168, C3406).']
HARNESS = dict(base.HARNESS)
HARNESS.update({
    '1N': '',            # 94-95: to the AT control unit - never drive the 5 V reference here
    '1R': '',            # 94-95: not the fan any more (fan relay is 1L)
    '1C': 'VIGN_IN',     # VIO: starter (START) signal, battery only while cranking (input only; not used as ignition sense)
    '2N': 'IN_AUX2',     # heated O2 sensor (narrowband)
    '2O': 'IN_AUX3',     # air flow meter signal (vane AFM; rusEFI's 1994 page calls it MAF)
    '2P': 'HARN_IAT',    # intake air thermosensor in the AFM (IAT jumper JP1 on STOCK to use it)
    '1D': '',            # data link connector
    '1F': '',            # spare analog in the stock ECU
    '1I': '',            # AT control unit
    '1K': '',            # MT only (unclear on the stock diagram)
    '1L': 'OUT_FAN',     # radiator fan relay
    '1M': 'IN_SW1',      # vehicle speed sensor
    '1N': '',            # AT control unit
    '1Q': 'IN_SW2',      # A/C pressure switch
    '1V': 'IN_SW3',      # clutch switch (MT) / AT control unit
    '2H': '',            # data link connector
    '2J': '',            # EGR function sensor
    '2L': 'IN_AUX1',     # electrical load (rear defroster) -> idle up
    '2M': 'IN_TPS',      # throttle position sensor (0-5 V)
    '2R': 'OUT_ALT',     # pressure regulator control solenoid (generic low side)
    '2S': 'OUT_LS7',     # condenser fan relay
    '2U': 'OUT_INJ1',    # injector No.1 (94-95: one wire per injector, sequential)
    '2V': 'OUT_INJ2',    # injector No.2
    '2Y': 'OUT_INJ3',    # injector No.3
    '2Z': 'OUT_INJ4',    # injector No.4
})


def build_parts():
    return base.build_parts(HARNESS, paired_injectors=False, idle_pullup=False, tps_links=False)   # 94-95: one wire per injector
