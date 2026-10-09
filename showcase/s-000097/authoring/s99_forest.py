"""Replace S97 primitive crowns with the exact S99 street-tree geometry.

The editable tree DSL is local to S97. MotionLoom exports one GLB per material
batch so Scatter instances share buffers and keep matching leaf/branch positions.
No S99 checkout is required to rebuild these derived assets.
"""
from pathlib import Path
import argparse
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PARTS = ('tree_bark', 'young_bark', 'foliage_deep', 'foliage_green', 'foliage_mid', 'foliage_tip')
TREE_SCALE = 0.12  # S97's 0.05 site scale × 2.4 growth of the metre-authored S99 tree.


def export_parts(exporter):
    source = (ROOT / 'assets/trees/s99-street-tree.motionloom').read_text()
    with tempfile.TemporaryDirectory(prefix='s97-tree-export-') as directory:
        for part in PARTS:
            model = f's97_source_{part}_mesh_model'
            # Keep original geometry/material declarations. Selecting one model
            # prevents alternating material draw calls in the large forest.
            selected = re.sub(r'<Model\b[^>]*/>', lambda m: m.group() if f'id="{model}"' in m.group() else '', source)
            script = Path(directory) / f'{part}.motionloom'
            script.write_text(selected)
            subprocess.run([str(exporter), str(script), str(ROOT / f'assets/trees/s99-tree-{part}.glb'), 'S97TreeSource', '0'], check=True)


def replace_forest(source, count=2048):
    assets = '\n'.join(f'    <ModelAsset id="s97_s99_tree_{part}" src="assets/trees/s99-tree-{part}.glb" />' for part in PARTS)
    # Find the end of the whole old tree library, not its first compound.
    start = source.find('    <GeometryAsset id="s97_trunk_a_geometry">')
    if start < 0:
        start = source.find('    <PrimitiveAsset id="s97_trunk_a"')
    if start >= 0:
        last = source.index('<CompoundAsset id="s97_tree_f">', start)
        end = source.index('</CompoundAsset>', last) + len('</CompoundAsset>')
        source = source[:start] + assets + source[end:]
    else:
        existing = re.compile(r'^[ \t]*<ModelAsset\b[^>]*\bid="s97_s99_tree_[^"]+"[^>]*/>[ \t]*(?:\r?\n)?', re.M)
        matches = list(existing.finditer(source))
        if matches:
            # Replace at the existing location. Consume only each tag's own
            # line ending, so indentation on the following tag is preserved.
            first = matches[0].start()
            source = existing.sub(lambda match: assets + '\n' if match.start() == first else '', source)
        else:
            source = source.replace('  </Assets>', assets + '\n  </Assets>', 1)
    # Old crown textures and factors are not applied to the genuine S99 leaves.
    for identity in ('s97_trunk_mat', 's97_leaf_a', 's97_leaf_b', 's97_leaf_c', 's97_leaf_d'):
        source = re.sub(r'^[ \t]*<MaterialAsset\b[^>]*\bid="' + identity + r'"[^>]*/>[ \t]*(?:\r?\n)?', '', source, flags=re.M)
    for identity in ('s97_bark_color', 's97_foliage_color'):
        source = re.sub(r'^[ \t]*<ImageAsset\b[^>]*\bid="' + identity + r'"[^>]*/>[ \t]*(?:\r?\n)?', '', source, flags=re.M)
    start = source.index('            <Scatter', source.index('<Model id="s97_guardrail_right_model"'))
    end = source.rfind('            <Scatter', start, source.index('id="s97_cut_rocks"'))
    scatters = []
    for index, part in enumerate(PARTS):
        identity = 's97_forest' if index == 0 else f's97_forest_{part}'
        scatters.append(f'''            <Scatter id="{identity}" surface="s97_terrain_model"
                     count="{count}" seed="97" exclusionMap="s97_forest_exclusion"
                     slopeRange={{[0,90]}} scaleRange={{[{0.42*TREE_SCALE:.6f},{0.86*TREE_SCALE:.6f}]}}
                     rotationYRange={{[0,360]}} surfaceOffset="-0.01250"
                     castShadow="true" receiveShadow="true">
              <Variant asset="s97_s99_tree_{part}" weight="1" />
            </Scatter>''')
    source = source[:start] + '\n'.join(scatters) + '\n' + source[end:]
    source = source.replace('<!-- S97 - winding mountain road - textured PBR checkpoint rebuilt from reference/reference.png -->',
                            '<!-- S97 - winding mountain road - S99 native street-tree forest, shared derived GLBs -->', 1)
    return source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exporter', type=Path, help='MotionLoom export_scene_glb executable; rebuild derived GLBs when given')
    parser.add_argument('--input', type=Path, default=ROOT / 'main.motionloom')
    parser.add_argument('--output', type=Path, default=ROOT / 'main.motionloom')
    parser.add_argument('--count', type=int, default=2048, help='Whole trees; each of six aligned material Scatters uses the same count; use 10760 for the full-density stress trial')
    args = parser.parse_args()
    if args.count < 1:
        parser.error('--count must be positive')
    if args.exporter:
        export_parts(args.exporter.resolve())
    for part in PARTS:
        if not (ROOT / f'assets/trees/s99-tree-{part}.glb').is_file():
            parser.error('Missing derived tree GLBs; rebuild with --exporter first')
    result = replace_forest(args.input.read_text(), args.count)
    args.output.write_text(result)
    print(json.dumps({'output': str(args.output), 'trees': args.count, 'leaves': 2200*args.count,
                      'treeTriangles': 80980*args.count, 'sharedMaterialParts': len(PARTS)}, indent=2))


if __name__ == '__main__':
    main()
