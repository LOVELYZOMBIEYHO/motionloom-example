#!/usr/bin/env python3
"""Densify the accepted S94 ring cage without changing its fitted surface."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path


VERTEX = re.compile(
    r"\s*<Vertex position=\{\[([^,]+),\s*([^,]+),\s*([^\]]+)\]\} uv=\{\[([^,]+),([^\]]+)\]\} />"
)


def mix(a: tuple[float, ...], b: tuple[float, ...], t: float) -> tuple[float, ...]:
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def sample(rows: list[list[tuple[float, ...]]], row: float, sector: float) -> tuple[float, ...]:
    r0 = min(int(math.floor(row)), len(rows) - 1)
    r1 = min(r0 + 1, len(rows) - 1)
    s0 = int(math.floor(sector)) % len(rows[0])
    s1 = (s0 + 1) % len(rows[0])
    rt = row - r0
    st = sector - math.floor(sector)
    return mix(mix(rows[r0][s0], rows[r0][s1], st), mix(rows[r1][s0], rows[r1][s1], st), rt)


def format_number(value: float) -> str:
    text = f"{value:.7f}".rstrip("0").rstrip(".")
    return "0" if text in {"-0", ""} else text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = args.source.read_text()
    asset_start = source.index('<MeshAsset id="s94_head_mesh"')
    body_start = source.index(">", asset_start) + 1
    asset_end = source.index("    </MeshAsset>", body_start)
    body = source[body_start:asset_end]
    vertices = [tuple(float(value) for value in match.groups()) for match in VERTEX.finditer(body)]
    if len(vertices) != 362:
        raise SystemExit(f"expected the accepted 362-vertex cage, found {len(vertices)}")

    old_rows = [vertices[index:index + 24] for index in range(0, 360, 24)]
    new_rows = 29
    new_sectors = 48
    generated: list[str] = []
    for row in range(new_rows):
        for sector in range(new_sectors):
            values = sample(old_rows, row / 2.0, sector / 2.0)
            position = values[:3]
            uv = (sector / new_sectors, row / (new_rows - 1))
            generated.append(
                "      <Vertex position={["
                + ", ".join(format_number(value) for value in position)
                + "]} uv={["
                + ", ".join(format_number(value) for value in uv)
                + "]} />"
            )

    bottom = len(generated)
    top = bottom + 1
    for values in (vertices[360], vertices[361]):
        generated.append(
            "      <Vertex position={["
            + ", ".join(format_number(value) for value in values[:3])
            + "]} uv={["
            + ", ".join(format_number(value) for value in values[3:])
            + "]} />"
        )
    for row in range(new_rows - 1):
        for sector in range(new_sectors):
            next_sector = (sector + 1) % new_sectors
            a = row * new_sectors + sector
            b = row * new_sectors + next_sector
            c = (row + 1) * new_sectors + next_sector
            d = (row + 1) * new_sectors + sector
            generated.append(f"      <Face indices={{[{a},{b},{c},{d}]}} />")
    for sector in range(new_sectors):
        next_sector = (sector + 1) % new_sectors
        generated.append(f"      <Face indices={{[{bottom},{next_sector},{sector}]}} />")
        a = (new_rows - 1) * new_sectors + sector
        b = (new_rows - 1) * new_sectors + next_sector
        generated.append(f"      <Face indices={{[{top},{a},{b}]}} />")

    header = source[asset_start:body_start].replace('subdivision="1"', 'subdivision="0"')
    output = (
        source[:asset_start]
        + header
        + "\n"
        + "\n".join(generated)
        + "\n"
        + source[asset_end:]
    )
    args.output.write_text(output)


if __name__ == "__main__":
    main()
