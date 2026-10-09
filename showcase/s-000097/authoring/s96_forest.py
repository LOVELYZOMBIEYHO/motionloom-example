"""Apply the S96 material study to S97 without changing sibling showcases.

The existing camera, road and original seed-97 tree transforms remain source
data. Detailed trees are retained near the camera subject; textured tree cards
with irregular three-dimensional crowns supply the distant forest. All runtime
assets are local to S97. This is explicit authored detail selection, not a claim
of automatic runtime LOD.
"""

from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import math
import random
import re

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "authoring"
SUBJECT = (3.8244574069976807, 2.165529489517212)
SPECIES = ("dark-green", "blue-green", "light-green")
HEIGHTS = (8.0, 9.0, 7.0)


def replace_asset(source, tag, identity, replacement):
    pattern = rf'<{tag}\b(?=[^>]*\bid="{identity}")[^>]*/>'
    source, count = re.subn(pattern, lambda _: replacement, source, count=1)
    if count != 1:
        raise ValueError(f"Expected one {tag} {identity}, found {count}")
    return source


def marked(source, marker, replacement, anchor):
    start = f"<!-- BEGIN {marker} -->"
    end = f"<!-- END {marker} -->"
    if start in source:
        return re.sub(re.escape(start) + r".*?" + re.escape(end),
                      lambda _: start + "\n" + replacement + "\n" + end,
                      source, count=1, flags=re.S)
    if anchor not in source:
        raise ValueError(f"Missing insertion anchor {anchor}")
    return source.replace(anchor, start + "\n" + replacement + "\n" + end
                          + "\n" + anchor, 1)


def model(identity, asset, position, scale, yaw):
    xyz = ",".join(f"{v:.8f}" for v in position)
    return (f'            <Model id="{identity}" asset="{asset}" '
            f'position={{[{xyz}]}} scale="{scale:.8f}" '
            f'rotationY="{yaw:.6f}" castShadow="true" receiveShadow="true" />')


