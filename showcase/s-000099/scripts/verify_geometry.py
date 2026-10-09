#!/usr/bin/env python3
"""Check emitted wall voids and camera positions against S99's design contract."""
from pathlib import Path
import hashlib
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1]
script = ROOT.joinpath('main.motionloom').read_text()


def attributes(tag):
    return dict(re.findall(r'(\w+)="([^"]*)"', tag))


def vector(tag, key):
    match = re.search(r'\b'+key+r'=\{\[([^]]+)\]\}', tag)
    return [float(v) for v in match[1].split(',')] if match else None


# Read the emitted DSL, rather than the generator's layout manifest, for solids.
boxes = {}
geometries = {}
for geometry_id, body in re.findall(r'<GeometryAsset id="([^"]+)">(.*?)</GeometryAsset>', script, re.S):
    primitives = re.findall(r'<Primitive\b[^>]+/>', body)
    if primitives and attributes(primitives[0]).get('shape') == 'box':
        geometries[geometry_id] = vector(primitives[0], 'size')
for tag in re.findall(r'<MeshAsset\b[^>]+/>', script):
    attr = attributes(tag)
    if attr.get('geometry') in geometries:
        boxes[attr['id']] = geometries[attr['geometry']]
solids = {}
for tag in re.findall(r'<Model\b[^>]+/>', script):
    attr = attributes(tag)
    size = boxes.get(attr['asset'])
    if not size:
        continue
    position = vector(tag, 'position')
    rotation = vector(tag, 'rotation') or [0, 0, 0]
    angle = math.radians(rotation[1])
    hx = (abs(math.cos(angle))*size[0]+abs(math.sin(angle))*size[2])/2
    hz = (abs(math.sin(angle))*size[0]+abs(math.cos(angle))*size[2])/2
    solids[attr['id']] = dict(position=position, half=[hx,size[1]/2,hz])


def overlap(a, b):
    return min(a[1],b[1])-max(a[0],b[0]) > 1e-5


openings = [
    ('south','x',-5.3,-.8,0,2.6), ('south','x',.15,1.25,0,2.4),
    ('south','x',3.25,5.5,.85,2.5), ('north','x',-5.3,-1.6,1.25,2.5),
    ('north','x',3.3,5.5,1,2.5), ('west','z',-.7,2.1,.65,2.6),
    ('east','z',-.8,.6,1.65,2.5), ('east','z',1.7,3.3,.85,2.5),
    ('privacy','z',-.5,.6,0,2.4), ('hall','z',-3,-2.1,0,2.25),
    ('hall','z',-.65,.25,0,2.25), ('hall','z',1.5,2.4,0,2.25),
]
checks = []
for wall,axis,a,b,sill,head in openings:
    candidates = [(name,s) for name,s in solids.items() if re.fullmatch('s99_'+wall+r'_\d+',name)]
    assert candidates, f'Missing wall {wall}'
    blockers = []
    for name,solid in candidates:
        p,h = solid['position'],solid['half']
        i = 0 if axis == 'x' else 2
        if overlap([a,b],[p[i]-h[i],p[i]+h[i]]) and overlap([sill,head],[p[1]-h[1],p[1]+h[1]]):
            blockers.append(name)
    assert not blockers, f'Wall fills intended opening: {blockers}'
    checks.append(dict(wall=wall,span=[a,b],vertical=[sill,head],solid_blockers=blockers))

# The primary camera previously intersected an open door. Check every authored
# camera endpoint against final box geometry, with a small lens clearance.
camera_checks = []
endpoints = []
for tag in re.findall(r'<Camera3D\b[^>]+/>',script):
    endpoints.append((attributes(tag)['id'],vector(tag,'position')))
for block in re.findall(r'<AnimationTarget\b[^>]+>.*?</AnimationTarget>',script,re.S):
    attr = attributes(block.split('>')[0]+'>')
    if attr.get('property') == 'position' and attr.get('node','').startswith('s99_'):
        for key in re.findall(r'<Key\b[^>]+/>',block):
            value = attributes(key)['value']
            endpoints.append((attr['node'],[float(v) for v in value.strip('[]').split(',')]))
for name,position in endpoints:
    blockers = []
    for solid_name,solid in solids.items():
        p,h = solid['position'],solid['half']
        if all(abs(position[i]-p[i]) < h[i]+.025 for i in range(3)):
            blockers.append(solid_name)
    assert not blockers, f'Camera {name} is inside solid geometry: {blockers}'
    camera_checks.append(dict(camera=name,position=position,box_blockers=blockers))

# A room leaf must open east into its room instead of obstructing the private hall.
for name in ['guest_door','bath_door','primary_door']:
    s = solids['s99_'+name]
    assert s['position'][0]-s['half'][0] > 2.65, f'{name} obstructs hall'

report = dict(source_sha256=hashlib.sha256(script.encode()).hexdigest(),
              status='passed',opening_checks=checks,camera_endpoint_checks=camera_checks,
              scope='Authored wall solids and box bounds; not a building-code, accessibility, swept-camera or interactive-navigation certification.')
ROOT.joinpath('evidence/geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'Passed {len(checks)} wall voids and {len(camera_checks)} camera endpoints; three room doors clear the hall.')
