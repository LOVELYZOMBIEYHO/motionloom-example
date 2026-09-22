"""Fit the road placement so the render lands on the photo's road.

The probe scene draws only the asphalt ribbon as a red emissive strip on a
black background with the showcase camera. For every photo waypoint the script
looks for the ridge (centre) of the rendered red strip inside a small search
window around the current prediction and folds the measured residual back into
authoring/road-offsets.json, the image-space correction build_scene.py applies
to the traced centerline.

This local measurement is deliberately simpler than tracing the probe with the
full ridge walker: the probe draw is the projection of the same centerline, so
the rendered road is always within a few tens of pixels of the prediction and
a windowed ridge snap cannot take a wrong turn at a hairpin.

Run from the workspace root:
    python3 motionloom-example/showcase/s-000097/authoring/fit_road.py --iters 10
"""

import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PROBE = os.path.join(HERE, "fit-probe.motionloom")
PROBE_PNG = os.path.join(WORKSPACE, ".render-output", "s97-probe.png")
RENDER_BIN = os.path.join(WORKSPACE, "anica", "target", "release", "examples", "render_file_frame")
PATH_JSON = os.path.join(HERE, "road-path.json")
OFFSETS_JSON = os.path.join(HERE, "road-offsets.json")
sys.path.insert(0, HERE)
import analyze_reference  # noqa: E402


def probe_mask():
    """Render the probe and return (mask, distance, width, height) at trace scale."""
    subprocess.run([sys.executable, os.path.join(HERE, "build_scene.py"), "probe"],
                   check=True, cwd=WORKSPACE, stdout=subprocess.DEVNULL)
    subprocess.run([RENDER_BIN, PROBE, PROBE_PNG, "0", "gpu"], check=True,
                   stdout=subprocess.DEVNULL)
    width, height, rgb = analyze_reference.decode_png(PROBE_PNG)
    mask = analyze_reference.build_mask(width, height, rgb, "red")
    mask = analyze_reference.largest_component(mask, width, height)
    dist = analyze_reference.distance_transform(mask, width, height)
    return mask, dist, width, height


def ridge_near(mask, dist, width, height, px, py, radius):
    """Subpixel centre of the red strip ridge inside a window, or None."""
    ix, iy = int(px + 0.5), int(py + 0.5)
    best = 0
    for y in range(max(1, iy - radius), min(height - 1, iy + radius)):
        base = y * width
        for x in range(max(1, ix - radius), min(width - 1, ix + radius)):
            if mask[base + x] and dist[base + x] > best:
                best = dist[base + x]
    if best < 12:
        return None
    total_x = total_y = weight = 0.0
    for y in range(max(1, iy - radius), min(height - 1, iy + radius)):
        base = y * width
        for x in range(max(1, ix - radius), min(width - 1, ix + radius)):
            value = dist[base + x]
            if mask[base + x] and value >= best - 6:
                total_x += x * value
                total_y += y * value
                weight += value
    if weight == 0.0:
        return None
    return total_x / weight, total_y / weight


def measure(offsets, radius=40):
    mask, dist, width, height = probe_mask()
    reference = json.load(open(PATH_JSON))["points"]
    residuals = []
    for index, point in enumerate(reference):
        prediction_x = point["x"] + offsets[index][0]
        prediction_y = point["y"] + offsets[index][1]
        ridge = ridge_near(mask, dist, width, height,
                           prediction_x, prediction_y, radius)
        if ridge is None:
            residuals.append([0.0, 0.0])
            continue
        residuals.append([point["x"] - ridge[0], point["y"] - ridge[1]])
    error = sum(math.hypot(dx, dy) for dx, dy in residuals) / len(residuals)
    return residuals, error


def main():
    iterations = 8
    if "--iters" in sys.argv:
        iterations = int(sys.argv[sys.argv.index("--iters") + 1])
    offsets = [[0.0, 0.0] for _ in json.load(open(PATH_JSON))["points"]]
    if os.path.exists(OFFSETS_JSON):
        offsets = json.load(open(OFFSETS_JSON))["offsets"]
    residuals, error = measure(offsets)
    print(f"baseline: residual {error:.1f}px")
    step_x, step_y = 0.6, 0.4
    best_offsets, best_error = [row[:] for row in offsets], error
    for iteration in range(iterations):
        candidate = [[offsets[i][0] + residuals[i][0] * step_x,
                      offsets[i][1] + residuals[i][1] * step_y]
                     for i in range(len(offsets))]
        residuals, error = measure(candidate)
        if error <= best_error:
            print(f"iteration {iteration}: {best_error:.1f} -> {error:.1f}px "
                  f"steps ({step_x:.2f},{step_y:.2f})")
            best_offsets, best_error = [row[:] for row in candidate], error
            offsets = candidate
        else:
            step_x *= 0.5
            step_y *= 0.5
            print(f"iteration {iteration}: grew to {error:.1f}px, "
                  f"halving steps to ({step_x:.3f},{step_y:.3f})")
            offsets = [row[:] for row in best_offsets]
            residuals, error = measure(offsets)
        json.dump({"offsets": best_offsets}, open(OFFSETS_JSON, "w"), indent=1)
        if best_error < 2.5 or (step_x < 0.02 and step_y < 0.02):
            break
    json.dump({"offsets": best_offsets}, open(OFFSETS_JSON, "w"), indent=1)
    print(f"final residual {best_error:.1f}px; wrote {OFFSETS_JSON}")


if __name__ == "__main__":
    sys.exit(main())
