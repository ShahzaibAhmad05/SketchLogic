# render_circuit.py
import math
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
from PIL import Image, ImageDraw

# -------------------------
# Geometry helpers
# -------------------------

# Put this near your other helpers
def _swap_90_270(rot):
    r = int(round(float(rot))) % 360
    if r == 90:
        return 270
    if r == 270:
        return 90
    return r

def rotate_point(px: float, py: float, cx: float, cy: float, deg: float) -> Tuple[float, float]:
    """Rotate point (px,py) around center (cx,cy) by deg (counterclockwise)."""
    rad = math.radians(deg)
    dx, dy = px - cx, py - cy
    c, s = math.cos(rad), math.sin(rad)
    return (cx + c * dx - s * dy, cy + s * dx + c * dy)

def rotated_rect_bounds(x: float, y: float, w: float, h: float, deg: float) -> Tuple[float, float, float, float]:
    """Bounds after rotating axis-aligned rect around its center by deg."""
    cx, cy = x + w / 2.0, y + h / 2.0
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    rc = [rotate_point(px, py, cx, cy, deg) for (px, py) in corners]
    xs, ys = [p[0] for p in rc], [p[1] for p in rc]
    return min(xs), min(ys), max(xs), max(ys)

def mid_point(p1: Tuple[int, int], p2: Tuple[int, int]) -> Tuple[float, float]:
    return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)

# -------------------------
# Gate symbol drawing (local RGBA image; then rotated & pasted)
# -------------------------
def _new_gate_layer(w: int, h: int) -> Tuple[Image.Image, ImageDraw.ImageDraw]:
    # Transparent layer to draw crisp symbols, then rotate & paste
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    return layer, draw

def _proportions(w: int, h: int):
    # Consistent proportions across symbols
    pad = max(2, int(min(w, h) * 0.06))
    lw  = max(2, int(min(w, h) * 0.06))
    top, bot = pad, h - pad
    left, right = pad, w - pad
    return left, right, top, bot, lw

def draw_AND_rgba(w: int, h: int) -> Image.Image:
    layer, draw = _new_gate_layer(w, h)
    left, right, top, bot, lw = _proportions(w, h)

    # Rect part
    x1 = left + int(0.55 * (right - left))           # end of straight section
    draw.line([(left, top), (x1, top)], fill="black", width=lw)
    draw.line([(left, bot), (x1, bot)], fill="black", width=lw)
    draw.line([(left, top), (left, bot)], fill="black", width=lw)

    # Semicircle (front)
    r = (bot - top) / 2.0
    arc_box = [x1 - r, top, x1 + r, bot]
    draw.arc(arc_box, 270, 90, fill="black", width=lw)
    return layer

def draw_OR_rgba(w: int, h: int) -> Image.Image:
    layer, draw = _new_gate_layer(w, h)
    left, right, top, bot, lw = _proportions(w, h)

    # Front arc (like AND)
    x1 = left + int(0.55 * (right - left))
    r_front = (bot - top) / 2.0
    arc_front = [x1 - r_front, top, x1 + r_front, bot]
    draw.arc(arc_front, 270, 90, fill="black", width=lw)

    # Top/bottom trailing strokes
    draw.line([(left + lw, top), (x1, top)], fill="black", width=lw)
    draw.line([(left + lw, bot), (x1, bot)], fill="black", width=lw)

    # Back arc (concave)
    r_back = (bot - top) * 0.7
    arc_back = [left - r_back * 0.45, top, left + r_back * 0.55, bot]
    draw.arc(arc_back, 270, 90, fill="black", width=lw)
    return layer

def draw_XOR_rgba(w: int, h: int) -> Image.Image:
    # OR + extra back arc offset
    layer, draw = _new_gate_layer(w, h)
    left, right, top, bot, lw = _proportions(w, h)

    # Front arc
    x1 = left + int(0.55 * (right - left))
    r_front = (bot - top) / 2.0
    arc_front = [x1 - r_front, top, x1 + r_front, bot]
    draw.arc(arc_front, 270, 90, fill="black", width=lw)

    # Top/bottom
    draw.line([(left + lw, top), (x1, top)], fill="black", width=lw)
    draw.line([(left + lw, bot), (x1, bot)], fill="black", width=lw)

    # Back arcs
    r1 = (bot - top) * 0.7
    r2 = (bot - top) * 0.7
    arc_back1 = [left - r1 * 0.55, top, left + r1 * 0.45, bot]
    arc_back2 = [arc_back1[0] - lw * 3, top, arc_back1[2] - lw * 3, bot]
    draw.arc(arc_back1, 270, 90, fill="black", width=lw)
    draw.arc(arc_back2, 270, 90, fill="black", width=lw)
    return layer

