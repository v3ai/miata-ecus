"""Shared bits for the 1996-2005 motherboards: same building blocks as the NA boards, a different
harness header, and (until a stock case is measured) the NA case outline as a stand-in."""
import mb_common as C
import mb_na6 as NA

OUTLINE, CASE_HOLES, W, H, DAUGHTER = NA.OUTLINE, NA.CASE_HOLES, NA.W, NA.H, NA.DAUGHTER
CASE_NOTE_PROVISIONAL = (
    '**PROVISIONAL.** No source gives this case\'s board outline and mounting holes yet (the open-source boards for '
    'these years either use their own enclosure or a different Mazda case). Until a stock board or case is measured, '
    'this board uses the NA case outline and holes as a stand-in, with the header centred on the top edge. Moving to '
    'the real outline is a change of OUTLINE / CASE_HOLES / HDR_1A in the year module plus an automatic reroute. '
    '**Do not order this board before the case is measured.**')


def build(header_fp, header_value, header_desc, harness, fuses=(), holes=None):
    """parts for a year board: header, case holes, the common I/O, optional fused 12 V feeds"""
    C.parts.clear()
    C.add('J1', header_value, header_fp, '', harness, header_desc)
    for ref in (holes or CASE_HOLES):
        C.add(ref, 'M4', 'ecu_mb:MountingHole_M4_4.5mm_Pad7', '', {1: 'GND'}, 'Case mounting boss, M4 x 10')
    C.common_parts()
    for ref, net, desc in fuses:
        C.add(ref, '2A hold', 'Fuse:Fuse_1812_4532Metric', 'C46641168', {1: 'VBAT_IN', 2: net},
              f'Resettable fuse, {desc} (R+O SMD1812-200-30: 2 A hold, 30 V)')
    return C.parts


def place(hdr_1a, fuses=()):
    P = NA.placement()
    P['J1'] = (hdr_1a[0], hdr_1a[1], 0)
    for k, ref in enumerate(fuses):
        P[ref] = (8.0, 30.0 + 7.0 * k, 90)
    return P
