from enum import Enum
from typing import Self


class Topology(Enum):
    BOUNDED = "bounded"
    TOROIDAL = "toroidal"
    SPHERE = "sphere"

    def label(self) -> str:
        return {
            Topology.BOUNDED: "Bounded",
            Topology.TOROIDAL: "Toroidal",
            Topology.SPHERE: "Sphere",
        }[self]

    def next(self) -> Self:
        order = (Topology.BOUNDED, Topology.TOROIDAL, Topology.SPHERE)
        idx = order.index(self)
        return order[(idx + 1) % len(order)]

    def prev(self) -> Self:
        order = (Topology.BOUNDED, Topology.TOROIDAL, Topology.SPHERE)
        idx = order.index(self)
        return order[(idx - 1) % len(order)]

    @classmethod
    def from_toroidal(cls, toroidal: bool) -> Self:
        return cls.TOROIDAL if toroidal else cls.BOUNDED
