"""Generate the S95 shark MeshAsset cage and the frozen four-view scene.

Design: one closed quad tube (21 rings x 12 columns + two poles, 254 vertices,
264 faces). Fins are shaped by dedicated ring cross-sections instead of
separate components, so the surface stays connected, manifold and quad based.

Axes: -X snout, +X tail, +Y dorsal, +Z shark's left flank.
Views: frame 0 left, 48 front (rotationY 90), 96 top (rotationX 90),
144 bottom (rotationX -90).

Ring parameters are calibrated against the measured reference profiles
(tools/ref_profile.py): body length 4.05 units, axis at image mid height.
"""

import json
import math
import os

COLUMNS = 12
RING_COUNT = 21

# ring: (x, y_center, half_top, half_bottom, half_width)
RINGS = [
    (-2.00, 0.00, 0.050, 0.050, 0.060),  # 0 snout tip
    (-1.92, 0.00, 0.100, 0.110, 0.220),  # 1
    (-1.78, 0.00, 0.170, 0.170, 0.330),  # 2 snout
    (-1.60, 0.00, 0.230, 0.260, 0.400),  # 3 mouth
    (-1.35, 0.00, 0.300, 0.370, 0.450),  # 4 eye
    (-1.10, 0.00, 0.360, 0.410, 0.480),  # 5 gills front
    (-0.88, 0.00, 0.400, 0.450, 0.490),  # 6 gills rear / pectoral root
    (-0.66, 0.00, 0.430, 0.460, 0.480),  # 7 pectoral
    (-0.46, 0.00, 0.440, 0.470, 0.460),  # 8 pectoral
    (-0.26, 0.00, 0.450, 0.470, 0.440),  # 9 pectoral tip / dorsal leading
    (-0.06, 0.00, 0.440, 0.460, 0.440),  # 10 dorsal tip
    (0.12, 0.00, 0.440, 0.440, 0.440),   # 11 dorsal trailing
    (0.30, 0.00, 0.400, 0.420, 0.430),   # 12
    (0.50, 0.00, 0.340, 0.380, 0.400),   # 13
    (0.72, 0.00, 0.270, 0.340, 0.340),   # 14 pelvic
    (0.95, 0.00, 0.190, 0.240, 0.260),   # 15
    (1.18, 0.00, 0.140, 0.170, 0.170),   # 16
    (1.35, 0.00, 0.090, 0.110, 0.110),   # 17 peduncle
    (1.55, 0.02, 0.200, 0.200, 0.050),   # 18 caudal blade front
    (1.80, 0.04, 0.560, 0.500, 0.045),   # 19 caudal lobes
    (1.90, 0.04, 0.680, 0.440, 0.035),   # 20 caudal trailing
]
SNOUT_POLE = (-2.05, 0.00, 0.0)
TAIL_POLE = (1.98, 0.16, 0.0)

# Dorsal fin: ring -> (top height, pinch factor for the adjacent columns).
DORSAL = {
    9: (0.52, 0.34),
    10: (0.82, 0.16),
    11: (0.46, 0.30),
    12: (0.40, 0.62),
}

# Pectoral fin: ring -> (z_scale, y_drop) for columns 2/3/4 and 8/9/10.
PECTORAL = {
    6: (1.00, 0.12),
    7: (1.55, 0.42),
    8: (2.40, 0.78),
    9: (2.95, 1.00),
    10: (2.40, 0.80),
    11: (1.55, 0.42),
    12: (1.00, 0.12),
}

# Pelvic fin: small bottom-side bumps.
PELVIC = {14: (1.20, 0.10)}

# Second dorsal and anal fin: small top/bottom extensions.
SECOND_DORSAL = {15: 0.0}
ANAL = {15: 0.02}


