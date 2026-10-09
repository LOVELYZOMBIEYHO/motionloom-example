#!/usr/bin/env python3
"""Check authored city roof/plinth faces for near-coplanar material conflicts."""
import argparse
import hashlib
import json
from pathlib import Path
from verify_preservation import parse, walk

ROOT = Path(__file__).resolve().parents[1]


def inspect(path):
    source = path.read_text()
    nodes = list(walk(parse(source)))
    geometries = {n.attrs['id']: n for n in nodes if n.tag == 'GeometryAsset'}
    meshes = {n.attrs['id']: n for n in nodes if n.tag == 'MeshAsset'}
    legacy_primitives = {n.attrs['id']: n for n in nodes if n.tag == 'PrimitiveAsset'}
    buildings = []
    for building_index, node in enumerate(n for n in nodes if n.tag == 'CompoundAsset'
                                          and str(n.attrs.get('id', '')).startswith('s99_city_detail_')):
        boxes = []
        for index, child in enumerate(node.children):
            mesh = meshes.get(child.attrs.get('asset'))
            geometry = geometries.get(mesh.attrs.get('geometry')) if mesh else None
            asset = next((c for c in geometry.children if c.tag == 'Primitive'), None) if geometry else None
            if asset is None:
                asset = legacy_primitives.get(child.attrs.get('asset'))
            if asset is None or asset.attrs.get('shape') != 'box' or child.attrs.get('rotation'):
                continue
            boxes.append(dict(instance=index, size=asset.attrs['size'],
                              position=child.attrs['position'],
                              material=mesh.attrs['material'] if mesh else asset.attrs['material']))
        # Material-batched native meshes store six four-vertex quads per box.
        # Inspect their actual geometry as well as the residual CompoundAsset.
        prefix = f's99_city_merged_{building_index}_'
        for mesh_id, mesh in meshes.items():
            if not mesh_id.startswith(prefix):
                continue
            geometry = geometries[mesh.attrs['geometry']]
            vertices = [child.attrs['position'] for cage in geometry.children
                        if cage.tag == 'Mesh' for child in cage.children if child.tag == 'Vertex']
            assert len(vertices) % 24 == 0, mesh_id
            for offset in range(0, len(vertices), 24):
                group = vertices[offset:offset + 24]
                lower = [min(vertex[axis] for vertex in group) for axis in range(3)]
                upper = [max(vertex[axis] for vertex in group) for axis in range(3)]
                boxes.append(dict(instance=f'{mesh_id}:{offset // 24}',
                                  size=[upper[axis] - lower[axis] for axis in range(3)],
                                  position=[(upper[axis] + lower[axis]) / 2 for axis in range(3)],
                                  material=mesh.attrs['material']))
        roof = [b for b in boxes if b['material'] == 'city_roof']
        plinth = [b for b in boxes if b['material'] == 'city_sill'
                  and b['size'][0] > 4 and b['size'][2] > 4 and b['position'][1] < .1]
        assert len(roof) == len(plinth) == 1, node.attrs['id']
        conflicts = []
        for target, axes in [(roof[0], [1]), (plinth[0], [0, 2])]:
            for other in boxes:
                if target is other or target['material'] == other['material']:
                    continue
                for axis in axes:
                    for sign in ([1] if axis == 1 else [-1, 1]):
                        a = target['position'][axis] + sign*target['size'][axis]/2
                        b = other['position'][axis] + sign*other['size'][axis]/2
                        # The DSL uses five significant digits. Include up to
                        # 0.1 mm of rounding drift, which still risks fighting.
                        if abs(a-b) > 1e-4:
                            continue
                        overlap = [min(target['position'][d]+target['size'][d]/2,
                                       other['position'][d]+other['size'][d]/2)
                                   - max(target['position'][d]-target['size'][d]/2,
                                         other['position'][d]-other['size'][d]/2)
                                   for d in range(3) if d != axis]
                        if min(overlap) > 1e-5:
                            conflicts.append(dict(surface='roof' if axis == 1 else 'plinth',
                                                  target=target['instance'], other=other['instance'],
                                                  axis=axis, sign=sign))
        buildings.append(dict(id=node.attrs['id'], conflicts=conflicts))
    assert len(buildings) == 4
    return dict(source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                passCheck=not any(b['conflicts'] for b in buildings), buildings=buildings,
                conflict_count=sum(len(b['conflicts']) for b in buildings))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', type=Path)
    args = parser.parse_args()
    report = inspect(ROOT/'main.motionloom')
    report['plane_tolerance_metres'] = 1e-4
    if args.baseline:
        baseline = inspect(args.baseline)
        report['baseline_source_sha256'] = baseline['source_sha256']
        report['baseline_conflict_count'] = baseline['conflict_count']
    (ROOT/'evidence/city-surface-check.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f"City roof/plinth coplanar material conflicts: {report['conflict_count']}")
    raise SystemExit(0 if report['passCheck'] else 1)
