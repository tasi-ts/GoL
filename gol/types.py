"""Shared type aliases for board cells (flat coords vs geodesic mesh ids)."""

from typing import TypeAlias, TypeVar

Coord: TypeAlias = tuple[int, int]
MeshId: TypeAlias = int
CellT = TypeVar("CellT")
