import json
import at
from lat2db.tools.factories.pyat import factory


def bessyii_pyat_lattice_from_dics(seq, energy: float = 1.7185e9):
    r = at.Lattice(seq, name="BESSY II storage ring", energy=energy)
    r.enable_6d()
    r.cavpts = "CAV*"
    r.set_cavity_phase(cavpts=r.cavpts)
    return r


def bessyii_pyat_lattice(filename: str, energy: float = 1.7185e9) -> at.Lattice:

    with open(filename, "rt") as fp:
        d = json.load(fp)
    seq = factory(d, energy=energy)
    return bessyii_pyat_lattice_from_dics(seq, energy=energy)
