"""Fill enclosed holes in the threshold-12 bottom mask and emit MaskData RLE.

The bottom panel is a white shark on a light-gray background: the belly sits
within a few gray levels of the backdrop, so the threshold mask has interior
gaps. Anything not reachable from the image border is interior and becomes
foreground.
"""

import json
from collections import deque

mask = json.load(open("analysis/pass2-bottom/analysis.json"))["foregroundMask"]
width, height = mask["width"], mask["height"]
pixels = bytearray(width * height)
value = 1 if mask["startsForeground"] else 0
index = 0
for run in mask["runs"]:
    for offset in range(run):
        pixels[index + offset] = value
    value ^= 1
    index += run
assert index == width * height

reachable = bytearray(width * height)
queue = deque()
for x in range(width):
    for y in (0, height - 1):
        i = y * width + x
        if not pixels[i] and not reachable[i]:
            reachable[i] = 1
            queue.append(i)
for y in range(height):
    for x in (0, width - 1):
        i = y * width + x
        if not pixels[i] and not reachable[i]:
            reachable[i] = 1
            queue.append(i)
while queue:
    current = queue.popleft()
    x = current % width
    y = current // width
    for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
        if 0 <= nx < width and 0 <= ny < height:
            i = ny * width + nx
            if not pixels[i] and not reachable[i]:
                reachable[i] = 1
                queue.append(i)

filled = [1 if (pixels[i] or not reachable[i]) else 0 for i in range(width * height)]
removed = sum(1 for i in range(width * height) if pixels[i] and not filled[i])
added = sum(1 for i in range(width * height) if not pixels[i] and filled[i])
print("filled mask: added", added, "pixels, removed", removed)

starts = filled[0] == 1
runs = []
current = starts
count = 0
for pixel in filled:
    bit = pixel == 1
    if bit == current:
        count += 1
    else:
        runs.append(count)
        current = bit
        count = 1
runs.append(count)

json.dump(
    {"width": width, "height": height, "startsForeground": starts, "runs": runs},
    open("authoring/bottom-supplied-mask.json", "w"),
)
print("wrote authoring/bottom-supplied-mask.json with", len(runs), "runs")

# Simple PNG dump for visual inspection.
import struct
import zlib


def png_bytes(mask_pixels):
    rows = []
    for y in range(height):
        row = bytearray()
        for x in range(width):
            row.extend((255, 255, 255) if mask_pixels[y * width + x] else (0, 0, 0))
        rows.append(bytes(row))

    def chunk(tag, payload):
        data = tag + payload
        return struct.pack(">I", len(payload)) + data + struct.pack(">I", zlib.crc32(data) & 0xFFFFFFFF)

    raw = bytearray()
    for row in rows:
        raw.append(0)
        raw.extend(row)
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    with open("analysis/bottom-filled-mask.png", "wb") as handle:
        handle.write(b"\x89PNG\r\n\x1a\n")
        handle.write(chunk(b"IHDR", header))
        handle.write(chunk(b"IDAT", zlib.compress(bytes(raw), 6)))
        handle.write(chunk(b"IEND", b""))


png_bytes(filled)
print("wrote analysis/bottom-filled-mask.png")
