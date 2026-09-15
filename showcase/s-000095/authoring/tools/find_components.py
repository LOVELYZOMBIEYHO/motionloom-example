"""Locate the shark and the text labels inside each quadrant of the composite."""

import sys
from collections import deque

sys.argv = ["panels.py"]
exec(open("tools/panels.py").read().split("divider_rows =")[0])

BACKGROUND = (183, 184, 185)
THRESHOLD = 14

foreground = bytearray(WIDTH * HEIGHT)
for y in range(HEIGHT):
    for x in range(WIDTH):
        r, g, b = pixel(x, y)
        if abs(r - BACKGROUND[0]) + abs(g - BACKGROUND[1]) + abs(b - BACKGROUND[2]) > THRESHOLD:
            foreground[y * WIDTH + x] = 1

label = [-1] * (WIDTH * HEIGHT)
components = []
for start in range(WIDTH * HEIGHT):
    if not foreground[start] or label[start] >= 0:
        continue
    index = len(components)
    queue = deque([start])
    label[start] = index
    pixels = []
    while queue:
        current = queue.popleft()
        pixels.append(current)
        x = current % WIDTH
        y = current // WIDTH
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                n = ny * WIDTH + nx
                if foreground[n] and label[n] < 0:
                    label[n] = index
                    queue.append(n)
    components.append(pixels)

components.sort(key=len, reverse=True)

print("quadrants:")
for name, (x0, y0, x1, y1) in {
    "left": (0, 0, WIDTH // 2, HEIGHT // 2),
    "front": (WIDTH // 2, 0, WIDTH, HEIGHT // 2),
    "top": (0, HEIGHT // 2, WIDTH // 2, HEIGHT),
    "bottom": (WIDTH // 2, HEIGHT // 2, WIDTH, HEIGHT),
}.items():
    inside = []
    for pixels in components:
        xs = [p % WIDTH for p in pixels]
        ys = [p // WIDTH for p in pixels]
        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)
        if x0 <= cx < x1 and y0 <= cy < y1 and len(pixels) > 200:
            inside.append(
                {
                    "area": len(pixels),
                    "bbox": [min(xs), min(ys), max(xs), max(ys)],
                }
            )
    inside.sort(key=lambda item: item["area"], reverse=True)
    print(f"== {name}: {len(inside)} components over 200px")
    for item in inside[:5]:
        print("   area", item["area"], "bbox", item["bbox"])
