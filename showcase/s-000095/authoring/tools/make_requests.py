"""Build the final analyzeImageReference requests with bound feature hints.

Feature bindings point at real shark-cage vertices/edges/chains so that every
evaluated semantic feature carries an internal residual rather than a
nearestContour fallback. Reference pixel positions were verified visually with
tools/annotate_features.py.
"""

import json

COLUMNS = 12


def vertex(ring, column):
    return ring * COLUMNS + column


SNOUT_POLE = 252
TAIL_POLE = 253


VIEWS = {
    "left": {
        "image": "source/left-padded.png",
        "size": [819, 455],
        "foregroundPoints": [[400, 220], [150, 230], [700, 215]],
        "backgroundPoints": [[6, 6], [812, 6], [6, 448], [812, 448]],
        "threshold": 30,
        "features": [
            ("snout_tip", "point", [[9, 224]], {"type": "vertex", "vertex": SNOUT_POLE}, 0.95, 8),
            ("eye_center", "point", [[79, 213]],
             {"type": "edge", "vertices": [vertex(2, 3), vertex(3, 3)], "t": 0.55}, 0.85, 6),
            ("mouth_line", "polyline", [[28, 250], [60, 262], [95, 274]],
             {"type": "vertexChain", "vertices": [vertex(1, 5), vertex(2, 5), vertex(3, 5), vertex(4, 5)],
              "closed": False}, 0.80, 6),
            ("gill_lines", "polyline", [[178, 232], [190, 236], [202, 240], [214, 242], [226, 244]],
             {"type": "vertexChain", "vertices": [vertex(5, 3), vertex(6, 3)],
              "closed": False}, 0.70, 6),
            ("dorsal_fin_tip", "point", [[414, 64]], {"type": "vertex", "vertex": vertex(11, 0)}, 0.92, 8),
            ("dorsal_fin_contour", "polyline", [[388, 116], [414, 64], [444, 122]],
             {"type": "vertexChain",
              "vertices": [vertex(10, 0), vertex(11, 0), vertex(12, 0)],
              "closed": False}, 0.85, 8),
            ("pectoral_fin_tip", "point", [[365, 393]], {"type": "vertex", "vertex": vertex(9, 3)}, 0.90, 8),
            ("pectoral_fin_contour", "polyline", [[265, 280], [365, 393], [420, 318]],
             {"type": "vertexChain",
              "vertices": [vertex(7, 3), vertex(8, 3), vertex(9, 3), vertex(10, 3)],
              "closed": False}, 0.80, 8),
            ("tail_upper_tip", "point", [[807, 90]], {"type": "vertex", "vertex": vertex(19, 0)}, 0.88, 8),
            ("tail_lower_tip", "point", [[784, 337]], {"type": "vertex", "vertex": vertex(19, 6)}, 0.85, 8),
            ("caudal_peduncle", "point", [[695, 205]],
             {"type": "edge", "vertices": [vertex(16, 3), vertex(17, 3)], "t": 0.5}, 0.75, 6),
            ("belly_apex", "point", [[430, 311]], {"type": "vertex", "vertex": vertex(9, 6)}, 0.85, 8),
            ("body_centerline", "polyline", [[90, 233], [215, 234], [340, 232], [465, 231], [590, 231], [690, 230]],
             {"type": "vertexChain",
              "vertices": [vertex(3, 3), vertex(6, 3), vertex(9, 3), vertex(12, 3), vertex(15, 3), vertex(17, 3)],
              "closed": False}, 0.80, 8),
        ],
        "depth": [
            {"relation": "inFrontOf", "subject": "pectoral_fin_tip", "object": "belly_apex",
             "evidence": "leftProfileOcclusion", "value": None, "confidence": 0.60},
        ],
    },
    "front": {
        "image": "source/front-padded.png",
        "size": [742, 412],
        "foregroundPoints": [[370, 210], [260, 160], [480, 260]],
        "backgroundPoints": [[6, 6], [735, 6], [6, 405], [735, 405]],
        "threshold": 30,
        "features": [
            ("snout_tip", "point", [[368, 196]], {"type": "vertex", "vertex": SNOUT_POLE}, 0.90, 8),
            ("mouth_line", "polyline", [[268, 296], [310, 310], [360, 316], [412, 310], [452, 296]],
             {"type": "vertexChain",
              "vertices": [vertex(3, 4), vertex(3, 5), vertex(3, 6), vertex(3, 7), vertex(3, 8)],
              "closed": False}, 0.80, 6),
            ("eye_left", "point", [[297, 205]], {"type": "vertex", "vertex": vertex(4, 3)}, 0.45, 12),
            ("eye_right", "point", [[383, 200]], {"type": "vertex", "vertex": vertex(4, 9)}, 0.45, 12),
            ("dorsal_fin_tip", "point", [[372, 10]], {"type": "vertex", "vertex": vertex(11, 0)}, 0.85, 8),
            ("pectoral_tip_left", "point", [[630, 397]], {"type": "vertex", "vertex": vertex(9, 3)}, 0.85, 8),
            ("pectoral_tip_right", "point", [[111, 400]], {"type": "vertex", "vertex": vertex(9, 9)}, 0.85, 8),
            ("belly_apex", "point", [[373, 395]], {"type": "vertex", "vertex": vertex(9, 6)}, 0.80, 8),
        ],
        "depth": [
            {"relation": "inFrontOf", "subject": "snout_tip", "object": "dorsal_fin_tip",
             "evidence": "frontViewOcclusion", "value": None, "confidence": 0.65},
        ],
    },
    "top": {
        "image": "source/top-padded.png",
        "size": [772, 429],
        "foregroundPoints": [[350, 215], [180, 225], [600, 200]],
        "backgroundPoints": [[6, 6], [765, 6], [6, 422], [765, 422]],
        "threshold": 30,
        "features": [
            ("snout_tip", "point", [[45, 204]], {"type": "vertex", "vertex": SNOUT_POLE}, 0.90, 8),
            ("dorsal_fin_tip", "point", [[355, 8]], {"type": "vertex", "vertex": vertex(11, 0)}, 0.80, 8),
            ("dorsal_fin_contour", "polyline", [[331, 54], [355, 8], [379, 58]],
             {"type": "vertexChain",
              "vertices": [vertex(10, 0), vertex(11, 0), vertex(12, 0), vertex(13, 0)],
              "closed": False}, 0.75, 8),
            ("pectoral_tip_left", "point", [[340, 420]], {"type": "vertex", "vertex": vertex(9, 3)}, 0.80, 8),
            ("tail_upper_tip", "point", [[716, 129]], {"type": "vertex", "vertex": vertex(19, 0)}, 0.70, 8),
            ("tail_lower_tip", "point", [[719, 300]], {"type": "vertex", "vertex": vertex(19, 6)}, 0.70, 8),
            ("body_centerline", "polyline", [[120, 216], [300, 215], [480, 213], [620, 212]],
             {"type": "vertexChain",
              "vertices": [vertex(3, 0), vertex(8, 0), vertex(13, 0), vertex(17, 0)],
              "closed": False}, 0.75, 8),
        ],
        "depth": [
            {"relation": "inFrontOf", "subject": "dorsal_fin_tip", "object": "body_centerline",
             "evidence": "topViewFinProtrusion", "value": None, "confidence": 0.70},
        ],
    },
    "bottom": {
        "image": "source/bottom-padded.png",
        "size": [772, 429],
        "foregroundPoints": [[350, 215], [180, 225], [600, 200]],
        "backgroundPoints": [[6, 6], [765, 6], [6, 422], [765, 422]],
        "threshold": 12,
        "suppliedMask": "authoring/bottom-supplied-mask.json",
        "features": [
            ("mouth_line", "polyline", [[62, 232], [100, 240], [140, 248], [180, 252]],
             {"type": "vertexChain",
              "vertices": [vertex(3, 4), vertex(3, 5), vertex(3, 6), vertex(3, 7), vertex(3, 8)],
              "closed": False}, 0.80, 6),
            ("pectoral_tip_left", "point", [[340, 10]], {"type": "vertex", "vertex": vertex(9, 3)}, 0.75, 8),
            ("pectoral_tip_right", "point", [[340, 420]], {"type": "vertex", "vertex": vertex(9, 9)}, 0.75, 8),
            ("belly_apex", "point", [[430, 269]], {"type": "vertex", "vertex": vertex(9, 6)}, 0.80, 8),
            ("gill_lines", "polyline", [[150, 190], [150, 240]],
             {"type": "vertexChain", "vertices": [vertex(4, 3), vertex(5, 3), vertex(6, 3)],
              "closed": False}, 0.55, 8),
            ("tail_upper_tip", "point", [[716, 105]], {"type": "vertex", "vertex": vertex(19, 0)}, 0.65, 8),
            ("tail_lower_tip", "point", [[740, 315]], {"type": "vertex", "vertex": vertex(19, 6)}, 0.65, 8),
            ("body_centerline", "polyline", [[120, 215], [300, 213], [480, 212], [620, 210]],
             {"type": "vertexChain",
              "vertices": [vertex(6, 6), vertex(10, 6), vertex(14, 6)],
              "closed": False}, 0.75, 8),
        ],
        "depth": [
            {"relation": "inFrontOf", "subject": "body_centerline", "object": "dorsal_fin_tip",
             "evidence": "bottomViewDorsalOccluded", "value": None, "confidence": 0.60},
        ],
    },
}

