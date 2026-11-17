# C102 verdict: partly (geometry true, severity overstated; also applies to ORDERED board)
Checked: evidence/cur_db and ord_db pcb_pads.csv. U1 pins 21/22 (VREF+/VDDA) pads at x=153.3, y=102.0/102.5. C11/C12 (+3V3A) pads at x=144.2, y=105.1/103.7, so about 8.5-9.5 mm away, on the far side of FB1; no cap at the pins. C3 (100n) at x=149.6, 3.7 mm from pin 19; C1/C2 similarly 3-6 mm. Pins 50/75 fine. Datasheet DS8626 p.136: "as close as possible to the chip" (qualitative, no mm figure).
Ordered: ord_db has identical C3/C11/C12/FB1/U1 coordinates, so ordered=true (the cluster's ordered:false is wrong).
Not in review brief s6 or VERIFICATION.md (grep for decoupl/VDDA found only F103 items), so it is news.
Consequence: not checked. 3-9 mm 0603 caps on a 6-layer (cur) / 4-layer (ord) board with a plane are common and typically work; the ADC-noise effect is unquantified. Severity low-medium, not a showstopper.
Fix: ordered board - solder a 100n 0402/0603 on top between pins 21/22 and GND (or bodge across pin 22 and nearby GND pin 20/ pin 10 area) if desired; cur - move C12 to pin side, ferrite upstream.
