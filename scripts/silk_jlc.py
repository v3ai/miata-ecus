"""silk_jlc.py board.kicad_pcb: bring the silkscreen up to JLCPCB's minimums (line width 0.15 mm, text height 1.0 mm),
in place. KiCad's library footprints draw their outlines at 0.12 mm and this project's dense parts carried 0.8 mm
reference text; JLC prints those faint or not at all. Lines and arcs on the silkscreen get 0.15 mm, texts at least
1.0 mm (width the same) with 0.15 mm strokes. Run by daughter_release.sh and mb_release.sh before the fab export."""
import sys
import pcbnew

FromMM, ToMM = pcbnew.FromMM, pcbnew.ToMM
W, H = 0.15, 1.0
SILK = (pcbnew.F_SilkS, pcbnew.B_SilkS)


def fix_text(t):
    n = 0
    if ToMM(t.GetTextHeight()) < H - 1e-3 or ToMM(t.GetTextWidth()) < H - 1e-3:
        h = max(ToMM(t.GetTextHeight()), H)
        t.SetTextSize(pcbnew.VECTOR2I(FromMM(h), FromMM(h))); n += 1
    if ToMM(t.GetTextThickness()) < W - 1e-3:
        t.SetTextThickness(FromMM(W)); n += 1
    return n


def fix(board):
    lines = texts = 0
    items = list(board.GetDrawings())
    for fp in board.GetFootprints():
        items += [fp.Reference(), fp.Value()] + list(fp.GraphicalItems())
    for it in items:
        if it.GetLayer() not in SILK:
            continue
        if it.GetClass() in ('PCB_TEXT', 'FP_TEXT', 'PCB_FIELD'):
            texts += bool(fix_text(it))
        elif hasattr(it, 'GetWidth') and 0 < ToMM(it.GetWidth()) < W - 1e-3:
            it.SetWidth(FromMM(W)); lines += 1
    return lines, texts


if __name__ == '__main__':
    b = pcbnew.LoadBoard(sys.argv[1])
    l, t = fix(b)
    b.Save(sys.argv[1])
    print(f'silkscreen: {l} lines widened to {W} mm, {t} texts raised to {H} mm / {W} mm strokes')
