"""Core data models. All lengths are in centimetres, all weights in kilograms.

Axes of the container:
    x = length (0 is the back wall, the far end from the doors)
    y = width
    z = height (0 is the floor)
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Box:
    id: str
    length: int
    width: int
    height: int
    weight: float = 0.0

    def __post_init__(self) -> None:
        for name in ("length", "width", "height"):
            value = getattr(self, name)
            if value <= 0:
                raise ValueError(f"box {self.id}: {name} must be greater than 0, got {value}")
        if self.weight < 0:
            raise ValueError(f"box {self.id}: weight cannot be negative, got {self.weight}")

    @property
    def volume(self) -> int:
        return self.length * self.width * self.height

    def orientations(self) -> list[tuple[int, int, int]]:
        """Footprint rotations only: the box always stays upright (this side up)."""
        upright = [(self.length, self.width, self.height), (self.width, self.length, self.height)]
        return list(dict.fromkeys(upright))  # drop the duplicate for square footprints


@dataclass(frozen=True)
class Container:
    length: int
    width: int
    height: int
    max_weight: float = float("inf")

    def __post_init__(self) -> None:
        for name in ("length", "width", "height"):
            value = getattr(self, name)
            if value <= 0:
                raise ValueError(f"container: {name} must be greater than 0, got {value}")
        if self.max_weight < 0:
            raise ValueError(f"container: max_weight cannot be negative, got {self.max_weight}")

    @property
    def volume(self) -> int:
        return self.length * self.width * self.height


@dataclass(frozen=True)
class Placement:
    """A box placed at (x, y, z) with its rotated dimensions (dx, dy, dz)."""
    box: Box
    x: int
    y: int
    z: int
    dx: int
    dy: int
    dz: int

    @property
    def x2(self) -> int:
        return self.x + self.dx

    @property
    def y2(self) -> int:
        return self.y + self.dy

    @property
    def z2(self) -> int:
        return self.z + self.dz


@dataclass
class Plan:
    container: Container
    placements: list[Placement]
    unplaced: list[Box]

    @property
    def fill_rate(self) -> float:
        used = sum(p.dx * p.dy * p.dz for p in self.placements)
        return used / self.container.volume

    @property
    def total_weight(self) -> float:
        return sum(p.box.weight for p in self.placements)
