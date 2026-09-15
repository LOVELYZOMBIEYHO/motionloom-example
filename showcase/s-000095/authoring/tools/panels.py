"""Find the four shark panels and the shark bounding boxes in the composite.

Pure-python; reads the PPM dump of the source composite.
"""

import sys
from collections import deque

PATH = sys.argv[1] if len(sys.argv) > 1 else "source/composite.ppm"


def read_ppm(path):
    with open(path, "rb") as handle:
        data = handle.read()
    if not data.startswith(b"P6"):
        raise SystemExit("expected P6 ppm")
    fields = []
    index = 2
    while len(fields) < 3:
        while data[index : index + 1].isspace():
            index += 1
        if data[index : index + 1] == b"#":
            while data[index : index + 1] != b"\n":
                index += 1
            continue
        start = index
        while not data[index : index + 1].isspace():
            index += 1
        fields.append(int(data[start:index]))
    index += 1
    width, height, _maximum = fields
    pixels = data[index : index + width * height * 3]
    return width, height, pixels


WIDTH, HEIGHT, PIXELS = read_ppm(PATH)


def pixel(x, y):
    offset = (y * WIDTH + x) * 3
    return PIXELS[offset], PIXELS[offset + 1], PIXELS[offset + 2]


def row_is_divider(y):
    light = 0
    for x in range(0, WIDTH, 4):
        r, g, b = pixel(x, y)
        if r > 235 and g > 235 and b > 235:
            light += 1
    return light > (WIDTH // 4) * 0.9


def column_is_divider(x):
    light = 0
    for y in range(0, HEIGHT, 4):
        r, g, b = pixel(x, y)
        if r > 235 and g > 235 and b > 235:
            light += 1
    return light > (HEIGHT // 4) * 0.9


divider_rows = [y for y in range(HEIGHT) if row_is_divider(y)]
divider_columns = [x for x in range(WIDTH) if column_is_divider(x)]


def groups(values):
    result = []
    for value in values:
        if result and value == result[-1][-1] + 1:
            result[-1].append(value)
        else:
            result.append([value])
    return [(group[0], group[-1]) for group in result]


print("size", WIDTH, HEIGHT)
print("divider rows", groups(divider_rows))
print("divider columns", groups(divider_columns))

# Sample the panel background and a few shark pixels for contrast notes.
for (x, y, label) in [
    (30, 30, "top-left panel corner"),
    (WIDTH - 30, 30, "top-right corner"),
    (30, HEIGHT - 30, "bottom-left corner"),
]:
    print(label, pixel(x, y))
