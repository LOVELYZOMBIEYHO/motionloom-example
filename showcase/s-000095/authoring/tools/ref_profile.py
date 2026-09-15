"""Print reference mask row extents per view for calibration."""

import json
import sys

view = sys.argv[1]
step = int(sys.argv[2]) if len(sys.argv) > 2 else 20
analysis = json.load(open(f"analysis/ref-{view}/analysis.json"))
mask = analysis["foregroundMask"]
width, height = mask["width"], mask["height"]
pixels = bytearray(width * height)
value = 1 if mask["startsForeground"] else 0
index = 0
for run in mask["runs"]:
    for offset in range(run):
        pixels[index + offset] = value
    value ^= 1
    index += run
print(f"== {view} {width}x{height}")
for y in range(0, height, step):
    xs = [x for x in range(width) if pixels[y * width + x]]
    if xs:
        print(f"  y={y:3d} x=[{min(xs):4d},{max(xs):4d}] width={max(xs)-min(xs)+1:4d}")
