#!/usr/bin/env python3
"""Share identical geometry and group control-cage tags.

S99 keeps its hand-fitted botanical geometry. Two street trees share one
material-batched crown, and eight planters reuse four distinct forms. City
facade boxes are also grouped into material-bound meshes.
MotionLoom's lexical tag parser accepts sibling tags on one source line.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
GEOMETRY = re.compile(r'(?P<indent>^[ \t]*)<GeometryAsset id="(?P<id>[^"]+)">(?P<body>.*?)</GeometryAsset>\s*', re.M | re.S)
MESH = re.compile(r'(?P<indent>^[ \t]*)<Mesh>\s*(?P<body>.*?)\s*</Mesh>', re.M | re.S)
CHILD = re.compile(r'<(?:Vertex|Face)\s+[^>]*?/>', re.S)
BATCH = 64


def compact(source: str) -> str:
    # S98's reusable GeometryAsset pattern also applies here: city facade
    # modules repeat the same primitive dimensions, and some botanical cages
    # occur in multiple material batches. Preserve the first declaration.
    first_by_body: dict[str, str] = {}
    aliases: dict[str, str] = {}

    def deduplicate(match: re.Match[str]) -> str:
        # Only ignore whitespace between child tags. Whitespace inside a
        # quoted attribute value may carry meaning and must stay distinct.
        body_key = re.sub(r'>\s+<', '><', match.group('body').strip())
        identifier = match.group('id')
        if body_key in first_by_body:
            aliases[identifier] = first_by_body[body_key]
            return ''
        first_by_body[body_key] = identifier
        return match.group(0)

    source = GEOMETRY.sub(deduplicate, source)
    for alias, canonical in aliases.items():
        source = source.replace(f'geometry="{alias}"', f'geometry="{canonical}"')
        source = source.replace(f'source="{alias}"', f'source="{canonical}"')
    changed = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal changed
        body = match.group('body')
        tags = CHILD.findall(body)
        if not tags or re.sub(CHILD, '', body).strip():
            raise ValueError('Mesh contains unsupported content; refusing to alter it')
        vertex_count = sum(tag.startswith('<Vertex') for tag in tags)
        if any(tag.startswith('<Vertex') for tag in tags[vertex_count:]):
            raise ValueError('Vertex follows Face; refusing to reorder mesh data')
        indent = match.group('indent')
        batches = []
        # Keep the vertex/face boundary visible for readers and validators.
        for group in (tags[:vertex_count], tags[vertex_count:]):
            batches.extend(' '.join(group[i:i+BATCH]) for i in range(0, len(group), BATCH))
        changed += 1
        return (indent+'<Mesh>\n'+''.join(indent+'  '+line+'\n' for line in batches)
                +indent+'</Mesh>')

    output = MESH.sub(replace, source)
    if changed != 95:
        raise ValueError(f'Expected 52 planting cages and 43 unique city batches, found {changed} meshes')
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='fail if main is not compact')
    args = parser.parse_args()
    path = ROOT/'main.motionloom'
    original = path.read_text()
    result = compact(original)
    if args.check:
        if original != result:
            raise SystemExit('main.motionloom needs compact_dsl.py')
    elif original != result:
        path.write_text(result)
    print(f'{original.count(chr(10)):,} -> {result.count(chr(10)):,} lines; '
          f'{len(original):,} -> {len(result):,} characters')


if __name__ == '__main__':
    main()
