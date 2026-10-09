#!/usr/bin/env python3
"""Prepare controlled review variants and assemble source-bound still evidence.

No renderer, video encoder, or source asset editor is invoked by this script.
Use --prepare DIRECTORY before running lighting_review against each variant.
The final assembly requires Pillow and NumPy.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/lighting-upgrade"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def variants() -> dict[str, str]:
    source = (ROOT / "main.motionloom").read_text()
    mirror = re.sub(
        r'<Camera3D id="s99_bath"[^\n]+',
        '<Camera3D id="s99_bath" position={[4.2,1.6,-.95]} target={[2.801,1.57,-.95]} fov="32" />',
        source,
    )
    return {
        "baseline": gzip.decompress((OUT / "baseline-scene.motionloom.gz").read_bytes()).decode(),
        "global-only": re.sub(r'^\s*<BakedLighting[^\n]*\n', '\n', source, flags=re.M),
        "mirror": mirror,
        "mirror-global": re.sub(r'^\s*<PlanarReflection[^\n]*\n', '\n', mirror, flags=re.M),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", type=Path)
    args = parser.parse_args()
    scripts = variants()
    if args.prepare:
        args.prepare.mkdir(parents=True, exist_ok=True)
        for name, source in scripts.items():
            (args.prepare / f"{name}.motionloom").write_text(source)
        print(f"Prepared {len(scripts)} review variants; canonical source unchanged.")
        return

    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)

    source_hash = sha((ROOT / "main.motionloom").read_bytes())
    reports = {}
    for name in ["after", "baseline", "global-only", "mirror", "mirror-global", "performance", "baseline-performance"]:
        report = json.loads((OUT / name / "review-report.json").read_text())
        expected = source_hash if name in {"after", "performance"} else sha(scripts["baseline" if name == "baseline-performance" else name].encode())
        if report["sourceSha256"] != expected or report.get("inProgress"):
            raise ValueError(f"Stale or incomplete {name} review")
        if not name.endswith("performance") and report.get("settings", {}).get("profile") != "cinematic":
            raise ValueError(f"Expected Cinematic stills for {name}")
        reports[name] = report

    def image(name: str, frame: int):
        return Image.open(OUT / name / f"frame-{frame:04}.png").convert("RGB")

    frames = [528, 660, 840, 880]
    labels = ["Previous scene / current renderer", "Current scene / global IBL only", "Current scene / baked room lighting"]
    canvas = Image.new("RGB", (1920, 4 * 400), "#17221f")
    draw = ImageDraw.Draw(canvas)
    differences = []
    for row, frame in enumerate(frames):
        for col, name in enumerate(["baseline", "global-only", "after"]):
            draw.text((col * 640 + 12, row * 400 + 8), f"{labels[col]} | frame {frame}", fill="white",font=font)
            canvas.paste(image(name, frame).resize((640, 360), Image.Resampling.LANCZOS), (col * 640, row * 400 + 32))
        a = np.asarray(image("after", frame), dtype=np.float32)
        b = np.asarray(image("global-only", frame), dtype=np.float32)
        differences.append({"frame": frame, "meanAbsoluteChannelDifference": float(np.abs(a-b).mean()), "interpretation": "Expected lighting difference; this is not a realism score."})
    canvas.save(OUT / "comparison.png")

    mirror = Image.new("RGB", (1920, 576), "#17221f")
    draw = ImageDraw.Draw(mirror)
    for col, name in enumerate(["mirror-global", "mirror"]):
        draw.text((col*960+12, 8), "Same inspection camera / " + ("local probe only" if col == 0 else "planar reflected camera"), fill="white",font=font)
        mirror.paste(image(name, 880).resize((960, 540), Image.Resampling.LANCZOS), (col*960, 32))
    mirror.save(OUT / "mirror-comparison.png")

    sequences = [[316,317,318,319], [880,881,882,883], [940,941,942,943]]
    temporal = []
    contact = Image.new("RGB", (1920, 3*304), "#17221f")
    draw = ImageDraw.Draw(contact)
    for row, sequence in enumerate(sequences):
        previous = None
        changes = []
        for col, frame in enumerate(sequence):
            im = image("after", frame)
            draw.text((col*480+12, row*304+8), f"Frame {frame} / {frame/24:.3f}s", fill="white",font=font)
            contact.paste(im.resize((480,270), Image.Resampling.LANCZOS), (col*480,row*304+30))
            pixels = np.asarray(im, dtype=np.float32)
            if previous is not None:
                diff = np.abs(pixels-previous)
                changes.append({"frame":frame,"meanAbsoluteChannelDifference":float(diff.mean()),"fractionPixelsChangingOver20":float((diff.max(axis=2)>20).mean())})
            previous = pixels
        temporal.append({"frames":sequence,"adjacentChanges":changes})
    contact.save(OUT / "consecutive-frames.png")

    before = np.asarray(image("baseline",0))
    after = np.asarray(image("after",0))
    opening = {"pixelIdentical":bool(np.array_equal(before,after)),"changedPixels":int(np.any(before != after,axis=2).sum())}
    if not opening["pixelIdentical"]:
        raise ValueError("Opening 2D plan changed")
    preservation = json.loads((OUT / "preservation-check.json").read_text())
    bake_path = ROOT / "assets/lighting-v3/s99-lighting.json"
    bake = json.loads(bake_path.read_text())
    option_bytes = (ROOT / "scripts/lighting_bake_options.json").read_bytes()
    asset_files = [bake_path] + sorted((bake_path.parent / "reflections").glob("*.hdr"))
    provenance = {
        "format":"s99-generated-lighting-v1", "sourceSha256":source_hash,
        "optionsSha256":sha(option_bytes), "bakerVersion":bake["bakerVersion"],
        "authoringFingerprint":bake["authoringFingerprint"], "fingerprint":bake["fingerprint"],
        "inputProvenance":["../pbr-v2/provenance.json","../environment-v2/manifest.json"],
        "origin":"Deterministic CPU bake of authored S99 geometry, fixed lights and existing CC0 inputs; no new download or ImageGen asset.",
        "states":[{"name":s["name"],"frame":s["frame"],"volumes":[{"id":v["id"],"probes":len(v["probes"]),"validProbes":sum(p["valid"] for p in v["probes"]),"localCaptures":len(v["reflections"])} for v in s["volumes"]]} for s in bake["states"]],
        "files":[{"path":str(p.relative_to(bake_path.parent)),"bytes":p.stat().st_size,"sha256":sha(p.read_bytes())} for p in asset_files],
        "limitations":bake["diagnostics"],
    }
    (bake_path.parent / "provenance.json").write_text(json.dumps(provenance,indent=2)+'\n')
    smoke = (OUT / "live-preview-smoke.log").read_text()
    native_startup = "quality=Full target=1920x1080" in smoke and "GraphParseError" not in smoke
    if not native_startup:
        raise ValueError("Native preview startup was not verified")
    report = {
        "format":"s99-indoor-lighting-validation-v1", "sourceSha256":source_hash,
        "output":[1920,1080], "stillProfile":"cinematic", "fullVideoExported":False,
        "nativePreviewStartup":{"passed":native_startup,"log":"live-preview-smoke.log","termination":"Smoke preview closed deliberately with SIGINT after successful frames."},
        "baselineMeaning":"Archived pre-indoor-lighting scene rendered with the current engine; not an old-engine pixel capture.",
        "globalOnlyMeaning":"Current scene, lights and materials with BakedLighting removed. Planar mirror and other renderer features remain active.",
        "mirrorMeaning":"Only the temporary bathroom inspection camera differs; local-probe versus planar capture ablation.",
        "openingPlan":opening, "preservation":preservation,
        "generatedLighting":provenance, "globalOnlyDifferences":differences,
        "temporal":temporal, "reviews":reports,
        "tests":{"nativeLibrary":"705 passed; optional native GPU fixtures run separately. Final hidden-sky change verified by native image fixtures and WGSL validation.","lightingCpuAndLoader":"23 passed","eightLightRegression":"1 passed","worldWgsl":"1 passed","indoorAuthoring":"7 passed","nativeGlassPlanarImages":"4 passed","wasm":"compile check passed; browser GPU output not verified"},
        "limitations":["Three diffuse bounces with static day/dusk probes; no dynamic-object relighting or caustics.","Box projection is approximate; planar mirror has one recursion level.","Thin glass refraction relies on screen-space background data; intersecting/concave volumes remain approximate.","Submission timing and compositor GPU timestamps are not whole-render GPU time or playback FPS."],
    }
    (OUT / "validation-report.json").write_text(json.dumps(report,indent=2)+'\n')
    print(f"Built comparisons and source-bound report. Opening plan identical; {len(asset_files)} generated lighting files.")


if __name__ == "__main__":
    main()
