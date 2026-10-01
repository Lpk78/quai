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
        # Written as `not >= 0` rather than `< 0` so that NaN is refused: every comparison with
        # NaN is False, so `NaN < 0` would accept it and the solver's `weight > max_weight` would
        # then be False for every box, removing the limit instead of enforcing it. That is the one
        # invalid input that produces a plan which looks valid, which is what #15 and #23 exist to
        # prevent. `inf` (the default, no limit) and `0` (nothing may be loaded) both pass.
        if not self.max_weight >= 0:
            raise ValueError(f"container: max_weight must be a number that is not negative, got "
                             f"{self.max_weight}")

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
        # Container refuses a zero side, but a plan must not crash if one gets through anyway.
        if self.container.volume <= 0:
            return 0.0
        used = sum(p.dx * p.dy * p.dz for p in self.placements)
        return used / self.container.volume

    @property
    def total_weight(self) -> float:
        return sum(p.box.weight for p in self.placements)

    @property
    def loading_order(self) -> list[str]:
        """The boxes that were loaded, in the order they went in: first loaded first."""
        return [p.box.id for p in self.placements]