def cross_section(ring):
    x, y_center, half_top, half_bottom, half_width = RINGS[ring]
    points = []
    for column in range(COLUMNS):
        angle = math.radians(column * 360.0 / COLUMNS)
        cosine = math.cos(angle)
        sine = math.sin(angle)
        half = half_top if cosine >= 0 else half_bottom
        y = y_center + half * cosine
        z = half_width * sine
        # Dorsal fin blade: raise the top column and pinch the neighbours.
        if ring in DORSAL and column in (0, 1, COLUMNS - 1):
            top, pinch = DORSAL[ring]
            if column == 0:
                y = y_center + top
            else:
                y = y_center + top * 0.70
                z = half_width * sine * pinch
        if ring in SECOND_DORSAL and column in (0, 1, COLUMNS - 1):
            top = SECOND_DORSAL[ring]
            y = y_center + half_top + top * (1.0 if column == 0 else 0.6)
            if column != 0:
                z = half_width * sine * 0.5
        # Anal fin.
        if ring in ANAL and column in (5, 6, 7):
            y = y_center - half_bottom - ANAL[ring] * (1.0 if column == 6 else 0.5)
            if column != COLUMNS // 2:
                z = half_width * sine * 0.5
        # Pectoral fins: widen and droop the lower ring columns with a shared
        # weight profile so adjacent columns never fold across each other.
        if ring in PECTORAL:
            z_scale, drop = PECTORAL[ring]
            z_weight = {0: 0.0, 1: 0.2, 2: 0.9, 3: 1.0, 4: 0.9, 5: 0.3,
                        6: 0.0, 7: 0.3, 8: 0.9, 9: 1.0, 10: 0.9, 11: 0.2}[column]
            drop_weight = {0: 0.0, 1: 0.0, 2: 0.35, 3: 1.0, 4: 0.35, 5: 0.10,
                           6: 0.0, 7: 0.10, 8: 0.35, 9: 1.0, 10: 0.35, 11: 0.0}[column]
            z = z * (1.0 + (z_scale - 1.0) * z_weight)
            y = y - drop * drop_weight
        # Pelvic fins.
        if ring in PELVIC and column in (4, 5, 6, 7, 8):
            z_scale, drop = PELVIC[ring]
            weight = 1.0 if column in (5, 7) else 0.45
            z *= z_scale
            y -= drop * weight
        points.append((x, y, z))
    return points


def build_cage():
    positions = []
    for ring in range(RING_COUNT):
        positions.extend(cross_section(ring))
    snout = len(positions)
    positions.append(SNOUT_POLE)
    tail = len(positions)
    positions.append(TAIL_POLE)
    faces = []
    for ring in range(RING_COUNT - 1):
        for column in range(COLUMNS):
            a = ring * COLUMNS + column
            b = ring * COLUMNS + (column + 1) % COLUMNS
            c = (ring + 1) * COLUMNS + (column + 1) % COLUMNS
            d = (ring + 1) * COLUMNS + column
            faces.append([a, b, c, d])
    for column in range(COLUMNS):
        a = column
        b = (column + 1) % COLUMNS
        faces.append([snout, b, a])
        a = (RING_COUNT - 1) * COLUMNS + column
        b = (RING_COUNT - 1) * COLUMNS + (column + 1) % COLUMNS
        faces.append([tail, a, b])
    return positions, faces, snout, tail


def format_number(value):
    text = f"{value:.5f}"
    while text.endswith("0"):
        text = text[:-1]
    if text.endswith("."):
        text += "0"
    return text


def vertex_line(position, ring, column):
    u = column / COLUMNS
    v = ring / (RING_COUNT - 1)
    return (
        f'      <Vertex position={{[{format_number(position[0])}, '
        f"{format_number(position[1])}, {format_number(position[2])}]}} "
        f"uv={{[{u:.4f},{v:.4f}]}} />"
    )


