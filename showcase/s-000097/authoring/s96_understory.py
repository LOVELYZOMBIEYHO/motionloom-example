#!/usr/bin/env python3
"""Bake S97's static, masked S96 grass into two material batches.

The native Scatter integer hash, float32 low-discrepancy sequence, nearest
exclusion lookup and bilinear terrain sampling are ported from MotionLoom.
The 16,000 accepted tufts retain their crossed-card geometry, original UVs and
embedded PNG bytes. This is authored static geometry rather than runtime LOD.
"""
from __future__ import annotations

import argparse
from array import array
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ('grass-long-blades.glb', 'grass-compact-tuft.glb')
SEED = 96097
COUNT = 16000
FLOAT = struct.Struct('<f')


def f32(value):
    return FLOAT.unpack(FLOAT.pack(value))[0]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def repeat_hash_unit(seed, index, channel):
    value = seed ^ ((index * 0x85EBCA6B) & 0xFFFFFFFF) ^ ((channel * 0xC2B2AE35) & 0xFFFFFFFF)
    value ^= value >> 16
    value = (value * 0x7FEB352D) & 0xFFFFFFFF
    value ^= value >> 15
    value = (value * 0x846CA68B) & 0xFFFFFFFF
    value ^= value >> 16
    return f32(f32(value) / f32(0xFFFFFFFF))


def rgba_png_red(path):
    data = path.read_bytes()
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError(f'Expected PNG: {path}')
    offset, compressed = 8, bytearray()
    width = height = None
    while offset < len(data):
        size, kind = struct.unpack_from('>I4s', data, offset)
        payload = data[offset + 8:offset + 8 + size]
        offset += size + 12
        if kind == b'IHDR':
            width, height, depth, mode, compression, filtering, interlace = struct.unpack('>IIBBBBB', payload)
            if (depth, mode, compression, filtering, interlace) != (8, 6, 0, 0, 0):
                raise ValueError('Expected original noninterlaced RGBA8 placement PNG')
        elif kind == b'IDAT':
            compressed.extend(payload)
    pixels = zlib.decompress(compressed)
    stride = width * 4 + 1
    if len(pixels) != stride * height or any(pixels[row * stride] for row in range(height)):
        raise ValueError('Expected filter-zero rows from S97 original placement-map writer')
    red = [pixels[row * stride + 1 + column * 4] for row in range(height) for column in range(width)]
    return width, height, red, data


def read_glb(path):
    data = path.read_bytes()
    magic, version, size = struct.unpack_from('<4sII', data)
    if (magic, version, size) != (b'glTF', 2, len(data)):
        raise ValueError(f'Invalid GLB: {path}')
    offset, chunks = 12, {}
    while offset < len(data):
        length, kind = struct.unpack_from('<II', data, offset)
        offset += 8
        chunks[kind] = data[offset:offset + length]
        offset += length
    if offset != len(data):
        raise ValueError(f'Invalid GLB chunks: {path}')
    return json.loads(chunks[0x4E4F534A]), chunks[0x004E4942], data


def accessor(document, binary, identity):
    value = document['accessors'][identity]
    view = document['bufferViews'][value['bufferView']]
    width = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3}[value['type']]
    letter, size = {5126: ('f', 4), 5125: ('I', 4), 5123: ('H', 2)}[value['componentType']]
    start = view.get('byteOffset', 0) + value.get('byteOffset', 0)
    stride = view.get('byteStride', width * size)
    return [struct.unpack_from('<' + str(width) + letter, binary, start + index * stride)
            for index in range(value['count'])]