for view, spec in VIEWS.items():
    segmentation = {
        "mode": "guided",
        "analysisRegion": [0, 0, spec["size"][0], spec["size"][1]],
        "foregroundPoints": spec["foregroundPoints"],
        "backgroundPoints": spec["backgroundPoints"],
        "backgroundColor": None,
        "threshold": spec["threshold"],
        "suppliedMask": None,
        "minComponentPixels": 512,
        "maxContourPoints": 512,
    }
    if spec.get("suppliedMask"):
        segmentation["mode"] = "mask"
        segmentation["suppliedMask"] = json.load(open(spec["suppliedMask"]))
    features = [
        {
            "id": name,
            "kind": kind,
            "points": points,
            "semanticLabel": name,
            "binding": binding,
            "confidence": confidence,
            "snapRadius": snap,
        }
        for (name, kind, points, binding, confidence, snap) in spec["features"]
    ]
    request = {
        "schemaVersion": "1.0",
        "imageId": f"s95-shark-{view}-01",
        "view": view,
        "segmentation": segmentation,
        "requestedLandmarks": ["topmost", "bottommost", "leftmost", "rightmost"],
        "featureHints": features,
        "depthHints": spec["depth"],
    }
    path = f"authoring/{view}-request.json"
    json.dump(request, open(path, "w"), indent=1)
    print("wrote", path, "features", len(features), "depthHints", len(spec["depth"]))
