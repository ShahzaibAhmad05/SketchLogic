from typing import Dict, Any
from PIL import Image, ImageDraw, ImageFont

def _load_font_fixed_size(font_size: int) -> ImageFont.ImageFont:
    # Use the default PIL font with the given size only.
    return ImageFont.load_default(size=font_size)

def draw_circuit_on_image(
    image_path: str,
    data: Dict[str, Any],
    *,
    font_size: int = -1,                     # font size in pixels (-1 for default)
    wire_width: int = 5,
    bottom_gap: int = 6,                     # gap from gate bottom to label background
    bg_pad: int = 4,                         # padding around label text inside its background
    gate_outline_color=(0, 255, 0, 255),
    gate_outline_width: int = 6,             # thicker rectangle border
) -> Image.Image:
    """
    Draw gates (rectangles) with bottom-centered labels and wires (red polylines).
    Also draws a list of Boolean formulas bottom-right, right-aligned.

    - Gate label: black text, no outline, bold simulated, on a filled background
      (same color as the rectangle outline), vertically centered within that background.
    - Boolean formulas: black text, no outline, bold simulated, stacked at bottom-right.
    """
    img = Image.open(image_path).convert("RGBA")

    # DEFAULT FONT SIZING
    if font_size == -1:
        imgWidth, imgHeight = img.size  # width, height in pixels
        font_size = int(imgWidth * 0.02)
        bg_pad = int(font_size * 0.05)

    draw = ImageDraw.Draw(img)
    font = _load_font_fixed_size(font_size)

    # RECTANGLES FOR GATES
    for gate in data.get("gates", []):
        x = int(gate.get("x", 0))
        y = int(gate.get("y", 0))
        w = int(gate.get("width", 0))
        h = int(gate.get("height", 0))
        label = f"{gate.get('type', '')} @ {gate.get('rotation', '')}"

        # Rectangle (thicker border)
        draw.rectangle([(x, y), (x + w, y + h)], outline=gate_outline_color, width=gate_outline_width)

        # Measure label
        bbox = draw.textbbox((0, 0), label, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

        # Background size & placement (bottom-centered with bottom_gap)
        bg_w = tw + 2 * bg_pad
        bg_h = th + 2 * bg_pad
        center_x = x + w / 2
        bg_left = int(center_x - bg_w / 2)
        bg_right = bg_left + bg_w
        bg_bottom = y + h - bottom_gap
        bg_top = bg_bottom - bg_h

        # Draw background (same color as gate outline)
        draw.rectangle([bg_left, bg_top, bg_right, bg_bottom], fill=gate_outline_color)

        # Vertically centered text within background
        tx = int(bg_left + (bg_w - tw) / 2)
        ty = int(bg_top + (bg_h - th) / 2)

        # Draw text in black
        draw.text((tx, ty), label, font=font, fill=(0, 0, 0, 255))

    # POLYLINES FOR WIRES
    for poly in data.get("wires", {}).values():
        if poly and len(poly) >= 2:
            pts = [(int(p[0]), int(p[1])) for p in poly if isinstance(p, (list, tuple)) and len(p) >= 2]
            if len(pts) >= 2:
                draw.line(pts, fill=(255, 0, 0, 255), width=wire_width)

    return img
