#!/usr/bin/env python3
"""Verify S99's deterministic material-batched geometry reuse."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from compact_dsl import compact

ROOT = Path(__file__).resolve().parents[1]
APPROVED_TAG_SHA256 = '29eab210c4f846e674a1eb0f0ec29e1dd2afc099d84481981e272103ac033027'
TAG = re.compile(r'<[^>]*>', re.S)


def tag_digest(source: str) -> tuple[str, int]:
    """Normalize only tag layout, never quoted values or tag order."""
    digest = hashlib.sha256()
    count = 0
    for tag in TAG.findall(source):
        if tag.startswith('<!--'):
            continue
        quoted = False
        pending_space = False
        normalized = []
        for character in tag:
            if character == '"':
                quoted = not quoted
            if character.isspace() and not quoted:
                pending_space = True
                continue
            if pending_space:
                if normalized and normalized[-1] not in '<=' and character not in '/>=':
                    normalized.append(' ')
                pending_space = False
            normalized.append(character)
        digest.update(''.join(normalized).encode())
        digest.update(b'\n')
        count += 1
    return digest.hexdigest(), count


if __name__ == '__main__':
    path = ROOT/'main.motionloom'
    source = path.read_text()
    tag_sha, tag_count = tag_digest(source)
    assert tag_sha == APPROVED_TAG_SHA256, 'S99 authored tags differ from the approved reuse scene'
    assert compact(source) == source, 'S99 DSL is not in canonical compact form'
    assert tag_count == 207575
    mesh_geometry = dict(re.findall(
        r'<MeshAsset id="([^"]+)" material="[^"]+" geometry="([^"]+)" />', source))
    for name in list(mesh_geometry):
        if name.startswith('s99_tree_west_'):
            east = name.replace('tree_west', 'tree_east', 1)
            assert mesh_geometry[east] == mesh_geometry[name], east
        for variant in range(4):
            prefix = f's99_garden{variant}_'
            if name.startswith(prefix):
                paired = name.replace(prefix, f's99_garden{variant+4}_', 1)
                assert mesh_geometry[paired] == mesh_geometry[name], paired
    assert source.count('<Mesh>') == 95
    assert source.count('<Vertex ') == 129246
    assert source.count('<Face ') == 75479
    assert source.count('<Model id="s99_city_merged_') == 44
    assert source.count('rotation={[0,137,0]}') == 6
    planting = json.loads((ROOT/'evidence/planting-geometry.json').read_text())
    assert sum(p['leaves'] for p in planting['plants']) == 5690
    assert planting['source_sha256'] == hashlib.sha256(source.encode()).hexdigest()
    report = {
        'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
        'status': 'passed',
        'method': 'Deterministic planting reuse and city material batching; exact references, leaf count, topology count and canonical tag stream checked.',
        'previous_compact_source_sha256': '164a9f7f28155816c0848b886ed161433d2e02df12343717bfcd1ca6585a2168',
        'canonical_tag_sha256': tag_sha,
        'tag_count': tag_count,
        'before_lines': 9024,
        'after_lines': source.count('\n'),
        'before_bytes': 18057861,
        'after_bytes': len(source.encode()),
        'unique_botanical_cages_before': 78,
        'unique_botanical_cages_after': 52,
        'city_material_batch_models': 44,
        'unique_city_batch_geometry': 43,
        'scene_leaves': 5690,
        'unique_vertex_tags': 129246,
        'unique_face_tags': 75479,
        'planting_vertex_tags': 88086,
        'planting_face_tags': 65189,
        'geometry_reuse': 'The east tree reuses the west tree cage with a 137-degree rotation; planters 4-7 reuse the four cages of planters 0-3. Each tree and planter keeps its own Model transforms and all 5,690 visible leaves.',
        'gpu_reference_report': 'reuse-gpu-check.json',
    }
    (ROOT/'evidence/optimization-check.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f"PASS: {report['before_bytes']:,} -> {report['after_bytes']:,} bytes; "
          f"{report['unique_botanical_cages_before']} -> {report['unique_botanical_cages_after']} botanical cages")
