"""Build the S97 winding mountain road scene (textured PBR checkpoint).

Rebuilds the reference aerial photo (reference/reference.png) as native
MotionLoom geometry, without Blender or any imported model:

  * a heightfield TerrainAsset whose heightmap is generated here: a steep
    mountainside cut by a flat bench along the traced road centerline, with
    steep cut banks uphill and softer fill slopes downhill;
  * one reusable CurveAsset and SweepAssets for asphalt, paint and guardrails;
  * a dense forest of CompoundAsset trees (primitive trunk/cones/ellipsoids)
    scattered with a deterministic hash grid outside the road corridor.

The road centerline is the trace of the photo, optionally corrected by
authoring/road-offsets.json, which fit_road.py measures from a red probe
render so the scene camera projects the road exactly onto the photo's road.

Run from the workspace root:
    python3 motionloom-example/showcase/s-000097/authoring/build_scene.py
    python3 motionloom-example/showcase/s-000097/authoring/build_scene.py probe
"""

import json
import math
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SHOWCASE = os.path.join(WORKSPACE, "motionloom-example", "showcase", "s-000097")
MAIN_OUT = os.path.join(SHOWCASE, "main.motionloom")
PROBE_OUT = os.path.join(HERE, "fit-probe.motionloom")
HEIGHT_PNG = os.path.join(SHOWCASE, "assets", "terrain", "s97-height.png")
FOREST_EXCLUSION_PNG = os.path.join(
    SHOWCASE, "assets", "terrain", "s97-forest-exclusion.png")
ROCK_DENSITY_PNG = os.path.join(
    SHOWCASE, "assets", "terrain", "s97-rock-density.png")
PATH_JSON = os.path.join(HERE, "road-path.json")
OFFSETS_JSON = os.path.join(HERE, "road-offsets.json")

# The reference frame maps onto a 254 x 143 m patch of mountainside
# (0.152 m per pixel, which makes the photo's asphalt band a real two-lane
# mountain road about 8.4 m wide). The terrain extends past that patch so a
# tilted camera never sees its edge.
IMAGE_W, IMAGE_H = 1672, 941
WORLD_W, WORLD_H = 254.0, 143.0
METERS_PER_PIXEL = WORLD_W / (IMAGE_W - 1)
TERRAIN_W, TERRAIN_H = 318.0, 179.0

# Everything above is authored in "site units" (metres of imaginary terrain).
# The document itself is emitted at 1:20 because the engine's directional
# shadow volume is a fixed 28 m box: a full-size mountainside would fall
# outside it and receive no cast shadows at all. A scale model keeps every
# ratio identical while shadows, AO, and depth resolution work as designed.
SCALE = 0.05

# Terrain mesh resolution: 0.333 site-m per height texel at full LOD.
HM_W, HM_H = 954, 537


def sc(value):
    return value * SCALE

# Road bench shaping.
BENCH_DROP = 0.30
BENCH_HALF = 3.6
CUT_BLEND = 2.2
FILL_BLEND = 4.5
CROWN = 0.10
ASPHALT_HALF = 2.75

# Mountainside falls toward the bottom-right of the reference frame.
FALL_DIR = (0.55, 0.835)
FALL_SLOPE = 0.335

# Forest scatter.
TREE_SPACING = 2.2
TREE_JITTER = 1.0

# Aerial camera: near-nadir with a slight tilt toward the viewer's side.
# Camera3D fov is the horizontal field of view in degrees. fit_road.py refines
# the distance, fov and lateral offsets in authoring/camera.json.
# Camera3D fov is the vertical field of view and the renderer clamps it to a
# 10 degree minimum, so the framing distance follows from the footprint.
CAMERA_TILT_DEG = 5.0
CAMERA_DISTANCE = 807.3
CAMERA_FOV = 10.0


# --------------------------------------------------------------------------
# deterministic noise helpers
# --------------------------------------------------------------------------

def hash2(ix, iy, seed):
    value = (ix * 374761393 + iy * 668265263 + seed * 1442695040888963407) & 0xFFFFFFFF
    value = (value ^ (value >> 13)) * 1274126177 & 0xFFFFFFFF
    value = (value ^ (value >> 16)) & 0xFFFFFFFF
    return value / 4294967295.0


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def value_noise(x, z, seed):
    ix, iz = math.floor(x), math.floor(z)
    fx, fz = x - ix, z - iz
    ux, uz = smoothstep(fx), smoothstep(fz)
    a = hash2(ix, iz, seed)
    b = hash2(ix + 1, iz, seed)
    c = hash2(ix, iz + 1, seed)
    d = hash2(ix + 1, iz + 1, seed)
    return (a * (1 - ux) + b * ux) * (1 - uz) + (c * (1 - ux) + d * ux) * uz


def fbm(x, z, seed, octaves):
    total = 0.0
    amplitude = 1.0
    frequency = 1.0
    norm = 0.0
    for index in range(octaves):
        total += amplitude * (value_noise(x * frequency, z * frequency,
                                          seed + index * 17) * 2.0 - 1.0)
        norm += amplitude
        amplitude *= 0.5
        frequency *= 2.04
    return total / norm


