
from .bessyii_pyat_lattice import bessyii_pyat_lattice
from ..pyat_simulator.accelerator_simulator import PyATAcceleratorSimulator
from ..pyat_simulator.simulator_backend import SimulatorBackend
from ...core.bl.delta_backend import DeltaBackendRWProxy, StateCache
from ...core.interfaces.backend.backend import BackendRW


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
