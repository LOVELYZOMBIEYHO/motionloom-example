#!/usr/bin/env python3
"""Compose frozen analysis reports into a MotionLoom multiview request."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("analysis_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    frames = {"front": 0, "right": 48, "back": 96, "left": 144}
    request = {
        "schemaVersion": "1.0",
        "targetAssetId": "s94_head_mesh",
        "targetModelId": "s94_head_model",
        "references": [
            {
                "id": view,
                "frame": frame,
                "analysis": json.loads(
                    (args.analysis_root / view / "analysis.json").read_text()
                ),
            }
            for view, frame in frames.items()
        ],
        "options": {
            "cameraPolicy": "frozen",
            "allowBoundary": False,
            "allowMultipleComponents": False,
            "maxVertexResiduals": 512,
            "metricWeights": {
                "silhouette": 0.25,
                "boundary": 0.20,
                "landmarks": 0.25,
                "features": 0.20,
                "depth": 0.10,
            },
            "qualityGates": {
                "minimumMaskIou": 0.90,
                "maximumP95EdgeDistancePx": 40.0,
                "maximumLandmarkMeanDistancePx": 12.0,
                "maximumFeatureMeanDistancePx": 12.0,
                "maximumDepthViolations": 0,
            },
        },
    }
    args.output.write_text(json.dumps(request, indent=2) + "\n")


if __name__ == "__main__":
    main()
