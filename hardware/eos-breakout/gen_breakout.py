#!/usr/bin/python3
"""Generate the Enhanced Options Slot breakout board (KiCad 10, pcbnew API).

Run with the system Python that ships the pcbnew module:

    /usr/bin/python3 gen_breakout.py

Writes eos-breakout.kicad_pcb next to this script.

The board carries the original Compaq 2x25 1.27 mm right-angle receptacle
(desoldered from the modem's J4 position) and fans it out to a 2x25 2.54 mm
header. It is drawn as seen from the modem's TOP side; the receptacle body
mounts on the BOTTOM side, as on the modem.

Layout rules that make this routable on two layers without running traces
between 1.27 mm pads:
  - odd pins (row farther from the edge) leave upward on F.Cu and fan out
    to the lower header row;
  - even pins (row nearer the edge) leave downward into the 2 mm strip
    between the pads and the board edge, run out past the ends of the
    connector, go up the sides and over the top of the header, and drop
    onto the upper header row.
"""
import os
import sys
import pcbnew
from pcbnew import FromMM, VECTOR2I

HERE = os.path.dirname(os.path.abspath(__file__))

# Two variants:
#   (default)  rev A, 2 layers. Even-pin traces are 0.12 mm with 0.115 mm
#              gaps, so it needs a fab with 0.10 mm trace/space capability.
#   oshpark    rev B, 4 layers. Spreads the even-pin escape over four
#              layers so everything meets OSH Park's 4-layer rules
#              (5 mil trace/space, 15 mil board-edge keepout) with margin.
VARIANT = sys.argv[1] if len(sys.argv) > 1 else "2layer"
assert VARIANT in ("2layer", "oshpark"), VARIANT
FOUR = VARIANT == "oshpark"
NAME = "eos-breakout-oshpark" if FOUR else "eos-breakout"
REV = "B" if FOUR else "A"
OUT = os.path.join(HERE, NAME + ".kicad_pcb")

# ---------------------------------------------------------------- geometry
X1 = 50.0            # x of slot pins 1/2 (column 0)
Y_EDGE = 100.0       # mating (bottom) edge of the board
EDGE_TO_ROW = 2.55   # measured on the modem: edge to nearest hole row
P = 1.27             # receptacle pitch, both directions
Y_EVEN = Y_EDGE - EDGE_TO_ROW      # even pins: row nearest the edge
Y_ODD = Y_EVEN - P                 # odd pins: row farther from the edge
SLOT_DRILL, SLOT_PAD = 0.65, 1.0

HP = 2.54            # header pitch
H1 = X1              # header column 0 sits above slot column 0
HDR_DRILL, HDR_PAD = 1.0, 1.7

W_ODD = 0.25         # odd-pin trace width
W_EVEN = 0.16 if FOUR else 0.12   # even-pin trace width (limited by the edge strip)

# odd fan-out: one horizontal level per column, column 24 lowest
FAN_Y0 = Y_ODD - 0.98        # level of column 24
FAN_PITCH = 0.5
Y_HDR_ODD = FAN_Y0 - FAN_PITCH * 23 - 2.2    # lower header row (odd pins)
Y_HDR_EVEN = Y_HDR_ODD - HP                  # upper header row (even pins)

# even escape: lanes in the strip between the even row and the edge
LANE_Y0 = Y_EVEN + SLOT_PAD / 2 + (0.30 if FOUR else 0.25)
LANE_PITCH = 0.36 if FOUR else 0.235
CH_PITCH = 0.4 if FOUR else 0.3   # spacing once out of the strip
MAX_LANES = 4 if FOUR else 7           # per layer, per exit direction
X_CH_LEFT = X1 - 1.6         # first vertical channel left of the connector
X_CH_RIGHT = H1 + HP * 24 + HDR_PAD / 2 + 0.6
TOP_Y0 = Y_HDR_EVEN - HDR_PAD / 2 - 0.45     # first lane above the header

X_LEFT = X1 - 5.5
RIGHT_LANES = 3 if FOUR else 6
X_RIGHT = X_CH_RIGHT + CH_PITCH * (RIGHT_LANES - 1) + 1.0
Y_TOP = TOP_Y0 - CH_PITCH * (MAX_LANES - 1) - 8.4   # room for the even-pin labels

