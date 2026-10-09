#!/usr/bin/env python3
"""Build a portable close material review with two raking-light positions.

This small fixture reuses the canonical finishes. Capture frames 0/24 for the
finish boards and 48/72 for fine weave detail under opposite raking light.
It is not a replacement for reviewing the furnished house.
"""
from pathlib import Path
import re

from material_upgrade import material_assets

ROOT = Path(__file__).resolve().parent


def build() -> str:
    assets = material_assets().replace('src="assets/', 'src="../assets/')
    panels = []
    models = []
    for i, material in enumerate(['oak', 'worktop', 'linen_upholstery', 'plaster']):
        panels.append(
            f'    <GeometryAsset id="patch{i}_geometry">'
            '<Primitive shape="box" size={[1.15,0.95,0.12]} '
            'bevelRadius="0.018" bevelSegments="3" /><UV mode="box" /></GeometryAsset>\n'
            f'    <MeshAsset id="patch{i}" geometry="patch{i}_geometry" material="{material}" />')
        x = (i - 1.5) * 1.4
        models.append(f'            <Model id="patch_model{i}" asset="patch{i}" '
                      f'position={{[{x:.4g},0.8,0]}} castShadow="true" receiveShadow="true" />')
    panel_xml = '\n'.join(panels)
    model_xml = '\n'.join(models)
    source = f'''<Graph fps="24" duration="4s" size={{[1600,900]}}>
  <RenderStyle id="swatch_style">
    <SurfaceStyle shading="physical" />
    <LightingStyle ambientIntensity="0.1" />
    <PostStyle toneMapping="aces" exposure="1.08" />
    <AntiAliasingStyle method="taa" quality="high" fallback="smaa" sharpness="0.04" />
  </RenderStyle>
  <Assets>
{assets}{panel_xml}
    <MaterialAsset id="swatch_floor_material" baseColor="#CCC6BB" roughness="0.9" />
    <GeometryAsset id="swatch_floor_geometry"><Primitive shape="box" size={{[7,0.05,2]}} /></GeometryAsset>
    <MeshAsset id="swatch_floor" geometry="swatch_floor_geometry" material="swatch_floor_material" />
  </Assets>
  <Scene id="material_review" renderStyle="swatch_style">
    <Timeline><Track space="3d"><Sequence from="0s" duration="4s"><CompositeGroup space="3d" depth="true">
      <Camera3D id="swatch_camera" position={{[0.6,1.6,6.8]}} target={{[0,0.75,0]}} fov="48" />
      <Camera3D id="fabric_camera" position={{[0.7,0.8,0.55]}} target={{[0.7,0.8,0]}} fov="35" />
      <EnvironmentLight asset="s99_environment" visible="false" intensity="0.5" diffuseIntensity="0.7" specularIntensity="0.4" rotationY="-90.33" />
      <DirectionalLight id="raking_light" direction={{[curve("0:-0.8,1:0.8:linear,2:-0.8:linear,3:0.8:linear"),-0.35,-0.3]}} intensity="3" color="#FFF0DC" castShadow="true" />
      <AmbientOcclusion intensity="0.3" radius="0.12" />
      <ContactShadow intensity="0.5" distance="0.15" softness="0.6" />
      <Model id="swatch_floor_model" asset="swatch_floor" position={{[0,0.25,0]}} />
{model_xml}
    </CompositeGroup></Sequence></Track></Timeline>
  </Scene>
  <AnimationTarget node="material_review" property="activeCamera">
    <Key time="0s" value="swatch_camera" />
    <Key time="2s" value="fabric_camera" />
  </AnimationTarget>
  <Present from="material_review" />
</Graph>
'''
    # Numeric attributes from the material module use compact leading decimals;
    # normalise them for the current serde numeric parser, as the main generator does.
    return re.sub(r'(?<=["\[,])(-?)\.(\d)', r'\g<1>0.\2', source)


if __name__ == '__main__':
    output = ROOT / 'material-swatches.motionloom'
    output.write_text(build())
    print(f'Built {output}')
