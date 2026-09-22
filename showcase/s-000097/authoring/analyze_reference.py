"""Trace a road image into measurable scene data.

Two tracing modes share one decoder and one ridge walker:

  * reference mode classifies the bright, low-saturation asphalt band in the
    aerial photo (reference/reference.png) and walks the ridge of a chamfer
    distance transform to recover an ordered centerline;
  * red mode classifies a saturated red probe ribbon rendered by
    authoring/fit-probe.motionloom, used to measure exactly where the scene
    camera projects the road.

Usage (from the workspace root):
    python3 .../analyze_reference.py trace PHOTO.png OUT.json [--red]
    python3 .../analyze_reference.py mask  PHOTO.png OUT.png [--red]
"""

import json
import math
import os
import struct
import sys
import zlib

DOWNSCALE = 2


def decode_png(path):
    """Decode an 8-bit RGB/RGBA PNG into (width, height, bytearray RGB)."""
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    pos = 8
    width = height = None
    bit_depth = color_type = None
    idat = bytearray()
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        chunk = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if chunk == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(">IIBB", payload[:10])
        elif chunk == b"IDAT":
            idat += payload
        elif chunk == b"IEND":
            break
    if bit_depth != 8 or color_type not in (2, 6):
        raise ValueError("expected 8-bit RGB or RGBA PNG")
    channels = 3 if color_type == 2 else 4
    raw = zlib.decompress(bytes(idat))
    stride = width * channels
    out = bytearray(width * height * 3)
    previous = bytearray(stride)
    for y in range(height):
        filter_type = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            left = line[i - channels] if i >= channels else 0
            up = previous[i]
            up_left = previous[i - channels] if i >= channels else 0
            value = line[i]
            if filter_type == 1:
                value = (value + left) & 0xFF
            elif filter_type == 2:
                value = (value + up) & 0xFF
            elif filter_type == 3:
                value = (value + (left + up) // 2) & 0xFF
            elif filter_type == 4:
                p = left + up - up_left
                pa, pb, pc = abs(p - left), abs(p - up), abs(p - up_left)
                pred = left if (pa <= pb and pa <= pc) else (up if pb <= pc else up_left)
                value = (value + pred) & 0xFF
            line[i] = value
        previous = line
        row = y * width * 3
        for x in range(width):
            src = x * channels
            out[row + x * 3] = line[src]
            out[row + x * 3 + 1] = line[src + 1]
            out[row + x * 3 + 2] = line[src + 2]
    return width, height, out


def write_png(path, width, height, rgb):
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        raw += rgb[y * width * 3:(y + 1) * width * 3]

    def chunk(tag, payload):
        return (struct.pack(">I", len(payload)) + tag + payload
                + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
                           + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
                           + chunk(b"IEND", b""))


def is_asphalt(r, g, b):
    """Bright, low-saturation pixels: asphalt, edge paint and pale rock."""
    brightness = (r + g + b) / 3.0
    spread = max(r, g, b) - min(r, g, b)
    return brightness > 118 and spread < 26


def is_red(r, g, b):
    return r > 110 and r - max(g, b) > 55


def build_mask(width, height, rgb, mode):
    test = is_red if mode == "red" else is_asphalt
    mask = bytearray(width * height)
    for i in range(width * height):
        if test(rgb[i * 3], rgb[i * 3 + 1], rgb[i * 3 + 2]):
            mask[i] = 1
    for _ in range(2):
        nxt = bytearray(mask)
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                total = 0
                for dy in (-1, 0, 1):
                    row = (y + dy) * width + x
                    total += mask[row - 1] + mask[row] + mask[row + 1]
                nxt[y * width + x] = 1 if total >= 6 else (0 if total <= 3 else mask[y * width + x])
        mask = nxt
    return mask


def distance_transform(mask, width, height):
    big = 1 << 20
    dist = [0 if not value else big for value in mask]
    for y in range(height):
        base = y * width
        for x in range(width):
            i = base + x
            if not mask[i]:
                continue
            best = dist[i]
            if x > 0:
                best = min(best, dist[i - 1] + 3)
                if y > 0:
                    best = min(best, dist[i - width - 1] + 4)
                if y < height - 1:
                    best = min(best, dist[i + width - 1] + 4)
            if y > 0:
                best = min(best, dist[i - width] + 3)
            if y < height - 1:
                best = min(best, dist[i + width] + 3)
            if x < width - 1:
                best = min(best, dist[i + 1] + 3)
                if y > 0:
                    best = min(best, dist[i - width + 1] + 4)
                if y < height - 1:
                    best = min(best, dist[i + width + 1] + 4)
            dist[i] = best
    for y in range(height - 1, -1, -1):
        base = y * width
        for x in range(width - 1, -1, -1):
            i = base + x
            if not mask[i]:
                continue
            best = dist[i]
            if x < width - 1:
                best = min(best, dist[i + 1] + 3)
                if y > 0:
                    best = min(best, dist[i - width + 1] + 4)
                if y < height - 1:
                    best = min(best, dist[i + width + 1] + 4)
            if y > 0:
                best = min(best, dist[i - width] + 3)
            if y < height - 1:
                best = min(best, dist[i + width] + 3)
            if x > 0:
                best = min(best, dist[i - 1] + 3)
                if y > 0:
                    best = min(best, dist[i - width - 1] + 4)
                if y < height - 1:
                    best = min(best, dist[i + width - 1] + 4)
            dist[i] = best
    return dist


def largest_component(mask, width, height):
    """Keep only the biggest 4-connected mask blob (drops stray gray patches)."""
    labels = [-1] * (width * height)
    best_label, best_size = -1, 0
    label = 0
    for start in range(width * height):
        if not mask[start] or labels[start] >= 0:
            continue
        stack = [start]
        labels[start] = label
        size = 0
        while stack:
            i = stack.pop()
            size += 1
            x, y = i % width, i // width
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < width and 0 <= ny < height:
                    j = ny * width + nx
                    if mask[j] and labels[j] < 0:
                        labels[j] = label
                        stack.append(j)
        if size > best_size:
            best_size, best_label = size, label
        label += 1
    return bytearray(1 if labels[i] == best_label else 0 for i in range(width * height))


def walk_ridge(mask, dist, width, height, start, angle):
    """Greedy walk along the distance-transform ridge in one direction."""
    step = 5.0
    path = [(start[0], start[1])]
    x, y = start
    for _ in range(6000):
        candidates = []
        for offset in (range(-180, 181, 6) if angle is None else range(-60, 61, 6)):
            direction = offset if angle is None else angle + offset
            radians = direction * math.pi / 180.0
            nx = x + step * math.cos(radians)
            ny = y + step * math.sin(radians)
            ix, iy = int(nx + 0.5), int(ny + 0.5)
            if ix < 1 or iy < 1 or ix >= width - 1 or iy >= height - 1:
                continue
            if not mask[iy * width + ix]:
                continue
            candidates.append((dist[iy * width + ix], direction, nx, ny))
        if not candidates:
            break
        candidates.sort(reverse=True)
        score, direction, nx, ny = candidates[0]
        if score < 6:
            break
        angle = direction
        x, y = nx, ny
        path.append((x, y))
    return path


def track_centerline(mask, dist, width, height):
    """Walk the ridge out from its widest point in both directions."""
    start_index, best = 0, -1.0
    for index, value in enumerate(dist):
        if mask[index] and value > best:
            best, start_index = value, index
    start = (float(start_index % width), float(start_index // width))
    forward = walk_ridge(mask, dist, width, height, start, None)
    if len(forward) > 1:
        angle = math.degrees(math.atan2(forward[1][1] - start[1], forward[1][0] - start[0]))
    else:
        angle = None
    backward = walk_ridge(mask, dist, width, height, start, None if angle is None else angle + 180.0)
    return list(reversed(backward[1:])) + forward


def simplify(path, minimum=12.0):
    simplified = [path[0]]
    for point in path[1:-1]:
        px, py = simplified[-1]
        if (point[0] - px) ** 2 + (point[1] - py) ** 2 >= minimum * minimum:
            simplified.append(point)
    simplified.append(path[-1])
    return simplified


def trace(image_path, mode):
    width, height, rgb = decode_png(image_path)
    original_w, original_h = width, height
    if DOWNSCALE > 1:
        small_w, small_h = width // DOWNSCALE, height // DOWNSCALE
        small = bytearray(small_w * small_h * 3)
        for y in range(small_h):
            row = y * DOWNSCALE * width * 3
            for x in range(small_w):
                src = row + x * DOWNSCALE * 3
                dst = (y * small_w + x) * 3
                small[dst] = rgb[src]
                small[dst + 1] = rgb[src + 1]
                small[dst + 2] = rgb[src + 2]
        width, height, rgb = small_w, small_h, small
    mask = build_mask(width, height, rgb, mode)
    mask = largest_component(mask, width, height)
    dist = distance_transform(mask, width, height)
    path = track_centerline(mask, dist, width, height)
    simplified = simplify(path)
    records = []
    for x, y in simplified:
        ix, iy = int(x + 0.5), int(y + 0.5)
        half_width = dist[iy * width + ix] / 4.0 * DOWNSCALE
        records.append({"x": round(x * DOWNSCALE, 1), "y": round(y * DOWNSCALE, 1),
                        "halfWidth": round(half_width, 1)})
    return {"imageWidth": original_w, "imageHeight": original_h, "points": records}, \
        (width, height, mask, dist, path)


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 1
    command, image_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    mode = "red" if "--red" in sys.argv else "reference"
    if command == "trace":
        data, _ = trace(image_path, mode)
        json.dump(data, open(out_path, "w"), indent=1)
        print(f"{image_path}: {len(data['points'])} waypoints -> {out_path}")
        return 0
    if command == "mask":
        _, (width, height, mask, dist, path) = trace(image_path, mode)
        overlay = bytearray(width * height * 3)
        for i in range(width * height):
            value = max(40, 255 - dist[i] // 2)
            overlay[i * 3] = overlay[i * 3 + 1] = overlay[i * 3 + 2] = value if mask[i] else 40
        for x, y in path:
            ix, iy = int(x + 0.5), int(y + 0.5)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    i = (iy + dy) * width + (ix + dx)
                    overlay[i * 3] = 255
                    overlay[i * 3 + 1] = 40
                    overlay[i * 3 + 2] = 40
        write_png(out_path, width, height, overlay)
        print(f"{image_path}: mask overlay -> {out_path}")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