def natural_height(x, z):
    """Undulating mountainside before the road bench is carved."""
    base = -FALL_SLOPE * (x * FALL_DIR[0] + z * FALL_DIR[1])
    base += 5.4 * fbm(x / 78.0, z / 78.0, 11, 3)
    base += 1.9 * fbm(x / 26.0, z / 26.0, 23, 3)
    base += 0.55 * fbm(x / 7.4, z / 7.4, 41, 2)
    return base


# --------------------------------------------------------------------------
# road centerline
# --------------------------------------------------------------------------

def load_centerline():
    """Traced photo waypoints (image px) mapped to world meters, plus any
    correction measured from the previous probe render."""
    data = json.load(open(PATH_JSON))
    offsets = None
    if os.path.exists(OFFSETS_JSON):
        offsets = json.load(open(OFFSETS_JSON))["offsets"]
    points = []
    for index, point in enumerate(data["points"]):
        px = point["x"] + (offsets[index][0] if offsets else 0.0)
        py = point["y"] + (offsets[index][1] if offsets else 0.0)
        points.append([px, py, point["halfWidth"] * METERS_PER_PIXEL])

    # The probe fit nudges every waypoint independently, so its corrections
    # carry per-point noise. Two smoothing passes keep the traced curvature
    # (the hairpins survive) while removing the jitter that would otherwise
    # render as kinks in the ribbon.
    for _ in range(2):
        smoothed = [points[0][:]]
        for index in range(1, len(points) - 1):
            smoothed.append([(points[index - 1][axis] + 2 * points[index][axis]
                              + points[index + 1][axis]) / 4.0 for axis in range(3)])
        smoothed.append(points[-1][:])
        points = smoothed
    points = [(p[0] * METERS_PER_PIXEL - WORLD_W * 0.5,
               p[1] * METERS_PER_PIXEL - WORLD_H * 0.5, p[2]) for p in points]
    dense = []
    spacing = 0.5
    for index in range(len(points) - 1):
        p0 = points[max(0, index - 1)]
        p1 = points[index]
        p2 = points[index + 1]
        p3 = points[min(len(points) - 1, index + 2)]
        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        steps = max(2, int(length / spacing))
        for step in range(steps):
            t = step / steps
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            z = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            dense.append([x, z, p1[2]])
    dense.append([points[-1][0], points[-1][1], points[-1][2]])
    return dense


def road_profile(dense):
    """Smooth, monotone-climbing road elevation sampled on the centerline."""
    heights = [natural_height(p[0], p[1]) for p in dense]
    count = len(heights)
    for _ in range(6):
        smoothed = heights[:]
        for index in range(count):
            lo = max(0, index - 9)
            hi = min(count, index + 10)
            smoothed[index] = sum(heights[lo:hi]) / (hi - lo)
        heights = smoothed
    # The traced path starts at the high end (top-left of the photo); clamp any
    # residual uphill wobble so the profile only ever climbs that way.
    for index in range(count - 2, -1, -1):
        heights[index] = max(heights[index], heights[index + 1])
    for _ in range(3):
        smoothed = heights[:]
        for index in range(1, count - 1):
            smoothed[index] = (heights[index - 1] + 2 * heights[index]
                                + heights[index + 1]) / 4.0
        heights = smoothed
    for index, point in enumerate(dense):
        point.append(heights[index])
    return dense


# --------------------------------------------------------------------------
# bench carving on the heightmap
# --------------------------------------------------------------------------

def carve_terrain(dense):
    """Rasterize the road corridor onto the height grid."""
    cell_x = TERRAIN_W / (HM_W - 1)
    cell_z = TERRAIN_H / (HM_H - 1)
    distance = [1e9] * (HM_W * HM_H)
    road_h = [0.0] * (HM_W * HM_H)

    step = 6
    reach = BENCH_HALF + FILL_BLEND + 2.0
    for start in range(0, len(dense) - step, step):
        ax, az = dense[start][0], dense[start][1]
        bx, bz = dense[start + step][0], dense[start + step][1]
        height_a = dense[start][3]
        height_b = dense[start + step][3]
        margin = reach + 0.5
        min_x = int((min(ax, bx) - margin + TERRAIN_W * 0.5) / cell_x) - 1
        max_x = int((max(ax, bx) + margin + TERRAIN_W * 0.5) / cell_x) + 1
        min_z = int((min(az, bz) - margin + TERRAIN_H * 0.5) / cell_z) - 1
        max_z = int((max(az, bz) + margin + TERRAIN_H * 0.5) / cell_z) + 1
        min_x, max_x = max(0, min_x), min(HM_W - 1, max_x)
        min_z, max_z = max(0, min_z), min(HM_H - 1, max_z)
        dx, dz = bx - ax, bz - az
        length_sq = dx * dx + dz * dz
        for iz in range(min_z, max_z + 1):
            wz = iz * cell_z - TERRAIN_H * 0.5
            base = iz * HM_W
            for ix in range(min_x, max_x + 1):
                wx = ix * cell_x - TERRAIN_W * 0.5
                t = 0.0 if length_sq == 0 else ((wx - ax) * dx + (wz - az) * dz) / length_sq
                t = max(0.0, min(1.0, t))
                px, pz = ax + dx * t, az + dz * t
                d = math.hypot(wx - px, wz - pz)
                if d < distance[base + ix]:
                    distance[base + ix] = d
                    road_h[base + ix] = height_a + (height_b - height_a) * t

    heights = [0.0] * (HM_W * HM_H)
    for iz in range(HM_H):
        wz = iz * cell_z - TERRAIN_H * 0.5
        base = iz * HM_W
        for ix in range(HM_W):
            wx = ix * cell_x - TERRAIN_W * 0.5
            natural = natural_height(wx, wz)
            d = distance[base + ix]
            if d > 1e8:
                heights[base + ix] = natural
                continue
            bench = road_h[base + ix] - BENCH_DROP
            if d <= BENCH_HALF:
                heights[base + ix] = bench
                continue
            blend = CUT_BLEND if natural > bench else FILL_BLEND
            if d >= BENCH_HALF + blend:
                heights[base + ix] = natural
                continue
            t = smoothstep((d - BENCH_HALF) / blend)
            heights[base + ix] = bench + (natural - bench) * t
    return heights, distance, road_h


