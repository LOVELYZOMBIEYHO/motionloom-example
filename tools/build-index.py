#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_ROOT = ROOT / "core"
SHOWCASE_ROOT = ROOT / "showcase"
SCHEMA_PATH = ROOT / "schema" / "example.schema.json"
TAG_REGISTRY_PATH = ROOT / "schema" / "tag-registry.json"
DOMAINS = ("scene", "world", "process", "composition", "text")
DOMAIN_PREFIX = {
    "scene": "cs",
    "world": "cw",
    "process": "cp",
    "composition": "cm",
    "text": "ct",
}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data) -> None:
    write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def slug(value: str) -> str:
    import re

    value = value.lower().replace("_", "-").replace(" ", "-")
    return re.sub("-+", "-", re.sub("[^a-z0-9-]+", "-", value)).strip("-") or "example"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_tag_registry() -> dict:
    return json.loads(TAG_REGISTRY_PATH.read_text(encoding="utf-8"))


SCHEMA = load_schema()
TAG_REGISTRY = load_tag_registry()
FEATURE_TAGS = set(TAG_REGISTRY.get("feature_tags", []))
DSL_TAGS = set(TAG_REGISTRY.get("dsl_tags", []))
RESERVED_FEATURE_TAGS = set(TAG_REGISTRY.get("reserved_feature_tags", []))


def fail(path: Path, message: str) -> None:
    raise SystemExit(f"{path.relative_to(ROOT)}: {message}")


def validate_string_array(path: Path, record: dict, key: str) -> None:
    value = record.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        fail(path, f"'{key}' must be an array of strings")


def validate_example_record(path: Path, record: dict, domain_dir: str) -> None:
    for key in SCHEMA.get("required", []):
        if key not in record:
            fail(path, f"missing required key '{key}'")

    props = SCHEMA.get("properties", {})
    id_value = record.get("id")
    if not isinstance(id_value, str) or not re.fullmatch(props["id"]["pattern"], id_value):
        fail(path, "id must match cs/cw/cp/cm/ct-000000")

    type_value = record.get("type")
    if type_value not in props["type"]["enum"]:
        fail(path, f"type must be one of {props['type']['enum']}")

    domain = record.get("domain")
    if domain not in props["domain"]["enum"]:
        fail(path, f"domain must be one of {props['domain']['enum']}")
    if domain != domain_dir:
        fail(path, f"domain '{domain}' does not match folder '{domain_dir}'")

    if type_value == "core":
        expected_prefix = DOMAIN_PREFIX[domain]
        if not id_value.startswith(f"{expected_prefix}-"):
            fail(path, f"id prefix must be '{expected_prefix}-' for domain '{domain}'")

    for key in ("title", "source_path"):
        if not isinstance(record.get(key), str):
            fail(path, f"'{key}' must be a string")
    if "demo_url" in record and not isinstance(record["demo_url"], str):
        fail(path, "'demo_url' must be a string")

    for key in ("features", "dsl", "teaches"):
        validate_string_array(path, record, key)
    for key in ("related", "requires"):
        if key in record:
            validate_string_array(path, record, key)

    unknown_features = sorted(set(record["features"]) - FEATURE_TAGS)
    if unknown_features:
        fail(path, f"unknown feature tag(s): {', '.join(unknown_features)}")
    reserved_features = sorted(set(record["features"]) & RESERVED_FEATURE_TAGS)
    if reserved_features:
        fail(path, f"reserved feature tag(s): {', '.join(reserved_features)}")

    unknown_dsl = sorted(set(record["dsl"]) - DSL_TAGS)
    if unknown_dsl:
        fail(path, f"unknown DSL tag(s): {', '.join(unknown_dsl)}")


