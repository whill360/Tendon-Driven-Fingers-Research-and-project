"""Data structures for tendon networks.

A Tendon is a single cable with moment arms at the three finger joints
(MCP, PIP, DIP) and a max applied force. A TendonNetwork bundles tendons
into an actuation scheme — that's the unit the rest of the code operates on.

Sign convention: positive moment arm = flexion contribution at that joint,
negative = extension. Units: moment arms in mm, force in N, torque in N*mm.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Sequence

import numpy as np


@dataclass
class Tendon:
    name: str
    moment_arms: np.ndarray  # shape (3,): [MCP, PIP, DIP] in mm
    max_force: float          # N

    def __post_init__(self) -> None:
        self.moment_arms = np.asarray(self.moment_arms, dtype=float)
        if self.moment_arms.shape != (3,):
            raise ValueError(
                f"moment_arms for tendon {self.name!r} must be shape (3,), "
                f"got {self.moment_arms.shape}"
            )
        if self.max_force < 0:
            raise ValueError(f"max_force for tendon {self.name!r} must be >= 0")

    @property
    def basis_vector(self) -> np.ndarray:
        """Torque vector produced per 1 N of tension on this tendon."""
        return self.moment_arms.copy()

    @property
    def max_torque_vector(self) -> np.ndarray:
        """Torque vector produced at max tendon force."""
        return self.max_force * self.moment_arms


@dataclass
class TendonNetwork:
    name: str
    tendons: List[Tendon] = field(default_factory=list)

    def add(self, tendon: Tendon) -> "TendonNetwork":
        self.tendons.append(tendon)
        return self

    def __len__(self) -> int:
        return len(self.tendons)

    def __iter__(self) -> Iterable[Tendon]:
        return iter(self.tendons)

    @property
    def names(self) -> List[str]:
        return [t.name for t in self.tendons]

    @property
    def basis_matrix(self) -> np.ndarray:
        """Stack of basis vectors, shape (n_tendons, 3)."""
        if not self.tendons:
            return np.zeros((0, 3))
        return np.stack([t.basis_vector for t in self.tendons])

    @property
    def max_torques(self) -> np.ndarray:
        """Stack of max-force torque vectors, shape (n_tendons, 3)."""
        if not self.tendons:
            return np.zeros((0, 3))
        return np.stack([t.max_torque_vector for t in self.tendons])

    def torque_at(self, forces: Sequence[float]) -> np.ndarray:
        """Net joint torque for a given vector of tendon tensions (length n_tendons)."""
        f = np.asarray(forces, dtype=float)
        if f.shape != (len(self),):
            raise ValueError(
                f"forces must have shape ({len(self)},), got {f.shape}"
            )
        return f @ self.basis_matrix
