#!/usr/bin/env python3
"""Propose S99 furniture/cloth meshes using existing canonical GeometryAsset DSL.

Only allowlisted GeometryAsset blocks are replaced. Shared MeshAsset bindings,
CompoundAsset transforms, Models, anchors, materials and all timeline content
stay byte-for-byte intact. Explicit vertices use metre UV coordinates; existing
WeightedNormals smooths the deliberate UV-chart splits without moving vertices.
This is deterministic authored shaping, not cloth/pressure simulation.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import re

# Keep IDs and the original metre-space envelopes from build_showcase.py.
TARGETS = {
    "s99_p292_geometry": ((.48, .07, .48), "chair_seat", "Rounded bent-wood seat with a shallow sitting dish"),
    "s99_p293_geometry": ((.48, .30, .065), "chair_back", "Continuous bowed back shell, curved toward the sitter at both ends"),
    "s99_p304_geometry": ((.85, .22, .81), "sofa_seat", "Inflated cushion with a shallow central sitting compression"),
    "s99_p305_geometry": ((.89, .56, .20), "sofa_back", "Inflated back pad with a lower lumbar compression and inset seam"),
    "s99_p306_geometry": ((.20, .49, 1.0), "sofa_arm", "Soft inflated arm with a gently compressed top"),
    "s99_p307_geometry": ((.46, .42, .18), "upright_pillow", "Puffed lounge pillow with a pinched perimeter seam"),
    "s99_p308_geometry": ((.43, .39, .17), "upright_pillow", "Puffed lounge pillow with a pinched perimeter seam"),
    "s99_p330_geometry": ((.48, .03, 1.58), "bed_throw", "Thin throw with deterministic low folds and restrained edge sag above the duvet"),
    "s99_p332_geometry": ((.48, .17, .57), "bed_pillow", "Inflated lying pillow with soft top compression and perimeter seam"),
    "s99_p345_geometry": ((.65, .16, .40), "bed_pillow", "Inflated guest pillow with soft top compression and perimeter seam"),
    "s99_p361_geometry": ((.012, .53, .37), "towel", "Thin hanging towel with vertical folds and slightly irregular lower hem"),
}


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def add(a, b):
    return [a[i] + b[i] for i in range(3)]


def sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def cross(a, b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def length(a):
    return math.sqrt(dot(a, a))


def smoothstep(a, b, x):
    t = max(0., min(1., (x-a)/(b-a)))
    return t*t*(3.-2.*t)


class Mesh:
    def __init__(self):
        self.vertices = []
        self.uvs = []
        self.faces = []

    def vertex(self, position, uv):
        # Six decimals retain micrometre geometry precision and identical seams.
        self.vertices.append([round(v, 6) for v in position])
        self.uvs.append([round(v, 6) for v in uv])
        return len(self.vertices)-1

    def face(self, ids, reverse=False):
        self.faces.append(list(reversed(ids)) if reverse else list(ids))

    def xml(self, identifier):
        def vector(values):
            return "{[" + ",".join(f"{v:.6f}".rstrip("0").rstrip(".") if v else "0" for v in values) + "]}"
        lines = [f'    <GeometryAsset id="{identifier}">', '      <Mesh>']
        lines += [f'        <Vertex position={vector(p)} uv={vector(uv)} />' for p, uv in zip(self.vertices, self.uvs)]
        lines += ['        <Face indices={[' + ','.join(str(i) for i in face) + ']} />' for face in self.faces]
        lines += ['      </Mesh>', '      <Modifiers>',
                  '        <WeightedNormals strength="1" keepSharpEdges="false" />',
                  '      </Modifiers>', '    </GeometryAsset>']
        return "\n".join(lines)

    def inspect(self, original_size, underside_extension=0.):
        edges = defaultdict(list)
        welded = {}
        for point in self.vertices:
            welded.setdefault(tuple(point), len(welded))
        signed_volume = 0.
        min_area = math.inf
        uv_ratios = []
        for face in self.faces:
            ids = [welded[tuple(self.vertices[i])] for i in face]
            if len(set(ids)) != len(ids):
                raise ValueError("collapsed mesh face")
            for a, b in zip(ids, ids[1:] + ids[:1]):
                edges[tuple(sorted((a, b)))].append((a, b))
            for j in range(1, len(face)-1):
                a, b, c = (self.vertices[i] for i in [face[0], face[j], face[j+1]])
                area = length(cross(sub(b, a), sub(c, a))) / 2.
                min_area = min(min_area, area)
                signed_volume += dot(a, cross(b, c))/6.
                ua, ub, uc = (self.uvs[i] for i in [face[0], face[j], face[j+1]])
                uv_area = abs((ub[0]-ua[0])*(uc[1]-ua[1])-(ub[1]-ua[1])*(uc[0]-ua[0]))/2.
                if uv_area <= 1e-12:
                    raise ValueError("degenerate metre UV triangle")
                uv_ratios.append(area/uv_area)
        boundary = sum(len(directions) == 1 for directions in edges.values())
        nonmanifold = sum(len(directions) != 2 for directions in edges.values())
        inconsistent = sum(len(directions) == 2 and directions[0] != tuple(reversed(directions[1])) for directions in edges.values())
        minimum = [min(p[i] for p in self.vertices) for i in range(3)]
        maximum = [max(p[i] for p in self.vertices) for i in range(3)]
        original_minimum = [-s/2. for s in original_size]
        approved_minimum = original_minimum.copy()
        approved_minimum[1] -= underside_extension
        within_original = all(minimum[i] >= original_minimum[i]-1e-6 and maximum[i] <= original_size[i]/2.+1e-6 for i in range(3))
        within = all(minimum[i] >= approved_minimum[i]-1e-6 and maximum[i] <= original_size[i]/2.+1e-6 for i in range(3))
        if nonmanifold or inconsistent or min_area <= 1e-10 or signed_volume <= 0. or not within:
            raise ValueError(f"geometry validation failed: edges={nonmanifold}, winding={inconsistent}, area={min_area}, volume={signed_volume}, bounded={within}")
        return dict(vertices=len(self.vertices), weldedVertices=len(welded), faces=len(self.faces),
                    triangles=sum(len(f)-2 for f in self.faces), boundsMin=minimum, boundsMax=maximum,
                    originalBoundsMin=original_minimum, originalBoundsMax=[s/2. for s in original_size],
                    approvedBoundsMin=approved_minimum, approvedUndersideExtensionM=underside_extension,
                    insideOriginalEnvelope=within_original, insideApprovedEnvelope=within,
                    weldedBoundaryEdges=boundary,
                    weldedNonmanifoldEdges=nonmanifold, inconsistentWindingEdges=inconsistent,
                    minimumTriangleAreaM2=min_area, enclosedVolumeM3=signed_volume,
                    uvUnits="metres; existing material sampling scales unchanged",
                    uvAreaStretchRange=[min(uv_ratios), max(uv_ratios)],
                    normals="Existing WeightedNormals, area-weighted and smoothed across coincident UV-chart vertices")


def cushion(size, kind):
    mesh = Mesh()
    # Lp cube projection creates puffed faces with a continuous rounded rim.
    exponent = 3.0 if "pillow" in kind else 5.0
    steps = 14 if "pillow" in kind else 16
    for axis in range(3):
        u_axis, v_axis = (axis+1)%3, (axis+2)%3
        for sign in [-1., 1.]:
            indices = []
            for row in range(steps+1):
                v = -1.+2.*row/steps
                for column in range(steps+1):
                    u = -1.+2.*column/steps
                    q = [0., 0., 0.]
                    q[axis], q[u_axis], q[v_axis] = sign, u, v
                    norm = sum(abs(t)**exponent for t in q)**(1./exponent)
                    q = [t/norm for t in q]
                    p = [q[i]*size[i]/2. for i in range(3)]
                    if kind == "sofa_seat":
                        p[1] -= .018*max(q[1], 0.)*math.exp(-3.5*((q[0]-.10)**2+(q[2]-.12)**2))
                        # The original cushion floats 30 mm over the frame.
                        # Extend only its underside; visible top/footprint stay.
                        p[1] += .030*min(q[1], 0.)
                    elif kind == "sofa_back":
                        p[2] -= max(q[2], 0.)*(.009*math.exp(-4.*(q[0]**2+(q[1]+.4)**2))
                                  +.0025*math.exp(-((q[1]+.76)/.065)**2))
                    elif kind == "sofa_arm":
                        p[1] -= .005*max(q[1], 0.)*math.exp(-3.*(q[0]**2+q[2]**2))
                    else:
                        normal_axis = 2 if kind == "upright_pillow" else 1
                        seam = math.exp(-(q[normal_axis]/.18)**2)
                        for i in range(3):
                            if i != normal_axis:
                                p[i] *= 1.-.016*seam
                        if kind == "bed_pillow":
                            p[1] -= .006*max(q[1], 0.)*math.exp(-4.*(q[0]**2+q[2]**2))
                    indices.append(mesh.vertex(p, [(u+1.)*size[u_axis]/2., (v+1.)*size[v_axis]/2.]))
            for row in range(steps):
                for column in range(steps):
                    a = indices[row*(steps+1)+column]
                    mesh.face([a, a+1, a+steps+2, a+steps+1], sign < 0.)
    return mesh


def sheet(size, kind):
    mesh = Mesh()
    if kind == "chair_back":
        u_axis, v_axis, normal_axis, columns, rows = 0, 1, 2, 20, 12
        thickness, corner_exponent = .026, 8.
    elif kind == "chair_seat":
        u_axis, v_axis, normal_axis, columns, rows = 0, 2, 1, 16, 16
        thickness, corner_exponent = .054, 8.
    elif kind == "bed_throw":
        u_axis, v_axis, normal_axis, columns, rows = 0, 2, 1, 18, 44
        thickness, corner_exponent = .003, 32.
    else:
        u_axis, v_axis, normal_axis, columns, rows = 2, 1, 0, 24, 32
        thickness, corner_exponent = .0015, 32.
    basis_u, basis_v = [0., 0., 0.], [0., 0., 0.]
    basis_u[u_axis], basis_v[v_axis] = 1., 1.
    reverse = cross(basis_u, basis_v)[normal_axis] < 0.
    front, back = [], []
    for side in [1., -1.]:
        ids = front if side == 1. else back
        for row in range(rows+1):
            v = -1.+2.*row/rows
            for column in range(columns+1):
                u = -1.+2.*column/columns
                maximum = max(abs(u), abs(v))
                factor = maximum/(abs(u)**corner_exponent+abs(v)**corner_exponent)**(1./corner_exponent) if maximum else 1.
                uu, vv = u*factor, v*factor
                p = [0., 0., 0.]
                p[u_axis], p[v_axis] = uu*size[u_axis]/2., vv*size[v_axis]/2.
                if kind == "chair_back":
                    center = -.012+.027*uu*uu
                elif kind == "chair_seat":
                    center = .006-.012*(1.-uu*uu)*(1.-vv*vv)
                elif kind == "bed_throw":
                    # The footprint sits entirely over bedding. Keep folds and
                    # sag above its 0.70 m support rather than intersecting it.
                    center = -.001+.005*math.sin(2.1*math.pi*uu+.7)*math.cos(.8*math.pi*vv)
                    center += .002*math.sin(5.2*math.pi*vv+.9*uu)
                    center -= .006*smoothstep(.83, 1., abs(vv))
                else:
                    fade = 1.-.45*smoothstep(.5, 1., vv)
                    center = .0034*fade*math.sin(3.4*math.pi*uu+.35*math.sin(math.pi*vv))
                    # Raise the low hem locally; never extend the old envelope.
                    p[v_axis] += .003*(1.-vv)/2.*math.sin(2.2*math.pi*uu)**2
                p[normal_axis] = center+side*thickness/2.
                ids.append(mesh.vertex(p, [(u+1.)*size[u_axis]/2., (v+1.)*size[v_axis]/2.]))
        for row in range(rows):
            for column in range(columns):
                a = row*(columns+1)+column
                mesh.face([ids[a], ids[a+1], ids[a+columns+2], ids[a+columns+1]], reverse != (side < 0.))
    perimeter = ([i for i in range(columns+1)]
                 +[row*(columns+1)+columns for row in range(1, rows+1)]
                 +[rows*(columns+1)+i for i in range(columns-1, -1, -1)]
                 +[row*(columns+1) for row in range(rows-1, 0, -1)])
    # Independent narrow edge UV chart follows border arclength in metres.
    strip_front, strip_back, distance = [], [], 0.
    for j, index in enumerate(perimeter+[perimeter[0]]):
        if j:
            distance += length(sub(mesh.vertices[front[index]], mesh.vertices[front[perimeter[j-1]]]))
        strip_front.append(mesh.vertex(mesh.vertices[front[index]], [distance, thickness]))
        strip_back.append(mesh.vertex(mesh.vertices[back[index]], [distance, 0.]))
    for j in range(len(perimeter)):
        mesh.face([strip_front[j], strip_back[j], strip_back[j+1], strip_front[j+1]], reverse)
    return mesh, thickness


def geometry_pattern(identifier):
    return re.compile(r'<GeometryAsset\s+id="'+re.escape(identifier)+r'"\s*>.*?</GeometryAsset>', re.S)


def masked_source(source):
    for identifier in TARGETS:
        source, count = geometry_pattern(identifier).subn(f"GEOMETRY_ALLOWLIST:{identifier}", source)
        if count != 1:
            raise ValueError(f"expected exactly one {identifier}; found {count}")
    return source


def build(source):
    before_mask = masked_source(source)
    replacements, records = {}, []
    for identifier, (size, kind, intent) in TARGETS.items():
        old = geometry_pattern(identifier).search(source).group()
        primitive = re.search(r'<Primitive\s+shape="box"\s+size=\{\[([^\]]+)\]\}', old)
        if primitive and (len(primitive.group(1).split(',')) != 3 or any(abs(float(v)-s) > 1e-8 for v, s in zip(primitive.group(1).split(','), size))):
            raise ValueError(f"unexpected original dimensions for {identifier}")
        if not primitive and '<Mesh>' not in old:
            raise ValueError(f"unsupported source generator for {identifier}")
        if kind.startswith('chair') or kind in ['bed_throw', 'towel']:
            mesh, thickness = sheet(size, kind)
        else:
            mesh, thickness = cushion(size, kind), None
        details = mesh.inspect(size, .030 if kind == 'sofa_seat' else 0.)
        asset = identifier.removesuffix('_geometry')
        details.update(geometryId=identifier, meshAssetId=asset, intendedShape=intent,
                       analyticThicknessM=thickness, originalGeometrySha256=digest(old),
                       modelReferences=re.findall(r'<Model\b[^>]*\basset="'+re.escape(asset)+r'"[^>]*/>', source),
                       compoundInstances=re.findall(r'<Instance\b[^>]*\basset="'+re.escape(asset)+r'"[^>]*/>', source))
        parent_compounds = [match.group(1) for match in re.finditer(
            r'<CompoundAsset\s+id="([^"]+)"[^>]*>(.*?)</CompoundAsset>', source, re.S)
            if re.search(r'<Instance\b[^>]*\basset="'+re.escape(asset)+r'"', match.group(2))]
        model_assets = [asset]+parent_compounds
        details['modelIds'] = [match.group(1) for match in re.finditer(
            r'<Model\b[^>]*\bid="([^"]+)"[^>]*\basset="([^"]+)"[^>]*/>', source)
            if match.group(2) in model_assets]
        replacements[identifier] = mesh.xml(identifier).lstrip()
        if not primitive and old.strip() != replacements[identifier].strip():
            raise ValueError(f"refusing to replace a custom Mesh in {identifier}; start from the preserved primitive baseline")
        details['proposedGeometrySha256'] = digest(replacements[identifier])
        records.append(details)
    output = source
    for identifier, block in replacements.items():
        output = geometry_pattern(identifier).sub(lambda _: block, output)
    if masked_source(output) != before_mask:
        raise ValueError("nonallowlisted source changed")
    return output, replacements, dict(
        schemaVersion=1, sourceSha256=digest(source), proposalSha256=digest(output),
        sourceOutsideAllowlistSha256=digest(before_mask), proposalOutsideAllowlistSha256=digest(masked_source(output)),
        exactAllowlist=list(TARGETS), geometry=records,
        modelAllowlist=sorted({model for record in records for model in record['modelIds']}),
        totals=dict(vertices=sum(r['vertices'] for r in records), triangles=sum(r['triangles'] for r in records)),
        untouched='All MeshAsset/material declarations, CompoundAsset/Instance transforms, Models/anchors, cameras, timeline, 2D, plants, city, lighting and other GeometryAssets remain byte-identical.',
        constraints=['All geometry stays inside the original local envelope except the approved 30 mm sofa-seat underside contact extension; footprint, visible tops and object/compound transforms are unchanged.',
                     'Normals use existing WeightedNormals; coincident vertices split only for UV charts, and welded position topology is closed/oriented.',
                     'UVs carry metres before existing material scale; no normalized 0–1 remapping or material sampling edits.',
                     'Deterministic authored folds/compression, not simulated cloth, physical seating pressure or reference fitting.',
                     'The throw remains within its existing bedding footprint; folds and shallow sag stay above the duvet. Large edge overhang would need a separately approved footprint change.'],
        validation=dict(pythonGeometryChecks='passed', motionloomParser='pending root integration', gpuVisualReview='not run', fullVideo='not requested'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--fragment', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    fragment = args.fragment or args.output.with_suffix('.geometry.motionloom')
    report_path = args.report or args.output.with_suffix('.geometry-report.json')
    destinations = [path.resolve() for path in [args.output, fragment, report_path]]
    if args.source.resolve() in destinations or len(set(destinations)) != 3:
        parser.error('all proposal output paths must be distinct from each other and source; canonical source is never edited in place')
    source = args.source.read_text()
    output, blocks, report = build(source)
    for path in [args.output, fragment, report_path]:
        path.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output)
    fragment.write_text('<Assets>\n'+ '\n'.join('    '+b for b in blocks.values()) +'\n</Assets>\n')
    report_path.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(proposal=str(args.output.resolve()), fragment=str(fragment.resolve()), report=str(report_path.resolve()),
                          changedGeometryIds=report['exactAllowlist'], totals=report['totals'])))


if __name__ == '__main__':
    main()
