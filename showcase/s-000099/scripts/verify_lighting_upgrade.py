#!/usr/bin/env python3
"""Protect S99 staging while permitting the explicit indoor lighting upgrade.

The pre-lighting full DSL is archived separately. Generated asset IDs resolve
before hashing; every model, including city/plants, is checked. This phase
protects UVs and existing surface materials, except architectural window glass,
the bathroom mirror and shower screen. Analytic light nodes, baked/planar
lighting nodes and the prior explicit exposure/energy calibration may change.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys

from verify_preservation import ASSET_TAGS, TEXTURE_ATTRIBUTES, differences, parse, walk
from verify_material_upgrade import CALIBRATION_FIELDS, LIGHT_TAGS, sha

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence/lighting-upgrade"
FORMAT = "s99-lighting-upgrade-preservation-v1"
LIGHTING_NODES = LIGHT_TAGS | {"BakedLighting", "PlanarReflection"}


def allowed_surface(model_id: str) -> bool:
    return (model_id in {"s99_mirror", "s99_shower_screen"}
            or (model_id.startswith("s99_") and not model_id.startswith("s99_city")
                and "_glass" in model_id))


def semantics(script: str) -> dict:
    document = parse(script)
    nodes = list(walk(document))
    assets = {str(n.attrs["id"]): n for n in nodes if n.tag in ASSET_TAGS}
    if len(assets) != sum(n.tag in ASSET_TAGS for n in nodes):
        raise ValueError("Duplicate asset IDs")
    memo = {}
    resolving = set()
    image_memo = {}

    def material(identifier: str) -> dict:
        node = assets[identifier]
        attrs = {k: v for k, v in node.attrs.items() if k != "id"}
        for field in TEXTURE_ATTRIBUTES:
            if field in attrs:
                image_id = str(attrs[field])
                image = assets[image_id]
                src = ROOT / str(image.attrs["src"])
                if image_id not in image_memo:
                    image_memo[image_id] = hashlib.sha256(src.read_bytes()).hexdigest()
                attrs[field] = {"imageSHA256": image_memo[image_id],
                                "attributes": {k: v for k, v in image.attrs.items()
                                               if k not in {"id", "src"}}}
        return attrs

    def geometry(identifier: str, surface: bool) -> dict:
        key = (identifier, surface)
        if key in memo:
            return memo[key]
        if key in resolving:
            raise ValueError(f"Cyclic geometry {identifier}")
        resolving.add(key)

        def resolve(node):
            attrs = {k: v for k, v in node.attrs.items() if k != "id"}
            for field in ("asset", "geometry"):
                if field in attrs:
                    attrs[field] = geometry(str(attrs[field]), surface)
            if "material" in attrs:
                if surface:
                    attrs["material"] = material(str(attrs["material"]))
                else:
                    attrs.pop("material")
            if "materials" in attrs:
                if surface:
                    attrs["materials"] = [material(str(v)) for v in attrs["materials"]]
                else:
                    attrs.pop("materials")
            value = {"tag": node.tag, "attributes": attrs}
            if node.children:
                value["children"] = [resolve(n) for n in node.children]
            return value

        value = resolve(assets[identifier])
        resolving.remove(key)
        memo[key] = value
        return value

    counts = Counter()
    models = {}
    light_ids = {str(n.attrs["id"]) for n in nodes if n.tag in LIGHT_TAGS and "id" in n.attrs}

    def protect(node):
        if node.tag == "Assets" or node.tag in ASSET_TAGS or node.tag in LIGHTING_NODES:
            return None
        counts[node.tag] += 1
        attrs = dict(node.attrs)
        for field in CALIBRATION_FIELDS.get(node.tag, set()):
            attrs.pop(field, None)
        light_animation = (node.tag == "AnimationTarget"
                           and str(attrs.get("node", "")) in light_ids
                           and attrs.get("property") == "intensity")
        if node.tag == "Model":
            identifier = str(attrs["id"])
            if identifier in models:
                raise ValueError(f"Duplicate model {identifier}")
            attrs["asset"] = {"resolvedSHA256": sha(geometry(str(attrs["asset"]),
                                                          not allowed_surface(identifier)))}
            if "material" in attrs:
                if allowed_surface(identifier):
                    attrs.pop("material")
                else:
                    attrs["material"] = material(str(attrs["material"]))
            models[identifier] = attrs
        children = []
        for child in node.children:
            value = protect(child)
            if value is not None:
                if light_animation and child.tag == "Key":
                    value["attributes"].pop("value", None)
                children.append(value)
        value = {"tag": node.tag, "attributes": attrs}
        if children:
            value["children"] = children
        return value

    graph = next(n for n in document.children if n.tag == "Graph")
    tree = protect(graph)
    payload = {"sceneTree": tree, "models": models}
    return {"format": FORMAT, "semanticSHA256": sha(payload), "payload": payload,
            "protectedModels": len(models), "protectedCameras": counts["Camera3D"],
            "protectedAnimationChannels": counts["AnimationTarget"],
            "protectedOverlayCounts": {k: counts[k] for k in ("Layer", "Text", "Path", "Rect")}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("snapshot", "verify"))
    parser.add_argument("--script", type=Path, default=ROOT / "main.motionloom")
    parser.add_argument("--report", type=Path, default=EVIDENCE / "preservation-check.json")
    args = parser.parse_args()
    baseline_path = EVIDENCE / "baseline-scene-semantics.json"
    if args.mode == "snapshot":
        if baseline_path.exists():
            raise ValueError("Refusing to overwrite existing lighting baseline")
        raw = gzip.decompress((EVIDENCE / "baseline-scene.motionloom.gz").read_bytes())
        metadata = json.loads((EVIDENCE / "baseline-scene-metadata.json").read_text())
        if hashlib.sha256(raw).hexdigest() != metadata["sourceSHA256"]:
            raise ValueError("Archived baseline SHA mismatch")
        value = semantics(raw.decode())
        value["sourceSHA256"] = metadata["sourceSHA256"]
        baseline_path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        print(f"SNAPSHOT: {value['protectedModels']} models, {value['protectedCameras']} cameras; {value['semanticSHA256']}")
        return 0
    baseline = json.loads(baseline_path.read_text())
    if baseline["format"] != FORMAT:
        raise ValueError("Lighting baseline format mismatch")
    raw = args.script.read_bytes()
    current = semantics(raw.decode())
    changes = differences(baseline["payload"], current["payload"])
    report = {k: v for k, v in current.items() if k != "payload"}
    report.update({"status": "failed" if changes else "passed",
                   "sourceSHA256": hashlib.sha256(raw).hexdigest(),
                   "baselineSourceSHA256": baseline["sourceSHA256"],
                   "baselineSemanticSHA256": baseline["semanticSHA256"],
                   "protectedDifferences": changes,
                   "scope": "All 501 model geometries, normals/UV/tangents/topology, transforms/shadows, staging, 7 cameras, Graph/timeline/overlay and existing material/texture data. Only architectural glass/mirror/shower-screen surface material, analytic/baked/planar lighting nodes and explicit energy/exposure calibration may change."})
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"{'FAIL' if changes else 'PASS'}: {current['protectedModels']} models, {current['protectedCameras']} cameras, {current['protectedAnimationChannels']} animation channels; {len(changes)} protected differences")
    for change in changes[:12]:
        print(change)
    return int(bool(changes))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, StopIteration) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(2)
