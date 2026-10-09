#!/usr/bin/env python3
"""Protect S99 layout and staging during an explicitly scoped realism revision.

All model IDs/transforms/shadow flags, cameras, animation channels, timeline,
Graph settings and 2D overlays remain exact. Resolved geometry (including UVs)
remains exact except individual furniture Model IDs in the reviewable allowlist.
Materials and light nodes may change. Generated asset numbering is ignored.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys

from verify_preservation import ASSET_TAGS, differences, parse, walk
from verify_material_upgrade import LIGHT_TAGS, sha

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/realism-upgrade"
FORMAT = "s99-realism-upgrade-preservation-v1"
LIGHTING_TAGS = LIGHT_TAGS | {
    "BakedLighting", "PlanarReflection", "AmbientOcclusion", "ContactShadow",
    "LightingStyle", "AtmosphereFog",
}
CALIBRATION = {"PostStyle": {"exposure"},
               "ColorManagement": {"exposure", "whiteBalance"}}


def snapshot(script: str) -> dict:
    document = parse(script)
    nodes = list(walk(document))
    assets = {}
    for node in nodes:
        if node.tag in ASSET_TAGS:
            identifier = str(node.attrs["id"])
            if identifier in assets:
                raise ValueError(f"Duplicate asset {identifier}")
            assets[identifier] = node
    memo = {}
    resolving = set()

    def geometry(identifier):
        if identifier in memo:
            return memo[identifier]
        if identifier in resolving:
            raise ValueError(f"Cyclic geometry {identifier}")
        node = assets[identifier]
        if node.tag in {"MaterialAsset", "ImageAsset"}:
            raise ValueError(f"Geometry resolves to {node.tag}: {identifier}")
        resolving.add(identifier)

        def resolve(n):
            attrs = {k: v for k, v in n.attrs.items()
                     if k not in {"id", "material", "materials"}}
            for key in ("asset", "geometry", "source"):
                if key in attrs:
                    attrs[key] = geometry(str(attrs[key]))
            value = {"tag": n.tag, "attributes": attrs}
            if n.children:
                value["children"] = [resolve(child) for child in n.children]
            return value

        value = resolve(node)
        resolving.remove(identifier)
        memo[identifier] = value
        return value

    counts = Counter()
    model_attrs = {}
    geometry_hashes = {}

    def protect(node):
        if node.tag == "Assets" or node.tag in ASSET_TAGS or node.tag in LIGHTING_TAGS:
            return None
        counts[node.tag] += 1
        attrs = dict(node.attrs)
        for key in CALIBRATION.get(node.tag, set()):
            attrs.pop(key, None)
        if node.tag == "Model":
            identifier = str(attrs["id"])
            if identifier in model_attrs:
                raise ValueError(f"Duplicate model {identifier}")
            geometry_hashes[identifier] = sha(geometry(str(attrs.pop("asset"))))
            attrs.pop("material", None)
            attrs.pop("materials", None)
            model_attrs[identifier] = attrs
        children = [value for child in node.children
                    if (value := protect(child)) is not None]
        result = {"tag": node.tag, "attributes": attrs}
        if children:
            result["children"] = children
        return result

    graph = next(node for node in document.children if node.tag == "Graph")
    tree = protect(graph)
    payload = {"sceneTree": tree, "modelAttributes": model_attrs}
    return {"format": FORMAT, "sourceSHA256": hashlib.sha256(script.encode()).hexdigest(),
            "semanticSHA256": sha(payload), "protectedPayload": payload,
            "geometryByModel": geometry_hashes, "modelCount": len(model_attrs),
            "cameraCount": counts["Camera3D"], "animationChannelCount": counts["AnimationTarget"],
            "overlayCounts": {tag: counts[tag] for tag in ("Layer", "Text", "Path", "Rect")}}


def read_allowlist(path: Path) -> set[str]:
    value = json.loads(path.read_text())
    if value.get("format") != "s99-realism-geometry-allowlist-v1":
        raise ValueError("Furniture allowlist format mismatch")
    names = value.get("modelIds", [])
    if not isinstance(names, list) or any(not isinstance(v, str) for v in names):
        raise ValueError("Furniture allowlist modelIds must be an explicit string array")
    if len(set(names)) != len(names):
        raise ValueError("Duplicate furniture allowlist ID")
    return set(names)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("snapshot", "verify"))
    parser.add_argument("--script", type=Path, default=ROOT / "main.motionloom")
    parser.add_argument("--allowlist", type=Path, default=ROOT / "scripts/realism_geometry_allowlist.json")
    parser.add_argument("--report", type=Path, default=OUT / "preservation-check.json")
    args = parser.parse_args()
    baseline_path = OUT / "baseline-scene-semantics.json"
    if args.mode == "snapshot":
        if baseline_path.exists():
            raise ValueError("Refusing to overwrite the realism baseline")
        source = gzip.decompress((OUT / "baseline-scene.motionloom.gz").read_bytes())
        metadata = json.loads((OUT / "baseline-scene-metadata.json").read_text())
        if hashlib.sha256(source).hexdigest() != metadata["sourceSHA256"]:
            raise ValueError("Baseline archive/source SHA mismatch")
        baseline = snapshot(source.decode())
        baseline_path.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n")
        print(f"SNAPSHOT: {baseline['modelCount']} models, {baseline['cameraCount']} cameras, {baseline['animationChannelCount']} channels; {baseline['semanticSHA256']}")
        return 0
    baseline = json.loads(baseline_path.read_text())
    if baseline["format"] != FORMAT:
        raise ValueError("Realism baseline format mismatch")
    current = snapshot(args.script.read_text())
    allowed = read_allowlist(args.allowlist)
    if unknown := allowed - baseline["geometryByModel"].keys():
        raise ValueError(f"Allowlist IDs missing from baseline: {sorted(unknown)}")
    changes = differences(baseline["protectedPayload"], current["protectedPayload"])
    geometry_changes = {name: {"before": before, "after": current["geometryByModel"].get(name)}
                        for name, before in baseline["geometryByModel"].items()
                        if before != current["geometryByModel"].get(name)}
    protected_geometry = {k: v for k, v in geometry_changes.items() if k not in allowed}
    added = sorted(current["geometryByModel"].keys() - baseline["geometryByModel"].keys())
    passed = not changes and not protected_geometry and not added
    report = {"format": FORMAT, "status": "passed" if passed else "failed",
              "sourceSHA256": current["sourceSHA256"], "baselineSourceSHA256": baseline["sourceSHA256"],
              "semanticSHA256": current["semanticSHA256"], "baselineSemanticSHA256": baseline["semanticSHA256"],
              "protectedModels": current["modelCount"], "protectedCameras": current["cameraCount"],
              "protectedAnimationChannels": current["animationChannelCount"],
              "protectedOverlayCounts": current["overlayCounts"],
              "protectedDifferences": changes, "protectedGeometryDifferences": protected_geometry,
              "addedModels": added, "geometryAllowlist": sorted(allowed),
              "allowedFurnitureGeometryChanges": {k: v for k, v in geometry_changes.items() if k in allowed},
              "unchangedGeometryModels": len(baseline["geometryByModel"]) - len(geometry_changes),
              "scope": "All model IDs/transforms/shadows, cameras, channels/timeline, Graph and 2D overlays exact; architecture/plants/city and other non-allowlisted geometry including normals/UV/tangents/topology exact. Only explicit allowlisted furniture geometry, lighting and material data may change."}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"{'PASS' if passed else 'FAIL'}: {current['modelCount']} models, {current['cameraCount']} cameras, {current['animationChannelCount']} channels; {len(protected_geometry)} protected geometry differences, {len(changes)} staging differences; {len(geometry_changes) - len(protected_geometry)} allowed furniture changes")
    for change in changes[:12]:
        print(change)
    for identifier in list(protected_geometry)[:12]:
        print(f"Protected geometry changed: {identifier}")
    return int(not passed)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, StopIteration) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(2)
