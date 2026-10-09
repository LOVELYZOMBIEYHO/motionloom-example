#!/usr/bin/env python3
"""Apply the reviewed S99 realism revision to its preserved baseline.

Uses existing DSL tags only. Light/material edits and the explicit furniture
allowlist are deterministic; no architecture/cameras/staging are regenerated.
Run bake_lighting.py afterward because transport and capture fingerprints change.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re

from realism_geometry import build as build_geometry

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/realism-upgrade"


def attributes(source, tag, identifier, changes):
    pattern = rf'<{tag}\b[^>]*\bid="{re.escape(identifier)}"[^>]*/>'
    def replace(match):
        node = match.group()
        for name, value in changes.items():
            attr = rf'\b{re.escape(name)}=(?:"[^"]*"|\{{[^}}]*\}})'
            if re.search(attr, node):
                node = re.sub(attr, f'{name}={value}', node, count=1)
            else:
                node = node[:-2].rstrip() + f' {name}={value} />'
        return node
    result, count = re.subn(pattern, replace, source)
    if count != 1:
        raise ValueError(f"Expected one {tag} {identifier}, got {count}")
    return result


def build(source):
    source, _, report = build_geometry(source)
    source = source.replace('shadowStyle="soft" />', 'shadowStyle="soft" shadowMode="perLight" />', 1)
    source = attributes(source, "DirectionalLight", "s99_sun", {
        "angularDiameter": '"0.5"', "shadowStrength": '"1"',
        "color": '"#FFF4E4"',
        "intensity": '{curve("0:2.8, 37:2.8, 40:0.28:ease_in_out, 44:0.28")}',
    })
    source = attributes(source, "EnvironmentLight", "s99_ibl", {
        "intensity": '{curve("0:1.1, 37:1.1, 40:0.2:ease_in_out, 44:0.2")}',
        "diffuseIntensity": '"0.85"', "specularIntensity": '"0.5"',
    })
    for identifier in ("s99_pendant_left", "s99_pendant_right"):
        # Integrated rectangle energy scales with its area. 37.03704*.18²
        # defines point-equivalent energy; daylight uses 1.2, dusk retains 6.
        source = attributes(source, "PointLight", identifier, {
            "direction": '{[0,-1,0]}', "width": '"0.18"', "height": '"0.18"',
            "castShadow": '"true"',
            "intensity": '{curve("0:37.03704,37:37.03704,40:185.18519:ease_in_out,44:185.18519")}',
        })
        pattern = rf'<PointLight\b[^>]*\bid="{identifier}"[^>]*/>'
        source = re.sub(pattern, lambda m: re.sub(r'\s+range="[^"]*"', '', m.group().replace('<PointLight', '<RectAreaLight', 1)), source)
    for identifier in ("s99_living_lamp", "s99_primary_lamp_left", "s99_primary_lamp_right", "s99_bath_fixture"):
        source = attributes(source, "PointLight", identifier, {"castShadow": '"true"', "sourceRadius": '"0.025"'})
    for identifier, daytime, dusk in (("s99_living_lamp", 1.8, 7), ("s99_primary_lamp_left", 1, 4), ("s99_primary_lamp_right", 1, 4), ("s99_bath_fixture", 1.5, 6)):
        source = attributes(source, "PointLight", identifier, {"intensity": f'{{curve("0:{daytime},37:{daytime},40:{dusk}:ease_in_out,44:{dusk}")}}'})
    source = source.replace('<AmbientOcclusion intensity="0.72" radius="0.35" />', '<AmbientOcclusion intensity="0.4" radius="0.35" />')
    source = source.replace('<ContactShadow intensity="0.85" distance="0.18" softness="0.55" />', '<ContactShadow intensity="0.45" distance="0.18" softness="0.55" />')
    for name, weight, roughness in (("oak", .1, .28), ("oak_floor", .1, .32), ("walnut", .12, .24), ("vertical_oak_joinery", .1, .28)):
        source = attributes(source, "MaterialAsset", name, {"clearcoat": f'"{weight}"', "clearcoatRoughness": f'"{roughness}"'})
    for name, weight, roughness in (("linen_upholstery", .15, .65), ("sage_fabric", .15, .65), ("clay_fabric", .15, .65), ("woven_rug", .18, .85), ("bedding_fabric", .15, .7), ("towel_fabric", .22, .85), ("shade_fabric", .08, .8)):
        source = attributes(source, "MaterialAsset", name, {"sheen": f'"{weight}"', "sheenColor": '"#FFF9EF"', "sheenRoughness": f'"{roughness}"'})
    return source, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "main.motionloom")
    args = parser.parse_args()
    baseline = gzip.decompress((OUT / "baseline-scene.motionloom.gz").read_bytes())
    metadata = json.loads((OUT / "baseline-scene-metadata.json").read_text())
    if hashlib.sha256(baseline).hexdigest() != metadata["sourceSHA256"]:
        raise ValueError("Baseline source SHA mismatch")
    result, report = build(baseline.decode())
    args.output.write_text(result)
    (OUT / "geometry/geometry-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Applied reviewed existing-tag revision: {args.output}; SHA256 {hashlib.sha256(result.encode()).hexdigest()}")


if __name__ == "__main__":
    main()
