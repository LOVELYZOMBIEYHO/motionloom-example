#!/usr/bin/env python3
"""Compare preserved S99 semantics while ignoring generated asset numbering.

This standalone check never executes build_showcase.py or rewrites scene files.
It resolves each protected Model's asset into geometry/material attributes,
including CompoundAsset child instances and texture hashes. It is intentionally
a narrow lexical DSL reader for the literal asset grammar used by S99, not a
replacement for MotionLoom's authoring analyzer.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
import html
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PREFIXES = (
    "s99_city", "s99_tree", "s99_garden", "s99_lounge_plant",
    "s99_terrace_plant", "s99_entry_plant", "s99_vase_stem", "s99_vase_sprigs",
)
ASSET_TAGS = {"PrimitiveAsset", "CompoundAsset", "MeshAsset", "GeometryAsset", "MaterialAsset", "ImageAsset"}
RESOURCE_TAGS = {
    "Camera3D", "EnvironmentLight", "DirectionalLight", "RectAreaLight",
    "PointLight", "SpotLight", "AmbientOcclusion", "ContactShadow",
    "ColorManagement", "AtmosphereFog", "RenderStyle",
}
TEXTURE_ATTRIBUTES = {
    "baseColorTexture", "normalTexture", "metallicRoughnessTexture",
    "occlusionTexture", "emissiveTexture", "heightTexture",
}


@dataclass
class Node:
    tag: str
    attrs: dict[str, object]
    children: list["Node"] = field(default_factory=list)


def canonical(raw: str) -> object:
    value = html.unescape(raw.strip())
    if value.startswith("{") and value.endswith("}"):
        value = value[1:-1].strip()
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    if value in ("true", "false"):
        return value == "true"
    try:
        number = float(value)
        return int(number) if number.is_integer() else number
    except ValueError:
        pass
    if value.startswith("[") and value.endswith("]"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
    # Expressions preserve strings but ignore cosmetic whitespace elsewhere.
    return re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"|\s+',
                  lambda m: m.group(0) if m.group(0).startswith('"') else "", value)


def attributes(source: str) -> dict[str, object]:
    result: dict[str, object] = {}
    position = 0
    while position < len(source):
        match = re.match(r"\s*([A-Za-z_][\w.-]*)\s*=\s*", source[position:])
        if not match:
            break
        key = match.group(1)
        position += match.end()
        start = position
        if source[position] == '"':
            position += 1
            while position < len(source) and source[position] != '"':
                if source[position] == "\\":
                    position += 1
                position += 1
            position += 1
        elif source[position] == "{":
            depth = 0
            quote = False
            while position < len(source):
                char = source[position]
                if char == '"' and (position == 0 or source[position - 1] != "\\"):
                    quote = not quote
                if not quote:
                    depth += (char == "{") - (char == "}")
                position += 1
                if depth == 0:
                    break
        else:
            while position < len(source) and not source[position].isspace():
                position += 1
        if key in result:
            raise ValueError(f"Duplicate attribute {key}")
        result[key] = canonical(source[start:position])
    return result


def parse(script: str) -> Node:
    # Strip whole XML comments before scanning tags.
    script = re.sub(r"<!--.*?-->", "", script, flags=re.S)
    root = Node("document", {})
    stack = [root]
    position = 0
    while True:
        start = script.find("<", position)
        if start < 0:
            break
        position = start + 1
        quote = False
        depth = 0
        while position < len(script):
            char = script[position]
            if char == '"' and script[position - 1] != "\\":
                quote = not quote
            if not quote:
                depth += (char == "{") - (char == "}")
                if char == ">" and depth == 0:
                    break
            position += 1
        token = script[start + 1:position].strip()
        position += 1
        if token.startswith("/"):
            if len(stack) == 1 or stack[-1].tag != token[1:].strip():
                raise ValueError(f"Unmatched closing tag {token}")
            stack.pop()
            continue
        match = re.match(r"([A-Za-z_][\w.-]*)\b(.*)", token, re.S)
        if not match:
            continue
        self_closing = token.endswith("/")
        node = Node(match.group(1), attributes(match.group(2).rstrip("/").strip()))
        stack[-1].children.append(node)
        if not self_closing:
            stack.append(node)
    if len(stack) != 1:
        raise ValueError("Unclosed DSL tags")
    return root


def walk(node: Node):
    yield node
    for child in node.children:
        yield from walk(child)


def excluded(identifier: str) -> bool:
    return identifier.startswith(EXCLUDED_PREFIXES)


def snapshot(path: Path, asset_root: Path | None = None) -> dict:
    script = path.read_text()
    asset_root = asset_root or path.parent
    nodes = list(walk(parse(script)))
    assets = {str(n.attrs["id"]): n for n in nodes
              if n.tag in ASSET_TAGS and "id" in n.attrs}
    resolving: set[str] = set()

    def resolved(identifier: str) -> dict:
        if identifier not in assets:
            raise ValueError(f"Unresolved asset {identifier}")
        if identifier in resolving:
            raise ValueError(f"Cyclic asset {identifier}")
        resolving.add(identifier)
        node = assets[identifier]
        attrs = dict(node.attrs)
        attrs.pop("id", None)
        if node.tag == "MeshAsset" and "geometry" in attrs:
            # Canonical GeometryAsset/MeshAsset syntax supersedes the older
            # material-bound PrimitiveAsset and inline MeshAsset syntax. Map
            # it back to the baseline's shape for semantic comparison.
            geometry_id = str(attrs.pop("geometry"))
            geometry = assets[geometry_id]
            generator = next((c for c in geometry.children
                              if c.tag in ("Primitive", "Mesh")), None)
            if generator is None:
                raise ValueError(f"Unresolved geometry generator {geometry_id}")
            material = resolved(str(attrs["material"]))
            resolving.remove(identifier)
            if generator.tag == "Primitive":
                return {"tag": "PrimitiveAsset", "attributes": {
                    **generator.attrs, "material": material,
                }}
            return {"tag": "MeshAsset", "attributes": {
                "material": material, "subdivision": 0,
            }, "children": [{"tag": c.tag, "attributes": c.attrs}
                            for c in generator.children]}
        if "material" in attrs:
            attrs["material"] = resolved(str(attrs["material"]))
        for name in TEXTURE_ATTRIBUTES:
            if name in attrs:
                attrs[name] = resolved(str(attrs[name]))
        if node.tag == "ImageAsset" and "src" in attrs:
            image = asset_root / str(attrs["src"])
            attrs["contentSHA256"] = hashlib.sha256(image.read_bytes()).hexdigest()
        children = []
        for child in node.children:
            child_attrs = dict(child.attrs)
            child_attrs.pop("id", None)
            if "asset" in child_attrs:
                child_attrs["asset"] = resolved(str(child_attrs["asset"]))
            children.append({"tag": child.tag, "attributes": child_attrs})
        resolving.remove(identifier)
        result = {"tag": node.tag, "attributes": attrs}
        if children:
            result["children"] = children
        return result

    protected_models = {}
    skipped_models = []
    resources = {}
    animations = []
    anonymous = {}
    for node in nodes:
        identifier = str(node.attrs.get("id", ""))
        if node.tag == "Model":
            if excluded(identifier):
                skipped_models.append(identifier)
                continue
            if not identifier:
                raise ValueError("Protected Model must have a semantic id")
            attrs = dict(node.attrs)
            attrs.pop("id", None)
            attrs["asset"] = resolved(str(attrs["asset"]))
            if identifier in protected_models:
                raise ValueError(f"Duplicate Model id {identifier}")
            protected_models[identifier] = attrs
        elif node.tag in RESOURCE_TAGS:
            attrs = dict(node.attrs)
            attrs.pop("id", None)
            if node.tag == "EnvironmentLight":
                attrs["asset"] = resolved(str(attrs["asset"]))
            if not identifier:
                anonymous[node.tag] = anonymous.get(node.tag, 0) + 1
                identifier = f"{node.tag}#{anonymous[node.tag]}"
            resources[identifier] = {
                "tag": node.tag, "attributes": attrs,
                "children": [{"tag": c.tag, "attributes": c.attrs} for c in node.children],
            }
        elif node.tag == "AnimationTarget" and not excluded(str(node.attrs.get("node", ""))):
            animations.append({"attributes": node.attrs,
                               "keys": [c.attrs for c in node.children]})
    graph = next(n for n in nodes if n.tag == "Graph")
    scene = next(n for n in nodes if n.tag == "Scene")
    payload = {
        "graph": graph.attrs,
        "scene": scene.attrs,
        "models": protected_models,
        "resources": resources,
        "animations": animations,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return {
        "format": "s99-semantic-preservation-v1",
        "source": str(path.resolve()),
        "sourceSHA256": hashlib.sha256(script.encode()).hexdigest(),
        "semanticSHA256": hashlib.sha256(encoded).hexdigest(),
        "excludedModelPrefixes": list(EXCLUDED_PREFIXES),
        "excludedModelCount": len(skipped_models),
        "excludedModelIds": sorted(skipped_models),
        "protectedModelCount": len(protected_models),
        "payload": payload,
    }


def differences(before: object, after: object, prefix: str = "") -> list[str]:
    if type(before) != type(after):
        return [prefix + " (type changed)"]
    if isinstance(before, dict):
        changes = []
        for key in sorted(before.keys() | after.keys()):
            name = prefix + "." + str(key) if prefix else str(key)
            if key not in before:
                changes.append(name + " (added)")
            elif key not in after:
                changes.append(name + " (removed)")
            else:
                changes.extend(differences(before[key], after[key], name))
        return changes
    if isinstance(before, list):
        if len(before) != len(after):
            return [prefix + " (list length changed)"]
        changes = []
        for index, (left, right) in enumerate(zip(before, after)):
            changes.extend(differences(left, right, f"{prefix}[{index}]"))
        return changes
    return [] if before == after else [prefix + f" ({before!r} -> {after!r})"]


def without_legacy_mapping(value):
    """Ignore the removed triplanar metadata from pre-canonical baselines."""
    if isinstance(value, dict):
        return {key: without_legacy_mapping(child) for key, child in value.items()
                if key != "mapping"}
    if isinstance(value, list):
        return [without_legacy_mapping(child) for child in value]
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["snapshot", "verify"])
    parser.add_argument("--script", type=Path, default=ROOT / "main.motionloom")
    parser.add_argument("--asset-root", type=Path)
    parser.add_argument("--allow-resolution-change", action="store_true",
                        help="Allow only same-aspect-ratio Graph size/renderSize changes; preserve all scene semantics.")
    parser.add_argument("--baseline", type=Path,
                        default=ROOT / "scripts/preservation-baseline.json")
    options = parser.parse_args()
    current = snapshot(options.script, options.asset_root)
    if options.mode == "snapshot":
        options.baseline.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
        print(f"Saved {current['protectedModelCount']} protected models and "
              f"{len(current['payload']['resources'])} resources to {options.baseline}")
        print(f"Semantic SHA256 {current['semanticSHA256']}")
        return 0
    baseline = json.loads(options.baseline.read_text())
    comparison = json.loads(json.dumps(current["payload"]))
    resolution_changes = {}
    if options.allow_resolution_change:
        for key in ("size", "renderSize"):
            before = baseline["payload"]["graph"][key]
            after = comparison["graph"][key]
            if before != after:
                if not (len(after) == 2 and all(isinstance(v, (int, float)) and v > 0 for v in after)
                        and before[0]*after[1] == before[1]*after[0]):
                    raise ValueError("Resolution changes must retain the original aspect ratio")
                resolution_changes[key] = {"before": before, "after": after}
                comparison["graph"][key] = before
    changes = differences(without_legacy_mapping(baseline["payload"]),
                          without_legacy_mapping(comparison))
    if changes:
        print(f"FAILED: {len(changes)} protected semantic difference(s)")
        for change in changes[:100]:
            print(change)
        return 1
    print(f"PASS: {current['protectedModelCount']} protected models, cameras, lights, "
          "materials, texture bytes and animation channels are unchanged")
    print(f"Semantic SHA256 {current['semanticSHA256']}")
    ROOT.joinpath('evidence/preservation-check.json').write_text(json.dumps({
        'source_sha256': current['sourceSHA256'],
        'baseline_source_sha256': baseline['sourceSHA256'],
        'status': 'passed',
        'semantic_sha256': current['semanticSHA256'],
        'protected_models': current['protectedModelCount'],
        'protected_resources': len(current['payload']['resources']),
        'allowed_resolution_changes': resolution_changes,
        'scope': 'Resolved house/furniture geometry, material values and texture bytes, cameras, lighting, render style and animation channels; plants and city buildings excluded. Removed legacy triplanar metadata is normalized across the approved baseline and canonical GeometryAsset syntax.',
    }, indent=2)+'\n')
    return 0


if __name__ == "__main__":
    sys.exit(main())
