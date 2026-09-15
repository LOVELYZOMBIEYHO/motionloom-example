"""Compare reference and candidate mask extents per image row."""

import json
import sys

EVAL = sys.argv[1] if len(sys.argv) > 1 else "fit/calib-1/evaluation.json"
STEP = int(sys.argv[2]) if len(sys.argv) > 2 else 20

evaluation = json.load(open(EVAL))


def decode(mask):
    width, height = mask["width"], mask["height"]
    pixels = bytearray(width * height)
    value = 1 if mask["startsForeground"] else 0
    index = 0
    for run in mask["runs"]:
        for offset in range(run):
            pixels[index + offset] = value
        value ^= 1
        index += run
    return pixels, width, height


for view in evaluation["views"]:
    reference = json.load(open(f"analysis/ref-{view['id']}/analysis.json"))
    ref_pixels, width, height = decode(reference["foregroundMask"])
    cand_pixels, _, _ = decode(view["candidateMask"])
    print(f"== {view['id']} iou={view['maskIou']:.4f} p95={view['p95EdgeDistancePx']:.1f}")
    for y in range(0, height, STEP):
        row = y * width
        xs = [x for x in range(width) if ref_pixels[row + x]]
        cs = [x for x in range(width) if cand_pixels[row + x]]
        if not xs and not cs:
            continue
        ref_text = f"({min(xs)},{max(xs)})" if xs else "none"
        cand_text = f"({min(cs)},{max(cs)})" if cs else "none"
        delta = ""
        if xs and cs:
            delta = f" dL={min(cs)-min(xs):+4d} dR={max(cs)-max(xs):+4d}"
        print(f"  y={y:3d} ref={ref_text:>12} cand={cand_text:>12}{delta}")