def load_natural_height():
    spec = importlib.util.spec_from_file_location("s97_original_authoring", HERE / "build_scene.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.natural_height


def build(near_radius):
    path = ROOT / "main.motionloom"
    source = path.read_text()
    placements = json.loads((HERE / "tree-layout-source.json").read_text())
    original_camera = re.search(r'<Camera3D\b.*?/>', source, re.S).group(0)
    source = re.sub(r'<!-- S97 .*?-->',
                    '<!-- S97 - S96 texture study, detailed roadside trees and a mountain forest -->',
                    source, count=1)
    source = re.sub(r'<RenderStyle id="s97_forest_pbr">.*?</RenderStyle>', '''<RenderStyle id="s97_forest_pbr">
    <SurfaceStyle shading="filmic_physical_v1" specular="1" />
    <LightingStyle ambientIntensity="1" ambientColor="#FFFFFF" shadowStyle="soft" />
    <PostStyle toneMapping="filmic_aces_v1" exposure="0.97" contrast="1.02" saturation="1.0" whiteBalance="6500" />
    <AntiAliasingStyle method="taa" quality="ultra" fallback="smaa" sharpness="0.04" />
  </RenderStyle>''', source, count=1, flags=re.S)
    source = replace_asset(source, "MaterialAsset", "s97_ground_mat",
                           '<MaterialAsset id="s97_ground_mat" shading="pbr" baseColor="#00000000" alphaMode="mask" alphaCutoff="0.5" roughness="1" specular="0" />')
    source = replace_asset(source, "MaterialAsset", "s97_asphalt_mat", '''<MaterialAsset
      id="s97_asphalt_mat" shading="pbr" baseColor="#969A9A"
      baseColorTexture="s97_asphalt_color" metallic="0" roughness="0.98"
      specular="0.05" textureScale={[5.5,10]} variationAmount={[0.025,0.02]}
    />''')
    source = replace_asset(source, "MaterialAsset", "s97_rock_mat", '''<MaterialAsset
      id="s97_rock_mat" shading="pbr" baseColor="#C4C0AA"
      baseColorTexture="s97_moss_rock_color" normalTexture="s97_moss_rock_normal"
      normalScale="0.5" metallic="0" roughness="1" specular="0.08"
    />''')
    source = re.sub(r'(<TerrainAsset\b(?=[^>]*\bid="s97_terrain")[^>]*\blod=)"[^"]*"',
                    r'\1"quarter"', source, count=1)
    source = re.sub(r'^\s*<ModelAsset id="s97_s99_tree_[^"]+"[^>]*/>\n', '', source, flags=re.M)
    asset_lines = [
        '    <ImageAsset id="s97_daylight_radiance" src="assets/environment/sunny-forest-sky.png" colorSpace="srgb" />',
        '    <ImageAsset id="s97_moss_rock_color" src="assets/reference-forest/textures/s96-image-09.jpg" colorSpace="srgb" />',
        '    <ImageAsset id="s97_moss_rock_normal" src="assets/reference-forest/textures/s96-image-10.png" colorSpace="linear-srgb" />',
        '    <ModelAsset id="s97_visible_ground" src="assets/terrain/s97-smooth-terrain.glb" />',
        '    <ModelAsset id="s97_ground_surround" src="assets/terrain/s97-terrain-surround.glb" />',
        '    <ModelAsset id="s97_near_tree" src="assets/trees/s97-near-tree-textured.glb" />',
        '    <ModelAsset id="s97_understory_batch" src="assets/reference-forest/s97-understory-batched.glb" />',
        '    <ModelAsset id="s97_forest_batch" src="assets/reference-forest/s97-forest-batched.glb" />',
    ]
    source = marked(source, "S97 QUALITY ASSETS", "\n".join(asset_lines),
                    '    <CurveAsset id="s97_road_curve"')
    # One real sun and an open environment avoid an emissive, closed sky mesh
    # blocking path-traced secondary rays while preview ignores its shadows.
    for tag, identity in [("DirectionalLight", "s97_sun"),
                          ("DirectionalLight", "s97_fill"),
                          ("EnvironmentLight", "s97_daylight"),
                          ("AmbientOcclusion", "s97_ao"),
                          ("AtmosphereFog", "s97_aerial_haze")]:
        pattern = (rf'<{tag}\b(?=[^>]*\bid="{identity}")'
                   rf'[^>]*(?:/>|>.*?</{tag}>)')
        source = re.sub(pattern, '', source, flags=re.S)
    lighting = '''            <DirectionalLight id="s97_sun" direction={[-0.56,-0.66,-0.50]}
              color="#FFF1DC" intensity="3.2" castShadow="true" shadowStrength="0.80" />
            <EnvironmentLight id="s97_daylight" asset="s97_daylight_radiance"
              mapping="equirectangular" rotationY="-116.5" intensity="0.32"
              visible="true" backgroundIntensity="0.8"
              diffuseIntensity="1" specularIntensity="1" />
            <AmbientOcclusion id="s97_ao" intensity="0.22" radius="0.025" />
            <AtmosphereFog id="s97_aerial_haze" density="0.008" anisotropy="0.35"
              scatteringColor={[0.76,0.82,0.90]} baseHeight="-1" heightFalloff="0.35"
              boundsMin={[-16,-7,-14]} boundsMax={[16,7.5,14]} edgeFeather="0.5"
              affectEnvironment="false" />'''
    source = marked(source, "S97 SHARED LIGHTING", lighting,
                    '            <!-- Full-site descent, roadside orbit, then leaf-level inspection. -->')
    source = replace_asset(source, "Model", "s97_terrain_model", '''<Model
              id="s97_terrain_model" asset="s97_terrain" position={[0,0,0]}
              castShadow="false" receiveShadow="false"
            />''')
    ground_models = '''            <!-- The transparent TerrainAsset remains the deterministic Scatter placement surface. -->
            <Model id="s97_visible_ground_model" asset="s97_visible_ground" castShadow="true" receiveShadow="true">
              <MaterialBinding modelSourceMaterial="S97_S96_GrassGround" tint="#A099A6" tintAmount="1" />
            </Model>
            <Model id="s97_surround_model" asset="s97_ground_surround" castShadow="true" receiveShadow="true">
              <MaterialBinding modelSourceMaterial="S97_S96_GrassGround" tint="#A099A6" tintAmount="1" />
            </Model>'''
    source = marked(source, "S97 QUALITY GROUND", ground_models,
                    '            <Model id="s97_asphalt_model"')
    near = []
    models = []
    detailed_layout = []
    rng = random.Random(96097)
    for tree in placements:
        x, y, z = tree["position"]
        distance = math.hypot(x-SUBJECT[0], z-SUBJECT[1])
        if distance <= near_radius:
            asset, scale = "s97_near_tree", tree["scale"]
            near.append(tree["index"])
            source_file = "assets/trees/s97-near-tree-textured.glb"
        else:
            choice = rng.choices(range(3), [0.43, 0.37, 0.20])[0]
            asset = f"s97_tree_{SPECIES[choice]}"
            scale = tree["scale"] * 4.201077 / HEIGHTS[choice]
            # Curved alpha-masked foliage sheets keep a leafy silhouette from
            # above without introducing a solid dome in the side view.
            source_file = f"assets/reference-forest/tree-{SPECIES[choice]}-canopy.glb"
        detailed_layout.append({"index":tree["index"],"asset":asset,
            "sourceFile":source_file,"position":tree["position"],
            "scale":scale,"rotationY":tree["rotationY"]})
        if asset == "s97_near_tree":
            models.append(model(f's97_tree_{tree["index"]:04}', asset,
                                tree["position"], scale, tree["rotationY"]))
    # Additional vegetation hides the old rectangular core edge from the descent.
    # Beyond this margin the surround uses the same uncarved natural_height.
    height = load_natural_height()
    outer_count = 0
    for iz in range(65):
        for ix in range(78):
            x = -15.4 + ix * 0.4 + rng.uniform(-0.16, 0.16)
            z = -12.8 + iz * 0.4 + rng.uniform(-0.16, 0.16)
            if abs(x) < 8.45 and abs(z) < 4.975:
                continue
            if abs(x) > 15.6 or abs(z) > 13.15:
                continue
            choice = rng.choices(range(3), [0.43, 0.37, 0.20])[0]
            scale = rng.uniform(0.036, 0.055)
            y = height(x / 0.05, z / 0.05) * 0.05 - 0.012
            detailed_layout.append({"index":f"surround-{outer_count}",
                "asset":f"s97_tree_{SPECIES[choice]}",
                "sourceFile":f"assets/reference-forest/tree-{SPECIES[choice]}-canopy.glb",
                "position":[x,y,z],"scale":scale,"rotationY":rng.uniform(0,360)})
            outer_count += 1
    source = re.sub(r'\s*<Scatter\b(?=[^>]*\bid="s97_forest[^"]*")[^>]*>.*?</Scatter>',
                    '', source, flags=re.S)
    models.insert(0, '            <Model id="s97_distant_forest_model" asset="s97_forest_batch" castShadow="true" receiveShadow="true" />')
    source = marked(source, "S97 QUALITY FOREST", "\n".join(models),
                    '            <Scatter\n              id="s97_cut_rocks"')
    grass = '            <Model id="s97_understory_model" asset="s97_understory_batch" castShadow="false" receiveShadow="true" />'
    source = marked(source, "S97 QUALITY UNDERSTORY", grass,
                    '            <Scatter\n              id="s97_cut_rocks"')
    source = re.sub(r'(<Scatter\s+id="s97_cut_rocks"\s+surface="s97_terrain_model"\s+count=)"\d+"',
                    r'\1"360"', source, count=1)
    # Keep the road-facing camera's geometry clearance, and make boulders less uniform.
    source = re.sub(r'(<Scatter\s+id="s97_cut_rocks".*?scaleRange=)\{\[[^\]]+\]\}',
                    r'\1{[0.40,1.05]}', source, count=1, flags=re.S)
    new_camera = re.search(r'<Camera3D\b.*?/>', source, re.S).group(0)
    if new_camera != original_camera:
        raise ValueError("The camera must remain unchanged")
    source = re.sub(r"^[ \t]+$", "", source, flags=re.M)
    path.write_text(source)
    (HERE / "s96-tree-layout.json").write_text(json.dumps(detailed_layout,indent=2)+"\n")
    manifest = {
        "sourceSha256": hashlib.sha256(source.encode()).hexdigest(),
        "seed": 96097,
        "originalCoreTrees": len(placements),
        "full3DNearTrees": len(near),
        "full3DTreeIndices": near,
        "nearRadiusWorldUnits": near_radius,
        "surroundTrees": outer_count,
        "totalTrees": len(placements)+outer_count,
        "layeredDistantTrees": sum(row["asset"] != "s97_near_tree" for row in detailed_layout),
        "staticBatchLayout": "s96-tree-layout.json",
        "understoryTufts": 16000,
        "cameraUnchanged": True,
        "originalCorePositionsAndYawsUnchanged": True,
        "originalCoreNominalHeightsPreserved": True,
        "distantScalePolicy": "Convert original tree height into each source asset's normalized units",
        "detailSelection": "Explicit authored geometry split, not automatic runtime LOD",
        "sources": ["tree-layout-source.json", "camera-exploration.json",
                    "../assets/reference-forest/provenance.json"],
    }
    (HERE / "s96-forest-layout.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--near-radius", type=float, default=1.05)
    args = parser.parse_args()
    build(args.near_radius)