def validate_output(path, batches):
    document, binary, _ = read_glb(path)
    primitives = document['meshes'][0]['primitives']
    if len(primitives) != 2 or len(document['images']) != 2:
        raise ValueError('Expected exactly two grass material batches and images')
    total_vertices = total_triangles = 0
    normal_error = 0
    for primitive, batch, image in zip(primitives, batches, document['images']):
        positions = accessor(document, binary, primitive['attributes']['POSITION'])
        normals = accessor(document, binary, primitive['attributes']['NORMAL'])
        uvs = accessor(document, binary, primitive['attributes']['TEXCOORD_0'])
        indices = [value[0] for value in accessor(document, binary, primitive['indices'])]
        if not len(positions) == len(normals) == len(uvs) == batch['vertices']:
            raise ValueError('Invalid grass attribute lengths')
        if len(indices) != batch['triangles'] * 3 or min(indices) < 0 or max(indices) >= len(positions):
            raise ValueError('Invalid grass triangle indices')
        if not all(math.isfinite(value) for vectors in (positions, normals, uvs) for vector in vectors for value in vector):
            raise ValueError('Non-finite grass geometry')
        normal_error = max(normal_error, max(abs(math.sqrt(sum(value * value for value in normal)) - 1) for normal in normals))
        if any(not 0 <= value <= 1 for uv in uvs for value in uv):
            raise ValueError('Original grass UV range changed')
        actual_bounds = {'min': [min(p[axis] for p in positions) for axis in range(3)],
                         'max': [max(p[axis] for p in positions) for axis in range(3)]}
        if actual_bounds != batch['bounds']:
            raise ValueError('Grass bounds do not match positions')
        material = document['materials'][primitive['material']]
        if material['alphaMode'] != 'MASK' or material['doubleSided'] is not True:
            raise ValueError('Original masked two-sided grass semantics changed')
        view = document['bufferViews'][image['bufferView']]
        payload = binary[view['byteOffset']:view['byteOffset'] + view['byteLength']]
        if 'uri' in image or sha256(payload) != batch['textureSha256']:
            raise ValueError('Original embedded grass image bytes changed')
        total_vertices += len(positions)
        total_triangles += len(indices) // 3
    if (total_vertices, total_triangles) != (128000, 64000) or normal_error > 1e-6:
        raise ValueError('Unexpected grass totals or normal lengths')
    return {'headerAndChunks': 'passed', 'indicesFiniteGeometryAndBounds': 'passed',
            'originalUVRange': 'passed', 'originalEmbeddedTextureBytes': 'passed',
            'alphaMaskAndDoubleSided': 'passed', 'normalUnitMaxError': normal_error,
            'vertices': total_vertices, 'triangles': total_triangles}


def placements():
    source = (ROOT / 'main.motionloom').read_text()
    terrain = re.search(r'<TerrainAsset\b(?=[^>]*\bid="s97_terrain")[^>]*/>', source).group()
    size = [f32(float(value)) for value in re.search(r'size=\{\[([^]]+)\]\}', terrain).group(1).split(',')]
    height_scale = f32(float(re.search(r'heightScale="([^"]+)"', terrain).group(1)))
    height_offset = f32(float(re.search(r'heightOffset="([^"]+)"', terrain).group(1)))
    width, height, height_red, height_bytes = rgba_png_red(ROOT / 'assets/terrain/s97-height.png')
    ew, eh, exclusion, exclusion_bytes = rgba_png_red(ROOT / 'assets/terrain/s97-forest-exclusion.png')
    values = [f32(value / 255.0) for value in height_red]

    def sample(u, v):
        fx = f32(min(1, max(0, u)) * (width - 1))
        fy = f32(min(1, max(0, v)) * (height - 1))
        x0, y0 = math.floor(fx), math.floor(fy)
        x1, y1 = min(x0 + 1, width - 1), min(y0 + 1, height - 1)
        tx, ty = f32(fx - x0), f32(fy - y0)
        top = f32(f32(values[y0 * width + x0] * f32(1 - tx)) + f32(values[y0 * width + x1] * tx))
        bottom = f32(f32(values[y1 * width + x0] * f32(1 - tx)) + f32(values[y1 * width + x1] * tx))
        blend = f32(f32(top * f32(1 - ty)) + f32(bottom * ty))
        return f32(height_offset + f32(blend * height_scale))

    du, dv = f32(1 / (width - 1)), f32(1 / (height - 1))
    dx, dz = max(f32(f32(size[0] * du) * 2), .0001), max(f32(f32(size[1] * dv) * 2), .0001)
    shift_u, shift_v = repeat_hash_unit(SEED, 0, 91), repeat_hash_unit(SEED, 0, 97)
    increment_u, increment_v = f32(.7548777), f32(.5698403)
    low, high = f32(.035), f32(.067)
    accepted, rejected_mask, rejected_slope = [], 0, 0
    for attempt in range(COUNT * 64):
        u = f32(f32(f32(attempt + .5) * increment_u) + shift_u)
        v = f32(f32(f32(attempt + .5) * increment_v) + shift_v)
        u, v = f32(u - math.trunc(u)), f32(v - math.trunc(v))
        x_pixel = int(math.floor(f32(u * (ew - 1)) + .5))
        y_pixel = int(math.floor(f32(v * (eh - 1)) + .5))
        if exclusion[y_pixel * ew + x_pixel] >= 128:
            rejected_mask += 1
            continue
        gx = f32(f32(sample(f32(u + du), v) - sample(f32(u - du), v)) / dx)
        gz = f32(f32(sample(u, f32(v + dv)) - sample(u, f32(v - dv))) / dz)
        slope = f32(math.degrees(f32(math.atan(f32(math.hypot(gx, gz))))))
        if slope > 58:
            rejected_slope += 1
            continue
        # Native Scatter stores positions in six-decimal literal expressions.
        x = f32(float(f'{f32(f32(u - .5) * size[0]):.6f}'))
        z = f32(float(f'{f32(f32(v - .5) * size[1]):.6f}'))
        y = f32(float(f'{f32(sample(u, v) + f32(-.010)):.6f}'))
        choice = 0 if f32(repeat_hash_unit(SEED, attempt, 107) * 100) <= 45 else 1
        scale = f32(low + f32(f32(high - low) * repeat_hash_unit(SEED, attempt, 109)))
        yaw = f32(360 * repeat_hash_unit(SEED, attempt, 113))
        accepted.append({'attempt': attempt, 'species': choice, 'position': (x, y, z),
                         'scale': scale, 'rotationY': yaw, 'slope': slope})
        if len(accepted) == COUNT:
            break
    if len(accepted) != COUNT:
        raise ValueError(f'Placed only {len(accepted)} of {COUNT} tufts')
    return accepted, {'seed': SEED, 'count': COUNT, 'slopeRange': [0, 58],
                     'scaleRange': [.035, .067], 'rotationYRange': [0, 360], 'surfaceOffset': -.010,
                     'variantWeights': [45, 55], 'heightMapSha256': sha256(height_bytes),
                     'exclusionMapSha256': sha256(exclusion_bytes), 'acceptedAttempts': accepted[-1]['attempt'] + 1,
                     'rejectedByExclusionMap': rejected_mask, 'rejectedBySlope': rejected_slope,
                     'maximumAcceptedSlope': max(tree['slope'] for tree in accepted),
                     'terrainSize': size, 'heightScale': height_scale, 'heightOffset': height_offset,
                     'method': 'Port of native Scatter integer hash, float32 irrational sequence, nearest red exclusion lookup, bilinear height and neighboring-height slope. Position literals round to native six decimals. Float32 trig/hypot/atan use rounded Python libm; no native bitwise-equivalence claim.'}


