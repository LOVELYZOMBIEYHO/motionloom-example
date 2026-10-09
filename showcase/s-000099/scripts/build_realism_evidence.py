#!/usr/bin/env python3
"""Prepare isolated baseline assets and assemble source-bound S99 still evidence.

This script never invokes cargo, a renderer, a video encoder or the generator.
--prepare writes review inputs and argument arrays for the existing
scripts/lighting_review.rs harness. Assembly requires completed capture reports,
Pillow and NumPy. Historical material/lighting evidence remains untouched.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import tarfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/realism-upgrade"
DEFAULT_FRAMES = [0, 360, 528, 660, 840, 880, 984, 1055]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def prepare(directory: Path, renderer: str, frames: list[int], ablation: bool) -> None:
    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    metadata = read(OUT / "baseline-scene-metadata.json")
    baseline = gzip.decompress((OUT / metadata["archive"]).read_bytes())
    if sha(baseline) != metadata["sourceSHA256"]:
        raise ValueError("Archived baseline source SHA mismatch")
    archive = OUT / metadata["assetArchive"]["file"]
    if sha(archive.read_bytes()) != metadata["assetArchive"]["sha256"]:
        raise ValueError("Archived baseline assets SHA mismatch")
    baseline_root = directory / "baseline-input"
    baseline_root.mkdir(parents=True, exist_ok=True)
    # Extract only the reviewed regular-file inventory; no generic extractall.
    with tarfile.open(archive, "r:gz") as bundle:
        for name, expected in metadata["retainedAssets"].items():
            relative = Path(name)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError(f"Unsafe archived asset path {name}")
            member = bundle.getmember(name)
            if not member.isfile():
                raise ValueError(f"Expected a regular archived asset: {name}")
            handle = bundle.extractfile(member)
            if handle is None:
                raise ValueError(f"Missing archived asset data: {name}")
            data = handle.read()
            if sha(data) != expected["sha256"] or len(data) != expected["bytes"]:
                raise ValueError(f"Archived asset inventory mismatch: {name}")
            target = baseline_root / relative
            if target.exists() and sha(target.read_bytes()) != expected["sha256"]:
                raise ValueError(f"Refusing to overwrite unrelated baseline asset: {target}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    baseline_script = baseline_root / "main.motionloom"
    baseline_script.write_bytes(baseline)
    current = (ROOT / "main.motionloom").read_bytes()
    after_script = directory / "after.motionloom"
    after_script.write_bytes(current)
    variants = {"baseline": (baseline_script, baseline_root, metadata["sourceSHA256"]),
                "after": (after_script, ROOT, sha(current))}
    if ablation:
        global_source = re.sub(r'^\s*<BakedLighting[^\n]*\n', '\n', current.decode(), flags=re.M)
        global_script = directory / "global-only.motionloom"
        global_script.write_text(global_source)
        variants["global-only"] = (global_script, ROOT, sha(global_source.encode()))
    commands = []
    for name, (script, asset_root, source_sha) in variants.items():
        commands.append({"name": name, "sourceSHA256": source_sha, "source": str(script),
                         "assetRoot": str(asset_root), "output": str(OUT / name),
                         "argv": [renderer, str(script), str(asset_root), str(OUT / name),
                                  "cinematic", ",".join(map(str, frames)), "--warm=8"]})
    write(OUT / "review-plan.json", {"format": "s99-realism-still-plan-v1",
          "sourceSHA256": sha(current), "baselineSourceSHA256": metadata["sourceSHA256"],
          "harnessSource": "scripts/lighting_review.rs",
          "harnessSourceSHA256": sha((ROOT / "scripts/lighting_review.rs").read_bytes()),
          "frames": frames, "commands": commands,
          "baselineMeaning": "Archived pre-realism scene and matching archived assets, rendered using the current renderer.",
          "globalOnlyMeaning": "Current scene with BakedLighting removed; analytic lights and planar reflection remain active.",
          "fullVideoExported": False})
    print(f"Prepared {len(commands)} still-only commands and {len(metadata['retainedAssets'])} exact baseline assets; see {OUT / 'review-plan.json'}")


def assemble() -> None:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    plan = read(OUT / "review-plan.json")
    source_sha = sha((ROOT / "main.motionloom").read_bytes())
    if source_sha != plan["sourceSHA256"]:
        raise ValueError("Canonical source changed after review preparation")
    preservation = read(OUT / "preservation-check.json")
    if preservation["status"] != "passed" or preservation["sourceSHA256"] != source_sha:
        raise ValueError("Need a passing preservation check for this exact source")
    reports = {}
    captures = []
    for command in plan["commands"]:
        folder = Path(command["output"])
        report = read(folder / "review-report.json")
        authoring = read(folder / "authoring-report.json")
        if report.get("inProgress", True) or report["sourceSha256"] != command["sourceSHA256"]:
            raise ValueError(f"Stale/incomplete review: {command['name']}")
        settings = report["settings"]
        if (settings["profile"] != "cinematic"
                or settings.get("dynamic_resolution", settings.get("dynamicResolution", False))
                or settings.get("min_resolution_scale", settings.get("minResolutionScale", 1.0)) != 1.0):
            raise ValueError(f"Need fixed Cinematic review: {command['name']}")
        if authoring.get("status") != "clean" or not authoring.get("renderable"):
            raise ValueError(f"Authoring analysis failed: {command['name']}")
        by_frame = {capture["frame"]: capture for capture in report["captures"]}
        for frame in plan["frames"]:
            record = by_frame[frame]
            path = folder / record["file"]
            with Image.open(path) as image:
                if list(image.size) != record["dimensions"] or image.size != (1920, 1080):
                    raise ValueError(f"Need verified 1920x1080 still: {path}")
                image.verify()
            captures.append({"variant": command["name"], "frame": frame,
                             "file": str(path.relative_to(OUT)), "sha256": sha(path.read_bytes()),
                             "sourceSHA256": command["sourceSHA256"], "dimensions": [1920, 1080]})
        reports[command["name"]] = report

    def image(name, frame):
        return Image.open(OUT / name / f"frame-{frame:04}.png").convert("RGB")

    def font(size):
        for path in ["/System/Library/Fonts/Helvetica.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
            if Path(path).exists():
                return ImageFont.truetype(path, size)
        return ImageFont.load_default()

    baseline_opening = np.asarray(image("baseline", 0))
    after_opening = np.asarray(image("after", 0))
    opening = {"pixelIdentical": bool(np.array_equal(baseline_opening, after_opening)),
               "changedPixels": int(np.any(baseline_opening != after_opening, axis=2).sum())}
    if not opening["pixelIdentical"]:
        raise ValueError("Opening 2D plan pixels changed")
    rows = [frame for frame in plan["frames"] if frame not in {0, 1055}]
    labels = {360: "EXTERIOR", 528: "LIVING", 660: "KITCHEN", 840: "BEDROOM", 880: "BATH", 984: "DUSK"}
    columns = ["baseline", "after"]
    if "global-only" in reports:
        columns.insert(1, "global-only")
    width = 720 if len(columns) == 2 else 640
    height = round(width * 9 / 16)
    canvas = Image.new("RGB", (len(columns) * width, len(rows) * (height + 44)), "#15201c")
    draw = ImageDraw.Draw(canvas)
    pixel_differences = []
    for row, frame in enumerate(rows):
        for column, name in enumerate(columns):
            x, y = column * width, row * (height + 44)
            title = {"baseline": "BEFORE / CURRENT RENDERER", "after": "REALISM REVISION", "global-only": "REVISION / GLOBAL IBL"}[name]
            draw.text((x + 12, y + 10), f"{labels.get(frame, 'FRAME ' + str(frame))} | {title}", fill="white", font=font(20))
            canvas.paste(image(name, frame).resize((width, height), Image.Resampling.LANCZOS), (x, y + 44))
        before = np.asarray(image("baseline", frame), dtype=np.float32)
        after = np.asarray(image("after", frame), dtype=np.float32)
        pixel_differences.append({"frame": frame, "meanAbsoluteEncodedChannelDifference": float(np.abs(after-before).mean()),
                                  "interpretation": "Expected scene/rendering difference; not a realism score or linear HDR measurement."})
    canvas.save(OUT / "before-after.png")
    metadata = read(OUT / "baseline-scene-metadata.json")
    changed_assets = []
    retained_assets = []
    for name, old in metadata["retainedAssets"].items():
        path = ROOT / name
        current_sha = sha(path.read_bytes()) if path.exists() else None
        record = {"path": name, "baselineSHA256": old["sha256"], "currentSHA256": current_sha}
        (retained_assets if current_sha == old["sha256"] else changed_assets).append(record)
    manifests = [{"path": str(p.relative_to(ROOT)), "sha256": sha(p.read_bytes())}
                 for p in sorted((ROOT / "assets").rglob("*.json"))
                 if p.name in {"provenance.json", "manifest.json"}]
    write(OUT / "validation-report.json", {
        "format": "s99-realism-validation-v1", "status": "passed", "sourceSHA256": source_sha,
        "baselineSourceSHA256": metadata["sourceSHA256"], "output": [1920, 1080],
        "stillProfile": "cinematic", "fullVideoExported": False,
        "baselineMeaning": plan["baselineMeaning"], "openingPlan": opening,
        "preservation": preservation, "captures": captures, "reviews": reports,
        "pixelDifferences": pixel_differences, "assetManifests": manifests,
        "retainedAssets": retained_assets, "changedAssets": changed_assets,
        "baselineAssetArchive": metadata["assetArchive"],
        "figures": ["before-after.png"],
        "scope": "Sampled source-bound stills; no automatic photorealism rating and no full-motion temporal certification.",
        "performanceInterpretation": "Any included submission timings are CPU/queue/submission observations, not certified playback FPS or complete 3D GPU time."})
    print(f"PASS: {len(captures)} source-bound stills; opening plan identical; before/after and evidence report assembled.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", type=Path)
    parser.add_argument("--renderer", default="review_harness", help="Existing compiled lighting_review.rs executable; never invoked here")
    parser.add_argument("--frames", default=",".join(map(str, DEFAULT_FRAMES)))
    parser.add_argument("--ablation", action="store_true", help="Also prepare current source without BakedLighting")
    args = parser.parse_args()
    if args.prepare:
        frames = [int(v) for v in args.frames.split(",")]
        if (len(frames) != len(set(frames)) or 0 not in frames
                or not any(frame not in {0, 1055} for frame in frames)):
            raise ValueError("Use unique frames including opening frame 0 and at least one scene frame")
        prepare(args.prepare, args.renderer, frames, args.ablation)
    else:
        assemble()


if __name__ == "__main__":
    main()
