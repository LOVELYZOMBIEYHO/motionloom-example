#!/usr/bin/env python3
"""Check S99 geometry, staging and overlays across a material/HDR upgrade.

This check reads the DSL without executing the generator. Asset references are
resolved before geometry is hashed, so generated numbering and deduplication do
not affect the comparison. All Models, including plants and city, are covered.
Only material assignments, UV/tangent data and the explicit calibration fields
below are outside the protected payload. The older preservation baseline is
never overwritten; it intentionally protects the previous materials as well.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

from verify_preservation import ASSET_TAGS, Node, differences, parse, walk


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence/material-upgrade"
FORMAT = "s99-material-upgrade-preservation-v1"
LIGHT_TAGS = {
    "EnvironmentLight", "DirectionalLight", "RectAreaLight", "PointLight", "SpotLight",
}
# Light topology, positions, dimensions, visibility and shadow flags remain
# protected. HDR orientation/energy, light energy/color and exposure may change.
CALIBRATION_FIELDS = {
    "EnvironmentLight": {"asset", "intensity", "diffuseIntensity", "specularIntensity", "rotationY"},
    "DirectionalLight": {"intensity", "color", "direction", "shadowStrength"},
    "RectAreaLight": {"intensity", "color"},
    "PointLight": {"intensity", "color", "range"},
    "SpotLight": {"intensity", "color", "range"},
    "LightingStyle": {"ambientIntensity", "ambientColor"},
    "PostStyle": {"exposure"},
    "ColorManagement": {"exposure", "whiteBalance"},
}
UV_TAGS = {"UV", "Tangent", "Tangents"}
UV_FIELDS = {"uv", "uv0", "uv1", "tangent", "tangents"}
MATERIAL_FIELDS = {"material", "materials"}


def sha(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def snapshot(path: Path) -> dict:
    script = path.read_text()
    document = parse(script)
    nodes = list(walk(document))
    assets = {}
    for node in nodes:
        if node.tag in ASSET_TAGS:
            identifier = str(node.attrs.get("id", ""))
            if not identifier or identifier in assets:
                raise ValueError(f"Missing or duplicate asset id: {identifier!r}")
            assets[identifier] = node
    memo: dict[str, dict] = {}
    resolving: set[str] = set()

    def geometry_node(node: Node) -> dict | None:
        if node.tag in UV_TAGS or node.tag in {"MaterialAsset", "ImageAsset"}:
            return None
        attrs = {key: value for key, value in node.attrs.items()
                 if key not in UV_FIELDS | MATERIAL_FIELDS | {"id"}}
        for field in ("asset", "geometry"):
            if field in attrs:
                attrs[field] = geometry_asset(str(attrs[field]))
        children = [value for child in node.children
                    if (value := geometry_node(child)) is not None]
        value = {"tag": node.tag, "attributes": attrs}
        if children:
            value["children"] = children
        return value

    def geometry_asset(identifier: str) -> dict:
        if identifier in memo:
            return memo[identifier]
        if identifier not in assets:
            raise ValueError(f"Unresolved geometry asset: {identifier}")
        if identifier in resolving:
            raise ValueError(f"Cyclic geometry asset: {identifier}")
        resolving.add(identifier)
        node = assets[identifier]
        value = geometry_node(node)
        if value is None:
            raise ValueError(f"Model resolved to non-geometry asset: {identifier}")
        resolving.remove(identifier)
        memo[identifier] = value
        return value

    model_ids = set()
    models = {}
    calibrations = {}
    counts = Counter()
    light_ids = {str(node.attrs["id"]) for node in nodes
                 if node.tag in LIGHT_TAGS and "id" in node.attrs}

    def protected_node(node: Node, locator: str) -> dict | None:
        if node.tag == "Assets" or node.tag in ASSET_TAGS:
            return None
        counts[node.tag] += 1
        attrs = dict(node.attrs)
        if node.tag == "Model":
            identifier = str(attrs.get("id", ""))
            if not identifier or identifier in model_ids:
                raise ValueError(f"Missing or duplicate Model id: {identifier!r}")
            model_ids.add(identifier)
            attrs["asset"] = {"geometrySHA256": sha(geometry_asset(str(attrs["asset"])))}
            for field in MATERIAL_FIELDS:
                attrs.pop(field, None)
            models[identifier] = attrs
        allowed = CALIBRATION_FIELDS.get(node.tag, set())
        if allowed:
            changed = {field: attrs.pop(field) for field in sorted(allowed) if field in attrs}
            if changed:
                calibrations[locator] = changed
        animation_light = (node.tag == "AnimationTarget"
                           and str(attrs.get("node", "")) in light_ids
                           and attrs.get("property") == "intensity")
        children = []
        for index, child in enumerate(node.children):
            child_locator = f"{locator}/{child.tag}[{index}]"
            child_value = protected_node(child, child_locator)
            if child_value is not None:
                if animation_light and child.tag == "Key":
                    # Preserve timing/interpolation even when recalibrating
                    # an explicit light intensity animation channel.
                    key_value = child_value["attributes"].pop("value", None)
                    calibrations[child_locator] = {"value": key_value}
                children.append(child_value)
        value = {"tag": node.tag, "attributes": attrs}
        if children:
            value["children"] = children
        return value

    graph = next((node for node in document.children if node.tag == "Graph"), None)
    if graph is None:
        raise ValueError("Missing top-level Graph")
    protected = protected_node(graph, "Graph")
    payload = {"sceneTree": protected, "models": models}
    return {
        "format": FORMAT,
        "source": str(path.resolve()),
        "sourceSHA256": hashlib.sha256(script.encode()).hexdigest(),
        "semanticSHA256": sha(payload),
        "protectedModelCount": len(models),
        "protectedCameraCount": counts["Camera3D"],
        "protectedAnimationCount": counts["AnimationTarget"],
        "protectedOverlayCounts": {tag: counts[tag] for tag in ("Layer", "Text", "Path", "Rect")},
        "calibrationFields": {tag: sorted(fields) for tag, fields in sorted(CALIBRATION_FIELDS.items())},
        "calibrationValues": calibrations,
        "payload": payload,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("snapshot", "verify"))
    parser.add_argument("--script", type=Path, default=ROOT / "main.motionloom")
    parser.add_argument("--baseline", type=Path, default=EVIDENCE / "baseline-scene-semantics.json")
    parser.add_argument("--report", type=Path, default=EVIDENCE / "preservation-check.json")
    options = parser.parse_args()
    current = snapshot(options.script)
    if options.mode == "snapshot":
        if options.baseline.exists():
            raise ValueError(f"Refusing to replace an existing baseline: {options.baseline}")
        options.baseline.parent.mkdir(parents=True, exist_ok=True)
        options.baseline.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
        print(f"SNAPSHOT: {current['protectedModelCount']} models, "
              f"{current['protectedCameraCount']} cameras, "
              f"{current['protectedAnimationCount']} animation channels")
        print(f"Semantic SHA256 {current['semanticSHA256']}")
        return 0
    baseline = json.loads(options.baseline.read_text())
    if baseline.get("format") != FORMAT or baseline.get("calibrationFields") != current["calibrationFields"]:
        raise ValueError("Baseline format/calibration policy mismatch")
    changes = differences(baseline["payload"], current["payload"])
    calibration_changes = differences(baseline["calibrationValues"], current["calibrationValues"])
    report = {
        "status": "failed" if changes else "passed",
        "sourceSHA256": current["sourceSHA256"],
        "baselineSourceSHA256": baseline["sourceSHA256"],
        "semanticSHA256": current["semanticSHA256"],
        "baselineSemanticSHA256": baseline["semanticSHA256"],
        "protectedModels": current["protectedModelCount"],
        "protectedCameras": current["protectedCameraCount"],
        "protectedAnimationChannels": current["protectedAnimationCount"],
        "protectedOverlayCounts": current["protectedOverlayCounts"],
        "protectedDifferences": changes,
        "allowedCalibrationChanges": calibration_changes,
        "scope": "All models (including plants and city), resolved primitive parameters, mesh positions/normals/topology, compound instances, model transforms/shadows, scene/layout, cameras, timeline/animation, Graph dimensions/fps/duration and overlays. Material/ImageAsset data, UV/tangents and listed light/exposure calibration fields may change.",
    }
    options.report.parent.mkdir(parents=True, exist_ok=True)
    options.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if changes:
        print(f"FAILED: {len(changes)} protected semantic difference(s)")
        for change in changes[:20]:
            print(change)
        return 1
    print(f"PASS: {current['protectedModelCount']} models, "
          f"{current['protectedCameraCount']} cameras, "
          f"{current['protectedAnimationCount']} animation channels, overlays and Graph unchanged")
    print(f"Allowed calibration changes: {len(calibration_changes)}")
    print(f"Semantic SHA256 {current['semanticSHA256']}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(2)