def draw_NOT_rgba(w: int, h: int, bubble: bool = True) -> Image.Image:
    layer, draw = _new_gate_layer(w, h)
    left, right, top, bot, lw = _proportions(w, h)
    mid_y = (top + bot) / 2.0

    # Triangle
    x_tip = right - lw * 3
    pts = [(left, top), (left, bot), (x_tip, mid_y)]
    draw.polygon(pts, outline="black", fill=None)
    draw.line([pts[0], pts[1]], fill="black", width=lw)
    draw.line([pts[1], pts[2]], fill="black", width=lw)
    draw.line([pts[2], pts[0]], fill="black", width=lw)

    # Bubble at output (if requested)
    if bubble:
        r = max(2, int((bot - top) * 0.10))
        cx, cy = x_tip + r + lw, mid_y
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline="black", fill=(255, 255, 255, 0), width=lw)
    return layer

def add_bubble_at_output(layer: Image.Image) -> Image.Image:
    # Draws a small bubble just to the right of the layer's rightmost content.
    w, h = layer.size
    draw = ImageDraw.Draw(layer)
    r = max(2, int(h * 0.10))
    cx, cy = w - r - 2, h / 2.0
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline="black", fill=(255, 255, 255, 0), width=max(2, int(h * 0.06)))
    return layer

def gate_rgba(type_name: str, w: int, h: int) -> Image.Image:
    """Return an RGBA image of the gate symbol (unrotated, facing right)."""
    t = type_name.upper()
    if t == "AND":
        base = draw_AND_rgba(w, h)
    elif t == "OR":
        base = draw_OR_rgba(w, h)
    elif t == "XOR":
        base = draw_XOR_rgba(w, h)
    elif t == "NOT":
        base = draw_NOT_rgba(w, h, bubble=True)
        return base
    elif t == "NAND":
        base = draw_AND_rgba(w, h)
        add_bubble_at_output(base)
    elif t == "NOR":
        base = draw_OR_rgba(w, h)
        add_bubble_at_output(base)
    elif t == "XNOR":
        base = draw_XOR_rgba(w, h)
        add_bubble_at_output(base)
    else:
        # fallback: simple box
        base, draw = _new_gate_layer(w, h)
        left, right, top, bot, lw = _proportions(w, h)
        draw.rectangle([left, top, right, bot], outline="black", width=lw)
    return base

# -------------------------
# Canvas & drawing
# -------------------------
def compute_canvas_bounds(results: Dict[str, Any], margin: int = 40) -> Tuple[int, int, Tuple[int, int]]:
    """Return (W,H,offset) so all content fits with margin. Offset is the translation to apply when drawing."""
    gates = results.get("gates", [])
    wires = results.get("wires", {})
    probes = results.get("probes", [])
    toggles = results.get("toggles", [])

    minx, miny = float("inf"), float("inf")
    maxx, maxy = float("-inf"), float("-inf")

    # Gates: include rotated bounds to avoid clipping
    for g in gates:
        x, y, w, h = g["x"], g["y"], g["width"], g["height"]
        rot = float(g.get("rotation", 0))
        deg = _swap_90_270(rot)
        gx0, gy0, gx1, gy1 = rotated_rect_bounds(x, y, w, h, deg)
        minx, miny = min(minx, gx0), min(miny, gy0)
        maxx, maxy = max(maxx, gx1), max(maxy, gy1)

    # Wires
    for pts in wires.values():
        for (x, y) in pts:
            minx, miny = min(minx, x), min(miny, y)
            maxx, maxy = max(maxx, x), max(maxy, y)

    # Probes & toggles: pairs of points
    for p in probes:
        for (x, y) in p:
            minx, miny = min(minx, x), min(miny, y)
            maxx, maxy = max(maxx, x), max(maxy, y)
    for t in toggles:
        for (x, y) in t:
            minx, miny = min(minx, x), min(miny, y)
            maxx, maxy = max(maxx, x), max(maxy, y)

    if minx == float("inf"):
        # nothing? default small canvas
        W = H = 512
        return W, H, (margin, margin)

    W = int(math.ceil(maxx - minx)) + margin * 2
    H = int(math.ceil(maxy - miny)) + margin * 2
    offset = (int(round(margin - minx)), int(round(margin - miny)))
    return W, H, offset

def paste_rotated(center_x: float, center_y: float, img_rgba: Image.Image, deg: float, canvas: Image.Image):
    """Rotate layer by deg around its center and paste onto canvas centered at (center_x,center_y)."""
    rotated = img_rgba.rotate(deg, resample=Image.BICUBIC, expand=True)
    w2, h2 = rotated.size
    paste_xy = (int(round(center_x - w2 / 2.0)), int(round(center_y - h2 / 2.0)))
    canvas.alpha_composite(rotated, dest=paste_xy)