def main():
    positions, faces, snout, tail = build_cage()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root, "source")
    os.makedirs(out_dir, exist_ok=True)

    lines = []
    lines.append("<!-- S95 - SHARK UNIVERSAL MESHASSET - one connected authored surface -->")
    lines.append('<Graph fps={24} duration="8s" size={[900,500]} renderSize={[900,500]}>')
    lines.append('  <RenderStyle id="s95_studio">')
    lines.append('    <SurfaceStyle shading="physical" roughnessBias="0.10" specular="0.25" />')
    lines.append('    <LightingStyle ambientIntensity="0.55" ambientColor="#CDD3DA" shadowStyle="soft" />')
    lines.append('    <PostStyle toneMapping="aces" exposure="1.0" saturation="0.95" contrast="1.0"')
    lines.append('               whiteBalance="5800" bloomThreshold="1.4" bloomIntensity="0" />')
    lines.append('    <AntiAliasingStyle method="msaa" quality="high" fallback="smaa" sharpness="0" />')
    lines.append("  </RenderStyle>")
    lines.append("")
    lines.append("  <Assets>")
    lines.append('    <MaterialAsset id="s95_shark_clay" shading="pbr" baseColor="#8E9AA6"')
    lines.append('                   roughness="0.62" specular="0.30" metallic="0" />')
    lines.append('    <MeshAsset id="s95_shark_mesh" material="s95_shark_clay"')
    lines.append('               subdivision="0" subdivisionScheme="catmullClark">')
    for index, position in enumerate(positions):
        ring = min(index // COLUMNS, RING_COUNT - 1)
        column = index % COLUMNS
        lines.append(vertex_line(position, ring, column))
    for face in faces:
        lines.append(
            "      <Face indices={[%s]} />" % ",".join(str(value) for value in face)
        )
    lines.append("    </MeshAsset>")
    lines.append("  </Assets>")
    lines.append("")
    lines.append('  <Background color="#B7B8B9" />')
    lines.append('  <Scene id="S95Shark" renderStyle="s95_studio">')
    lines.append("    <Timeline>")
    lines.append('      <Track id="s95_world" space="3d">')
    lines.append('        <Sequence from="0s" duration="8s" out="hold">')
    lines.append('          <CompositeGroup id="s95_stage" space="3d" depth="true" format="rgba16f">')
    lines.append('            <Camera3D id="s95_camera" position={[0,0,6]} target={[0,0,0]}')
    lines.append('                      fov="22" depthOfField="false" />')
    lines.append('            <RectAreaLight position={[-2.4,3.0,3.4]} direction={[0.5,-0.5,-1]}')
    lines.append('                           width="3.2" height="3.2" color="#FFE6D5" intensity="5.4" />')
    lines.append('            <RectAreaLight position={[2.6,-0.6,2.4]} direction={[-0.7,0.1,-0.7]}')
    lines.append('                           width="2.6" height="2.6" color="#B9D2FF" intensity="2.4" />')
    lines.append('            <DirectionalLight direction={[0.15,-0.85,0.5]} color="#EDF3FF"')
    lines.append('                              intensity="0.9" castShadow="true" shadowStrength="0.55" />')
    lines.append('            <AmbientOcclusion radius="0.25" intensity="0.30" />')
    lines.append('            <Model id="s95_shark_model" asset="s95_shark_mesh" castShadow="true" />')
    lines.append("          </CompositeGroup>")
    lines.append("        </Sequence>")
    lines.append("      </Track>")
    lines.append("    </Timeline>")
    lines.append("  </Scene>")
    lines.append("")
    lines.append('  <AnimationTarget node="s95_shark_model" property="rotationX">')
    lines.append('    <Key time="0s" value="0" />')
    lines.append('    <Key time="2s" value="0" />')
    lines.append('    <Key time="4s" value="90" />')
    lines.append('    <Key time="6s" value="-90" />')
    lines.append('    <Key time="8s" value="-90" />')
    lines.append("  </AnimationTarget>")
    lines.append('  <AnimationTarget node="s95_shark_model" property="rotationY">')
    lines.append('    <Key time="0s" value="0" />')
    lines.append('    <Key time="2s" value="90" />')
    lines.append('    <Key time="4s" value="0" />')
    lines.append('    <Key time="6s" value="0" />')
    lines.append('    <Key time="8s" value="0" />')
    lines.append("  </AnimationTarget>")
    lines.append('  <Present from="S95Shark" />')
    lines.append("</Graph>")
    source = "\n".join(lines) + "\n"
    path = os.path.join(out_dir, "shark.motionloom")
    with open(path, "w") as handle:
        handle.write(source)
    print("wrote", path, "vertices", len(positions), "faces", len(faces))
    print("snout pole", snout, "tail pole", tail)

    index_map = {
        "columns": COLUMNS,
        "rings": RING_COUNT,
        "ringX": [ring[0] for ring in RINGS],
        "snoutPole": snout,
        "tailPole": tail,
        "vertexIndexFormula": "index = ring*12 + column for rings 0..20",
        "notes": "ring r, column c angle = c*30deg from +Y toward +Z",
    }
    with open(os.path.join(root, "authoring", "index-map.json"), "w") as handle:
        json.dump(index_map, handle, indent=1)


if __name__ == "__main__":
    main()
