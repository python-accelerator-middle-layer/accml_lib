import json
import at
from lat2db.tools.factories.pyat import factory


def bessyii_pyat_lattice(filename: str, energy: float=1.7185e9) -> at.Lattice:

    with open(filename, "rt") as fp:
        d = json.load(fp)
    seq = factory(d, energy=energy)

    r = at.Lattice(seq, name="BESSY II storage ring", energy=energy)
    r.enable_6d()
    r.cavpts = "CAV*"
    r.set_cavity_phase(cavpts=r.cavpts)
    return r