# --------------------------------------------------------------------------
# PNG writer
# --------------------------------------------------------------------------

def write_png_rgba(path, width, height, values):
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        row = y * width
        for x in range(width):
            value = values[row + x]
            raw += bytes((value, value, value, 255))

    def chunk(tag, payload):
        return (struct.pack(">I", len(payload)) + tag + payload
                + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))

    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
                           + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
                           + chunk(b"IEND", b""))


# --------------------------------------------------------------------------
# reusable curve and sweep emission
# --------------------------------------------------------------------------

def point_segment_distance_3d(point, start, end):
    """Distance used by deterministic RDP curve simplification."""
    delta = [end[axis] - start[axis] for axis in range(3)]
    relative = [point[axis] - start[axis] for axis in range(3)]
    denominator = sum(value * value for value in delta)
    ratio = sum(relative[axis] * delta[axis] for axis in range(3)) / denominator \
        if denominator > 1e-12 else 0.0
    ratio = max(0.0, min(1.0, ratio))
    closest = [start[axis] + delta[axis] * ratio for axis in range(3)]
    return math.sqrt(sum((point[axis] - closest[axis]) ** 2 for axis in range(3)))


def simplify_curve(points, tolerance=0.08):
    """Bound centerline deviation while removing dense generated samples."""
    if len(points) <= 2:
        return points
    furthest_index = 0
    furthest_distance = -1.0
    for index in range(1, len(points) - 1):
        distance = point_segment_distance_3d(points[index], points[0], points[-1])
        if distance > furthest_distance:
            furthest_distance = distance
            furthest_index = index
    if furthest_distance <= tolerance:
        return [points[0], points[-1]]
    left = simplify_curve(points[:furthest_index + 1], tolerance)
    right = simplify_curve(points[furthest_index:], tolerance)
    return left[:-1] + right


def curve_asset_lines(dense):
    """Emit one shared centerline with a sub-pixel simplification bound."""
    source = [[point[0], point[3], point[1]] for point in dense]
    points = simplify_curve(source)
    lines = [f'    <CurveAsset id="s97_road_curve" interpolation="linear" '
             f'maxSegmentLength="{sc(0.5):.5f}">']
    for x, y, z in points:
        lines.append("      <CurvePoint position={[%.5f,%.5f,%.5f]} />"
                     % (sc(x), sc(y), sc(z)))
    lines.append("    </CurveAsset>")
    print(f"road curve: {len(dense)} dense samples -> {len(points)} control points; "
          f"max deviation <= {sc(0.08):.4f} scene units")
    return lines


def sweep_asset(asset_id, material, profile, dash=None, closed=False):
    """Emit one generic curve/profile sweep using the shared road curve."""
    dash_attr = "" if dash is None else \
        f' dash={{[{sc(dash[0]):.5f},{sc(dash[1]):.5f}]}}'
    smooth_attr = "" if closed else ' smoothProfile="true"'
    lines = [f'    <SweepAsset id="{asset_id}" curve="s97_road_curve" material="{material}" '
             f'frame="worldUp" uvMode="distance" uvScale={{[1,2]}} '
             f'capStart="true" capEnd="true" collision="none"{smooth_attr}{dash_attr}>',
             f'      <Profile closed="{str(closed).lower()}">']
    for lateral, vertical in profile:
        lines.append("        <ProfilePoint position={[%.6f,%.6f]} />"
                     % (sc(lateral), sc(vertical)))
    lines.extend(["      </Profile>", "    </SweepAsset>"])
    return lines


def crown(offset):
    return CROWN * max(0.0, 1.0 - (abs(offset) / ASPHALT_HALF) ** 2)


