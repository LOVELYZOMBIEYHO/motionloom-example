#!/usr/bin/env python3
"""Rebuild S99's camera-independent two-state CPU lighting assets, without video.

Uses the reusable engine example with the checked-in room/settings JSON. Run
with --build after engine changes. No renderer or GPU work is started here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT.parents[2] / "motionloom"


def update_provenance(script: Path, options: Path, output: Path, asset: dict) -> dict:
    """Record only the files referenced by this successful bake, not stale captures."""
    asset_root = output.resolve().parent
    provenance_path = asset_root / "provenance.json"
    previous = json.loads(provenance_path.read_text()) if provenance_path.is_file() else {}
    source_sha = hashlib.sha256(script.read_bytes()).hexdigest()
    options_sha = hashlib.sha256(options.read_bytes()).hexdigest()
    paths = {output.resolve()}
    states = []
    for state in asset["states"]:
        volumes = []
        for volume in state["volumes"]:
            captures = [capture["src"] for capture in volume["reflections"]]
            for src in captures:
                path = (asset_root / src).resolve()
                if not path.is_relative_to(asset_root):
                    raise ValueError(f"Capture escapes the baked asset directory: {src}")
                paths.add(path)
            volumes.append({"id": volume["id"], "counts": volume["counts"],
                            "probes": len(volume["probes"]),
                            "validProbes": sum(probe["valid"] for probe in volume["probes"]),
                            "localCaptures": len(captures), "capturePaths": captures})
        states.append({"name": state["name"], "frame": state["frame"], "volumes": volumes})
    files = []
    for path in sorted(paths, key=lambda path: path.relative_to(asset_root).as_posix()):
        data = path.read_bytes()
        files.append({"path": path.relative_to(asset_root).as_posix(),
                      "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    limitations = list(dict.fromkeys([
        *previous.get("limitations", []), *asset.get("diagnostics", []),
        "Finite sun disks and projected point/spot source disks are sampled when authored; "
        "zero-size sources retain delta-light behavior. Rectangular sources sample their full area.",
        "The solver traces diffuse transport and local HDR captures; it does not solve glossy "
        "interreflection, caustics or moving geometry. Material-layer energy attenuation is an "
        "approximation for diffuse bounce transport.",
    ]))
    provenance = {**previous, "format": "s99-generated-lighting-v1",
                  "sourceSha256": source_sha, "optionsSha256": options_sha,
                  "schemaVersion": asset["schemaVersion"], "sceneId": asset["sceneId"],
                  "bakerVersion": asset["bakerVersion"],
                  "authoringFingerprint": asset.get("authoringFingerprint", ""),
                  "fingerprint": asset["fingerprint"], "options": json.loads(options.read_text()),
                  "states": states, "files": files, "limitations": limitations}
    provenance.setdefault("origin", "Deterministic CPU bake of authored S99 geometry, fixed lights "
                          "and existing CC0 inputs; no new download or ImageGen asset.")
    provenance.setdefault("inputProvenance", ["../pbr-v2/provenance.json",
                                             "../environment-v2/manifest.json"])
    temporary = provenance_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n")
    temporary.replace(provenance_path)
    return provenance


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true", help="Build the release CPU bake example first")
    parser.add_argument("--engine", type=Path, default=ENGINE)
    parser.add_argument("--options", type=Path, default=ROOT / "scripts/lighting_bake_options.json")
    parser.add_argument("--script", type=Path, default=ROOT / "main.motionloom")
    parser.add_argument("--output", type=Path, default=ROOT / "assets/lighting-v3/s99-lighting.json")
    parser.add_argument("--evidence", type=Path, default=ROOT / "evidence/lighting-upgrade",
                        help="Report directory; override for a new review phase")
    args = parser.parse_args()
    if args.build:
        subprocess.run(["cargo", "build", "--release", "--example", "bake_scene_lighting"],
                       cwd=args.engine, check=True)
    binary = args.engine / "target/release/examples/bake_scene_lighting"
    if not binary.is_file():
        parser.error(f"Missing {binary}; run with --build")
    began = time.perf_counter()
    subprocess.run([str(binary), str(args.script.resolve()), str(args.options.resolve()),
                    str(args.output.resolve())], cwd=ROOT, check=True)
    elapsed = time.perf_counter() - began
    asset = json.loads(args.output.read_text())
    provenance = update_provenance(args.script, args.options, args.output, asset)
    states = []
    for state in asset["states"]:
        rooms = []
        for volume in state["volumes"]:
            probes = volume["probes"]
            rooms.append({"id": volume["id"], "counts": volume["counts"],
                          "probeCount": len(probes),
                          "validProbes": sum(p["valid"] for p in probes),
                          "reflectionCaptures": [p["src"] for p in volume["reflections"]]})
        states.append({"name": state["name"], "frame": state["frame"], "volumes": rooms})
    report = {"format": "s99-cpu-lighting-bake-report-v1", "elapsedSeconds": round(elapsed, 3),
              "sourceSHA256": provenance["sourceSha256"],
              "optionsSHA256": provenance["optionsSha256"],
              "authoringFingerprint": asset.get("authoringFingerprint", ""),
              "bakerVersion": asset["bakerVersion"], "fingerprint": asset["fingerprint"],
              "states": states, "diagnostics": asset["diagnostics"],
              "scope": "CPU bake only. No GPU render or complete video output."}
    evidence = args.evidence
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "bake-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"Saved {args.output}: {elapsed:.2f}s; fingerprint {asset['fingerprint']['combined']}")


if __name__ == "__main__":
    main()
