from typing import Optional, Dict, Any, List
from PIL import Image, ImageDraw, ImageFont

def _load_font_fixed_size(font_size: int, font_path: Optional[str] = None) -> ImageFont.ImageFont:
    # Use the default PIL font with the given size only.
    # (Note: some Pillow builds ignore size for the default font.)
    return ImageFont.load_default(size=font_size)

def draw_circuit_on_image(
    image_path: str,
    data: Dict[str, Any],
    *,
    font_size: int = -1,
    font_path: Optional[str] = None,        # kept for signature compatibility; unused by the default loader
    wire_width: int = 5,
    bottom_gap: int = 6,                     # gap from gate bottom to label background
    bg_pad: int = 4,                         # padding around label text inside its background
    gate_outline_color=(0, 255, 0, 255),
    gate_outline_width: int = 6,             # thicker rectangle border
    fake_bold: bool = True,                  # simulate bold by multi-draw
    boolean_formulas: Optional[List[str]] = None,
    formula_edge_pad: int = 22,              # margin from image right/bottom edges
    formula_line_gap: int = 6                # gap between formula lines
) -> Image.Image:
    """
    Draw gates (rectangles) with bottom-centered labels and wires (red polylines).
    Also draws a list of Boolean formulas bottom-right, right-aligned.

    - Gate label: black text, no outline, bold simulated, on a filled background
      (same color as the rectangle outline), vertically centered within that background.
    - Boolean formulas: black text, no outline, bold simulated, stacked at bottom-right.
    """
    img = Image.open(image_path).convert("RGBA")
    imgWidth, imgHeight = img.size  # width, height in pixels
    if font_size == -1:
        font_size = int(min(imgWidth, imgHeight) * 0.03)
        bg_pad = int(font_size * 0.1)
        # formula_edge_pad = font_size
    draw = ImageDraw.Draw(img)
    font = _load_font_fixed_size(font_size, font_path)

    # ---- Gates: rectangles + bottom-centered label with background ----
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

        # Draw text in black, simulate bold if requested
        if fake_bold:
            for dx, dy in [(0, 0), (1, 0), (0, 1), (1, 1)]:
                draw.text((tx + dx, ty + dy - (bg_pad*2)), label, font=font, fill=(0, 0, 0, 255))
        else:
            draw.text((tx, ty), label, font=font, fill=(0, 0, 0, 255))

    # ---- Wires: red polylines ----
    for poly in data.get("wires", {}).values():
        if poly and len(poly) >= 2:
            pts = [(int(p[0]), int(p[1])) for p in poly if isinstance(p, (list, tuple)) and len(p) >= 2]
            if len(pts) >= 2:
                draw.line(pts, fill=(255, 0, 0, 255), width=wire_width)

    # ---- Boolean formulas: bottom-right, right-aligned ----
    # if not boolean_formulas: boolean_formulas = ['No Formulas Could be Extracted.']
    # if boolean_formulas:
    #     # Measure each line first to right-align precisely.
    #     measured = []
    #     for s in boolean_formulas:
    #         bbox = draw.textbbox((0, 0), s, font=font)
    #         tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    #         measured.append((s, tw, th))

    #     # Start from the bottom edge and stack upward.
    #     y_cursor = img.height - formula_edge_pad
    #     for s, tw, th in reversed(measured):  # last formula nearest the bottom
    #         y_cursor -= th  # move up by line height
    #         tx = img.width - formula_edge_pad - tw  # right-align
    #         ty = y_cursor

    #         if fake_bold:
    #             for dx, dy in [(0, 0), (1, 0), (0, 1), (1, 1)]:
    #                 draw.text((tx + dx, ty + dy), s, font=font, fill=(0, 0, 0, 255))
    #         else:
    #             draw.text((tx, ty), s, font=font, fill=(0, 0, 0, 255))

    #         y_cursor -= formula_line_gap  # spacing between lines

    return img

# Example:
# annotated = draw_circuit_on_image(
#     "path/to/background.png",
#     data_dict,
#     font_size=28,
#     boolean_formulas=["F1 = A·B", "F2 = ¬A + B", "F3 = (A ⊕ B)·C"]
# )
# annotated.show()
