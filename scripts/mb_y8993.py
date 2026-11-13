"""The 1989-95 motherboard (mb_na6.py) as fitted for 1989-93, for the simulation and checking tools: the same board
and harness nets, with each jumper turned into 0R links, fitted where the 1989-93 shunts sit (mb_na6.SHUNTS)."""
import mb_na6 as base
from mb_na6 import OUTLINE, CASE_HOLES, HDR_1A, DAUGHTER, W, H, placement, CASE_NOTE, HEADER_DESC   # noqa: F401

YEAR = '1989-93'
NAME = base.NAME
TITLE = base.TITLE + ', jumpers set for 1989-93'
HARNESS = base.HARNESS


def build_parts():
    return base.year_parts(YEAR)
