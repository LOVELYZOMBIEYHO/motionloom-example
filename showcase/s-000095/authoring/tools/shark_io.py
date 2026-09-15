"""Shared parsing and geometry helpers for the S95 shark MeshAsset fit.

Pure-Python (no numpy) so it runs with the system interpreter.
"""

import json
import math
import re
import sys

VERTEX_RE = re.compile(
    r'<Vertex\s+position=\{(\[([^\]]*)\])\}\s+uv=\{(\[[^\]]*\])\}\s*/>'
)
FACE_RE = re.compile(r'<Face\s+indices=\{(\[([^\]]*)\]\s*)\}\s*/>')


def parse_mesh(path):
    source = open(path, "r", encoding="utf-8").read()
    start = source.index('<MeshAsset id="s95_shark_mesh"')
    end = source.index("</MeshAsset>", start)
    block = source[start:end]
    positions = []
    uvs = []
    for match in VERTEX_RE.finditer(block):
        values = [float(v) for v in match.group(2).split(",")]
        if len(values) != 3:
            raise ValueError("bad vertex " + match.group(0))
        positions.append(values)
        uv = [float(v) for v in match.group(3).strip("[]").split(",")]
        uvs.append(uv)
    faces = []
    for match in FACE_RE.finditer(block):
        values = [int(v) for v in match.group(2).split(",")]
        faces.append(values)
    return {"source": source, "positions": positions, "uvs": uvs, "faces": faces}


def extent(positions):
    lo = [min(p[i] for p in positions) for i in range(3)]
    hi = [max(p[i] for p in positions) for i in range(3)]
    return lo, hi, max(hi[i] - lo[i] for i in range(3))


def decode_mask(mask):
    width = mask["width"]
    height = mask["height"]
    pixels = bytearray(width * height)
    value = 1 if mask["startsForeground"] else 0
    index = 0
    for run in mask["runs"]:
        if value:
            for offset in range(run):
                pixels[index + offset] = 1
            value = 0
        else:
            value = 1
        index += run
    assert index == width * height, (index, width * height)
    return pixels


def mask_boundary(pixels, width, height):
    points = []
    for y in range(height):
        row = y * width
        for x in range(width):
            if not pixels[row + x]:
                continue
            if (
                x == 0
                or y == 0
                or x + 1 == width
                or y + 1 == height
                or not pixels[row + x - 1]
                or not pixels[row + x + 1]
                or not pixels[row - width + x]
                or not pixels[row + width + x]
            ):
                points.append((x + 0.5, y + 0.5))
    return points


def nearest(point, candidates):
    best = None
    best_d = float("inf")
    px, py = point
    for cx, cy in candidates:
        dx = px - cx
        dy = py - cy
        d = dx * dx + dy * dy
        if d < best_d:
            best_d = d
            best = (cx, cy)
    return best, math.sqrt(best_d)


def rasterize_triangle(pixels, depth, width, height, a, b, c):
    minx = max(0, int(math.floor(min(a[0], b[0], c[0]))))
    maxx = min(width - 1, int(math.ceil(max(a[0], b[0], c[0]))))
    miny = max(0, int(math.floor(min(a[1], b[1], c[1]))))
    maxy = min(height - 1, int(math.ceil(max(a[1], b[1], c[1]))))
    area = (c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])
    if abs(area) < 1e-8:
        return
    for y in range(miny, maxy + 1):
        for x in range(minx, maxx + 1):
            px = x + 0.5
            py = y + 0.5
            wa = ((px - b[0]) * (c[1] - b[1]) - (py - b[1]) * (c[0] - b[0])) / area
            wb = ((px - c[0]) * (a[1] - c[1]) - (py - c[1]) * (a[0] - c[0])) / area
            wc = 1.0 - wa - wb
            if wa >= -1e-5 and wb >= -1e-5 and wc >= -1e-5:
                z = wa * a[2] + wb * b[2] + wc * c[2]
                index = y * width + x
                if z < depth[index]:
                    depth[index] = z
                    pixels[index] = 1


def solve_linear(matrix, rhs):
    n = len(rhs)
    aug = [list(matrix[i]) + [rhs[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("singular system")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        for j in range(col, n + 1):
            aug[col][j] /= scale
        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            if factor == 0.0:
                continue
            for j in range(col, n + 1):
                aug[r][j] -= factor * aug[col][j]
    return [aug[i][n] for i in range(n)]


def solve_least_squares(rows, rhs, ridge=0.0):
    """Minimum-norm-ish solution of A x = b via normal equations."""
    n = len(rows[0])
    ata = [[0.0] * n for _ in range(n)]
    atb = [0.0] * n
    for row, value in zip(rows, rhs):
        for i in range(n):
            atb[i] += row[i] * value
            for j in range(n):
                ata[i][j] += row[i] * row[j]
    if ridge:
        for i in range(n):
            ata[i][i] += ridge
    return solve_linear(ata, atb)


def resect_camera(correspondences):
    """DLT camera resectioning with p34 = 1.

    correspondences: list of ((X, Y, Z), (u, v)).
    Returns a 3x4 matrix (list of rows).
    """
    rows = []
    rhs = []
    for (X, Y, Z), (u, v) in correspondences:
        rows.append([X, Y, Z, 1, 0, 0, 0, 0, -u * X, -u * Y, -u * Z])
        rhs.append(u)
        rows.append([0, 0, 0, 0, X, Y, Z, 1, -v * X, -v * Y, -v * Z])
        rhs.append(v)
    solution = solve_least_squares(rows, rhs)
    return [
        solution[0:4] + [1.0],
        solution[4:8] + [1.0],
        [solution[8], solution[9], solution[10], 1.0],
    ]


def project(matrix, position):
    X, Y, Z = position
    value = [
        matrix[r][0] * X + matrix[r][1] * Y + matrix[r][2] * Z + matrix[r][3]
        for r in range(3)
    ]
    return (value[0] / value[2], value[1] / value[2])


def projection_jacobian(matrix, position):
    X, Y, Z = position
    value = [
        matrix[r][0] * X + matrix[r][1] * Y + matrix[r][2] * Z + matrix[r][3]
        for r in range(3)
    ]
    w = value[2]
    rows = []
    for image_axis in range(2):
        row = []
        for axis in range(3):
            num = matrix[image_axis][axis]
            derivative = (num * w - value[image_axis] * matrix[2][axis]) / (w * w)
            row.append(derivative)
        rows.append(row)
    return rows


def load_eval(path):
    return json.load(open(path, "r", encoding="utf-8"))


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: mesh_io.py MESH.motionloom")
    mesh = parse_mesh(sys.argv[1])
    lo, hi, ext = extent(mesh["positions"])
    print("vertices", len(mesh["positions"]), "faces", len(mesh["faces"]))
    print("bounds", lo, hi, "extent", ext)


if __name__ == "__main__":
    main()
