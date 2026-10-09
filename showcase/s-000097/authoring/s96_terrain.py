"""Build smooth S97 terrain with the original S96 grass-ground textures.

The terrain follows build_scene.carve_terrain() at its original grid resolution.
Float32 positions replace the 8-bit heightfield's visible staircase; the road,
vegetation placement map, and camera are not rewritten. S96 image payloads are
embedded byte for byte, without image processing or source-asset changes.

Scatter v1 still requires a TerrainAsset surface. Keep that original asset as
an invisible, non-shadowing placement proxy and show this GLB at scale 1 with
scaleMode="none". A quarter-LOD proxy retains the same Scatter placement map.
"""

from array import array
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import struct
import sys
import zlib

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT.parent / "s-000096/assets/landscape_forest__mountains.glb"
DEFAULT_OUTPUT = ROOT / "assets/terrain/s97-smooth-terrain.glb"
DEFAULT_SURROUND = ROOT / "assets/terrain/s97-terrain-surround.glb"
DEFAULT_REPORT = ROOT / "authoring/s96-terrain-provenance.json"


def sha256(payload):
    return hashlib.sha256(payload).hexdigest()


def read_glb(path):
    payload = path.read_bytes()
    magic, version, total = struct.unpack_from("<III", payload)
    if magic != 0x46546C67 or version != 2 or total != len(payload):
        raise ValueError(f"Invalid GLB header: {path}")
    json_size, json_kind = struct.unpack_from("<II", payload, 12)
    if json_kind != 0x4E4F534A:
        raise ValueError("GLB must begin with its JSON chunk")
    document = json.loads(payload[20:20 + json_size])
    bin_start = 20 + json_size
    bin_size, bin_kind = struct.unpack_from("<II", payload, bin_start)
    if bin_kind != 0x004E4942:
        raise ValueError("GLB must contain one embedded BIN chunk")
    return payload, document, payload[bin_start + 8:bin_start + 8 + bin_size]


def embedded_image(document, binary, index):
    image = document["images"][index]
    view = document["bufferViews"][image["bufferView"]]
    start = view.get("byteOffset", 0)
    return binary[start:start + view["byteLength"]], image["mimeType"]


