"""MPX5700AP (NXP case 867B-04, unibody, single pressure port) lying flat, leads bent 90 deg down.

Body geometry: NXP 867-family table (overall length 29.08-29.85, width 17.40-18.16, mounting-hole spacing
0.910 in = 23.11 BSC, part holes 3.89-4.04) and a photo of the part scaled by its 2.54 mm lead pitch
(lozenge = hull of an 8.85 mm-radius centre and 3.3 mm-radius ears; one barb, 11 mm long, its axis 4.0 mm
from the centre line toward pin 6). Pin 1 is the notched lead. Fitted marking side up, so pin 1 is on
the left with the leads toward the viewer; the port then leaves the far edge.
Footprint frame (unchanged from the earlier 867C footprint, so placements still hold): holes on y = 3.81,
pins on y = 16.51 at 2.54 mm pitch centred on x = 0, body toward -y.
"""
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mb', 'ecu_mb.pretty', 'MPX5700AP_867B_Flat.kicad_mod')
YC = 3.81                    # body centre line (through both mounting holes)
HX = 23.11 / 2               # hole half-spacing
R_BODY, R_EAR = 8.85, 3.3
PORT_X = 4.0                 # barb axis, toward pin 6 (+x)
PIN_Y = 16.51

body = unary_union([Point(0, YC).buffer(R_BODY, 64), Point(-HX, YC).buffer(R_EAR, 32),
                    Point(HX, YC).buffer(R_EAR, 32)]).convex_hull
edge = YC - (R_BODY ** 2 - PORT_X ** 2) ** 0.5          # body edge on the port axis
# barb: collar, neck, then a cone from 4.6 mm down to 3.4 mm at the tip
port = Polygon([(PORT_X - 2.0, edge + 0.5), (PORT_X - 2.0, edge - 1.0), (PORT_X - 1.65, edge - 1.0),
                (PORT_X - 1.65, edge - 4.5), (PORT_X - 2.3, edge - 4.5), (PORT_X - 1.7, edge - 11.0),
                (PORT_X + 1.7, edge - 11.0), (PORT_X + 2.3, edge - 4.5), (PORT_X + 1.65, edge - 4.5),
                (PORT_X + 1.65, edge - 1.0), (PORT_X + 2.0, edge - 1.0), (PORT_X + 2.0, edge + 0.5)])
leads = box(-6.35 - 1.0, YC, 6.35 + 1.0, PIN_Y + 1.0)
crt = unary_union([body, port, leads]).buffer(0.25, join_style=2).simplify(0.05)


def pts(poly):
    return ' '.join(f'(xy {x:.3f} {y:.3f})' for x, y in list(poly.exterior.coords)[:-1])


def poly(p, layer, w):
    return f'  (fp_poly (pts {pts(p)}) (stroke (width {w}) (type solid)) (fill none) (layer "{layer}"))'


port_out = port.difference(body)          # silk: only the part of the barb beyond the body
o = ['(footprint "MPX5700AP_867B_Flat" (version 20221018) (generator pcbnew) (layer "F.Cu")',
     '  (descr "NXP MPX5700AP / GP, case 867B (single port), lying flat, leads bent 90 deg, 2x M3. Marking side up.")',
     '  (tags "pressure sensor MAP unibody 867B")', '  (attr through_hole)',
     '  (fp_text reference "U2" (at -6.0 9.6) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
     '  (fp_text value "MPX5700AP" (at 0 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))',
     '  (fp_text user "MPX5700AP" (at 0 2.6) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
     '  (fp_text user "marking up" (at 0 5.0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
     poly(body, 'F.SilkS', 0.15), poly(body, 'F.Fab', 0.1), poly(crt, 'F.CrtYd', 0.05)]
for g in getattr(port_out, 'geoms', [port_out]):
    o.append(poly(g, 'F.SilkS', 0.15))
o.append(poly(port, 'F.Fab', 0.1))
for x in (-HX, HX):
    o.append(f'  (pad "" thru_hole circle (at {x:.4f} {YC}) (size 4.0 4.0) (drill 3.3) (layers "*.Cu" "*.Mask"))')
for k in range(6):
    shape = 'rect' if k == 0 else 'circle'
    o.append(f'  (pad "{k + 1}" thru_hole {shape} (at {-6.35 + 2.54 * k:.2f} {PIN_Y}) (size 1.524 1.524) (drill 0.8128) (layers "*.Cu" "*.Mask"))')
o.append(')')
open(OUT, 'w').write('\n'.join(o) + '\n')
print('wrote', OUT, 'body', [round(v, 2) for v in body.bounds], 'port tip y', round(edge - 11.0, 2))
