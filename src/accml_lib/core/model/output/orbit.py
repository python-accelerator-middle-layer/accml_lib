"""Orbit model as used at BESSY II

Based on 4 button bpms. Button data made available next to
x and y

Todo:
    can that be the start for a more general orbit
    model
"""
import functools
from dataclasses import dataclass
from typing import Hashable, Sequence, Dict


@dataclass
class BPMPosition:
    """transversal position as read by a single bpm

    If not available marked as nan. 64 bits provide
    enough data to store 32 bit int without conversion
    loss.

    Note bpm data are in nm

    Todo:
        naming that's more universal than x and y
        e.g. hor(izontal) and vert(ical)

        Will be an interesting concept e.g. at
        Novosibirsk's recovery linac. Then these
        should be rather dispersion_plan /
        non dispersion plane
    """

    x: float
    y: float


@dataclass
class BPMButtons:
    """
    todo:
        consider renaming bpm buttons to give them more meaning
    """

    a: float
    b: float
    c: float
    d: float


@dataclass
class BPMReading:
    name: Hashable
    pos: BPMPosition
    btns: BPMButtons


@dataclass
class Orbit:
    orbit: Sequence[BPMReading]

    def identifiers(self) -> Sequence[Hashable]:
        return tuple(self._lut.keys())

    def get_element(self, id_: Hashable) -> BPMReading:
        """
        Todo:
            consider to return a more descriptive Exception if
            identifier is not found
        """
        return self._lut[id_]

    @functools.cached_property
    def _lut(self) -> Dict[Hashable, BPMReading]:
        return {elem.name: elem for elem in self.orbit}