def read_height_png(path):
    """Read the unchanged RGBA8 PNG emitted by build_scene.write_png_rgba."""
    payload = path.read_bytes()
    if payload[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Expected a PNG heightmap")
    compressed = bytearray()
    offset = 8
    width = height = None
    while offset < len(payload):
        length = struct.unpack_from(">I", payload, offset)[0]
        kind = payload[offset + 4:offset + 8]
        data = payload[offset + 8:offset + 8 + length]
        if kind == b"IHDR":
            width, height, depth, mode, compression, filtering, interlace = struct.unpack(">IIBBBBB", data)
            if (depth, mode, compression, filtering, interlace) != (8, 6, 0, 0, 0):
                raise ValueError("Expected the original noninterlaced RGBA8 heightmap")
        elif kind == b"IDAT":
            compressed.extend(data)
        offset += 12 + length
    pixels = zlib.decompress(compressed)
    stride = width * 4 + 1
    heights = []
    for row in range(height):
        if pixels[row * stride] != 0:
            raise ValueError("Expected filter-zero rows from the original heightmap writer")
        heights.extend(pixels[row * stride + 1 + column * 4] for column in range(width))
    return width, height, heights, payload


def load_builder():
    path = ROOT / "authoring/build_scene.py"
    spec = importlib.util.spec_from_file_location("s97_original_terrain_builder", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def little_endian_bytes(values):
    if sys.byteorder != "little":
        values.byteswap()
    return values.tobytes()


def write_terrain_glb(output, builder, heights, tile_metres, images):
    width, height = builder.HM_W, builder.HM_H
    dx = builder.TERRAIN_W * builder.SCALE / (width - 1)
    dz = builder.TERRAIN_H * builder.SCALE / (height - 1)
    positions, normals, uvs = array("f"), array("f"), array("f")
    indices = array("I")
    for row in range(height):
        back, front = max(0, row - 1), min(height - 1, row + 1)
        z = row * dz - builder.TERRAIN_H * builder.SCALE / 2
        for column in range(width):
            left, right = max(0, column - 1), min(width - 1, column + 1)
            x = column * dx - builder.TERRAIN_W * builder.SCALE / 2
            y = heights[row * width + column] * builder.SCALE
            gradient_x = ((heights[row * width + right] - heights[row * width + left])
                          * builder.SCALE / ((right - left) * dx))
            gradient_z = ((heights[front * width + column] - heights[back * width + column])
                          * builder.SCALE / ((front - back) * dz))
            length = math.sqrt(gradient_x ** 2 + 1 + gradient_z ** 2)
            positions.extend((x, y, z))
            normals.extend((-gradient_x / length, 1 / length, -gradient_z / length))
            uvs.extend((column * builder.TERRAIN_W / (width - 1) / tile_metres,
                        row * builder.TERRAIN_H / (height - 1) / tile_metres))
    for row in range(height - 1):
        for column in range(width - 1):
            a = row * width + column
            b, c, d = a + width, a + width + 1, a + 1
            indices.extend((a, b, c, a, c, d))

    bounds = {
        "min": [-builder.TERRAIN_W * builder.SCALE / 2, min(heights) * builder.SCALE,
                -builder.TERRAIN_H * builder.SCALE / 2],
        "max": [builder.TERRAIN_W * builder.SCALE / 2, max(heights) * builder.SCALE,
                builder.TERRAIN_H * builder.SCALE / 2],
    }
    return write_mesh_glb(output, positions, normals, uvs, indices, bounds, images, "S97SmoothTerrain")


def write_mesh_glb(output, positions, normals, uvs, indices, bounds, images, name):
    bounds = {key: [struct.unpack("<f", struct.pack("<f", value))[0] for value in values]
              for key, values in bounds.items()}
    binary = bytearray()
    views = []

    def append(payload, target=None):
        while len(binary) % 4:
            binary.append(0)
        view = {"buffer": 0, "byteOffset": len(binary), "byteLength": len(payload)}
        if target is not None:
            view["target"] = target
        views.append(view)
        binary.extend(payload)
        return len(views) - 1

    vertex_count = len(positions) // 3
    accessors = [
        {"bufferView": append(little_endian_bytes(positions), 34962), "componentType": 5126,
         "count": vertex_count, "type": "VEC3", **bounds},
        {"bufferView": append(little_endian_bytes(normals), 34962), "componentType": 5126,
         "count": vertex_count, "type": "VEC3"},
        {"bufferView": append(little_endian_bytes(uvs), 34962), "componentType": 5126,
         "count": vertex_count, "type": "VEC2"},
        {"bufferView": append(little_endian_bytes(indices), 34963), "componentType": 5125,
         "count": len(indices), "type": "SCALAR", "min": [0], "max": [vertex_count - 1]},
    ]
    image_nodes = [{"bufferView": append(payload), "mimeType": mime}
                   for payload, mime in images]
    material = {
        "name": "S97_S96_GrassGround",
        "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1],
                                "baseColorTexture": {"index": 0},
                                "metallicFactor": 0, "roughnessFactor": 1},
        "normalTexture": {"index": 1, "scale": 0.85},
        "extensions": {"KHR_materials_specular": {"specularFactor": 0.12}},
        "doubleSided": False,
        "alphaMode": "OPAQUE",
    }
    document = {
        "asset": {"version": "2.0", "generator": "S97 s96_terrain.py; original float heightfield"},
        "extensionsUsed": ["KHR_materials_specular"],
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"name": name, "mesh": 0}],
        "meshes": [{"name": name, "primitives": [
            {"attributes": {"POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2},
             "indices": 3, "material": 0, "mode": 4}]}],
        "materials": [material],
        "samplers": [{"magFilter": 9729, "minFilter": 9987, "wrapS": 10497, "wrapT": 10497}],
        "textures": [{"sampler": 0, "source": 0}, {"sampler": 0, "source": 1}],
        "images": image_nodes,
        "accessors": accessors,
        "bufferViews": views,
        "buffers": [{"byteLength": len(binary)}],
    }
    encoded = json.dumps(document, separators=(",", ":")).encode()
    encoded += b" " * (-len(encoded) % 4)
    binary.extend(b"\x00" * (-len(binary) % 4))
    total = 12 + 8 + len(encoded) + 8 + len(binary)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as handle:
        handle.write(struct.pack("<III", 0x46546C67, 2, total))
        handle.write(struct.pack("<II", len(encoded), 0x4E4F534A))
        handle.write(encoded)
        handle.write(struct.pack("<II", len(binary), 0x004E4942))
        handle.write(binary)
    return document, bounds, len(indices) // 3