# Signal names: 486c manual pin numbers, functions per the LTE Lite guide.
NAMES = {
    1: "GND", 2: "D0", 3: "D1", 4: "D2", 5: "D3", 6: "D4", 7: "D5", 8: "D6",
    9: "D7", 10: "CS-", 11: "IOW-", 12: "IOR-", 13: "IRQA", 14: "RDY-",
    15: "+5V", 16: "+5V", 17: "RST", 18: "A0", 19: "A1", 20: "A2",
    21: "CLK", 22: "RSV", 23: "WAKE-", 24: "SLTON", 25: "SPK", 26: "GND",
    27: "GND", 28: "DMA", 29: "D15", 30: "D14", 31: "D13", 32: "D12",
    33: "D11", 34: "D10", 35: "D9", 36: "D8", 37: "A3", 38: "A4", 39: "A5",
    40: "A6", 41: "A7", 42: "A8", 43: "A9", 44: "SDMA-", 45: "TC",
    46: "IRQB", 47: "IO16-", 48: "DRQ", 49: "IOEN-", 50: "DAK",
}

# ------------------------------------------------------------------ board
board = pcbnew.BOARD()
board.SetCopperLayerCount(4 if FOUR else 2)
ds = board.GetDesignSettings()
ds.m_TrackMinWidth = FromMM(0.10)
ds.m_MinClearance = FromMM(0.10)
ds.m_ViasMinAnnularWidth = FromMM(0.15)
ds.m_CopperEdgeClearance = FromMM(0.25)
ds.m_MinThroughDrill = FromMM(0.3)
ds.m_HoleToHoleMin = FromMM(0.25)
ds.m_HoleClearance = FromMM(0.20)
ds.m_SolderMaskExpansion = FromMM(0.04)
ds.m_SolderMaskMinWidth = FromMM(0.0)
try:
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(FromMM(0.105))
    nc.SetTrackWidth(FromMM(W_ODD))
except Exception as exc:  # API differences between versions
    print("netclass setup skipped:", exc)

F, B = pcbnew.F_Cu, pcbnew.B_Cu


def pt(x, y):
    return VECTOR2I(FromMM(x), FromMM(y))


nets = {}
for n in range(1, 51):
    net = pcbnew.NETINFO_ITEM(board, f"P{n:02d}_{NAMES[n]}")
    board.Add(net)
    nets[n] = net


def track(n, layer, width, points):
    for a, b in zip(points, points[1:]):
        if a == b:
            continue
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pt(*a))
        t.SetEnd(pt(*b))
        t.SetWidth(FromMM(width))
        t.SetLayer(layer)
        t.SetNet(nets[n])
        board.Add(t)


def set_pad_size(pad, sx, sy):
    try:
        pad.SetSize(pcbnew.F_Cu, pt(sx, sy))
    except TypeError:
        pad.SetSize(pt(sx, sy))


def set_pad_shape(pad, shape):
    try:
        pad.SetShape(pcbnew.F_Cu, shape)
    except TypeError:
        pad.SetShape(shape)


def footprint(ref, value, x, y):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(pt(x, y))
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    board.Add(fp)
    return fp


def add_pad(fp, n, x, y, drill, size, square=False):
    pad = pcbnew.PAD(fp)
    pad.SetNumber(str(n))
    pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    set_pad_shape(pad, pcbnew.PAD_SHAPE_RECT if square else pcbnew.PAD_SHAPE_CIRCLE)
    set_pad_size(pad, size, size)
    pad.SetDrillSize(pt(drill, drill))
    pad.SetLayerSet(pad.PTHMask())
    pad.SetPosition(pt(x, y))
    pad.SetNet(nets[n])
    fp.Add(pad)


def slot_xy(n):
    col = (n - 1) // 2
    return X1 + P * col, (Y_ODD if n % 2 else Y_EVEN)


def hdr_xy(n):
    col = (n - 1) // 2
    return H1 + HP * col, (Y_HDR_ODD if n % 2 else Y_HDR_EVEN)


j1 = footprint("J1", "Compaq EOS receptacle 2x25 P1.27 (body on bottom side)",
               X1 + P * 12, (Y_ODD + Y_EVEN) / 2)
j2 = footprint("J2", "Header 2x25 P2.54", H1 + HP * 12, (Y_HDR_ODD + Y_HDR_EVEN) / 2)
for n in range(1, 51):
    add_pad(j1, n, *slot_xy(n), SLOT_DRILL, SLOT_PAD, square=(n == 1))
    add_pad(j2, n, *hdr_xy(n), HDR_DRILL, HDR_PAD, square=(n == 1))

# ----------------------------------------------------- odd pins: F.Cu fan
for col in range(25):
    n = 2 * col + 1
    sx, sy = slot_xy(n)
    hx, hy = hdr_xy(n)
    if col == 0:
        track(n, F, W_ODD, [(sx, sy), (hx, hy)])
        continue
    level = FAN_Y0 - FAN_PITCH * (24 - col)
    track(n, F, W_ODD, [(sx, sy), (sx, level), (hx, level), (hx, hy)])