def road_mesh_blocks(dense):
    blocks = [curve_asset_lines(dense)]
    blocks.append(sweep_asset("s97_asphalt", "s97_asphalt_mat",
                              [(-ASPHALT_HALF, 0.05), (-1.4, 0.05 + crown(-1.4)),
                               (0.0, 0.05 + CROWN), (1.4, 0.05 + crown(1.4)),
                               (ASPHALT_HALF, 0.05)]))
    # Paint remains raised because the aerial view cannot resolve coplanar surfaces.
    blocks.append(sweep_asset("s97_line_left", "s97_paint_mat",
                              [(-2.52, 0.24 + crown(2.52)),
                               (-2.30, 0.24 + crown(2.30))]))
    blocks.append(sweep_asset("s97_line_right", "s97_paint_mat",
                              [(2.30, 0.24 + crown(2.30)),
                               (2.52, 0.24 + crown(2.52))]))
    blocks.append(sweep_asset("s97_line_center", "s97_paint_mat",
                              [(-0.08, 0.25 + crown(0.08)),
                               (0.08, 0.25 + crown(0.08))], dash=(2.2, 2.8)))
    for tag, offset in (("left", -3.0), ("right", 3.0)):
        width = 0.12
        blocks.append(sweep_asset("s97_guardrail_" + tag, "s97_guardrail_mat",
                                  [(offset - width * 0.5, 0.42),
                                   (offset + width * 0.5, 0.42),
                                   (offset + width * 0.5, 0.92),
                                   (offset - width * 0.5, 0.92)], closed=True))
    return blocks


def road_meshes(dense):
    return [line for block in road_mesh_blocks(dense) for line in block]


# --------------------------------------------------------------------------
# forest
# --------------------------------------------------------------------------

TREE_LIBRARY = {
    # id, leaf material, parts: (primitive id, kind, args, position)
    "a": dict(leaf="s97_leaf_a", parts=[
        ("trunk", "cylinder", "radius=\"0.30\" height=\"3.0\" segments=\"8\"", (0, 1.5, 0)),
        ("cone1", "cone", "radius=\"2.4\" height=\"6.4\" segments=\"12\"", (0, 4.6, 0)),
        ("cone2", "cone", "radius=\"1.7\" height=\"6.0\" segments=\"12\"", (0, 9.0, 0)),
    ]),
    "b": dict(leaf="s97_leaf_a", parts=[
        ("trunk", "cylinder", "radius=\"0.26\" height=\"2.4\" segments=\"8\"", (0, 1.2, 0)),
        ("cone1", "cone", "radius=\"2.9\" height=\"5.2\" segments=\"12\"", (0, 4.1, 0)),
        ("cone2", "cone", "radius=\"2.2\" height=\"4.4\" segments=\"12\"", (0, 7.4, 0)),
        ("cone3", "cone", "radius=\"1.5\" height=\"2.8\" segments=\"12\"", (0, 9.9, 0)),
    ]),
    "c": dict(leaf="s97_leaf_b", parts=[
        ("trunk", "cylinder", "radius=\"0.30\" height=\"2.8\" segments=\"8\"", (0, 1.4, 0)),
        ("cone1", "cone", "radius=\"3.2\" height=\"5.0\" segments=\"12\"", (0, 4.0, 0)),
        ("cone2", "cone", "radius=\"2.4\" height=\"4.6\" segments=\"12\"", (0, 7.6, 0)),
        ("cone3", "cone", "radius=\"1.5\" height=\"3.2\" segments=\"12\"", (0, 10.4, 0)),
    ]),
    "d": dict(leaf="s97_leaf_c", parts=[
        ("trunk", "cylinder", "radius=\"0.42\" height=\"4.0\" segments=\"8\"", (0, 2.0, 0)),
        ("blob1", "sphere", "radius=\"2.9\" segments=\"14\" rings=\"9\"", (0, 5.6, 0)),
        ("blob2", "sphere", "radius=\"2.1\" segments=\"12\" rings=\"8\"", (1.8, 7.0, 0.9)),
      ]),
    "e": dict(leaf="s97_leaf_d", parts=[
        ("trunk", "cylinder", "radius=\"0.46\" height=\"4.4\" segments=\"8\"", (0, 2.2, 0)),
        ("blob1", "sphere", "radius=\"3.2\" segments=\"14\" rings=\"9\"", (0, 6.2, 0)),
        ("blob2", "sphere", "radius=\"2.6\" segments=\"12\" rings=\"8\"", (-2.0, 8.0, 1.1)),
        ("blob3", "sphere", "radius=\"2.2\" segments=\"12\" rings=\"8\"", (1.9, 7.8, -1.3)),
    ]),
    "f": dict(leaf="s97_leaf_d", parts=[
        ("trunk", "cylinder", "radius=\"0.52\" height=\"6.0\" segments=\"8\"", (0, 3.0, 0)),
        ("blob1", "sphere", "radius=\"2.7\" segments=\"14\" rings=\"9\"", (0, 8.0, 0)),
        ("blob2", "sphere", "radius=\"2.3\" segments=\"12\" rings=\"8\"", (1.2, 11.2, -0.8)),
    ]),
}


def scaled_args(args):
    """Rewrite radius/height attributes and radii lists into scaled units."""
    import re
    def scalar(match):
        return '%s="%.6f"' % (match.group(1), sc(float(match.group(2))))
    def radii(match):
        values = [sc(float(value)) for value in match.group(1).split(",")]
        return 'radii="{[%s]}"' % ",".join("%.6f" % value for value in values)
    args = re.sub(r'(radius|height)="([\d.]+)"', scalar, args)
    return re.sub(r'radii="\{\[([\d.,]+)\]\}"', radii, args)