def load_records() -> list[dict]:
    out: list[dict] = []
    seen_ids: set[str] = set()
    for domain in DOMAINS:
        for path in sorted((CORE_ROOT / domain).glob("*/example.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            validate_example_record(path, record, domain)
            if record["id"] in seen_ids:
                fail(path, f"duplicate id '{record['id']}'")
            seen_ids.add(record["id"])
            rel_dir = path.parent.relative_to(ROOT).as_posix()
            record["path"] = f"{rel_dir}/"
            out.append(record)
    for path in sorted(SHOWCASE_ROOT.glob("*/example.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        validate_example_record(path, record, record.get("domain", "scene"))
        if record["type"] != "showcase":
            fail(path, "showcase records must use type 'showcase'")
        if not re.fullmatch(r"s-[0-9]{6}", record["id"]):
            fail(path, "showcase id must match s-000000")
        if record["id"] in seen_ids:
            fail(path, f"duplicate id '{record['id']}'")
        seen_ids.add(record["id"])
        rel_dir = path.parent.relative_to(ROOT).as_posix()
        record["path"] = f"{rel_dir}/"
        out.append(record)
    return sorted(out, key=lambda r: (DOMAINS.index(r.get("domain", "scene")), r["id"]))


def record_link(from_file: Path, record: dict) -> str:
    target = ROOT / record["path"]
    return os.path.relpath(target, from_file.parent).replace(os.sep, "/") + "/"


def table(records: list[dict], title: str, from_file: Path) -> str:
    lines = [
        title,
        "",
        "| ID | Type | Domain | Title | Features | Teaches |",
        "|---|---|---|---|---|---|",
    ]
    for record in records:
        link = record_link(from_file, record)
        teaches = "<br>".join(record.get("teaches", [])[:2])
        features = ", ".join(record.get("features", [])[:5])
        lines.append(
            f"| [{record['id']}]({link}) | {record.get('type', '')} | {record.get('domain', '')} | {record['title']} | {features} | {teaches} |"
        )
    lines.append("")
    return "\n".join(lines)


def ids_by(records: list[dict], key: str) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for record in records:
        value = record.get(key)
        if isinstance(value, list):
            for item in value:
                grouped[slug(str(item))].append(record["id"])
        elif value:
            grouped[slug(str(value))].append(record["id"])
    return dict(sorted(grouped.items()))


def records_for_ids(records: list[dict], ids: list[str]) -> list[dict]:
    lookup = {record["id"]: record for record in records}
    return [lookup[id_] for id_ in ids if id_ in lookup]


all_records = load_records()
core = [r for r in all_records if r.get("type") == "core"]
showcase = [r for r in all_records if r.get("type") == "showcase"]

by_domain = ids_by(all_records, "domain")
by_type = ids_by(all_records, "type")
by_feature = ids_by(all_records, "features")
by_dsl = ids_by(all_records, "dsl")
domain_counts = {domain: len(by_domain.get(domain, [])) for domain in DOMAINS}

write(ROOT / "dataset/examples.jsonl", "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in all_records))
write(ROOT / "dataset/core.jsonl", "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in core))
write(ROOT / "dataset/showcase.jsonl", "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in showcase))
write_json(
    ROOT / "dataset/all.json",
    {
        "example_count": len(all_records),
        "core_count": len(core),
        "showcase_count": len(showcase),
        "domain_counts": domain_counts,
        "id_prefixes": DOMAIN_PREFIX,
        "examples": all_records,
    },
)
write_json(ROOT / "dataset/by-domain.json", by_domain)
write_json(ROOT / "dataset/by-type.json", by_type)
write_json(ROOT / "dataset/by-feature.json", by_feature)
write_json(ROOT / "dataset/by-dsl.json", by_dsl)
# Backward-friendly aliases for tools still expecting old names.
write_json(ROOT / "dataset/core-by-domain.json", ids_by(core, "domain"))
write_json(ROOT / "dataset/core-by-feature.json", ids_by(core, "features"))
write_json(ROOT / "dataset/core-by-dsl.json", ids_by(core, "dsl"))
write_json(
    ROOT / "dataset/source-map.json",
    {r.get("source_path", ""): r["id"] for r in all_records if r.get("source_path")},
)
write_json(
    ROOT / "dataset/demo-url-map.json",
    {
        "showcase": [
            {
                "id": r["id"],
                "title": r["title"],
                "url": r["path"],
                "demo_url": r.get("demo_url", ""),
            }
            for r in showcase
        ]
    },
)

browse = ROOT / "browse"
if browse.exists():
    shutil.rmtree(browse)

for folder in [
    browse / "domains",
    browse / "features",
    browse / "dsl",
]:
    folder.mkdir(parents=True, exist_ok=True)

write(browse / "all.md", table(all_records, "# All MotionLoom Examples", browse / "all.md"))
write(browse / "core.md", table(core, "# Core Examples", browse / "core.md"))
write(browse / "showcase.md", table(showcase, "# Showcase Examples", browse / "showcase.md"))

idx = ["# Domain Index", "", "| Domain | Prefix | Count |", "|---|---|---:|"]
for domain in DOMAINS:
    ids = by_domain.get(domain, [])
    idx.append(f"| [{domain}](domains/{domain}.md) | `{DOMAIN_PREFIX[domain]}-*` | {len(ids)} |")
    write(
        browse / "domains" / f"{domain}.md",
        table(records_for_ids(all_records, ids), f"# Domain: {domain}", browse / "domains" / f"{domain}.md"),
    )
idx.append("")
write(browse / "domains.md", "\n".join(idx))

idx = ["# Feature Index", "", "| Feature | Count |", "|---|---:|"]
for feature, ids in sorted(by_feature.items()):
    idx.append(f"| [{feature}](features/{feature}.md) | {len(ids)} |")
    write(
        browse / "features" / f"{feature}.md",
        table(records_for_ids(all_records, ids), f"# Feature: {feature}", browse / "features" / f"{feature}.md"),
    )
idx.append("")
write(browse / "features.md", "\n".join(idx))

idx = ["# DSL Pattern Index", "", "| DSL Pattern | Count |", "|---|---:|"]
for dsl, ids in sorted(by_dsl.items()):
    idx.append(f"| [{dsl}](dsl/{dsl}.md) | {len(ids)} |")
    write(
        browse / "dsl" / f"{dsl}.md",
        table(records_for_ids(all_records, ids), f"# DSL Pattern: {dsl}", browse / "dsl" / f"{dsl}.md"),
    )
idx.append("")
write(browse / "dsl.md", "\n".join(idx))

write(
    browse / "README.md",
    "# Browse MotionLoom Examples\n\n"
    "- [All Examples](all.md)\n"
    "- [Domain Index](domains.md)\n"
    "- [Feature Index](features.md)\n"
    "- [DSL Pattern Index](dsl.md)\n"
    "- [Core Examples](core.md)\n"
    "- [Showcase Examples](showcase.md)\n",
)
print(f"Generated {len(all_records)} examples: {domain_counts}")