def write_surround_glb(output, builder, heights, tile_metres, images):
    """Join a coarse outer ring to the exact full-resolution core perimeter."""
    width, height = builder.HM_W, builder.HM_H
    half_x = builder.TERRAIN_W * builder.SCALE / 2
    half_z = builder.TERRAIN_H * builder.SCALE / 2
    dx = builder.TERRAIN_W * builder.SCALE / (width - 1)
    dz = builder.TERRAIN_H * builder.SCALE / (height - 1)
    outer_half_x, outer_half_z = half_x * 2, half_z * 3
    outer_step = 4 * builder.SCALE
    outer_columns = math.ceil((outer_half_x - half_x) / outer_step)
    outer_rows = math.ceil((outer_half_z - half_z) / outer_step)
    xs = [(-outer_half_x + (outer_half_x - half_x) * index / outer_columns)
          for index in range(outer_columns)]
    xs += [column * dx - half_x for column in range(width)]
    xs += [half_x + (outer_half_x - half_x) * index / outer_columns
           for index in range(1, outer_columns + 1)]
    zs = [(-outer_half_z + (outer_half_z - half_z) * index / outer_rows)
          for index in range(outer_rows)]
    zs += [row * dz - half_z for row in range(height)]
    zs += [half_z + (outer_half_z - half_z) * index / outer_rows
           for index in range(1, outer_rows + 1)]
    x_start, x_end = outer_columns, outer_columns + width - 1
    z_start, z_end = outer_rows, outer_rows + height - 1

    def outer_height(x, z):
        clamped_x, clamped_z = max(-half_x, min(half_x, x)), max(-half_z, min(half_z, z))
        distance = max(abs(x - clamped_x), abs(z - clamped_z)) / builder.SCALE
        natural = builder.natural_height(x / builder.SCALE, z / builder.SCALE)
        if distance >= 8:
            return natural * builder.SCALE
        edge = terrain_sample(heights, builder, clamped_x, clamped_z)
        natural_edge = builder.natural_height(clamped_x / builder.SCALE, clamped_z / builder.SCALE)
        correction = (edge - natural_edge) * (1 - builder.smoothstep(distance / 8))
        return (natural + correction) * builder.SCALE

    positions, normals, uvs, indices = array("f"), array("f"), array("f"), array("I")
    vertices = {}
    boundary_count = 0
    minimum_height, maximum_height = math.inf, -math.inf
    for row, z in enumerate(zs):
        for column, x in enumerate(xs):
            if x_start < column < x_end and z_start < row < z_end:
                continue
            boundary = (x_start <= column <= x_end and z_start <= row <= z_end)
            if boundary:
                original_column, original_row = column - x_start, row - z_start
                y = heights[original_row * width + original_column] * builder.SCALE
                left, right = max(0, original_column - 1), min(width - 1, original_column + 1)
                back, front = max(0, original_row - 1), min(height - 1, original_row + 1)
                gx = ((heights[original_row * width + right] - heights[original_row * width + left])
                      * builder.SCALE / ((right - left) * dx))
                gz = ((heights[front * width + original_column] - heights[back * width + original_column])
                      * builder.SCALE / ((front - back) * dz))
                uv = (original_column * builder.TERRAIN_W / (width - 1) / tile_metres,
                      original_row * builder.TERRAIN_H / (height - 1) / tile_metres)
                boundary_count += 1
            else:
                y = outer_height(x, z)
                gx = (outer_height(x + dx, z) - outer_height(x - dx, z)) / (2 * dx)
                gz = (outer_height(x, z + dz) - outer_height(x, z - dz)) / (2 * dz)
                uv = ((x / builder.SCALE + builder.TERRAIN_W / 2) / tile_metres,
                      (z / builder.SCALE + builder.TERRAIN_H / 2) / tile_metres)
            length = math.sqrt(gx ** 2 + 1 + gz ** 2)
            vertices[(row, column)] = len(positions) // 3
            positions.extend((x, y, z))
            normals.extend((-gx / length, 1 / length, -gz / length))
            uvs.extend(uv)
            minimum_height, maximum_height = min(minimum_height, y), max(maximum_height, y)
    for row in range(len(zs) - 1):
        for column in range(len(xs) - 1):
            if x_start <= column < x_end and z_start <= row < z_end:
                continue
            a, b = vertices[(row, column)], vertices[(row + 1, column)]
            c, d = vertices[(row + 1, column + 1)], vertices[(row, column + 1)]
            indices.extend((a, b, c, a, c, d))
    bounds = {"min": [-outer_half_x, minimum_height, -outer_half_z],
              "max": [outer_half_x, maximum_height, outer_half_z]}
    document, bounds, triangles = write_mesh_glb(output, positions, normals, uvs, indices,
                                                bounds, images, "S97TerrainSurround")
    return document, bounds, triangles, boundary_count