def tree_asset_lines():
    lines = []
    for kind, spec in TREE_LIBRARY.items():
        for part_id, shape, args, _ in spec["parts"]:
            lines.append(f'    <PrimitiveAsset id="s97_{part_id}_{kind}" shape="{shape}" '
                         f'{scaled_args(args)} '
                         f'material="{spec["leaf"] if shape != "cylinder" else "s97_trunk_mat"}" collision="none" />')
        lines.append(f'    <CompoundAsset id="s97_tree_{kind}">')
        for part_id, shape, _, position in spec["parts"]:
            lines.append(f'      <Instance id="{part_id}" asset="s97_{part_id}_{kind}" '
                         f'position={{[{sc(position[0]):.5f},{sc(position[1]):.5f},{sc(position[2]):.5f}]}} />')
        lines.append('    </CompoundAsset>')
    return lines


def scatter_trees(distance, road_h):
    trees = []
    cell_x = TERRAIN_W / (HM_W - 1)
    cell_z = TERRAIN_H / (HM_H - 1)
    root_x = -TERRAIN_W * 0.5
    root_z = -TERRAIN_H * 0.5
    columns = int(TERRAIN_W / TREE_SPACING) + 1
    rows_count = int(TERRAIN_H / TREE_SPACING) + 1
    for row in range(rows_count):
        for column in range(columns):
            x = root_x + column * TREE_SPACING + (hash2(column, row, 7) * 2 - 1) * TREE_JITTER
            z = root_z + row * TREE_SPACING + (hash2(column, row, 19) * 2 - 1) * TREE_JITTER
            ix = max(0, min(HM_W - 1, int((x - root_x) / cell_x + 0.5)))
            iz = max(0, min(HM_H - 1, int((z - root_z) / cell_z + 0.5)))
            d = distance[iz * HM_W + ix]
            if d < BENCH_HALF + 0.35:
                continue
            natural = natural_height(x, z)
            if natural > road_h[iz * HM_W + ix] + 1.4 \
                    and d < BENCH_HALF + CUT_BLEND * 0.5:
                continue
            if hash2(column, row, 31) < 0.03:
                continue
            roll = hash2(column, row, 47)
            kind = ("a" if roll < 0.24 else "b" if roll < 0.48 else "c" if roll < 0.68
                    else "d" if roll < 0.82 else "e" if roll < 0.94 else "f")
            scale = 0.42 + hash2(column, row, 53) * 0.44
            trees.append((x, z, hash2(column, row, 61) * 360.0, scale, kind))
    return trees


# --------------------------------------------------------------------------
# scene assembly
# --------------------------------------------------------------------------

def camera_settings():
    """Camera tuple with optional refinements from the probe fit loop."""
    distance = CAMERA_DISTANCE
    fov = CAMERA_FOV
    cam_x = cam_z = 0.0
    target_x = target_z = 0.0
    camera_json = os.path.join(HERE, "camera.json")
    if os.path.exists(camera_json):
        data = json.load(open(camera_json))
        distance = data.get("distance", distance)
        fov = data.get("fov", fov)
        cam_x = data.get("camX", 0.0)
        cam_z = data.get("camZ", 0.0)
        target_x = data.get("targetX", 0.0)
        target_z = data.get("targetZ", 0.0)
    tilt = math.radians(CAMERA_TILT_DEG)
    return (sc(cam_x), sc(distance * math.cos(tilt)), sc(cam_z + distance * math.sin(tilt))), \
        (sc(target_x), 0.0, sc(target_z)), fov


def background_block(color="#C7D6E2"):
    return [f'  <Background color="{color}" />']


def build(probe=False):
    dense = road_profile(load_centerline())
    if probe:
        # The probe only needs the road ribbon; skipping the terrain carve and
        # the forest keeps the fit loop fast.
        build_probe(dense)
        return
    heights, distance, road_h = carve_terrain(dense)
    min_h = min(heights)
    max_h = max(heights)
    height_offset = math.floor(min_h - 2.0)
    height_scale = max_h - min_h + 5.0
    print(f"terrain height {min_h:.2f} .. {max_h:.2f} offset {height_offset} scale {height_scale:.2f}")

    os.makedirs(os.path.dirname(HEIGHT_PNG), exist_ok=True)
    write_png_rgba(HEIGHT_PNG, HM_W, HM_H, [
        max(0, min(255, int((value - height_offset) / height_scale * 255.0 + 0.5)))
        for value in heights])

    root_x = -TERRAIN_W * 0.5
    root_z = -TERRAIN_H * 0.5
    cell_x = TERRAIN_W / (HM_W - 1)
    cell_z = TERRAIN_H / (HM_H - 1)

    # White texels exclude the carved road corridor while black texels remain
    # available to Scatter on every renderer backend.
    forest_exclusion = []
    rock_density = []
    for iz in range(HM_H):
        z = root_z + iz * cell_z
        for ix in range(HM_W):
            x = root_x + ix * cell_x
            d = distance[iz * HM_W + ix]
            excluded = d < BENCH_HALF + 0.35
            if natural_height(x, z) > road_h[iz * HM_W + ix] + 1.4 \
                    and d < BENCH_HALF + CUT_BLEND * 0.5:
                excluded = True
            forest_exclusion.append(255 if excluded else 0)
            cut_height = natural_height(x, z) - road_h[iz * HM_W + ix]
            near_cut = max(0.0, 1.0 - abs(d - (BENCH_HALF + 1.5)) / 4.8)
            cut_bias = max(0.0, min(1.0, (cut_height + 0.4) / 3.0))
            density = near_cut * (0.35 + 0.65 * cut_bias)
            if d < BENCH_HALF + 0.15:
                density = 0.0
            rock_density.append(max(0, min(255, int(density * 255.0 + 0.5))))
    write_png_rgba(FOREST_EXCLUSION_PNG, HM_W, HM_H, forest_exclusion)
    write_png_rgba(ROCK_DENSITY_PNG, HM_W, HM_H, rock_density)

    trees = scatter_trees(distance, road_h)
    counts = {}
    for tree in trees:
        counts[tree[4]] = counts.get(tree[4], 0) + 1
    print(f"trees: {len(trees)} {counts}")
    emit_main(dense, len(trees), height_scale, height_offset)


