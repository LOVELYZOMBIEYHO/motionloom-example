#!/usr/bin/env python3
"""Texture the full 3D S99 tree for S97's close camera route.

This faithfully repacks the six local, MotionLoom-exported S99 GLBs. Every
indexed triangle position and normal is retained. The local editable cages
identify each disconnected tube or leaf, allowing cylindrical bark UVs and
individual curved-blade UVs instead of whole-tree photographic cards.

The leaf image is a rectangular leaf-surface texture: midrib at U=.5, base at
the image bottom, tip at the image top. The existing curved mesh supplies the
silhouette, so all six materials remain opaque. Images are embedded in GLB.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
PARTS = ('tree_bark', 'young_bark', 'foliage_deep', 'foliage_green', 'foliage_mid', 'foliage_tip')
LEAF_FACTORS = {
    'foliage_deep': (.68, .77, .64, 1),
    'foliage_green': (.85, .94, .80, 1),
    'foliage_mid': (.93, 1, .87, 1),
    'foliage_tip': (1, 1, .96, 1),
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def distance(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def mean(points):
    return tuple(sum(p[axis] for p in points) / len(points) for axis in range(3))


def read_glb(path):
    data = path.read_bytes()
    magic, version, length = struct.unpack_from('<4sII', data)
    if magic != b'glTF' or version != 2 or length != len(data):
        raise ValueError(f'Invalid GLB header: {path}')
    chunks = {}
    offset = 12
    while offset < len(data):
        size, kind = struct.unpack_from('<II', data, offset)
        offset += 8
        chunks[kind] = data[offset:offset + size]
        offset += size
    if offset != len(data):
        raise ValueError(f'Invalid GLB chunk length: {path}')
    return json.loads(chunks[0x4E4F534A]), chunks[0x004E4942], data


def accessor_values(document, binary, index):
    accessor = document['accessors'][index]
    view = document['bufferViews'][accessor['bufferView']]
    width = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[accessor['type']]
    letter, size = {5121: ('B', 1), 5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}[accessor['componentType']]
    offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
    stride = view.get('byteStride', width * size)
    return [struct.unpack_from('<' + str(width) + letter, binary, offset + i * stride)
            for i in range(accessor['count'])]


def source_cages():
    source_path = ROOT / 'assets/trees/s99-street-tree.motionloom'
    source = source_path.read_text()
    geometries = dict(re.findall(r'<GeometryAsset id="([^"]+)">(.*?)</GeometryAsset>', source, re.S))
    result = {}
    for part in PARTS:
        body = geometries[f's97_source_{part}_mesh_geometry']
        vertices = [(tuple(map(float, position.split(','))), tuple(map(float, uv.split(','))))
                    for position, uv in re.findall(r'<Vertex position=\{\[([^]]+)\]\} uv=\{\[([^]]+)\]\}', body)]
        faces = [tuple(map(int, indices.split(',')))
                 for indices in re.findall(r'<Face indices=\{\[([^]]+)\]\}', body)]
        parent = list(range(len(vertices)))

        def find(index):
            while index != parent[index]:
                parent[index] = parent[parent[index]]
                index = parent[index]
            return index

        for face in faces:
            root = find(face[0])
            for index in face[1:]:
                parent[find(index)] = root
        components = defaultdict(list)
        for index in range(len(vertices)):
            components[find(index)].append(index)
        result[part] = (vertices, faces, sorted(components.values(), key=min))
    return result, source_path


def component_uvs(part, vertices, components, bark_repeat_height):
    mapping = {}
    component_for_vertex = {}
    tube_cap_uv = {}
    rows_per_component = []
    for component_number, indices in enumerate(components):
        rows = defaultdict(list)
        for index in indices:
            rows[vertices[index][1][1]].append(index)
            component_for_vertex[index] = component_number
        ordered_rows = [sorted(rows[v], key=lambda index: vertices[index][1][0]) for v in sorted(rows)]
        centers = [mean([vertices[index][0] for index in row]) for row in ordered_rows]
        lengths = [0.0]
        for a, b in zip(centers, centers[1:]):
            lengths.append(lengths[-1] + distance(a, b))
        if lengths[-1] <= 0:
            raise ValueError(f'Degenerate component in {part}')
        rows_per_component.append(len(ordered_rows))
        if part.startswith('foliage_'):
            if len(indices) != 18 or len(ordered_rows) != 6 or any(len(row) != 3 for row in ordered_rows):
                raise ValueError(f'Expected an independent 6 × 3 leaf cage: {part}, {component_number}')
            # The center column is the raised midrib. Arclength follows the
            # cupped/drooping blade rather than its orientation in the scene.
            centers = [vertices[row[1]][0] for row in ordered_rows]
            lengths = [0.0]
            for a, b in zip(centers, centers[1:]):
                lengths.append(lengths[-1] + distance(a, b))
            for row, length in zip(ordered_rows, lengths):
                for column, index in enumerate(row):
                    mapping[index] = (column / 2, 1 - length / lengths[-1])
        else:
            sides = len(ordered_rows[0])
            if sides < 4 or any(len(row) != sides for row in ordered_rows):
                raise ValueError(f'Expected circular tube rings: {part}, {component_number}')
            for row, center, length in zip(ordered_rows, centers, lengths):
                for side, index in enumerate(row):
                    mapping[index] = (side / sides, length / bark_repeat_height)
                    # End-cap texture coordinates are planar; the side surface
                    # retains a circular wrap and centerline-distance grain.
                    angle = side * math.tau / sides
                    tube_cap_uv[index] = (.5 + .5 * math.cos(angle), .5 + .5 * math.sin(angle))
    return mapping, component_for_vertex, tube_cap_uv, rows_per_component


class GlbBuilder:
    def __init__(self):
        self.binary = bytearray()
        self.document = {
            'asset': {'version': '2.0', 'generator': 'S97 faithful textured S99 GLB repack'},
            'scene': 0, 'scenes': [{'nodes': []}], 'nodes': [], 'meshes': [],
            'buffers': [], 'bufferViews': [], 'accessors': [], 'images': [],
            'textures': [], 'samplers': [
                {'magFilter': 9729, 'minFilter': 9987, 'wrapS': 10497, 'wrapT': 10497},
                {'magFilter': 9729, 'minFilter': 9987, 'wrapS': 33071, 'wrapT': 33071},
            ], 'materials': [], 'extensionsUsed': ['KHR_materials_specular'],
        }

    def view(self, data, target=None):
        self.binary.extend(b'\0' * (-len(self.binary) % 4))
        view = {'buffer': 0, 'byteOffset': len(self.binary), 'byteLength': len(data)}
        if target is not None:
            view['target'] = target
        index = len(self.document['bufferViews'])
        self.document['bufferViews'].append(view)
        self.binary.extend(data)
        return index

    def values(self, values, width, component_type=5126, bounds=False):
        letter = 'f' if component_type == 5126 else 'I'
        packed = bytearray()
        for value in values:
            packed.extend(struct.pack('<' + str(width) + letter, *value))
        accessor = {'bufferView': self.view(packed, 34963 if width == 1 else 34962),
                    'componentType': component_type, 'count': len(values),
                    'type': 'SCALAR' if width == 1 else f'VEC{width}'}
        if bounds:
            accessor['min'] = [min(value[i] for value in values) for i in range(width)]
            accessor['max'] = [max(value[i] for value in values) for i in range(width)]
        index = len(self.document['accessors'])
        self.document['accessors'].append(accessor)
        return index

    def image(self, path, sampler):
        data = path.read_bytes()
        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError(f'Expected a PNG texture: {path}')
        image_index = len(self.document['images'])
        self.document['images'].append({'name': path.stem, 'bufferView': self.view(data), 'mimeType': 'image/png'})
        texture_index = len(self.document['textures'])
        self.document['textures'].append({'source': image_index, 'sampler': sampler})
        return texture_index, {'path': str(path.relative_to(ROOT)), 'sha256': sha256(data),
                               'dimensions': list(struct.unpack_from('>II', data, 16)), 'bytes': len(data)}

    def write(self, path):
        self.binary.extend(b'\0' * (-len(self.binary) % 4))
        self.document['buffers'] = [{'byteLength': len(self.binary)}]
        document = json.dumps(self.document, separators=(',', ':')).encode()
        document += b' ' * (-len(document) % 4)
        data = (struct.pack('<4sII', b'glTF', 2, 28 + len(document) + len(self.binary))
                + struct.pack('<II', len(document), 0x4E4F534A) + document
                + struct.pack('<II', len(self.binary), 0x004E4942) + self.binary)
        path.write_bytes(data)
        return data


def verify_output(path, report):
    document, binary, _ = read_glb(path)
    if len(document['meshes']) != 6 or len(document['materials']) != 6:
        raise ValueError('Expected six retained material batches')
    parts = {part['part']: part for part in report['parts']}
    vertex_count = triangle_count = 0
    for mesh in document['meshes']:
        part = mesh['name']
        primitive = mesh['primitives'][0]
        positions = accessor_values(document, binary, primitive['attributes']['POSITION'])
        normals = accessor_values(document, binary, primitive['attributes']['NORMAL'])
        uvs = accessor_values(document, binary, primitive['attributes']['TEXCOORD_0'])
        indices = [value[0] for value in accessor_values(document, binary, primitive['indices'])]
        if not len(positions) == len(normals) == len(uvs) == len(indices):
            raise ValueError(f'Unexpected repacked accessor lengths in {part}')
        if indices != list(range(len(indices))) or len(indices) % 3:
            raise ValueError(f'Invalid expanded indices in {part}')
        position_hash, normal_hash = hashlib.sha256(), hashlib.sha256()
        for index in indices:
            if not all(math.isfinite(value) for vector in (positions[index], normals[index], uvs[index]) for value in vector):
                raise ValueError(f'Non-finite geometry or UVs in {part}')
            position_hash.update(struct.pack('<3f', *positions[index]))
            normal_hash.update(struct.pack('<3f', *normals[index]))
        if position_hash.hexdigest() != parts[part]['trianglePositionSha256'] or normal_hash.hexdigest() != parts[part]['triangleNormalSha256']:
            raise ValueError(f'Triangle geometry changed while repacking {part}')
        material = document['materials'][primitive['material']]
        foliage = part.startswith('foliage_')
        if material['alphaMode'] != 'OPAQUE' or material['doubleSided'] != foliage:
            raise ValueError(f'Unexpected material visibility in {part}')
        if foliage and any(min(uv[axis] for uv in uvs) != 0 or max(uv[axis] for uv in uvs) != 1 for axis in range(2)):
            raise ValueError(f'Incomplete blade UV range in {part}')
        vertex_count += len(positions)
        triangle_count += len(indices) // 3
    for image, kind in zip(document['images'], ('bark', 'leaf')):
        view = document['bufferViews'][image['bufferView']]
        payload = binary[view['byteOffset']:view['byteOffset'] + view['byteLength']]
        if 'uri' in image or sha256(payload) != report['textures'][kind]['sha256']:
            raise ValueError(f'Embedded {kind} texture changed')
    return {'glbHeaderAndChunkLengths': 'passed', 'trianglePositionsAndNormalsByteExact': 'passed',
            'triangles': triangle_count, 'outputVertices': vertex_count,
            'embeddedPngPayloadsByteExact': 'passed', 'uvFiniteAndLeafEndpoints': 'passed',
            'materialsOpaqueAndLeavesDoubleSided': 'passed', 'nodeTransforms': 'identity'}


def repack(leaf_path, output_path, report_path, bark_repeat_height=.65):
    cages, source_path = source_cages()
    builder = GlbBuilder()
    bark_texture, bark_report = builder.image(ROOT / 'assets/materials/bark-basecolor.png', 0)
    leaf_texture, leaf_report = builder.image(leaf_path, 1)
    report = {'sourceCage': str(source_path.relative_to(ROOT)), 'sourceCageSha256': sha256(source_path.read_bytes()),
              'textures': {'bark': bark_report, 'leaf': leaf_report}, 'parts': [],
              'geometryMethod': 'Indexed source GLB triangle positions and normals are retained exactly; UV seams use duplicate triangle corners. No whole-tree image cards or canopy proxy geometry.',
              'barkUV': f'One circular wrap per disconnected tube; V is cumulative ring-center distance / {bark_repeat_height} m. Closing side triangles unwrap U=0 to U=1; end caps use radial planar UVs.',
              'leafUV': 'Each independent 18-vertex, 10-quad curved leaf cage has six 3-vertex rows. U=0/.5/1 maps left/midrib/right; V=1 at petiole/base and V=0 at tip follows normalized center-column arclength. Texture base belongs at image bottom.',
              'leafColorFactors': {part: list(factor) for part, factor in LEAF_FACTORS.items()},
              'units': 'Original S99 metres; no normalization or transform. Existing S97 hero scale 0.10111124813556671 remains applicable.'}
    expected_triangles = {'tree_bark': 1340, 'young_bark': 35640, 'foliage_deep': 7340,
                          'foliage_green': 17840, 'foliage_mid': 14800, 'foliage_tip': 4020}
    for material_index, part in enumerate(PARTS):
        path = ROOT / f'assets/trees/s99-tree-{part}.glb'
        document, binary, original_data = read_glb(path)
        primitive = document['meshes'][0]['primitives'][0]
        if len(document['meshes']) != 1 or len(document['meshes'][0]['primitives']) != 1 or primitive.get('mode', 4) != 4:
            raise ValueError(f'Expected one triangle mesh in {path}')
        positions = accessor_values(document, binary, primitive['attributes']['POSITION'])
        normals = accessor_values(document, binary, primitive['attributes']['NORMAL'])
        indices = [value[0] for value in accessor_values(document, binary, primitive['indices'])]
        vertices, faces, components = cages[part]
        uv_map, _, cap_uv, row_counts = component_uvs(part, vertices, components, bark_repeat_height)
        by_position = {position: index for index, (position, _) in enumerate(vertices)}
        if len(by_position) != len(vertices):
            raise ValueError(f'Ambiguous source positions in {part}')
        native_indices = [by_position[tuple(round(value, 6) for value in position)] for position in positions]
        expanded_positions, expanded_normals, expanded_uv = [], [], []
        original_triangle_hash = hashlib.sha256()
        original_normal_hash = hashlib.sha256()
        seam_triangles = caps = 0
        for offset in range(0, len(indices), 3):
            triangle = indices[offset:offset + 3]
            native = [native_indices[index] for index in triangle]
            uvs = [uv_map[index] for index in native]
            if not part.startswith('foliage_'):
                if len({vertices[index][1][1] for index in native}) == 1:
                    uvs = [cap_uv[index] for index in native]
                    caps += 1
                elif max(uv[0] for uv in uvs) - min(uv[0] for uv in uvs) > .5:
                    uvs = [(u + 1 if u < .5 else u, v) for u, v in uvs]
                    seam_triangles += 1
            for index, uv in zip(triangle, uvs):
                expanded_positions.append(positions[index])
                expanded_normals.append(normals[index])
                expanded_uv.append(uv)
                original_triangle_hash.update(struct.pack('<3f', *positions[index]))
                original_normal_hash.update(struct.pack('<3f', *normals[index]))
        triangles = len(indices) // 3
        if triangles != expected_triangles[part]:
            raise ValueError(f'Unexpected triangle count for {part}: {triangles}')
        position_index = builder.values(expanded_positions, 3, bounds=True)
        normal_index = builder.values(expanded_normals, 3)
        uv_index = builder.values(expanded_uv, 2)
        index_index = builder.values([(index,) for index in range(len(indices))], 1, 5125)
        original_material = document['materials'][primitive['material']]
        foliage = part.startswith('foliage_')
        builder.document['materials'].append({
            'name': f's97_near_{part}', 'alphaMode': 'OPAQUE', 'doubleSided': foliage,
            'pbrMetallicRoughness': {
                'baseColorTexture': {'index': leaf_texture if foliage else bark_texture},
                'baseColorFactor': list(LEAF_FACTORS[part]) if foliage else [1, 1, 1, 1],
                'metallicFactor': 0,
                'roughnessFactor': original_material['pbrMetallicRoughness']['roughnessFactor'],
            },
            'extensions': original_material.get('extensions', {}),
        })
        builder.document['meshes'].append({'name': part, 'primitives': [{
            'attributes': {'POSITION': position_index, 'NORMAL': normal_index, 'TEXCOORD_0': uv_index},
            'indices': index_index, 'material': material_index, 'mode': 4,
        }]})
        builder.document['nodes'].append({'mesh': material_index, 'name': part})
        builder.document['scenes'][0]['nodes'].append(material_index)
        report['parts'].append({
            'part': part, 'sourceGlbSha256': sha256(original_data), 'sourceCageVertices': len(vertices),
            'sourceCageFaces': len(faces), 'connectedCageComponents': len(components),
            'componentRows': dict(sorted((str(count), row_counts.count(count)) for count in set(row_counts))),
            'outputVertices': len(expanded_positions), 'triangles': triangles,
            'sideUVSeamTriangles': seam_triangles, 'planarCapTriangles': caps,
            'trianglePositionSha256': original_triangle_hash.hexdigest(),
            'triangleNormalSha256': original_normal_hash.hexdigest(),
            'bounds': [builder.document['accessors'][position_index]['min'], builder.document['accessors'][position_index]['max']],
        })
    data = builder.write(output_path)
    report['output'] = str(output_path.relative_to(ROOT))
    report['outputSha256'] = sha256(data)
    report['outputBytes'] = len(data)
    report['triangles'] = sum(part['triangles'] for part in report['parts'])
    report['leaves'] = sum(part['connectedCageComponents'] for part in report['parts'] if part['part'].startswith('foliage_'))
    report['verification'] = verify_output(output_path, report)
    report['status'] = 'passed geometry/UV/embedded-texture verification; visual review pending'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--leaf-texture', type=Path, default=ROOT / 'assets/materials/s97-leaf-detail.png')
    parser.add_argument('--output', type=Path, default=ROOT / 'assets/trees/s97-near-tree-textured.glb')
    parser.add_argument('--report', type=Path, default=ROOT / 'authoring/s97-near-tree-textured-report.json')
    parser.add_argument('--bark-repeat-height', type=float, default=.65)
    args = parser.parse_args()
    args.leaf_texture, args.output, args.report = (path.resolve() for path in (args.leaf_texture, args.output, args.report))
    for path in (args.leaf_texture, args.output, args.report):
        if not path.resolve().is_relative_to(ROOT):
            parser.error('Inputs and outputs must remain local to S97')
    if not args.leaf_texture.is_file():
        parser.error(f'Missing leaf-surface PNG: {args.leaf_texture}')
    if not math.isfinite(args.bark_repeat_height) or args.bark_repeat_height <= 0:
        parser.error('--bark-repeat-height must be a positive finite number')
    report = repack(args.leaf_texture, args.output, args.report, args.bark_repeat_height)
    print(json.dumps({key: report[key] for key in ('output', 'outputBytes', 'triangles', 'leaves', 'status')}, indent=2))


if __name__ == '__main__':
    main()
