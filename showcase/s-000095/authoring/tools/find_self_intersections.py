"""Locate self-intersecting triangle pairs in the shark cage."""

import sys

sys.path.insert(0, "tools")
from shark_io import parse_mesh


def sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def cross(a, b):
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def segment_triangle(start, end, triangle):
    direction = sub(end, start)
    edge1 = sub(triangle[1], triangle[0])
    edge2 = sub(triangle[2], triangle[0])
    p = cross(direction, edge2)
    determinant = dot(edge1, p)
    if abs(determinant) < 1e-7:
        return False
    inverse = 1.0 / determinant
    t = sub(start, triangle[0])
    u = dot(t, p) * inverse
    if not (0.0 <= u <= 1.0):
        return False
    q = cross(t, edge1)
    v = dot(direction, q) * inverse
    if v < 0.0 or u + v > 1.0:
        return False
    distance = dot(edge2, q) * inverse
    return 1e-6 <= distance <= 1.0 - 1e-6


def triangle_edges(points):
    return [
        (points[0], points[1]),
        (points[1], points[2]),
        (points[2], points[0]),
    ]


def main():
    mesh = parse_mesh(sys.argv[1] if len(sys.argv) > 1 else "source/shark.motionloom")
    positions = mesh["positions"]
    triangles = []
    for face in mesh["faces"]:
        for index in range(1, len(face) - 1):
            triangles.append((face[0], face[index], face[index + 1]))
    boxes = []
    for triangle in triangles:
        points = [positions[i] for i in triangle]
        minimum = [min(p[axis] for p in points) for axis in range(3)]
        maximum = [max(p[axis] for p in points) for axis in range(3)]
        boxes.append((minimum, maximum))
    hits = []
    for i in range(len(triangles)):
        for j in range(i + 1, len(triangles)):
            a, b = triangles[i], triangles[j]
            if set(a) & set(b):
                continue
            (amin, amax), (bmin, bmax) = boxes[i], boxes[j]
            if not all(amin[k] <= bmax[k] and bmin[k] <= amax[k] for k in range(3)):
                continue
            pa = [positions[index] for index in a]
            pb = [positions[index] for index in b]
            hit = any(
                segment_triangle(start, end, pb)
                for start, end in triangle_edges(pa)
            ) or any(
                segment_triangle(start, end, pa)
                for start, end in triangle_edges(pb)
            )
            if hit:
                hits.append((i, j))
    print("triangles", len(triangles), "self-intersections", len(hits))
    for i, j in hits[:20]:
        def describe(triangle):
            return " ".join(
                f"v{index}(r{index // 12},c{index % 12})" for index in triangle
            )
        print("  ", describe(triangles[i]), "x", describe(triangles[j]))


if __name__ == "__main__":
    main()
