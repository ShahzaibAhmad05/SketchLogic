"""
This script is meant to convert AABB annotations in the dataset to OBB annotations. It overwrites
the original files, so kindly keep a backup.

The dataset was previously annotated using AABB annotations. For identifying what format
the annotations are in, check a sample file from data/labels.

If the file has approximately this format:

14 0.526042 0.711085 0.174479 0.261792
14 0.210286 0.665094 0.157552 0.259434
14 0.207031 0.253538 0.161458 0.266509

then it is likely in AABB format. OBB format stores all four corners of the bounding box.
That approach reduces our number of classes four-fold.
"""

from pathlib import Path
import math


def convert_file(file_path: Path):
    """
    Convert a single AABB annotation file to OBB format.

    Args:
        file_path: Path to the AABB annotation file.

    Returns:
        None
    """

    with open(file_path, "r") as file:
        lines = file.readlines()

    new_lines = []

    for line in lines:
        parts = line.strip().split(" ")
        if not len(parts) == 5:
            print("Found invalid line in file: ", file_path)
            print("Line: ", line)
            continue

        old_class = int(parts[0])
        new_class, rotation_angle = convert_class(old_class)

        x, y, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
        points = convert_points(x, y, w, h, rotation_angle)
        new_points = convert_points_to_line(points)

        new_lines.append(
            f"{new_class} {new_points}\n"
        )

    with open(file_path, "w") as file:
        file.writelines(new_lines)


def convert_points_to_line(points: list[tuple[float, float]]) -> str:
    """
    Convert a list of points to a line string.
    """
    values = []

    for point in points:
        for v in point:
            values.append(str(round(v, 6)))

    return " ".join(values)


def convert_class(old_class: int) -> tuple[int, int]:
    """
    Convert a single AABB class to OBB class.

    Args:
        old_class: The old class index.

    Returns:
        A tuple containing the new class index and the rotation angle in degrees.
    """

    return old_class // 4, (old_class % 4) * 90


def convert_points(x: float, y: float, w: float, h: float, rotation_angle: int) -> list[tuple[float, float]]:
    """
    Convert AABB points to OBB points.

    Args:
        x: The x coordinate of the center of the AABB.
        y: The y coordinate of the center of the AABB.
        w: The width of the AABB.
        h: The height of the AABB.
        rotation_angle: The rotation angle in degrees.

    Returns:
        A list of tuples containing the OBB points.
    """

    angle = math.radians(rotation_angle)
    cos = math.cos(angle)
    sin = math.sin(angle)

    hh, hw = h / 2, w / 2
    offsets = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]

    return [        # 2D rotation + shifting back to image coordinates
        (x + dx * cos - dy * sin, y + dx * sin + dy * cos)
        for dx, dy in offsets
    ]


def main():
    paths = [
        Path("./data/labels/train"),
        Path("./data/labels/val")
    ]

    for path in paths:
        if not path.exists():
            print(f"Path {path} does not exist.")
            continue

    i = 0

    for path in paths:
        for file in path.iterdir():
            if not file.is_file() or not file.name.endswith(".txt"):
                continue

            convert_file(file)

            if i % 50 == 0:     # will inform every 50 passes
                print(f"Converted {i} files")
            i += 1

    print(f"Converted {i} files successfully.")


if __name__ == "__main__":
    main()