def build_probe(dense):
    position, target, fov = camera_settings()
    probe_assets = [line for block in road_mesh_blocks(dense)[:2] for line in block]
    document = f'''<!-- S97 camera-fit probe: red asphalt ribbon on black -->
<Graph fps={{24}} duration="1s" size={{[1920,1080]}} renderSize={{[1920,1080]}}>
  <Assets>
    <MaterialAsset id="s97_asphalt_mat" shading="pbr" baseColor="#FF0000" emissive="#FF0000" emissiveStrength="1.2" roughness="0.9" />
{chr(10).join(probe_assets)}
  </Assets>
{chr(10).join(background_block("#000000"))}
  <Scene id="S97Probe">
    <Timeline>
      <Track id="probe" space="3d" compositeOrder="30">
        <Sequence from="0s" duration="1s" out="hold">
          <CompositeGroup id="probe_island" space="3d" depth="true" format="rgba16f">
            <Camera3D id="s97_aerial" position={{[{position[0]:.3f},{position[1]:.3f},{position[2]:.3f}]}} target={{[{target[0]:.3f},{target[1]:.3f},{target[2]:.3f}]}} fov="{fov}" />
            <Model id="probe_asphalt" asset="s97_asphalt" />
          </CompositeGroup>
        </Sequence>
      </Track>
    </Timeline>
  </Scene>
  <Present from="S97Probe" />
</Graph>
'''
    open(PROBE_OUT, "w").write(document)
    print(f"wrote {PROBE_OUT}")


def build_markers():
    """Five emissive markers at known world points for camera calibration."""
    position, target, fov = camera_settings()
    markers = [
        ("s97_marker_red", "#FF0000", (-127.0, 0.0, -71.5)),
        ("s97_marker_green", "#00FF00", (127.0, 0.0, -71.5)),
        ("s97_marker_blue", "#0000FF", (-127.0, 0.0, 71.5)),
        ("s97_marker_yellow", "#FFFF00", (127.0, 0.0, 71.5)),
        ("s97_marker_magenta", "#FF00FF", (0.0, 0.0, 0.0)),
    ]
    primitives = []
    models = []
    for marker_id, color, world in markers:
        primitives.append(f'    <PrimitiveAsset id="{marker_id}_shape" shape="sphere" radius="{sc(2.0):.5f}" '
                          f'segments="16" rings="10" color="{color}" material="{marker_id}_mat" collision="none" />')
        primitives.append(f'    <MaterialAsset id="{marker_id}_mat" shading="pbr" baseColor="{color}" '
                          f'emissive="{color}" emissiveStrength="4" roughness="0.9" />')
        models.append(f'            <Model id="{marker_id}" asset="{marker_id}_shape" '
                      f'position={{[{sc(world[0]):.5f},{sc(world[1]):.5f},{sc(world[2]):.5f}]}} />')
    document = f'''<!-- S97 camera calibration markers -->
<Graph fps={{24}} duration="1s" size={{[1920,1080]}} renderSize={{[1920,1080]}}>
  <Assets>
{chr(10).join(primitives)}
  </Assets>
  <Background color="#000000" />
  <Scene id="S97Markers">
    <Timeline>
      <Track id="markers" space="3d" compositeOrder="30">
        <Sequence from="0s" duration="1s" out="hold">
          <CompositeGroup id="marker_island" space="3d" depth="true" format="rgba16f">
            <Camera3D id="s97_aerial" position={{[{position[0]:.3f},{position[1]:.3f},{position[2]:.3f}]}} target={{[{target[0]:.3f},{target[1]:.3f},{target[2]:.3f}]}} fov="{fov}" />
{chr(10).join(models)}
          </CompositeGroup>
        </Sequence>
      </Track>
    </Timeline>
  </Scene>
  <Present from="S97Markers" />
</Graph>
'''
    open(os.path.join(HERE, "camera-markers.motionloom"), "w").write(document)
    print("wrote camera-markers.motionloom")


