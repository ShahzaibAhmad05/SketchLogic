"""
File containing function for labelling a circuit image using
processed inference results.

"""

from typing import Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont


def _load_font_fixed_size(font_size: int) -> ImageFont.ImageFont:
    return ImageFont.load_default(size=font_size)


def draw_circuit_on_image(
    image_path: str,
    data: Dict[str, Any],
    *,
    font_size: int = -1,
    wire_width: int = 5,
    bottom_gap: int = 6,
    bg_pad: int = 4,
    gate_outline_color: Tuple[int, int, int, int] = (0, 255, 0, 255),
    gate_outline_width: int = 6,
    draw_wire_points: bool = True,
    wire_point_radius: int = 3,
) -> Image.Image:

    img = Image.open(image_path).convert("RGBA")

    if font_size == -1:
        img_w, _ = img.size
        font_size = max(10, int(img_w * 0.02))
        bg_pad = max(2, int(font_size * 0.20))

    draw = ImageDraw.Draw(img)
    font = _load_font_fixed_size(font_size)

    for gate in data.get("gates", []):
        x = int(gate.get("x", 0))
        y = int(gate.get("y", 0))
        w = int(gate.get("width", 0))
        h = int(gate.get("height", 0))
        gate_type = gate.get("type", "Unknown")
        rotation = gate.get("rotation", 0)

        if w <= 0 or h <= 0:
            continue

        label = f"{gate_type} @ {rotation}°"

        draw.rectangle(
            [(x, y), (x + w, y + h)],
            outline=gate_outline_color,
            width=gate_outline_width
        )

        bbox = draw.textbbox((0, 0), label, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

        bg_w = tw + 2 * bg_pad
        bg_h = th + 2 * bg_pad
        center_x = x + w / 2

        bg_left = int(center_x - bg_w / 2)
        bg_right = bg_left + bg_w
        bg_bottom = y + h - bottom_gap
        bg_top = bg_bottom - bg_h

        draw.rectangle(
            [bg_left, bg_top, bg_right, bg_bottom],
            fill=gate_outline_color
        )

        tx = int(bg_left + (bg_w - tw) / 2)
        ty = int(bg_top + (bg_h - th) / 2)

        draw.text((tx, ty), label, font=font, fill=(0, 0, 0, 255))

    wires = data.get("wires", {})
    if isinstance(wires, dict):
        for points in wires.values():
            if not points or len(points) < 2:
                continue

            pts = []
            for p in points:
                if isinstance(p, (list, tuple)) and len(p) == 2:
                    pts.append((int(p[0]), int(p[1])))

            if len(pts) >= 2:
                draw.line(pts, fill=(255, 0, 0, 255), width=wire_width)

            if draw_wire_points:
                for px, py in pts:
                    r = wire_point_radius
                    draw.ellipse(
                        [(px - r, py - r), (px + r, py + r)],
                        fill=(0, 0, 255, 255)
                    )

    return img
