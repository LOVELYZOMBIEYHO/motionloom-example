"""Draw draft feature points on the padded crops for visual verification."""

import json
import sys

sys.path.insert(0, "tools")
from png_writer import Canvas

FEATURES = json.load(open("authoring/features-draft.json"))


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


for view, features in FEATURES.items():
    width, height, pixels = read_ppm(f"source/{view}.ppm")
    canvas = Canvas(width, height, (24, 24, 28))
    for y in range(height):
        for x in range(width):
            offset = (y * width + x) * 3
            canvas.set(
                x,
                y,
                (
                    pixels[offset] // 2 + 90,
                    pixels[offset + 1] // 2 + 90,
                    pixels[offset + 2] // 2 + 90,
                ),
            )
    colors = [
        (255, 60, 60),
        (255, 170, 40),
        (80, 255, 120),
        (80, 200, 255),
        (255, 80, 255),
        (255, 255, 80),
    ]
    for index, (name, kind, points, binding, confidence, snap) in enumerate(features):
        color = colors[index % len(colors)]
        for point in points:
            canvas.dot(point[0], point[1], color, 3)
        if len(points) > 1:
            for a, b in zip(points, points[1:]):
                canvas.line(a, b, color)
    canvas.save(f"fit/features-{view}.png")
    print("wrote", f"fit/features-{view}.png")