def camera_drift(start, end, duration=12.0, steps=8):
    """Ease-in-out curve expression from `start` to `end` (per channel)."""
    parts = []
    for step in range(steps + 1):
        t = step / steps
        ease = 0.5 - 0.5 * math.cos(math.pi * t)
        parts.append("%.1f:%.5f" % (t * duration, start + (end - start) * ease))
    return "curve(\"%s\")" % ", ".join(part + ":linear" for part in parts)


def emit_main(dense, tree_count, height_scale, height_offset):
    position, target, fov = camera_settings()
    # A slow aerial push-in with a slight lateral drift; frame 0 keeps the
    # fitted reference framing.
    push = 0.978
    pos_x = position[0] + sc(0.35)
    pos_y = position[1] * push
    pos_z = position[2] * push
    tgt_x = target[0] + sc(0.30)
    tgt_z = target[2] - sc(0.10)
    camera_position = "[%s,%s,%s]" % (
        camera_drift(position[0], pos_x), camera_drift(position[1], pos_y),
        camera_drift(position[2], pos_z))
    camera_target = "[%s,%s,%s]" % (
        camera_drift(target[0], tgt_x), camera_drift(target[1], target[1]),
        camera_drift(target[2], tgt_z))
    document = f'''<!-- S97 - winding mountain road - textured PBR checkpoint rebuilt from reference/reference.png -->
<Graph fps={{24}} duration="12s" size={{[1920,1080]}} renderSize={{[1920,1080]}}>
  <RenderStyle id="s97_forest_pbr">
    <SurfaceStyle shading="physical" specular="0.22" />
    <LightingStyle ambientIntensity="0.42" ambientColor="#E4EDF6" shadowStyle="soft" />
    <PostStyle toneMapping="aces" exposure="1.12" contrast="1.03" saturation="1.04" whiteBalance="6100" />
    <AntiAliasingStyle method="taa" quality="ultra" fallback="smaa" sharpness="0.04" />
  </RenderStyle>
  <Assets>
    <ImageAsset id="s97_height" src="assets/terrain/s97-height.png" colorSpace="linear-srgb" />
    <ImageAsset id="s97_forest_exclusion" src="assets/terrain/s97-forest-exclusion.png" colorSpace="linear-srgb" />
    <ImageAsset id="s97_rock_density" src="assets/terrain/s97-rock-density.png" colorSpace="linear-srgb" />
    <ImageAsset id="s97_ground_color" src="assets/materials/forest-ground-basecolor.png" colorSpace="srgb" />
    <ImageAsset id="s97_asphalt_color" src="assets/materials/asphalt-basecolor.png" colorSpace="srgb" />
    <ImageAsset id="s97_asphalt_roughness" src="assets/materials/asphalt-roughness.png" colorSpace="linear-srgb" />
    <ImageAsset id="s97_bark_color" src="assets/materials/bark-basecolor.png" colorSpace="srgb" />
    <ImageAsset id="s97_foliage_color" src="assets/materials/foliage-basecolor.png" colorSpace="srgb" />

    <MaterialAsset id="s97_ground_mat" shading="pbr" baseColor="#B8B3A6"
                   baseColorTexture="s97_ground_color" metallic="0" roughness="0.92" specular="0.14"
                   mapping="triplanar" textureScale={{[0.55,0.55]}} variationAmount={{[0.08,0.05]}} />
    <MaterialAsset id="s97_asphalt_mat" shading="pbr" baseColor="#D6D8D9"
                   baseColorTexture="s97_asphalt_color" metallicRoughnessTexture="s97_asphalt_roughness"
                   metallic="0" roughness="1" roughnessChannel="luminance" specular="0.2"
                   mapping="uv" textureScale={{[2.2,0.24]}} variationAmount={{[0.04,0.03]}} />
    <MaterialAsset id="s97_paint_mat" shading="pbr" baseColor="#F2F3F4" metallic="0" roughness="0.6" specular="0.25" />
    <MaterialAsset id="s97_guardrail_mat" shading="pbr" baseColor="#C7CBCC" metallic="0.68" roughness="0.34" specular="0.8" />
    <MaterialAsset id="s97_rock_mat" shading="pbr" baseColor="#A69D8F" metallic="0" roughness="0.94" specular="0.12" />
    <MaterialAsset id="s97_trunk_mat" shading="pbr" baseColor="#D7C9B6"
                   baseColorTexture="s97_bark_color" metallic="0" roughness="0.9" specular="0.16"
                   mapping="uv" textureScale={{[1.2,2.8]}} variationAmount={{[0.06,0.04]}} />
    <MaterialAsset id="s97_leaf_a" shading="pbr" baseColor="#E2EAD8" baseColorTexture="s97_foliage_color"
                   metallic="0" roughness="0.9" specular="0.09" mapping="triplanar" textureScale={{[1.6,1.6]}} />
    <MaterialAsset id="s97_leaf_b" shading="pbr" baseColor="#EEF0D8" baseColorTexture="s97_foliage_color"
                   metallic="0" roughness="0.91" specular="0.08" mapping="triplanar" textureScale={{[1.45,1.45]}} />
    <MaterialAsset id="s97_leaf_c" shading="pbr" baseColor="#E4EDC8" baseColorTexture="s97_foliage_color"
                   metallic="0" roughness="0.92" specular="0.08" mapping="triplanar" textureScale={{[1.3,1.3]}} />
    <MaterialAsset id="s97_leaf_d" shading="pbr" baseColor="#F0F2D6" baseColorTexture="s97_foliage_color"
                   metallic="0" roughness="0.92" specular="0.07" mapping="triplanar" textureScale={{[1.2,1.2]}} />

    <TerrainAsset id="s97_terrain" heightMap="s97_height" size={{[{sc(TERRAIN_W):.4f},{sc(TERRAIN_H):.4f}]}}
                  heightScale="{sc(height_scale):.5f}" heightOffset="{sc(height_offset):.5f}"
                  material="s97_ground_mat" chunks={{[8,5]}} lod="full" collision="none" />

    <PrimitiveAsset id="s97_rock_a" shape="ellipsoid" radii={{[{sc(1.15):.5f},{sc(0.62):.5f},{sc(0.82):.5f}]}}
                    segments="10" rings="6" material="s97_rock_mat" collision="none" />
    <PrimitiveAsset id="s97_rock_b" shape="ellipsoid" radii={{[{sc(0.78):.5f},{sc(0.48):.5f},{sc(1.28):.5f}]}}
                    segments="10" rings="6" material="s97_rock_mat" collision="none" />
    <PrimitiveAsset id="s97_rock_c" shape="wedge" size={{[{sc(1.5):.5f},{sc(0.8):.5f},{sc(1.0):.5f}]}}
                    material="s97_rock_mat" collision="none" />

{chr(10).join(tree_asset_lines())}

{chr(10).join(road_meshes(dense))}
  </Assets>

{chr(10).join(background_block())}

  <Scene id="S97WindingRoad" renderStyle="s97_forest_pbr">
    <Timeline>
      <Track id="s97_world" space="3d" compositeOrder="30">
        <Sequence from="0s" duration="12s" out="hold">
          <CompositeGroup id="s97_island" space="3d" depth="true" format="rgba16f">
            <DirectionalLight id="s97_sun" direction={{[-0.5,-0.74,0.45]}}
                              color="#FFF4E2" intensity="4.4" castShadow="true" shadowStrength="0.78" />
            <DirectionalLight id="s97_fill" direction={{[0.55,-0.62,-0.55]}}
                              color="#C9DCEA" intensity="0.72" castShadow="false" />
            <AmbientOcclusion id="s97_ao" intensity="0.38" radius="{sc(1.6):.5f}" />
            <AtmosphereFog id="s97_aerial_haze" scatteringColor="#C8D2D3" density="0.003" affectEnvironment="false" />
            <Camera3D id="s97_aerial" position={{{camera_position}}} target={{{camera_target}}} fov="{fov}" />

            <Model id="s97_terrain_model" asset="s97_terrain" position={{[0,0,0]}}
                   castShadow="true" receiveShadow="true" />
            <Model id="s97_asphalt_model" asset="s97_asphalt" castShadow="true" receiveShadow="true" />
            <Model id="s97_line_left_model" asset="s97_line_left" receiveShadow="true" />
            <Model id="s97_line_right_model" asset="s97_line_right" receiveShadow="true" />
            <Model id="s97_line_center_model" asset="s97_line_center" receiveShadow="true" />
            <Model id="s97_guardrail_left_model" asset="s97_guardrail_left" castShadow="true" receiveShadow="true" />
            <Model id="s97_guardrail_right_model" asset="s97_guardrail_right" castShadow="true" receiveShadow="true" />
            <Scatter id="s97_forest" surface="s97_terrain_model"
                     count="{tree_count}" seed="97"
                     exclusionMap="s97_forest_exclusion"
                     slopeRange={{[0,90]}} scaleRange={{[0.42,0.86]}}
                     rotationYRange={{[0,360]}} surfaceOffset="{sc(-0.25):.5f}"
                     castShadow="true" receiveShadow="true">
              <Variant asset="s97_tree_a" weight="24" />
              <Variant asset="s97_tree_b" weight="24" />
              <Variant asset="s97_tree_c" weight="20" />
              <Variant asset="s97_tree_d" weight="14" />
              <Variant asset="s97_tree_e" weight="12" />
              <Variant asset="s97_tree_f" weight="6" />
            </Scatter>
            <Scatter id="s97_cut_rocks" surface="s97_terrain_model"
                     count="720" seed="197" densityMap="s97_rock_density"
                     exclusionMap="s97_forest_exclusion"
                     slopeRange={{[0,90]}} scaleRange={{[0.55,1.45]}}
                     rotationYRange={{[0,360]}} surfaceOffset="{sc(-0.12):.5f}"
                     castShadow="true" receiveShadow="true">
              <Variant asset="s97_rock_a" weight="42" />
              <Variant asset="s97_rock_b" weight="36" />
              <Variant asset="s97_rock_c" weight="22" />
            </Scatter>
          </CompositeGroup>
        </Sequence>
      </Track>
    </Timeline>
  </Scene>

  <Present from="S97WindingRoad" />
</Graph>
'''
    open(MAIN_OUT, "w").write(document)
    print(f"wrote {MAIN_OUT} ({len(document.splitlines())} lines)")


def main():
    if "markers" in sys.argv:
        build_markers()
        return 0
    build(probe="probe" in sys.argv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
