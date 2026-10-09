"""Extract grounded, reusable cards from the credited S96 landscape GLB.

Only positions and normals are rotated into the canonical Y-up frame;
positions are also uniformly scaled and translated. Original image bytes,
UVs, triangle indices, sampler settings, and material factors are preserved.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import struct
from pathlib import Path


DESTINATION = Path(__file__).resolve().parent
SOURCE = DESTINATION.parents[2] / "s-000096/assets/landscape_forest__mountains.glb"
SOURCE_URL = "https://sketchfab.com/3d-models/landscape-forest-mountains-94809d21d7aa4cfe9b658a111b35a42c"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
VARIANTS = (
    ("tree-dark-green", 3, 8.0, "tree"),
    ("tree-blue-green", 4, 9.0, "tree"),
    ("tree-light-green", 5, 7.0, "tree"),
    ("grass-long-blades", 1, 1.0, "grass"),
    ("grass-compact-tuft", 2, 0.8, "grass"),
)
CROWNS = {
    "tree-dark-green": {
        "height": 8.0, "phase": 0.31, "uvCrop": [0.0, 0.32, 1.0, 0.985],
        "layers": [(4.65, 5.0, 3.6, 0.42, 0.12, -0.08), (5.9, 4.5, 3.5, 0.55, -0.20, 0.08), (7.0, 3.2, 2.65, 0.36, 0.10, 0.14)],
    },
    "tree-blue-green": {
        "height": 9.0, "phase": 1.67, "uvCrop": [0.0, 0.28, 1.0, 0.99],
        "layers": [(5.05, 5.6, 4.5, 0.55, 0.20, 0.12), (6.55, 4.7, 3.9, 0.65, -0.16, -0.15), (7.9, 3.3, 3.0, 0.42, 0.12, -0.18)],
    },
    "tree-light-green": {
        "height": 7.0, "phase": 2.91, "uvCrop": [0.0, 0.27, 1.0, 0.98],
        "layers": [(3.75, 4.6, 3.5, 0.45, 0.14, 0.06), (4.9, 3.9, 3.1, 0.50, -0.12, 0.18), (5.9, 2.75, 2.5, 0.35, 0.15, -0.14)],
    },
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_glb(path: Path) -> tuple[dict, bytes, bytes]:
    data = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", data)
    assert magic == b"glTF" and version == 2 and length == len(data)
    json_length, json_type = struct.unpack_from("<II", data, 12)
    assert json_type == 0x4E4F534A
    document = json.loads(data[20 : 20 + json_length])
    offset = 20 + json_length
    binary_length, binary_type = struct.unpack_from("<II", data, offset)
    assert binary_type == 0x004E4942
    return document, data[offset + 8 : offset + 8 + binary_length], data


def accessor_bytes(document: dict, binary: bytes, index: int) -> bytes:
    accessor = document["accessors"][index]
    view = document["bufferViews"][accessor["bufferView"]]
    components = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
    sizes = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
    element_size = components[accessor["type"]] * sizes[accessor["componentType"]]
    stride = view.get("byteStride", element_size)
    start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    return b"".join(
        binary[start + i * stride : start + i * stride + element_size]
        for i in range(accessor["count"])
    )


def bounds(positions: list[tuple[float, float, float]]) -> dict:
    minimum = [min(point[axis] for point in positions) for axis in range(3)]
    maximum = [max(point[axis] for point in positions) for axis in range(3)]
    return {
        "min": minimum,
        "max": maximum,
        "dimensions": [b - a for a, b in zip(minimum, maximum)],
    }


def texture_indices(material: dict) -> set[int]:
    result: set[int] = set()

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key.endswith("Texture") and isinstance(value, dict) and "index" in value:
                    result.add(value["index"])
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(material)
    return result


def remap_material_textures(material: dict, mapping: dict[int, int]) -> dict:
    result = copy.deepcopy(material)

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key.endswith("Texture") and isinstance(value, dict) and "index" in value:
                    value["index"] = mapping[value["index"]]
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(result)
    return result


def extract_variant(source: dict, binary: bytes, name: str, mesh_index: int, height: float, kind: str) -> dict:
    source_mesh = source["meshes"][mesh_index]
    assert len(source_mesh["primitives"]) == 1
    source_primitive = source_mesh["primitives"][0]
    source_material_index = source_primitive["material"]
    source_material = source["materials"][source_material_index]
    position_accessor = source["accessors"][source_primitive["attributes"]["POSITION"]]
    assert position_accessor["componentType"] == 5126
    original_positions = list(struct.iter_unpack("<3f", accessor_bytes(source, binary, source_primitive["attributes"]["POSITION"])))
    original_bounds = bounds(original_positions)
    original_minimum, original_maximum = original_bounds["min"], original_bounds["max"]
    factor = height / (original_maximum[2] - original_minimum[2])
    center_x = (original_minimum[0] + original_maximum[0]) * 0.5
    center_y = (original_minimum[1] + original_maximum[1]) * 0.5
    # A positive 90-degree X rotation maps source -Z to canonical +Y.
    canonical_positions = [
        ((x - center_x) * factor, (original_maximum[2] - z) * factor, (y - center_y) * factor)
        for x, y, z in original_positions
    ]
    normalization = {"uniformScale": factor, "rotationXDegrees": 90, "sourceCenterX": center_x, "sourceCenterY": center_y, "sourceGroundZ": original_maximum[2], "targetHeightMetres": height}
    rotate_normal = lambda point: (point[0], -point[2], point[1])
    if kind == "sky":
        # The source dome is part of a radius-100 sphere centered on its origin.
        # Keep its original parent rotation, but discard the source placement.
        source_radius = max(math.sqrt(sum(value * value for value in point)) for point in original_positions)
        factor = height / source_radius
        mesh_node = next(index for index, node in enumerate(source["nodes"]) if node.get("mesh") == mesh_index)
        parent = next(node for node in source["nodes"] if mesh_node in node.get("children", []))
        matrix = parent["matrix"]
        axis_scale = math.sqrt(sum(matrix[index] ** 2 for index in (0, 1, 2)))
        rotation = [matrix[index] / axis_scale for index in (0, 1, 2, 4, 5, 6, 8, 9, 10)]

        def rotate_normal(point: tuple[float, float, float]) -> tuple[float, float, float]:
            return tuple(sum(rotation[column * 3 + row] * point[column] for column in range(3)) for row in range(3))

        canonical_positions = [tuple(value * factor for value in rotate_normal(point)) for point in original_positions]
        normalization = {"uniformScale": factor, "sourceSphereRadius": source_radius, "targetSphereRadiusMetres": height, "sphereCenter": [0, 0, 0], "sourceParentRotationColumnMajor3x3": rotation, "sourceParentTranslationDiscarded": matrix[12:15], "notes": "Partial spherical dome; retain original parent rotation and UV orientation. No grounding or bounding-box recentering."}

    output = {
        "asset": {
            "version": "2.0",
            "generator": "S97 faithful S96 card extraction",
            "copyright": "landscape forest & mountains by dasy444, CC BY 4.0",
        },
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"name": name, "mesh": 0}],
        "meshes": [],
        "materials": [],
        "textures": [],
        "images": [],
        "samplers": [],
        "accessors": [],
        "bufferViews": [],
    }
    payload = bytearray()

    def append_view(data: bytes, target: int | None = None) -> int:
        payload.extend(b"\0" * (-len(payload) % 4))
        view = {"buffer": 0, "byteOffset": len(payload), "byteLength": len(data)}
        if target is not None:
            view["target"] = target
        payload.extend(data)
        output["bufferViews"].append(view)
        return len(output["bufferViews"]) - 1

    def append_accessor(source_index: int, data: bytes, target: int, limits: dict | None = None) -> int:
        accessor = copy.deepcopy(source["accessors"][source_index])
        accessor["bufferView"] = append_view(data, target)
        accessor.pop("byteOffset", None)
        if limits is not None:
            accessor["min"], accessor["max"] = limits["min"], limits["max"]
        output["accessors"].append(accessor)
        return len(output["accessors"]) - 1

    attributes = {}
    for attribute, source_index in source_primitive["attributes"].items():
        data = accessor_bytes(source, binary, source_index)
        limits = None
        if attribute == "POSITION":
            data = b"".join(struct.pack("<3f", *point) for point in canonical_positions)
            canonical_positions = list(struct.iter_unpack("<3f", data))
            limits = bounds(canonical_positions)
        elif attribute == "NORMAL":
            normals = [rotate_normal(point) for point in struct.iter_unpack("<3f", data)]
            data = b"".join(struct.pack("<3f", *normal) for normal in normals)
            limits = bounds(normals)
        else:
            assert attribute.startswith("TEXCOORD_"), attribute
        attributes[attribute] = append_accessor(source_index, data, 34962, limits)
    indices = append_accessor(source_primitive["indices"], accessor_bytes(source, binary, source_primitive["indices"]), 34963)

    texture_mapping = {}
    image_mapping = {}
    sampler_mapping = {}
    for source_texture_index in sorted(texture_indices(source_material)):
        texture = copy.deepcopy(source["textures"][source_texture_index])
        source_image_index = texture["source"]
        if source_image_index not in image_mapping:
            source_image = source["images"][source_image_index]
            source_view = source["bufferViews"][source_image["bufferView"]]
            start = source_view.get("byteOffset", 0)
            image_data = binary[start : start + source_view["byteLength"]]
            image_mapping[source_image_index] = len(output["images"])
            output["images"].append({"name": f"s96-image-{source_image_index:02d}", "bufferView": append_view(image_data), "mimeType": source_image["mimeType"]})
        texture["source"] = image_mapping[source_image_index]
        if "sampler" in texture:
            source_sampler_index = texture["sampler"]
            if source_sampler_index not in sampler_mapping:
                sampler_mapping[source_sampler_index] = len(output["samplers"])
                output["samplers"].append(copy.deepcopy(source["samplers"][source_sampler_index]))
            texture["sampler"] = sampler_mapping[source_sampler_index]
        texture_mapping[source_texture_index] = len(output["textures"])
        output["textures"].append(texture)
    output["materials"] = [remap_material_textures(source_material, texture_mapping)]
    output["meshes"] = [{"name": name, "primitives": [{"attributes": attributes, "indices": indices, "material": 0, "mode": source_primitive.get("mode", 4)}]}]
    output["buffers"] = [{"byteLength": len(payload)}]
    json_data = json.dumps(output, separators=(",", ":")).encode()
    json_data += b" " * (-len(json_data) % 4)
    payload.extend(b"\0" * (-len(payload) % 4))
    result = struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(json_data) + 8 + len(payload))
    result += struct.pack("<II", len(json_data), 0x4E4F534A) + json_data
    result += struct.pack("<II", len(payload), 0x004E4942) + payload
    (DESTINATION / f"{name}.glb").write_bytes(result)
    return {
        "file": f"{name}.glb",
        "kind": kind,
        "sourceMeshIndex": mesh_index,
        "sourceMeshName": source_mesh.get("name"),
        "sourceMaterialIndex": source_material_index,
        "sourceMaterialName": source_material.get("name"),
        "sourceTextureToOutputTexture": texture_mapping,
        "sourceImageToOutputImage": image_mapping,
        "sourceLocalBounds": original_bounds,
        "canonicalBounds": bounds(canonical_positions),
        "normalization": normalization,
        "vertices": len(canonical_positions),
        "triangles": source["accessors"][source_primitive["indices"]]["count"] // 3,
        "material": output["materials"][0],
        "sha256": digest(result),
    }


def crown_geometry(parameters: dict) -> tuple[list, list, list, list]:
    """Three open curved foliage sheets; source alpha forms their silhouettes."""
    height, phase = parameters["height"], parameters["phase"]
    crop_u_min, crop_v_min, crop_u_max, crop_v_max = parameters["uvCrop"]
    cells = 6
    positions, uvs, triangles = [], [], []
    for layer, (base_y, width, depth, arch, slope_x, slope_z) in enumerate(parameters["layers"]):
        offset = len(positions)
        yaw = phase + layer * 1.91
        cos_yaw, sin_yaw = math.cos(yaw), math.sin(yaw)
        for row in range(cells + 1):
            v = row / cells
            z = v * 2 - 1
            for column in range(cells + 1):
                u = column / cells
                x = u * 2 - 1
                # A broad irregular bend gives foliage depth without a closed roof.
                local_x = x * width * 0.5 * (0.94 + 0.06 * math.cos(z * 2.7 + yaw))
                local_z = z * depth * 0.5 * (0.94 + 0.06 * math.sin(x * 3.1 - yaw))
                y = base_y + arch * (1 - x * x) * (1 - z * z)
                y += slope_x * local_x + slope_z * local_z
                y += 0.12 * math.sin(x * 4.2 + yaw) * math.cos(z * 3.4 - yaw)
                positions.append((local_x * cos_yaw - local_z * sin_yaw + 0.10 * math.sin(yaw), min(height, y), local_x * sin_yaw + local_z * cos_yaw + 0.12 * math.cos(yaw)))
                # The original image is intentionally upside down; retain V sense.
                # Cropping excludes its bare lower trunk, while full U preserves alpha edges.
                uvs.append((crop_u_min + u * (crop_u_max - crop_u_min), crop_v_min + v * (crop_v_max - crop_v_min)))
        for row in range(cells):
            for column in range(cells):
                a = offset + row * (cells + 1) + column
                b, c = a + 1, a + cells + 1
                d = c + 1
                triangles.extend(((a, c, b), (b, c, d)))
    normals = [[0.0, 0.0, 0.0] for _ in positions]
    for triangle in triangles:
        a, b, c = (positions[index] for index in triangle)
        u, v = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
        normal = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        for vertex in triangle:
            for axis in range(3):
                normals[vertex][axis] += normal[axis]
    normals = [tuple(value / max(math.sqrt(sum(component * component for component in normal)), 1e-12) for value in normal) for normal in normals]
    return positions, normals, uvs, triangles


def augment_crown(source: dict, source_binary: bytes, name: str, parameters: dict) -> dict:
    output, card_binary, _ = read_glb(DESTINATION / f"{name}.glb")
    payload = bytearray(card_binary)

    def append_view(data: bytes, target: int | None = None) -> int:
        payload.extend(b"\0" * (-len(payload) % 4))
        view = {"buffer": 0, "byteOffset": len(payload), "byteLength": len(data)}
        if target is not None:
            view["target"] = target
        payload.extend(data)
        output["bufferViews"].append(view)
        return len(output["bufferViews"]) - 1

    def append_accessor(values: list, components: int, component_type: int, target: int) -> int:
        format_character = "f" if component_type == 5126 else "I"
        data = b"".join(struct.pack("<" + format_character * components, *value) for value in values)
        accessor = {"bufferView": append_view(data, target), "componentType": component_type, "count": len(values), "type": {1: "SCALAR", 2: "VEC2", 3: "VEC3"}[components]}
        if components == 3 and component_type == 5126:
            accessor["min"], accessor["max"] = bounds(values)["min"], bounds(values)["max"]
        output["accessors"].append(accessor)
        return len(output["accessors"]) - 1

    positions, normals, uvs, triangles = crown_geometry(parameters)
    attributes = {
        "POSITION": append_accessor(positions, 3, 5126, 34962),
        "NORMAL": append_accessor(normals, 3, 5126, 34962),
        "TEXCOORD_0": append_accessor(uvs, 2, 5126, 34962),
    }
    indices = append_accessor([(index,) for triangle in triangles for index in triangle], 1, 5125, 34963)
    # Reuse the tree's exact original alpha-masked material and embedded image.
    # No opaque aerial image, extra texture, normal map, or changed alpha cutoff.
    output["meshes"][0]["name"] = f"{name}-canopy"
    output["meshes"][0]["primitives"].append({"attributes": attributes, "indices": indices, "material": 0, "mode": 4})
    output["nodes"][0]["name"] = f"{name}-canopy"
    output["asset"]["generator"] = "S97 original S96 cards with authored curved alpha-masked foliage layers"
    output["buffers"] = [{"byteLength": len(payload)}]
    json_data = json.dumps(output, separators=(",", ":")).encode()
    json_data += b" " * (-len(json_data) % 4)
    payload.extend(b"\0" * (-len(payload) % 4))
    data = struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(json_data) + 8 + len(payload))
    data += struct.pack("<II", len(json_data), 0x4E4F534A) + json_data
    data += struct.pack("<II", len(payload), 0x004E4942) + payload
    filename = f"{name}-canopy.glb"
    (DESTINATION / filename).write_bytes(data)
    card_positions = list(struct.iter_unpack("<3f", accessor_bytes(output, payload, output["meshes"][0]["primitives"][0]["attributes"]["POSITION"])))
    source_material_index = source["meshes"][dict((variant[0], variant[1]) for variant in VARIANTS)[name]]["primitives"][0]["material"]
    source_image_index = source["textures"][source["materials"][source_material_index]["pbrMetallicRoughness"]["baseColorTexture"]["index"]]["source"]
    return {
        "file": filename, "originalCardFile": f"{name}.glb", "vertices": 8 + len(positions), "triangles": 4 + len(triangles),
        "crownOnlyTriangles": len(triangles), "crownBounds": bounds(positions), "canonicalBounds": bounds(card_positions + positions),
        "sourceCanopyMaterialIndex": source_material_index, "sourceColorImageIndex": source_image_index, "sourceNormalImageIndex": None,
        "layers": parameters["layers"], "uvCrop": parameters["uvCrop"], "intendedSiteScale": 0.05,
        "authoredChanges": "Added three curved, irregularly tilted upper foliage sheets with cropped original whole-tree UVs. Reuses the exact original tree alpha-mask material, double-sided setting, cutoff and embedded image. Original crossed cards retained byte-for-byte. No opaque cap or added normal texture.",
        "sha256": digest(data),
    }



def validate_alpha_canopies(source: dict, binary: bytes, source_hash: str) -> dict:
    """Preservation and geometric checks for the current transparent additions."""
    assert digest(SOURCE.read_bytes()) == source_hash
    image_checks = []
    for index, source_image in enumerate(source["images"]):
        view = source["bufferViews"][source_image["bufferView"]]
        start = view.get("byteOffset", 0)
        image_data = binary[start:start + view["byteLength"]]
        suffix = "png" if source_image["mimeType"] == "image/png" else "jpg"
        assert (DESTINATION / f"textures/s96-image-{index:02d}.{suffix}").read_bytes() == image_data
        image_checks.append(index)
    checks = []
    for name, parameters in CROWNS.items():
        original, original_binary, _ = read_glb(DESTINATION / f"{name}.glb")
        augmented, augmented_binary, data = read_glb(DESTINATION / f"{name}-canopy.glb")
        original_primitive = original["meshes"][0]["primitives"][0]
        card_primitive, foliage_primitive = augmented["meshes"][0]["primitives"]
        assert original_primitive["attributes"].keys() == card_primitive["attributes"].keys()
        for attribute, original_accessor in original_primitive["attributes"].items():
            assert accessor_bytes(original, original_binary, original_accessor) == accessor_bytes(augmented, augmented_binary, card_primitive["attributes"][attribute])
        assert accessor_bytes(original, original_binary, original_primitive["indices"]) == accessor_bytes(augmented, augmented_binary, card_primitive["indices"])
        assert augmented["materials"] == original["materials"] and len(augmented["materials"]) == 1
        assert augmented["textures"] == original["textures"] and augmented["samplers"] == original["samplers"]
        assert len(augmented["images"]) == len(original["images"]) == 1
        for old_image, new_image in zip(original["images"], augmented["images"]):
            old_view, new_view = original["bufferViews"][old_image["bufferView"]], augmented["bufferViews"][new_image["bufferView"]]
            old_start, new_start = old_view.get("byteOffset", 0), new_view.get("byteOffset", 0)
            assert original_binary[old_start:old_start + old_view["byteLength"]] == augmented_binary[new_start:new_start + new_view["byteLength"]]
        assert foliage_primitive["material"] == card_primitive["material"] == 0
        attributes = foliage_primitive["attributes"]
        positions = list(struct.iter_unpack("<3f", accessor_bytes(augmented, augmented_binary, attributes["POSITION"])))
        normals = list(struct.iter_unpack("<3f", accessor_bytes(augmented, augmented_binary, attributes["NORMAL"])))
        uvs = list(struct.iter_unpack("<2f", accessor_bytes(augmented, augmented_binary, attributes["TEXCOORD_0"])))
        indices = list(struct.iter_unpack("<I", accessor_bytes(augmented, augmented_binary, foliage_primitive["indices"])))
        assert len(positions) == len(normals) == len(uvs) == 147 and len(indices) == 648
        assert all(0 <= index[0] < len(positions) for index in indices)
        assert all(math.isfinite(value) for group in (positions, normals, uvs) for point in group for value in point)
        assert all(abs(math.sqrt(sum(value * value for value in normal)) - 1) < 1e-5 for normal in normals)
        assert augmented["materials"][0]["alphaMode"] == "MASK" and augmented["materials"][0]["doubleSided"]
        checks.append({"file": f"{name}-canopy.glb", "originalCardAttributesAndIndicesByteExact": True, "originalMaterialAndImageExact": True, "validFiniteFoliageGeometry": True, "vertices": 155, "triangles": 220, "sha256": digest(data)})
    return {"passed": True, "sourceUnchanged": True, "all14ExternalImagesByteExact": image_checks, "canopies": checks, "nativeGpuEvidence": {"obliqueFrame0": "/private/tmp/s97-alpha-canopy-oblique.png", "overheadFrame12": "/private/tmp/s97-alpha-canopy-overhead.png"}}


def main() -> None:
    source, binary, original_data = read_glb(SOURCE)
    images = []
    (DESTINATION / "textures").mkdir(exist_ok=True)
    # Keep all original textures available for authored S97 landscape surfaces.
    for index, image in enumerate(source["images"]):
        view = source["bufferViews"][image["bufferView"]]
        start = view.get("byteOffset", 0)
        data = binary[start : start + view["byteLength"]]
        extension = "png" if image["mimeType"] == "image/png" else "jpg"
        filename = f"textures/s96-image-{index:02d}.{extension}"
        (DESTINATION / filename).write_bytes(data)
        images.append({"sourceImageIndex": index, "file": filename, "mimeType": image["mimeType"], "bytes": len(data), "sha256": digest(data)})
    variants = [extract_variant(source, binary, *variant) for variant in VARIANTS]
    sky_mesh_index = next(index for index, mesh in enumerate(source["meshes"]) if any(source["materials"][primitive["material"]].get("name") == "Material.011" for primitive in mesh["primitives"]))
    sky = extract_variant(source, binary, "mountain-sky-dome", sky_mesh_index, 45.0, "sky")
    augmented = [augment_crown(source, binary, name, parameters) for name, parameters in CROWNS.items()]
    report = {
        "source": "landscape forest & mountains",
        "author": "dasy444",
        "sourceUrl": SOURCE_URL,
        "license": "CC BY 4.0",
        "licenseUrl": LICENSE_URL,
        "sourceFile": "showcase/s-000096/assets/landscape_forest__mountains.glb",
        "sourceSha256": digest(original_data),
        "changes": "Extracted five original crossed-card meshes. Rotate local -Z to +Y, center horizontal card axes, uniformly resize and ground at Y=0. Images, UVs, indices, alpha masks, sampler settings and material factors are preserved. Original scene placements are discarded for independent placement.",
        "variants": variants,
        "skyDome": sky,
        "augmentedCanopies": augmented,
        "images": images,
        "sourceMaterials": source["materials"],
        "sourceTextures": source["textures"],
        "sourceSamplers": source["samplers"],
        "barkTexture": "No dedicated opaque bark material or bark image exists in the source. Bark is visible within alpha-masked whole-tree images 4, 5 and 6. Opaque image 7 is aerial forest canopy, not bark.",
    }
    report["alphaCanopyValidation"] = validate_alpha_canopies(source, binary, report["sourceSha256"])
    (DESTINATION / "provenance.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"variants": [{"file": variant["file"], "bounds": variant["canonicalBounds"], "triangles": variant["triangles"]} for variant in variants], "images": len(images)}, indent=2))


if __name__ == "__main__":
    main()