def draw_wires(draw: ImageDraw.ImageDraw, wires: Dict[str, List[Tuple[int, int]]], offset: Tuple[int, int], width: int = 3):
    ox, oy = offset
    for wire_id, pts in wires.items():
        if not pts or len(pts) < 2:
            continue
        path = [(int(x + ox), int(y + oy)) for (x, y) in pts]
        draw.line(path, fill="black", width=width)

def draw_probes(draw: ImageDraw.ImageDraw, probes: List[Tuple[Tuple[int, int], Tuple[int, int]]], offset: Tuple[int, int], radius: int = 6, width: int = 2):
    ox, oy = offset
    for p1, p2 in probes:
        mx, my = mid_point(p1, p2)
        cx, cy = int(mx + ox), int(my + oy)
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline="black", width=width, fill="white")

def draw_toggles(draw: ImageDraw.ImageDraw, toggles: List[Tuple[Tuple[int, int], Tuple[int, int]]], offset: Tuple[int, int], width: int = 5):
    ox, oy = offset
    for p1, p2 in toggles:
        # Draw the segment itself as the toggle
        x1, y1 = int(p1[0] + ox), int(p1[1] + oy)
        x2, y2 = int(p2[0] + ox), int(p2[1] + oy)
        draw.line([(x1, y1), (x2, y2)], fill="black", width=width)

def draw_gates(canvas: Image.Image, results: Dict[str, Any], offset: Tuple[int, int]):
    ox, oy = offset
    for g in results.get("gates", []):
        x, y, w, h = int(g["x"]), int(g["y"]), int(g["width"]), int(g["height"])
        rot = float(g.get("rotation", 0))
        deg = _swap_90_270(rot)
        t   = str(g.get("type", "AND")).upper()

        # Build symbol (unrotated, facing right), then rotate & paste at center
        symbol = gate_rgba(t, max(8, w), max(8, h))

        cx, cy = x + w / 2.0 + ox, y + h / 2.0 + oy
        paste_rotated(cx, cy, symbol, deg, canvas)

def render_circuit(results: Dict[str, Any],
                   out_path: str = "circuit_render.png",
                   background: str = "white",
                   margin: int = 40):
    """
    Render the given results dict to an image.
    results schema:
      - gates: list of {id,type,x,y,width,height,rotation,...}
      - wires: dict id -> [(x,y), ...]
      - probes: list of ((x1,y1),(x2,y2))
      - toggles: list of ((x1,y1),(x2,y2))
    """
    W, H, offset = compute_canvas_bounds(results, margin=margin)
    # Work in RGBA so we can paste rotated gates cleanly
    canvas = Image.new("RGBA", (W, H), background)

    # Draw wires first (so gates render on top)
    draw = ImageDraw.Draw(canvas)
    draw_wires(draw, results.get("wires", {}), offset, width=3)
    draw_probes(draw, results.get("probes", []), offset, radius=6, width=2)
    draw_toggles(draw, results.get("toggles", []), offset, width=5)

    # Gates on top
    draw_gates(canvas, results, offset)

    # Save as opaque PNG
    out_path = str(Path(out_path))
    canvas.convert("RGB").save(out_path, format="JPEG")
    return canvas.convert("RGB")

def main() -> None:
    # Example `results` based on your structure
    results = {
        'gates': [
            {'id': 1, 'type': 'AND', 'x': 189, 'y': 622, 'width': 242, 'height': 235,
             'rotation': 270, 'num_inputs': 2},
            {'id': 2, 'type': 'NOT', 'x': 536, 'y': 325, 'width': 180, 'height': 159,
             'rotation': 180, 'num_inputs': 1}
        ],
        'wires': {
            'd25e': [(328, 618), (330, 587), (332, 554), (334, 520), (336, 488)],
            '0e22': [(281, 857), (278, 887), (274, 919), (270, 950), (268, 982)],
            '3729': [(355, 857), (357, 887), (367, 916), (397, 910), (428, 905),
                     (459, 897), (458, 861), (456, 826), (454, 792), (452, 757),
                     (449, 722), (448, 687), (448, 652), (450, 619), (446, 586),
                     (443, 553), (437, 520), (433, 486), (426, 453), (442, 431),
                     (475, 429), (506, 425)],
            '4533': [(534, 419), (503, 426), (469, 429), (436, 431), (426, 457),
                     (433, 488), (437, 519), (442, 550), (446, 580), (449, 611),
                     (449, 642), (448, 676), (449, 709), (451, 741), (453, 772),
                     (454, 804), (457, 835), (458, 868), (458, 898), (424, 905),
                     (392, 911), (360, 911)]
        },
        'probes': [((260, 1078), (257, 1109))],
        'toggles': [((475, 429), (506, 425))]
    }

    out_file = render_circuit(results, out_path="circuit_render.png", background="white", margin=60)
    print(f"Saved: {out_file}")

if __name__ == "__main__":
    main()
