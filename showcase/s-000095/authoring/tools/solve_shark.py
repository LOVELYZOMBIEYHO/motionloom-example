"""Plan bounded shark MeshAsset proposals from the frozen multiview evaluation.

Resects one camera per view from the reported vertex correspondences, solves a
small 3D movement per mirrored vertex pair from the views that actually see the
vertex on the candidate silhouette, and writes a six-fingerprint proposal.
"""

import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shark_io import (
    decode_mask,
    mask_boundary,
    nearest,
    parse_mesh,
    project,
    projection_jacobian,
    resect_camera,
    solve_least_squares,
)

SILHOUETTE_PX = 3.5
MAX_REF_DISTANCE_PX = 90.0
COLUMNS = 12
RING_COUNT = 21


def mirror_index(vertex):
    if vertex >= RING_COUNT * COLUMNS:
        return vertex
    ring, column = divmod(vertex, COLUMNS)
    return ring * COLUMNS + (COLUMNS - column) % COLUMNS


def mirror_delta(delta):
    return [delta[0], delta[1], -delta[2]]


def parse_vertex_spec(spec):
    vertices = set()
    for chunk in spec.split(","):
        rings, cols = chunk.split(":")
        for ring in parse_range(rings):
            for col in parse_range(cols):
                vertices.add((ring % RING_COUNT) * COLUMNS + (col % COLUMNS))
    return sorted(vertices)


def parse_range(text):
    if "-" in text:
        start, end = text.split("-")
        return list(range(int(start), int(end) + 1))
    return [int(text)]


def load_context(mesh_path, evaluation_path):
    mesh = parse_mesh(mesh_path)
    evaluation = json.load(open(evaluation_path))
    contexts = {}
    for view in evaluation["views"]:
        analysis = json.load(
            open(f"analysis/ref-{view['id']}/analysis.json")
        )
        width, height = analysis["imageSize"]
        reference_mask = decode_mask(analysis["foregroundMask"])
        reference_boundary = mask_boundary(reference_mask, width, height)
        candidate_mask = decode_mask(view["candidateMask"])
        candidate_boundary = mask_boundary(candidate_mask, width, height)
        correspondences = [
            (mesh["positions"][row["vertex"]], tuple(row["screenPoint"]))
            for row in view["vertexResiduals"]
        ]
        camera = resect_camera(correspondences)
        errors = [
            math.dist(project(camera, position), screen)
            for position, screen in correspondences
        ]
        rms = math.sqrt(sum(value * value for value in errors) / max(1, len(errors)))
        rows = {}
        for row in view["vertexResiduals"]:
            screen = row["screenPoint"]
            _, candidate_distance = nearest(screen, candidate_boundary)
            _, reference_distance = nearest(screen, reference_boundary)
            target, _ = nearest(screen, reference_boundary)
            rows[row["vertex"]] = {
                "screen": screen,
                "cand": candidate_distance,
                "ref": reference_distance,
                "delta": [target[0] - screen[0], target[1] - screen[1]],
            }
        contexts[view["id"]] = {
            "camera": camera,
            "rms": rms,
            "rows": rows,
            "size": [width, height],
        }
    return mesh, evaluation, contexts


def build_constraints(vertex, contexts, views_filter, damp, max_px):
    rows = []
    rhs = []
    evidence = []
    for view_id, context in contexts.items():
        if views_filter and view_id not in views_filter:
            continue
        row = context["rows"].get(vertex)
        if row is None:
            continue
        if row["cand"] > SILHOUETTE_PX:
            continue
        if row["ref"] > MAX_REF_DISTANCE_PX:
            continue
        delta = [row["delta"][0] * damp, row["delta"][1] * damp]
        magnitude = math.hypot(*delta)
        if magnitude > max_px:
            scale = max_px / magnitude
            delta = [delta[0] * scale, delta[1] * scale]
        rows.extend(projection_jacobian(context["camera"], POSITIONS[vertex]))
        rhs.extend(delta)
        evidence.append(view_id)
    return rows, rhs, evidence