def build(output, report_path):
    placed, placement_report = placements()
    document = {'asset': {'version': '2.0', 'generator': 'S97 static two-material S96 understory bake'},
                'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'name': 's97-understory-batched', 'mesh': 0}],
                'meshes': [{'name': 's97-understory-batched', 'primitives': []}], 'buffers': [],
                'bufferViews': [], 'accessors': [], 'materials': [], 'textures': [], 'images': [],
                'samplers': [{'wrapS': 33071, 'wrapT': 33071, 'magFilter': 9729, 'minFilter': 9987}]}
    binary, batches = bytearray(), []

    def add_view(payload, target=None):
        binary.extend(b'\0' * (-len(binary) % 4))
        view = {'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(payload)}
        if target:
            view['target'] = target
        identity = len(document['bufferViews'])
        document['bufferViews'].append(view)
        binary.extend(payload)
        return identity

    def add_accessor(values, width, kind, bounds=False):
        if sys.byteorder != 'little':
            values.byteswap()
        definition = {'bufferView': add_view(values.tobytes(), 34963 if kind == 'I' else 34962),
                      'componentType': 5125 if kind == 'I' else 5126, 'count': len(values) // width,
                      'type': 'SCALAR' if width == 1 else f'VEC{width}'}
        if bounds:
            definition['min'] = [min(values[axis::width]) for axis in range(width)]
            definition['max'] = [max(values[axis::width]) for axis in range(width)]
        identity = len(document['accessors'])
        document['accessors'].append(definition)
        return identity

    for species, name in enumerate(ASSETS):
        path = ROOT / 'assets/reference-forest' / name
        original, source_binary, source_bytes = read_glb(path)
        primitive = original['meshes'][0]['primitives'][0]
        ps = accessor(original, source_binary, primitive['attributes']['POSITION'])
        ns = accessor(original, source_binary, primitive['attributes']['NORMAL'])
        us = accessor(original, source_binary, primitive['attributes']['TEXCOORD_0'])
        ids = [value[0] for value in accessor(original, source_binary, primitive['indices'])]
        if len(ps) != 8 or len(ids) != 12:
            raise ValueError(f'Expected two original crossed quads in {name}')
        positions, normals, uvs, indices = array('f'), array('f'), array('f'), array('I')
        selected = [tuft for tuft in placed if tuft['species'] == species]
        for tuft in selected:
            radians = f32(tuft['rotationY'] * f32(math.pi / 180))
            sine, cosine = f32(math.sin(radians)), f32(math.cos(radians))
            tx, ty, tz = tuft['position']
            scale = tuft['scale']
            base = len(positions) // 3
            for (x, y, z), (nx, ny, nz), uv in zip(ps, ns, us):
                x, y, z = f32(x * scale), f32(y * scale), f32(z * scale)
                positions.extend((f32(tx + f32(f32(x * cosine) + f32(z * sine))),
                                  f32(ty + y), f32(tz + f32(f32(-x * sine) + f32(z * cosine)))))
                normals.extend((f32(f32(nx * cosine) + f32(nz * sine)), ny,
                                f32(f32(-nx * sine) + f32(nz * cosine))))
                uvs.extend(uv)
            indices.extend(base + index for index in ids)
        pi = add_accessor(positions, 3, 'f', True)
        ni = add_accessor(normals, 3, 'f')
        ui = add_accessor(uvs, 2, 'f')
        ii = add_accessor(indices, 1, 'I')
        image = original['images'][0]
        view = original['bufferViews'][image['bufferView']]
        payload = source_binary[view.get('byteOffset', 0):view.get('byteOffset', 0) + view['byteLength']]
        document['images'].append({'name': image.get('name', name), 'bufferView': add_view(payload), 'mimeType': image['mimeType']})
        document['textures'].append({'sampler': 0, 'source': species})
        material = copy.deepcopy(original['materials'][primitive['material']])
        material['pbrMetallicRoughness']['baseColorTexture']['index'] = species
        document['materials'].append(material)
        document['meshes'][0]['primitives'].append({'attributes': {'POSITION': pi, 'NORMAL': ni, 'TEXCOORD_0': ui},
                                                  'indices': ii, 'material': species, 'mode': 4})
        batches.append({'source': str(path.relative_to(ROOT)), 'sourceSha256': sha256(source_bytes),
                        'tufts': len(selected), 'vertices': len(positions) // 3, 'triangles': len(indices) // 3,
                        'textureSha256': sha256(payload), 'embeddedTextureBytes': len(payload),
                        'textureBytesPreserved': True, 'originalMaterial': original['materials'][primitive['material']],
                        'bounds': {'min': document['accessors'][pi]['min'], 'max': document['accessors'][pi]['max']}})
    binary.extend(b'\0' * (-len(binary) % 4))
    document['buffers'] = [{'byteLength': len(binary)}]
    encoded = json.dumps(document, separators=(',', ':')).encode()
    encoded += b' ' * (-len(encoded) % 4)
    data = (struct.pack('<4sII', b'glTF', 2, 28 + len(encoded) + len(binary))
            + struct.pack('<II', len(encoded), 0x4E4F534A) + encoded
            + struct.pack('<II', len(binary), 0x004E4942) + binary)
    output.write_bytes(data)
    report = {'output': str(output.relative_to(ROOT)), 'outputSha256': sha256(data), 'outputBytes': len(data),
              'placement': placement_report, 'batches': batches,
              'tufts': len(placed), 'vertices': sum(batch['vertices'] for batch in batches),
              'triangles': sum(batch['triangles'] for batch in batches), 'materialPrimitives': 2,
              'integration': 'Replace only the 16,000-tuft Scatter with one identity Model: scale=1, scaleMode=none, castShadow=false, receiveShadow=true. Original grass textures and alpha-mask materials are unchanged.',
              'placementFingerprint': sha256(json.dumps(placed, separators=(',', ':')).encode()),
              'placementSamples': placed[:3] + placed[-3:],
              'verification': validate_output(output, batches),
              'status': 'passed binary/geometry/texture verification; native GPU visual validation pending'}
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ('output', 'outputBytes', 'tufts', 'vertices', 'triangles', 'materialPrimitives')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'assets/reference-forest/s97-understory-batched.glb')
    parser.add_argument('--report', type=Path, default=ROOT / 'authoring/s96-understory-report.json')
    args = parser.parse_args()
    args.output, args.report = args.output.resolve(), args.report.resolve()
    if any(not path.is_relative_to(ROOT) for path in (args.output, args.report)):
        parser.error('Outputs must remain local to S97')
    build(args.output, args.report)
