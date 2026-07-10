from enum import Enum


class Topology(Enum):
    BOUNDED = "bounded"
    TOROIDAL = "toroidal"
    SPHERE = "sphere"

    def label(self):
        return {
            Topology.BOUNDED: "Bounded",
            Topology.TOROIDAL: "Toroidal",
            Topology.SPHERE: "Sphere",
        }[self]

    def next(self):
        order = (Topology.BOUNDED, Topology.TOROIDAL, Topology.SPHERE)
        idx = order.index(self)
        return order[(idx + 1) % len(order)]

    def prev(self):
        order = (Topology.BOUNDED, Topology.TOROIDAL, Topology.SPHERE)
        idx = order.index(self)
        return order[(idx - 1) % len(order)]

    @classmethod
    def from_toroidal(cls, toroidal):
        return cls.TOROIDAL if toroidal else cls.BOUNDED