# ------------------------------------- even pins: strip, sides, over the top
# Left group: columns 0..12, exit left. Right group: columns 13..24, exit right.
# Within a group and layer, the column nearest the exit takes the lane nearest
# the pads and the innermost channel, which keeps every layer planar.
def route_even(cols, layer, side):
    for k, col in enumerate(cols):
        n = 2 * col + 2
        sx, sy = slot_xy(n)
        hx, hy = hdr_xy(n)
        lane = LANE_Y0 + LANE_PITCH * k
        xc = (X_CH_LEFT - CH_PITCH * k) if side == "L" else (X_CH_RIGHT + CH_PITCH * k)
        top = TOP_Y0 - CH_PITCH * k
        track(n, layer, W_EVEN,
              [(sx, sy), (sx, lane), (xc, lane), (xc, top), (hx, top), (hx, hy)])


LAYERS = [B, F, pcbnew.In1_Cu, pcbnew.In2_Cu] if FOUR else [B, F]
left = list(range(0, 13))            # nearest the left exit first
right = list(range(24, 12, -1))      # nearest the right exit first
for li, layer in enumerate(LAYERS):
    lcols = left[li::len(LAYERS)]
    rcols = right[li::len(LAYERS)]
    assert len(lcols) <= MAX_LANES and len(rcols) <= MAX_LANES
    route_even(lcols, layer, "L")
    route_even(rcols, layer, "R")

# ---------------------------------------------------------------- outline
def edge(a, b):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pt(*a))
    s.SetEnd(pt(*b))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(FromMM(0.1))
    board.Add(s)


corners = [(X_LEFT, Y_TOP), (X_RIGHT, Y_TOP), (X_RIGHT, Y_EDGE), (X_LEFT, Y_EDGE)]
for a, b in zip(corners, corners[1:] + corners[:1]):
    edge(a, b)

# ------------------------------------------------------------- silkscreen
def text(s, x, y, layer=pcbnew.F_SilkS, size=0.9, angle=0, just="C", thick=0.15):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(pt(x, y))
    t.SetLayer(layer)
    t.SetTextSize(pt(size, size))
    t.SetTextThickness(FromMM(thick))
    t.SetTextAngle(pcbnew.EDA_ANGLE(angle, pcbnew.DEGREES_T))
    t.SetHorizJustify({"L": pcbnew.GR_TEXT_H_ALIGN_LEFT,
                       "C": pcbnew.GR_TEXT_H_ALIGN_CENTER,
                       "R": pcbnew.GR_TEXT_H_ALIGN_RIGHT}[just])
    t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    board.Add(t)


for col in range(25):
    x = H1 + HP * col
    odd, even = 2 * col + 1, 2 * col + 2
    # reading bottom-to-top; odd names hang below the header, even names above
    text(f"{odd} {NAMES[odd]}", x, Y_HDR_ODD + HDR_PAD / 2 + 0.5, angle=90, just="R")
    text(f"{even} {NAMES[even]}", x, TOP_Y0 - CH_PITCH * (MAX_LANES - 1) - 0.6, angle=90, just="L")

text("1", X1 - 1.3, Y_ODD, size=0.8)
text("2", X1 - 1.3, Y_EVEN + 0.1, size=0.8)
text("49", X1 + P * 24 + 1.7, Y_ODD, size=0.8)
text("50", X1 + P * 24 + 1.7, Y_EVEN + 0.1, size=0.8)
text(f"COMPAQ EOS BREAKOUT  REV {REV}", X1 + P * 24 + 4.0, Y_ODD - 0.2,
     size=0.8, thick=0.13, just="L")
text("TOP SIDE - RECEPTACLE ON BOTTOM", X1 + P * 24 + 4.0, Y_EVEN + 0.1,
     size=0.8, thick=0.13, just="L")

text("SOLDER RECEPTACLE BODY ON THIS SIDE", X1 + P * 12, Y_ODD - 2.0,
     layer=pcbnew.B_SilkS, size=1.0)
text("SIGNAL NAMES PER LTE LITE GUIDE - VERIFY GND (1,26,27) AND +5V (15,16) FIRST",
     (X_LEFT + X_RIGHT) / 2, Y_ODD - 4.5, layer=pcbnew.B_SilkS, size=0.9, thick=0.14)

pcbnew.SaveBoard(OUT, board)
print("wrote", OUT)
print(f"board {X_RIGHT - X_LEFT:.2f} x {Y_EDGE - Y_TOP:.2f} mm; "
      f"pin 1 is {X1 - X_LEFT:.2f} mm from the left edge; "
      f"header rows at {Y_EDGE - Y_HDR_ODD:.2f} / {Y_EDGE - Y_HDR_EVEN:.2f} mm above the mating edge")
