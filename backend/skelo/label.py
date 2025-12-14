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
    gate_width: int = 100,                   # default gate width since not in new format
    gate_height: int = 60,                   # default gate height since not in new format
) -> Image.Image:
    """
    Draw gates (rectangles) with bottom-centered labels and wires (red polylines).
    Updated to work with the new JSON format.

    - Gate label: black text, no outline, bold simulated, on a filled background
      (same color as the rectangle outline), vertically centered within that background.
    """
    img = Image.open(image_path).convert("RGBA")

    # DEFAULT FONT SIZING
    if font_size == -1:
        imgWidth, imgHeight = img.size  # width, height in pixels
        font_size = int(imgWidth * 0.02)
        bg_pad = int(font_size * 0.05)

    draw = ImageDraw.Draw(img)
    font = _load_font_fixed_size(font_size)

    # RECTANGLES FOR GATES (updated for new format)
    for component in data.get("Components", []):
        # Extract coordinates and properties from new format
        x = int(component.get("X", 0))
        y = int(component.get("Y", 0))
        w = gate_width   # Use default width since not provided in new format
        h = gate_height  # Use default height since not provided in new format
        gate_type = component.get("Type", "Unknown")
        rotation = component.get("Rotation", 0)
        
        label = f"{gate_type} @ {rotation}°"

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

    # POLYLINES FOR WIRES (updated for new format)
    for wire in data.get("Wires", []):
        points = wire.get("Points", [])
        if len(points) >= 2:
            # Convert points from new format: [{"X": x, "Y": y}, ...] to [(x, y), ...]
            pts = [(int(point["X"]), int(point["Y"])) for point in points 
                   if isinstance(point, dict) and "X" in point and "Y" in point]
            if len(pts) >= 2:
                draw.line(pts, fill=(255, 0, 0, 255), width=wire_width)

    # DRAW WIRE POINTS as small circles
    for wire in data.get("Wires", []):
        points = wire.get("Points", [])
        for point in points:
            if isinstance(point, dict) and "X" in point and "Y" in point:
                x, y = int(point["X"]), int(point["Y"])
                # Draw a small circle at each wire point
                radius = 3
                draw.ellipse([(x - radius, y - radius), (x + radius, y + radius)], 
                           fill=(0, 0, 255, 255))  # Blue circles for wire points

    return img