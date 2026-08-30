"""Geodesic icosahedron mesh: subdivision, dual-cell adjacency, and render polygons."""

import math

import numpy as np
from numpy.typing import NDArray

PHI = (1.0 + math.sqrt(5.0)) / 2.0

Float64Array = NDArray[np.float64]

# Icosahedron vertices (before normalization).
_ICO_VERTS: Float64Array = np.array(
    [
        (-1, PHI, 0),
        (1, PHI, 0),
        (-1, -PHI, 0),
        (1, -PHI, 0),
        (0, -1, PHI),
        (0, 1, PHI),
        (0, -1, -PHI),
        (0, 1, -PHI),
        (PHI, 0, -1),
        (PHI, 0, 1),
        (-PHI, 0, -1),
        (-PHI, 0, 1),
    ],
    dtype=np.float64,
)

# 20 triangular faces (vertex indices).
_ICO_FACES: list[tuple[int, int, int]] = [
    (0, 11, 5),
    (0, 5, 1),
    (0, 1, 7),
    (0, 7, 10),
    (0, 10, 11),
    (1, 5, 9),
    (5, 11, 4),
    (11, 10, 2),
    (10, 7, 6),
    (7, 1, 8),
    (3, 9, 4),
    (3, 4, 2),
    (3, 2, 6),
    (3, 6, 8),
    (3, 8, 9),
    (4, 9, 5),
    (2, 4, 11),
    (6, 2, 10),
    (8, 6, 7),
    (9, 8, 1),
]


def _normalize(vectors: Float64Array) -> Float64Array:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms


def _edge_key(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


class GeodesicMesh:
    """Class-I geodesic sphere at frequency nu (nu >= 1).

    Cells correspond to mesh vertices (dual Goldberg polyhedron faces).
    Cell count: 10 * nu^2 + 2.
    """

    def __init__(self, frequency: int) -> None:
        if frequency < 1:
            raise ValueError("frequency must be >= 1")
        self.frequency = frequency
        vertices, faces = self._subdivide_icosahedron(frequency)
        self.vertices = _normalize(vertices)
        self.faces = faces
        self.cell_count = len(self.vertices)
        self.adjacency = self._build_adjacency()
        self.cell_polygons = self._build_cell_polygons()
        self.cell_centers = self.vertices.copy()

    @staticmethod
    def expected_cell_count(frequency: int) -> int:
        return 10 * frequency * frequency + 2

    def _subdivide_icosahedron(
        self, nu: int
    ) -> tuple[Float64Array, list[tuple[int, int, int]]]:
        base = _normalize(_ICO_VERTS.copy())
        vertex_map: dict[tuple[tuple[int, int], ...], int] = {}
        vertices: list[Float64Array] = []

        def canonical_key(
            ia: int, ib: int, ic: int, i: int, j: int
        ) -> tuple[tuple[int, int], ...]:
            qa = nu - i - j
            qb = i
            qc = j
            parts: list[tuple[int, int]] = []
            for ico_v, weight in ((ia, qa), (ib, qb), (ic, qc)):
                if weight > 0:
                    parts.append((ico_v, weight))
            return tuple(sorted(parts))

        def get_vertex(
            ia: int,
            ib: int,
            ic: int,
            i: int,
            j: int,
            va: Float64Array,
            vb: Float64Array,
            vc: Float64Array,
        ) -> int:
            key = canonical_key(ia, ib, ic, i, j)
            if key not in vertex_map:
                w_a = (nu - i - j) / nu
                w_b = i / nu
                w_c = j / nu
                point = w_a * va + w_b * vb + w_c * vc
                vertex_map[key] = len(vertices)
                vertices.append(point)
            return vertex_map[key]

        faces: list[tuple[int, int, int]] = []
        for ia, ib, ic in _ICO_FACES:
            va, vb, vc = base[ia], base[ib], base[ic]
            grid = [
                [
                    get_vertex(ia, ib, ic, i, j, va, vb, vc)
                    for j in range(nu - i + 1)
                ]
                for i in range(nu + 1)
            ]
            for i in range(nu):
                for j in range(nu - i):
                    a = grid[i][j]
                    b = grid[i + 1][j]
                    c = grid[i][j + 1]
                    faces.append((a, b, c))
                    if i + j < nu - 1:
                        d = grid[i + 1][j + 1]
                        faces.append((b, d, c))

        return np.array(vertices, dtype=np.float64), faces

    def _build_adjacency(self) -> list[set[int]]:
        adjacency: list[set[int]] = [set() for _ in range(self.cell_count)]
        for ia, ib, ic in self.faces:
            for a, b in ((ia, ib), (ib, ic), (ic, ia)):
                adjacency[a].add(b)
                adjacency[b].add(a)
        return adjacency

    def _build_cell_polygons(self) -> list[list[Float64Array]]:
        # For each vertex, collect incident triangle centroids in cyclic order.
        edge_to_triangles: dict[
            tuple[int, int], list[tuple[int, Float64Array, int, int]]
        ] = {}
        for tri_idx, (ia, ib, ic) in enumerate(self.faces):
            centroid = _normalize(
                np.array(
                    [
                        self.vertices[ia]
                        + self.vertices[ib]
                        + self.vertices[ic]
                    ]
                )
            )[0]
            for a, b in ((ia, ib), (ib, ic), (ic, ia)):
                key = _edge_key(a, b)
                edge_to_triangles.setdefault(key, []).append((tri_idx, centroid, a, b))

        polygons: list[list[Float64Array]] = []
        for vid in range(self.cell_count):
            incident: list[tuple[int, Float64Array]] = []
            seen_tris: set[int] = set()
            for neighbor in self.adjacency[vid]:
                key = _edge_key(vid, neighbor)
                for tri_idx, centroid, a, b in edge_to_triangles.get(key, []):
                    if vid in (a, b) and tri_idx not in seen_tris:
                        seen_tris.add(tri_idx)
                        incident.append((neighbor, centroid))
            if not incident:
                polygons.append([self.vertices[vid]])
                continue
            # Order neighbors cyclically around vid using cross-product sign.
            center = self.vertices[vid]
            ref = incident[0][1] - center
            ref = ref - np.dot(ref, center) * center
            ref_norm = np.linalg.norm(ref)
            if ref_norm == 0:
                polygons.append([c for _, c in incident])
                continue
            ref = ref / ref_norm
            axis = center / np.linalg.norm(center)
            perp = np.cross(axis, ref)

            def angle(item: tuple[int, Float64Array]) -> float:
                _, pt = item
                vec = pt - center
                vec = vec - np.dot(vec, center) * center
                vec_norm = np.linalg.norm(vec)
                if vec_norm == 0:
                    return 0.0
                vec = vec / vec_norm
                return math.atan2(np.dot(vec, perp), np.dot(vec, ref))

            ordered = [centroid for _, centroid in sorted(incident, key=angle)]
            polygons.append(ordered)
        return polygons
