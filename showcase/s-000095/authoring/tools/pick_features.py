"""Derive feature pixel positions per view and bind them to the shark cage.

Features are located from the segmentation mask geometry and from dark image
marks (eye, mouth, gills). Bindings point at real cage vertices, edges, or
vertex chains; nothing important stays on nearestContour.
"""

import json
import math

CAGE = {"rings": 21, "columns": 12}


def vertex(ring, column):
    return ring * CAGE["columns"] + column


SNOUT_POLE = 252
TAIL_POLE = 253


def read_ppm(path):
    data = open(path, "rb").read()
    fields = []
    index = 2
    while len(fields) < 3:
        while data[index : index + 1].isspace():
            index += 1
        start = index
        while not data[index : index + 1].isspace():
            index += 1
        fields.append(int(data[start:index]))
    index += 1
    width, height, _ = fields
    return width, height, data[index : index + width * height * 3]


def decode_mask(mask):
    width, height = mask["width"], mask["height"]
    pixels = bytearray(width * height)
    value = 1 if mask["startsForeground"] else 0
    index = 0
    for run in mask["runs"]:
        for offset in range(run):
            pixels[index + offset] = value
        value ^= 1
        index += run
    return pixels


def luminance(pixels, width, x, y):
    offset = (y * width + x) * 3
    return (
        pixels[offset] * 0.2126 + pixels[offset + 1] * 0.7152 + pixels[offset + 2] * 0.0722
    )


def mask_extremes(data):
    mask = decode_mask(data)
    width, height = data["width"], data["height"]
    result = {
        "leftmost": None,
        "rightmost": None,
        "topmost": None,
        "bottommost": None,
    }
    for y in range(height):
        for x in range(width):
            if not mask[y * width + x]:
                continue
            if result["leftmost"] is None or x < result["leftmost"][0]:
                result["leftmost"] = [x, y]
            if result["rightmost"] is None or x > result["rightmost"][0]:
                result["rightmost"] = [x, y]
            if result["topmost"] is None or y < result["topmost"][1]:
                result["topmost"] = [x, y]
            if result["bottommost"] is None or y > result["bottommost"][1]:
                result["bottommost"] = [x, y]
    return result


def extreme_in_box(data, box, mode):
    mask = decode_mask(data)
    width = data["width"]
    x0, y0, x1, y1 = box
    best = None
    for y in range(y0, y1):
        for x in range(x0, x1):
            if not mask[y * width + x]:
                continue
            if best is None:
                best = [x, y]
                continue
            if mode == "lowest" and y > best[1]:
                best = [x, y]
            if mode == "highest" and y < best[1]:
                best = [x, y]
            if mode == "rightmost" and x > best[0]:
                best = [x, y]
            if mode == "leftmost" and x < best[0]:
                best = [x, y]
    return best


def darkest_in_box(pixels, width, box):
    x0, y0, x1, y1 = box
    best = None
    best_value = 1e9
    for y in range(y0, y1):
        for x in range(x0, x1):
            value = luminance(pixels, width, x, y)
            if value < best_value:
                best_value = value
                best = [x, y]
    return best


def darkest_line(pixels, width, box, samples):
    x0, y0, x1, y1 = box
    points = []
    for step in range(samples):
        x = x0 + (x1 - x0) * step / max(1, samples - 1)
        xi = int(round(x))
        best = None
        best_value = 1e9
        for y in range(y0, y1):
            value = luminance(pixels, width, xi, y)
            if value < best_value:
                best_value = value
                best = [xi, y]
        points.append(best)
    return points