def terrain_sample(values, builder, x, z, triangular=False):
    """Sample either the Scatter bilinear surface or the rendered mesh triangles."""
    fx = max(0, min(builder.HM_W - 1, (x / builder.SCALE / builder.TERRAIN_W + 0.5) * (builder.HM_W - 1)))
    fz = max(0, min(builder.HM_H - 1, (z / builder.SCALE / builder.TERRAIN_H + 0.5) * (builder.HM_H - 1)))
    x0, z0 = min(int(fx), builder.HM_W - 2), min(int(fz), builder.HM_H - 2)
    tx, tz = fx - x0, fz - z0
    a, d = values[z0 * builder.HM_W + x0:z0 * builder.HM_W + x0 + 2]
    b, c = values[(z0 + 1) * builder.HM_W + x0:(z0 + 1) * builder.HM_W + x0 + 2]
    if triangular:
        return a + tz * (b - a) + tx * (c - b) if tz >= tx else a + tx * (d - a) + tz * (c - d)
    return (a * (1 - tx) + d * tx) * (1 - tz) + (b * (1 - tx) + c * tx) * tz


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--surround", type=Path, default=DEFAULT_SURROUND)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--tile-metres", type=float, default=5.0)
    args = parser.parse_args()
    if args.tile_metres <= 0:
        parser.error("--tile-metres must be positive")
    for path in (args.output, args.surround, args.report):
        if not path.resolve().is_relative_to(ROOT.resolve()):
            parser.error("Outputs must remain within S97")
    builder = load_builder()
    dense = builder.road_profile(builder.load_centerline())
    heights, _, _ = builder.carve_terrain(dense)
    source_bytes, source_document, source_binary = read_glb(args.source)
    images = [embedded_image(source_document, source_binary, index) for index in (0, 1)]
    document, bounds, triangles = write_terrain_glb(args.output, builder, heights, args.tile_metres, images)
    surround_document, surround_bounds, surround_triangles, boundary_count = write_surround_glb(
        args.surround, builder, heights, args.tile_metres, images)
    width, height, gray, height_bytes = read_height_png(ROOT / "assets/terrain/s97-height.png")
    if (width, height) != (builder.HM_W, builder.HM_H):
        raise ValueError("The original placement map no longer matches the authored terrain resolution")
    main_source = (ROOT / "main.motionloom").read_text()
    terrain_tag = re.search(r"<TerrainAsset\b[^>]*id=\"s97_terrain\"[^>]*/>", main_source, re.S).group()
    height_scale = float(re.search(r'heightScale="([^"]+)"', terrain_tag).group(1))
    height_offset = float(re.search(r'heightOffset="([^"]+)"', terrain_tag).group(1))
    quantized = [height_offset + value / 255 * height_scale for value in gray]
    smooth = [value * builder.SCALE for value in heights]
    deltas = [value - original for value, original in zip(smooth, quantized)]
    exploration = json.loads((ROOT / "authoring/camera-exploration.json").read_text())
    subject = exploration["subject"]["position"]
    points = [("heroRoot", subject[0], subject[2]),
              ("heroRoadPoint", exploration["roadPoint"][0], exploration["roadPoint"][2])]
    points.extend((f"cameraAt{key['time']}s", key["position"][0], key["position"][2])
                  for key in exploration["cameraKeys"])
    samples = []
    for label, x, z in points:
        original = terrain_sample(quantized, builder, x, z)
        new = terrain_sample(smooth, builder, x, z, triangular=True)
        samples.append({"label": label, "xz": [x, z], "originalScatterHeight": original,
                        "smoothRenderedHeight": new, "deltaWorldUnits": new - original})
    report = {
        "reportVersion": 1,
        "output": str(args.output.relative_to(ROOT)),
        "outputSha256": sha256(args.output.read_bytes()),
        "source": str(args.source.relative_to(ROOT.parent)),
        "sourceSha256": sha256(source_bytes),
        "sourceImages": [{"index": index, "mimeType": image[1], "sha256": sha256(image[0]),
                          "byteLength": len(image[0]), "bytePreserved": True}
                         for index, image in zip((0, 1), images)],
        "originalHeightmapSha256": sha256(height_bytes),
        "originalBuilderSha256": sha256((ROOT / "authoring/build_scene.py").read_bytes()),
        "roadPathSha256": sha256((ROOT / "authoring/road-path.json").read_bytes()),
        "roadOffsetsSha256": sha256((ROOT / "authoring/road-offsets.json").read_bytes()),
        "grid": [width, height], "vertices": width * height, "triangles": triangles,
        "boundsWorldUnits": bounds,
        "siteScale": builder.SCALE, "textureTileSiteMetres": args.tile_metres,
        "uvRepeats": [builder.TERRAIN_W / args.tile_metres, builder.TERRAIN_H / args.tile_metres],
        "material": document["materials"][0],
        "surround": {"output": str(args.surround.relative_to(ROOT)),
                     "outputSha256": sha256(args.surround.read_bytes()),
                     "vertices": surround_document["accessors"][0]["count"],
                     "triangles": surround_triangles, "boundsWorldUnits": surround_bounds,
                     "outerStepSiteMetres": 4, "boundaryBlendSiteMetres": 8,
                     "exactSharedBoundaryVertices": boundary_count,
                     "coreInteriorFaces": 0,
                     "seam": "Identical float32 positions, normals and UVs at every original perimeter sample"},
        "originalHeightStepWorldUnits": height_scale / 255,
        "heightDeltaWorldUnits": {"min": min(deltas), "max": max(deltas),
                                  "meanAbsolute": sum(abs(value) for value in deltas) / len(deltas),
                                  "rms": math.sqrt(sum(value * value for value in deltas) / len(deltas))},
        "samples": samples,
        "integration": {"modelScale": 1, "modelScaleMode": "none",
                        "scatterSurfaceRequiresTerrainAsset": True,
                        "preserveOriginalPlacementProxy": True,
                        "proxyMaterial": "Zero-alpha MASK material; castShadow=false; receiveShadow=false",
                        "proxyRenderLOD": "quarter",
                        "originalRoadVegetationCameraFilesChanged": False},
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"output": report["output"], "vertices": report["vertices"], "triangles": triangles,
                      "bounds": bounds, "heightDeltaWorldUnits": report["heightDeltaWorldUnits"],
                      "heroRoot": samples[0], "surround": report["surround"]}, indent=2))


if __name__ == "__main__":
    main()
