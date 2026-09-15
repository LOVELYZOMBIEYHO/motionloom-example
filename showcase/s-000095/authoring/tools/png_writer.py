"""Minimal RGB PNG writer (pure Python) for diagnostic overlays."""

import struct
import zlib


def write_png(path, width, height, rgb_rows):
    raw = bytearray()
    for row in rgb_rows:
        raw.append(0)
        raw.extend(row)
    compressed = zlib.compress(bytes(raw), 6)

    def chunk(tag, payload):
        data = tag + payload
        return (
            struct.pack(">I", len(payload))
            + data
            + struct.pack(">I", zlib.crc32(data) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    with open(path, "wb") as handle:
        handle.write(b"\x89PNG\r\n\x1a\n")
        handle.write(chunk(b"IHDR", header))
        handle.write(chunk(b"IDAT", compressed))
        handle.write(chunk(b"IEND", b""))


class Canvas:
    def __init__(self, width, height, background=(24, 24, 28)):
        self.width = width
        self.height = height
        self.pixels = [[list(background) for _ in range(width)] for _ in range(height)]

    def set(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = list(color)

    def dot(self, x, y, color, radius=2):
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                self.set(int(x) + dx, int(y) + dy, color)

    def line(self, a, b, color):
        x0, y0 = a
        x1, y1 = b
        steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for step in range(steps + 1):
            t = step / steps
            self.set(int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t)), color)

    def save(self, path):
        rows = [bytes(channel for pixel in row for channel in pixel) for row in self.pixels]
        write_png(path, self.width, self.height, rows)
