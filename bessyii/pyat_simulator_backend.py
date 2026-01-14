from accml.core.bl.delta_backend import DeltaBackendRWProxy, StateCache
from accml.core.interfaces.backend.backend import BackendRW
from accml.custom.simulators.pyat.accelerator_simulator import PyATAcceleratorSimulator
from accml.custom.simulators.pyat.simulator_backend import SimulatorBackend

from .bessyii_pyat_lattice import bessyii_pyat_lattice


def simulator_backend() -> BackendRW:
    return DeltaBackendRWProxy(
        backend=SimulatorBackend(
            name="BESSY_on_PyAT",
            acc=PyATAcceleratorSimulator(
                at_lattice=bessyii_pyat_lattice(
                    filename="bessy2_storage_ring_reflat.json"
                )
            ),
        ),
        cache=StateCache(name="BESSY_on_PyAT_delta_state_cache"),
    )
