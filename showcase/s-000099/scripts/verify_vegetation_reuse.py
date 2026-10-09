#!/usr/bin/env python3
"""Check S99's shared tree/planter meshes and conservative placement bounds."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'main.motionloom').read_text()
source_sha = hashlib.sha256(source.encode()).hexdigest()
prior = json.loads((ROOT / 'evidence/vegetation-check.json').read_text())
assert prior['sourceSHA256'] == '164a9f7f28155816c0848b886ed161433d2e02df12343717bfcd1ca6585a2168'
assert prior['pass'] and all(prior['checks'].values())

geometries = dict(re.findall(r'<GeometryAsset id="([^"]+)">(.*?)</GeometryAsset>', source, re.S))
meshes = dict(re.findall(r'<MeshAsset id="([^"]+)" material="[^"]+" geometry="([^"]+)" />', source))
for material in ('foliage_deep', 'foliage_green', 'foliage_mid', 'foliage_tip', 'tree_bark', 'young_bark'):
    west = f's99_tree_west_{material}_mesh'
    east = f's99_tree_east_{material}_mesh'
    assert meshes[west] == meshes[east]
for index in range(4):
    base = f's99_garden{index}_'
    repeated = f's99_garden{index+4}_'
    for asset in meshes:
        if asset.startswith(base):
            assert meshes[repeated + asset[len(base):]] == meshes[asset]

# Rigid rotation does not change topology, leaf attachment or a tree's radial
# footprint. Use the full cage's maximum radius for conservative clearance.
radius = 0.0
points = []
low_y = float('inf')
high_y = float('-inf')
for geometry in {meshes[name] for name in meshes if name.startswith('s99_tree_west_')}:
    for x, y, z in re.findall(r'<Vertex position=\{\[([^,]+),([^,]+),([^]]+)\]\}', geometries[geometry]):
        x, y, z = float(x), float(y), float(z)
        points.append((x, y, z))
        radius = max(radius, math.hypot(x, z))
        low_y = min(low_y, y)
        high_y = max(high_y, y)
assert 2.0 < radius < 2.3
house = prior['houseBodyEnvelope']
trees = [('tree_west', -8.35, 2.0, 0), ('tree_east', 8.0, -1.0, 137)]
clearance = []
for name, x, z, rotation in trees:
    # Check both possible Y-axis conventions, so the clearance proof does not
    # depend on how a scene backend composes the model's rotation quaternion.
    transformed = []
    for degrees in ({rotation, -rotation} if rotation else {0}):
        sine, cosine = math.sin(math.radians(degrees)), math.cos(math.radians(degrees))
        transformed.extend((x+cosine*px+sine*pz, z-sine*px+cosine*pz)
                           for px, _, pz in points)
    x_range = [min(p[0] for p in transformed), max(p[0] for p in transformed)]
    z_range = [min(p[1] for p in transformed), max(p[1] for p in transformed)]
    assert x_range[1] < house[0][0] or x_range[0] > house[0][1]
    for camera in prior['cameraChecks']:
        cx, _, cz = camera['translationHull']
        assert cx[1] < x_range[0] or cx[0] > x_range[1] or cz[1] < z_range[0] or cz[0] > z_range[1], (name, camera['id'])
    clearance.append({'name': name, 'conservative_x': x_range,
                      'conservative_z': z_range, 'vertical': [low_y, high_y]})

planting = json.loads((ROOT / 'evidence/planting-geometry.json').read_text())
assert planting['source_sha256'] == source_sha
assert len(planting['plants']) == 14
assert sum(p['leaves'] for p in planting['plants']) == 5690
distinct = sum(p['leaves'] for p in planting['plants']
               if p['name'] not in {'tree_east', 'garden4', 'garden5', 'garden6', 'garden7'})
assert distinct == 2914
assert len(re.findall(r'<Model id="s99_tree_east_[^"]+"[^>]+rotation=\{\[0,137,0\]\}', source)) == 6

report = {
    'source_sha256': source_sha,
    'status': 'passed',
    'prior_full_vegetation_audit_source_sha256': prior['sourceSHA256'],
    'method': 'The reused source cages passed the prior full topology and attachment audit. Shared GeometryAsset references are checked directly; rigid rotation preserves topology. Both Y-axis rotation sign conventions are bounded against the house and camera translation hulls.',
    'scene_leaves': 5690,
    'unique_leaf_forms': distinct,
    'tree_radius_metres': radius,
    'tree_clearance': clearance,
}
(ROOT / 'evidence/vegetation-reuse-check.json').write_text(json.dumps(report, indent=2)+'\n')
print(f'PASS: 5,690 visible leaves / {distinct:,} distinct leaf forms; tree radius {radius:.3f} m')