POSITIONS = []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh", default="source/shark-accepted.motionloom")
    parser.add_argument("--eval", default="fit/baseline/evaluation.json")
    parser.add_argument("--verts", required=True, help="e.g. '7-9:2-4'")
    parser.add_argument("--damp", type=float, default=0.7)
    parser.add_argument("--max-px", type=float, default=26.0)
    parser.add_argument("--max-local", type=float, default=0.075)
    parser.add_argument("--views", default="")
    parser.add_argument("--free", default="xyz")
    parser.add_argument("--cand-tolerance", type=float, default=SILHOUETTE_PX)
    parser.add_argument("--symmetric", action="store_true", default=True)
    parser.add_argument(
        "--spread",
        type=float,
        default=0.0,
        help="fraction of a solved column delta copied to adjacent columns",
    )
    parser.add_argument(
        "--smooth-rings",
        action="store_true",
        help="blend each solved ring's deltas and emit the whole ring",
    )
    parser.add_argument("--out", default="proposals/dry-run.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--reason", required=True)
    arguments = parser.parse_args()

    global POSITIONS
    mesh, evaluation, contexts = load_context(arguments.mesh, arguments.eval)
    POSITIONS = mesh["positions"]
    for view_id, context in contexts.items():
        print(f"camera {view_id}: rms={context['rms']:.3f}px rows={len(context['rows'])}")
    free_axes = [axis for axis in range(3) if "xyz"[axis] in arguments.free]
    views_filter = [name for name in arguments.views.split(",") if name]

    selected = parse_vertex_spec(arguments.verts)
    primary = sorted({min(vertex, mirror_index(vertex)) for vertex in selected})
    scale = 300.0
    ridge = (0.12 * scale) ** 2
    changes = []
    skipped = []
    for vertex in primary:
        partner = mirror_index(vertex)
        rows, rhs, evidence = build_constraints(
            vertex, contexts, views_filter, arguments.damp, arguments.max_px
        )
        views = sorted(set(evidence))
        if partner != vertex:
            partner_rows, partner_rhs, partner_evidence = build_constraints(
                partner, contexts, views_filter, arguments.damp, arguments.max_px
            )
            for row in partner_rows:
                row[2] = -row[2]
            rows = rows + partner_rows
            rhs = rhs + partner_rhs
            views = sorted(set(views) | set(partner_evidence))
        if not rows:
            skipped.append(vertex)
            continue
        reduced_rows = [[row[axis] for axis in free_axes] for row in rows]
        reduced = solve_least_squares(reduced_rows, rhs, ridge=ridge)
        delta = [0.0, 0.0, 0.0]
        for index, axis in enumerate(free_axes):
            delta[axis] = reduced[index]
        magnitude = math.sqrt(sum(value * value for value in delta))
        if magnitude > arguments.max_local:
            factor = arguments.max_local / magnitude
            delta = [value * factor for value in delta]
        if magnitude < 0.0012:
            skipped.append(vertex)
            continue
        before = POSITIONS[vertex]
        after = [round(before[i] + delta[i], 7) for i in range(3)]
        confidence = 0.9 if len(views) >= 2 else 0.7
        changes.append(
            {
                "vertex": vertex,
                "before": before,
                "after": after,
                "confidence": confidence,
                "evidenceViews": views,
            }
        )
        if partner != vertex:
            partner_before = POSITIONS[partner]
            partner_delta = mirror_delta(delta)
            partner_after = [
                round(partner_before[i] + partner_delta[i], 7) for i in range(3)
            ]
            changes.append(
                {
                    "vertex": partner,
                    "before": partner_before,
                    "after": partner_after,
                    "confidence": confidence,
                    "evidenceViews": views,
                }
            )

    if arguments.smooth_rings and changes:
        # Blend deltas around every solved ring and emit all twelve columns, so
        # the ring cannot develop a local spike that fails edge-stretch checks.
        by_ring = {}
        for change in changes:
            vertex = change["vertex"]
            if vertex >= RING_COUNT * COLUMNS:
                continue
            ring, column = divmod(vertex, COLUMNS)
            delta = [change["after"][i] - change["before"][i] for i in range(3)]
            by_ring.setdefault(ring, {})[column] = delta
        blended = {}
        for ring, columns in by_ring.items():
            for column in range(COLUMNS):
                base = columns.get(column, [0.0, 0.0, 0.0])
                left = columns.get((column - 1) % COLUMNS, [0.0, 0.0, 0.0])
                right = columns.get((column + 1) % COLUMNS, [0.0, 0.0, 0.0])
                blended[ring * COLUMNS + column] = [
                    0.5 * base[i] + 0.25 * left[i] + 0.25 * right[i] for i in range(3)
                ]
        for offset in range(2):
            smoothed = dict(blended)
            for ring, columns in by_ring.items():
                for column in range(COLUMNS):
                    index = ring * COLUMNS + column
                    left = blended[ring * COLUMNS + (column - 1) % COLUMNS]
                    right = blended[ring * COLUMNS + (column + 1) % COLUMNS]
                    smoothed[index] = [
                        0.6 * blended[index][i] + 0.2 * left[i] + 0.2 * right[i]
                        for i in range(3)
                    ]
            blended = smoothed
        vertex_to_change = {change["vertex"]: change for change in changes}
        for vertex, delta in blended.items():
            magnitude = math.sqrt(sum(value * value for value in delta))
            if magnitude < 0.0008:
                continue
            if magnitude > arguments.max_local:
                factor = arguments.max_local / magnitude
                delta = [value * factor for value in delta]
            # Mirror partner shares the blended movement.
            ring, column = divmod(vertex, COLUMNS)
            partner = ring * COLUMNS + (COLUMNS - column) % COLUMNS
            views = vertex_to_change.get(vertex, vertex_to_change.get(partner, {})).get(
                "evidenceViews", []
            )
            for target, values in ((vertex, delta), (partner, [delta[0], delta[1], -delta[2]])):
                if target == partner and partner == vertex:
                    continue
                before = POSITIONS[target]
                change = vertex_to_change.get(target)
                if change is None:
                    change = {
                        "vertex": target,
                        "before": before,
                        "after": [0.0, 0.0, 0.0],
                        "confidence": 0.7,
                        "evidenceViews": views,
                    }
                    changes.append(change)
                    vertex_to_change[target] = change
                change["after"] = [
                    round(POSITIONS[target][i] + values[i], 7) for i in range(3)
                ]

    if arguments.spread > 0.0 and changes:
        # Keep rings smooth: copy a tapered share of every solved delta to the
        # neighbouring columns so unconstrained vertices follow their ring.
        changed = {change["vertex"]: change for change in changes}
        extra = []
        for change in list(changes):
            vertex = change["vertex"]
            if vertex >= RING_COUNT * COLUMNS:
                continue
            ring, column = divmod(vertex, COLUMNS)
            delta = [change["after"][i] - change["before"][i] for i in range(3)]
            for offset in (1, 2):
                factor = arguments.spread ** offset
                for direction in (-1, 1):
                    neighbour = ring * COLUMNS + (column + direction * offset) % COLUMNS
                    if neighbour in changed:
                        continue
                    before = POSITIONS[neighbour]
                    after = [
                        round(before[i] + delta[i] * factor, 7) for i in range(3)
                    ]
                    entry = {
                        "vertex": neighbour,
                        "before": before,
                        "after": after,
                        "confidence": 0.6,
                        "evidenceViews": change["evidenceViews"],
                    }
                    extra.append(entry)
                    changed[neighbour] = entry
        changes.extend(extra)

    proposal = {
        "schemaVersion": "1.0",
        "sourceFingerprint": evaluation["sourceFingerprint"],
        "topologySignature": evaluation["topologySignature"],
        "cameraFingerprint": evaluation["cameraFingerprint"],
        "referenceSetFingerprint": evaluation["referenceSetFingerprint"],
        "metricProfileFingerprint": evaluation["metricProfileFingerprint"],
        "evaluationFingerprint": evaluation["evaluationFingerprint"],
        "targetAssetId": "s95_shark_mesh",
        "reason": arguments.reason,
        "changes": changes,
        "validation": {
            "allowBoundary": False,
            "allowMultipleComponents": False,
            "maxMoveRelativeToBounds": 0.02,
            "maxChangedVertices": 16,
            "maxEdgeLengthRatio": 1.25,
            "maxLaplacianDeltaRelativeToBounds": 0.04,
        },
    }
    if arguments.dry_run:
        print(
            json.dumps(
                {
                    "dryRun": True,
                    "changes": len(changes),
                    "top": sorted(
                        (
                            {
                                "vertex": c["vertex"],
                                "ring": c["vertex"] // COLUMNS,
                                "col": c["vertex"] % COLUMNS,
                                "delta": [
                                    round(c["after"][i] - c["before"][i], 4)
                                    for i in range(3)
                                ],
                                "mag": round(
                                    math.dist(c["before"], c["after"]), 4
                                ),
                                "views": c["evidenceViews"],
                            }
                            for c in changes
                        ),
                        key=lambda item: -item["mag"],
                    )[:24],
                }
            )
        )
        return
    if len(changes) > 16:
        raise SystemExit(f"proposal has {len(changes)} changes; limit is 16")
    os.makedirs(os.path.dirname(os.path.abspath(arguments.out)), exist_ok=True)
    with open(arguments.out, "w") as handle:
        json.dump(proposal, handle, indent=1)
    print(
        json.dumps(
            {
                "out": arguments.out,
                "changes": len(changes),
                "skipped": len(skipped),
                "maxMove": max(
                    (math.dist(c["before"], c["after"]) for c in changes), default=0.0
                ),
                "viewsUsed": sorted({view for c in changes for view in c["evidenceViews"]}),
            }
        )
    )


if __name__ == "__main__":
    main()