def main():
    features_per_view = {}

    # ---------------- left ----------------
    view = "left"
    width, height, pixels = read_ppm("source/left.ppm")
    analysis = json.load(open("analysis/pass1-left/analysis.json"))
    mask = decode_mask(analysis["foregroundMask"])
    ext = mask_extremes(analysis["foregroundMask"])
    dorsal = extreme_in_box(
        analysis["foregroundMask"], (280, 0, 470, height), "highest"
    )
    pectoral = extreme_in_box(
        analysis["foregroundMask"], (190, 250, 430, height), "lowest"
    )
    belly = extreme_in_box(
        analysis["foregroundMask"], (430, 250, 620, height), "lowest"
    )
    tail_upper = extreme_in_box(
        analysis["foregroundMask"], (640, 0, width, height), "highest"
    )
    tail_lower = extreme_in_box(
        analysis["foregroundMask"], (640, 0, width, height), "lowest"
    )
    snout = extreme_in_box(analysis["foregroundMask"], (0, 150, 60, 320), "leftmost")
    eye = darkest_in_box(pixels, width, (45, 120, 135, 215))
    mouth = darkest_line(pixels, width, (10, 240, 130, 300), 4)
    gills = []
    for index in range(5):
        x0 = 150 + index * 18
        gills.append(darkest_in_box(pixels, width, (x0, 200, x0 + 16, 300)))
    features_per_view[view] = [
        ("snout_tip", "point", [snout], {"type": "vertex", "vertex": SNOUT_POLE}, 0.95, 8),
        (
            "eye_center",
            "point",
            [eye],
            {"type": "edge", "vertices": [vertex(2, 3), vertex(3, 3)], "t": 0.55},
            0.85,
            6,
        ),
        (
            "mouth_line",
            "polyline",
            mouth,
            {
                "type": "vertexChain",
                "vertices": [vertex(1, 5), vertex(2, 5), vertex(3, 5), vertex(4, 5)],
                "closed": False,
            },
            0.8,
            6,
        ),
        (
            "gill_lines",
            "polyline",
            [point for point in gills if point],
            {
                "type": "vertexChain",
                "vertices": [vertex(4, 3), vertex(5, 3), vertex(6, 3)],
                "closed": False,
            },
            0.7,
            6,
        ),
        (
            "dorsal_fin_tip",
            "point",
            [dorsal],
            {"type": "vertex", "vertex": vertex(11, 0)},
            0.92,
            8,
        ),
        (
            "dorsal_fin_contour",
            "polyline",
            [dorsal, [dorsal[0] - 26, dorsal[1] + 52], [dorsal[0] + 30, dorsal[1] + 58]],
            {
                "type": "vertexChain",
                "vertices": [vertex(10, 0), vertex(11, 0), vertex(12, 0), vertex(13, 0)],
                "closed": False,
            },
            0.82,
            8,
        ),
        (
            "pectoral_fin_tip",
            "point",
            [pectoral],
            {"type": "vertex", "vertex": vertex(9, 3)},
            0.9,
            8,
        ),
        (
            "pectoral_fin_contour",
            "polyline",
            [pectoral, [pectoral[0] - 30, pectoral[1] - 42], [pectoral[0] + 34, pectoral[1] - 56]],
            {
                "type": "vertexChain",
                "vertices": [vertex(7, 3), vertex(8, 3), vertex(9, 3), vertex(10, 3)],
                "closed": False,
            },
            0.8,
            8,
        ),
        (
            "tail_upper_tip",
            "point",
            [tail_upper],
            {"type": "vertex", "vertex": vertex(19, 0)},
            0.88,
            8,
        ),
        (
            "tail_lower_tip",
            "point",
            [tail_lower],
            {"type": "vertex", "vertex": vertex(19, 6)},
            0.85,
            8,
        ),
        (
            "caudal_peduncle",
            "point",
            [[ext["rightmost"][0] - 130, ext["rightmost"][1]]],
            {"type": "edge", "vertices": [vertex(16, 3), vertex(17, 3)], "t": 0.5},
            0.75,
            6,
        ),
        (
            "belly_apex",
            "point",
            [belly],
            {"type": "vertex", "vertex": vertex(9, 6)},
            0.85,
            8,
        ),
        (
            "body_centerline",
            "polyline",
            [
                [90, 205],
                [250, 210],
                [420, 213],
                [580, 205],
                [700, 195],
            ],
            {
                "type": "vertexChain",
                "vertices": [vertex(6, 3), vertex(9, 3), vertex(12, 3), vertex(15, 3)],
                "closed": False,
            },
            0.8,
            8,
        ),
    ]

    # ---------------- front ----------------
    view = "front"
    width, height, pixels = read_ppm("source/front.ppm")
    analysis = json.load(open("analysis/pass1-front/analysis.json"))
    ext = mask_extremes(analysis["foregroundMask"])
    dorsal = extreme_in_box(analysis["foregroundMask"], (280, 0, 470, height), "highest")
    pectoral_left = extreme_in_box(
        analysis["foregroundMask"], (280, 220, width, height), "rightmost"
    )
    pectoral_right = extreme_in_box(
        analysis["foregroundMask"], (0, 220, 300, height), "leftmost"
    )
    belly = extreme_in_box(analysis["foregroundMask"], (200, 300, 520, height), "lowest")
    mouth = darkest_line(pixels, width, (170, 250, 400, 330), 5)
    snout = darkest_in_box(pixels, width, (250, 180, 320, 260))
    features_per_view[view] = [
        ("snout_tip", "point", [snout], {"type": "vertex", "vertex": SNOUT_POLE}, 0.9, 8),
        (
            "mouth_line",
            "polyline",
            mouth,
            {
                "type": "vertexChain",
                "vertices": [
                    vertex(3, 4),
                    vertex(3, 5),
                    vertex(3, 6),
                    vertex(3, 7),
                    vertex(3, 8),
                ],
                "closed": False,
            },
            0.8,
            6,
        ),
        (
            "eye_left",
            "point",
            [[ext["rightmost"][0] - 60, ext["topmost"][1] + 120]],
            {"type": "vertex", "vertex": vertex(4, 3)},
            0.6,
            10,
        ),
        (
            "eye_right",
            "point",
            [[ext["leftmost"][0] + 60, ext["topmost"][1] + 120]],
            {"type": "vertex", "vertex": vertex(4, 9)},
            0.6,
            10,
        ),
        (
            "dorsal_fin_tip",
            "point",
            [dorsal],
            {"type": "vertex", "vertex": vertex(11, 0)},
            0.85,
            8,
        ),
        (
            "pectoral_tip_left",
            "point",
            [pectoral_left],
            {"type": "vertex", "vertex": vertex(9, 3)},
            0.85,
            8,
        ),
        (
            "pectoral_tip_right",
            "point",
            [pectoral_right],
            {"type": "vertex", "vertex": vertex(9, 9)},
            0.85,
            8,
        ),
        (
            "belly_apex",
            "point",
            [belly],
            {"type": "vertex", "vertex": vertex(9, 6)},
            0.8,
            8,
        ),
        (
            "gill_lines",
            "polyline",
            [[ext["rightmost"][0] - 120, ext["topmost"][1] + 150], [ext["rightmost"][0] - 108, ext["topmost"][1] + 190]],
            {"type": "vertexChain", "vertices": [vertex(5, 3), vertex(6, 3)], "closed": False},
            0.6,
            8,
        ),
        (
            "body_centerline",
            "polyline",
            [[256, 300], [256, 250], [256, 200]],
            {"type": "vertexChain", "vertices": [vertex(6, 6), vertex(12, 6)], "closed": False},
            0.6,
            8,
        ),
    ]

    # ---------------- top ----------------
    view = "top"
    width, height, pixels = read_ppm("source/top.ppm")
    analysis = json.load(open("analysis/pass1-top/analysis.json"))
    ext = mask_extremes(analysis["foregroundMask"])
    dorsal = extreme_in_box(analysis["foregroundMask"], (190, 0, 380, height), "highest")
    pectoral_left = extreme_in_box(
        analysis["foregroundMask"], (160, 200, width, height), "lowest"
    )
    pectoral_right = extreme_in_box(analysis["foregroundMask"], (0, 150, 340, height), "highest")
    snout = extreme_in_box(analysis["foregroundMask"], (0, 100, 70, 340), "leftmost")
    tail_upper = extreme_in_box(analysis["foregroundMask"], (600, 0, width, height), "highest")
    tail_lower = extreme_in_box(analysis["foregroundMask"], (600, 0, width, height), "lowest")
    features_per_view[view] = [
        ("snout_tip", "point", [snout], {"type": "vertex", "vertex": SNOUT_POLE}, 0.9, 8),
        (
            "dorsal_fin_tip",
            "point",
            [dorsal],
            {"type": "vertex", "vertex": vertex(11, 0)},
            0.8,
            8,
        ),
        (
            "dorsal_fin_contour",
            "polyline",
            [dorsal, [dorsal[0] - 24, dorsal[1] + 46], [dorsal[0] + 24, dorsal[1] + 50]],
            {
                "type": "vertexChain",
                "vertices": [vertex(10, 0), vertex(11, 0), vertex(12, 0), vertex(13, 0)],
                "closed": False,
            },
            0.75,
            8,
        ),
        (
            "pectoral_tip_left",
            "point",
            [pectoral_left],
            {"type": "vertex", "vertex": vertex(9, 3)},
            0.8,
            8,
        ),
        (
            "pectoral_tip_right",
            "point",
            [pectoral_right],
            {"type": "vertex", "vertex": vertex(9, 9)},
            0.8,
            8,
        ),
        (
            "tail_upper_tip",
            "point",
            [tail_upper],
            {"type": "vertex", "vertex": vertex(19, 0)},
            0.7,
            8,
        ),
        (
            "tail_lower_tip",
            "point",
            [tail_lower],
            {"type": "vertex", "vertex": vertex(19, 6)},
            0.7,
            8,
        ),
        (
            "body_centerline",
            "polyline",
            [[120, 218], [300, 216], [480, 210], [640, 190]],
            {
                "type": "vertexChain",
                "vertices": [vertex(3, 0), vertex(8, 0), vertex(13, 0), vertex(17, 0)],
                "closed": False,
            },
            0.75,
            8,
        ),
    ]

    # ---------------- bottom ----------------
    view = "bottom"
    width, height, pixels = read_ppm("source/bottom.ppm")
    analysis = json.load(open("analysis/pass2-bottom/analysis.json"))
    pectoral_left = extreme_in_box(
        analysis["foregroundMask"], (180, 230, width, height), "lowest"
    )
    pectoral_right = extreme_in_box(
        analysis["foregroundMask"], (0, 130, 400, height), "highest"
    )
    belly = extreme_in_box(analysis["foregroundMask"], (430, 250, 660, height), "lowest")
    mouth = darkest_line(pixels, width, (60, 200, 220, 300), 5)
    features_per_view[view] = [
        (
            "mouth_line",
            "polyline",
            mouth,
            {
                "type": "vertexChain",
                "vertices": [vertex(3, 4), vertex(3, 5), vertex(3, 6), vertex(3, 7), vertex(3, 8)],
                "closed": False,
            },
            0.8,
            6,
        ),
        (
            "pectoral_tip_left",
            "point",
            [pectoral_left],
            {"type": "vertex", "vertex": vertex(9, 3)},
            0.8,
            8,
        ),
        (
            "pectoral_tip_right",
            "point",
            [pectoral_right],
            {"type": "vertex", "vertex": vertex(9, 9)},
            0.8,
            8,
        ),
        (
            "belly_apex",
            "point",
            [belly],
            {"type": "vertex", "vertex": vertex(9, 6)},
            0.8,
            8,
        ),
        (
            "gill_lines",
            "polyline",
            [[150, 190], [150, 240], [300, 210], [300, 250]],
            {
                "type": "vertexChain",
                "vertices": [vertex(4, 3), vertex(5, 3), vertex(6, 3), vertex(4, 9), vertex(5, 9), vertex(6, 9)],
                "closed": False,
            },
            0.6,
            8,
        ),
        (
            "body_centerline",
            "polyline",
            [[120, 218], [300, 216], [480, 212], [640, 195]],
            {
                "type": "vertexChain",
                "vertices": [vertex(6, 6), vertex(10, 6), vertex(14, 6)],
                "closed": False,
            },
            0.75,
            8,
        ),
    ]

    json.dump(features_per_view, open("authoring/features-draft.json", "w"), indent=1)
    for view, features in features_per_view.items():
        print(f"== {view}: {len(features)} features")
        for feature in features:
            print("   ", feature[0], feature[1], feature[2][:2])


if __name__ == "__main__":
    main()
