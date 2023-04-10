from dataclasses import dataclass
from math import pi
from typing import Iterable, Tuple, Union

from robotlib.geometry import trunc_angle
from robotlib.utils import build_repr


Angle = float
Length = float


@dataclass
class Link:
    length: Length


class Joint:
    def __init__(
            self,
            angle: Angle,
            min_angle: Angle = -pi,
            max_angle: Angle = pi,
            resolution: Angle = 0.,
    ):
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.resolution = resolution
        self.angle = angle

    @property
    def angle(self) -> Angle:
        return self._angle

    @angle.setter
    def angle(self, angle: Angle) -> None:
        angle = trunc_angle(angle)

        if self.resolution > 0:
            ticks = round(angle / self.resolution)
            angle = self.resolution * ticks

        self._angle = min(max(self.min_angle, angle), self.max_angle)

    def __repr__(self) -> str:
        return build_repr(self, 'angle', 'min_angle', 'max_angle')


@dataclass
class System:
    def __init__(
            self,
            joints: Iterable[Union['Joint', Angle]],
            links: Iterable[Union['Link', Length]],
    ):
        joints = tuple(
            joint if isinstance(joint, Joint) else Joint(joint)
            for joint in joints
        )

        links = tuple(
            link if isinstance(link, Link) else Link(link)
            for link in links
        )

        assert len(joints) == len(links), (
            f'Number of joints and links must be equal. '
            f'len(joints)={len(joints)}; len(links)={len(links)}'
        )

        self._joints = joints
        self._links = links

    @staticmethod
    def from_links(*lengths: Length) -> 'System':
        return System(
            joints=(Joint(0) for _ in range(len(lengths))),
            links=(Link(l) for l in lengths),
        )

    @property
    def joints(self) -> Tuple['Joint']:
        return self._joints

    @property
    def links(self) -> Tuple['Link']:
        return self._links

    @property
    def joints_links(self) -> Iterable[Tuple['Joint', 'Link']]:
        yield from zip(self.joints, self.links)

    @property
    def angles(self) -> Tuple[Angle]:
        return tuple(joint.angle for joint in self.joints)

    @angles.setter
    def angles(self, angles: Tuple[Angle]) -> None:
        assert len(angles) == len(self.joints), (
            f'Expected number of angles to equal number of joints. '
            f'len(angles)={len(angles)}; len(joints)={len(self.joints)}'
        )

        for joint, angle in zip(self.joints, angles):
            joint.angle = angle

    @property
    def dof(self) -> int:
        return len(self.joints)

    @property
    def max_length(self) -> Length:
        return sum(link.length for link in self.links)

    def __str__(self) -> str:
        parts = []
        for joint, link in self.joints_links:
            angle = Angle(joint.angle)
            parts.append(f'( {angle:.3} rad )--[ {link.length} ]')

        return '--'.join(parts)
